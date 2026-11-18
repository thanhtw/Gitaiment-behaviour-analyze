"""Independently audit points-per-minute summaries and ANOVA from source saves."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.oneway import anova_oneway

from ..data_io import VERSIONS, load_records, source_file


def anova_from_groups(groups):
    """Derive classical ANOVA and effect sizes from observed raw groups."""
    groups = [np.asarray(g, dtype=float) for g in groups]
    groups = [g[np.isfinite(g)] for g in groups]
    n, k = sum(map(len, groups)), len(groups)
    if k < 2 or any(len(g) < 2 for g in groups):
        raise ValueError('ANOVA requires at least two observed values in each of two groups')
    grand = np.concatenate(groups).mean()
    ss_between = sum(len(g) * (g.mean() - grand)**2 for g in groups)
    ss_within = sum(np.sum((g - g.mean())**2) for g in groups)
    df_between, df_within = k-1, n-k
    ms_within = ss_within / df_within
    f_value = (ss_between / df_between) / ms_within if ms_within else np.nan
    total = ss_between + ss_within
    return dict(n_observed=n, df_between=df_between, df_within=df_within,
                ss_between=ss_between, ss_within=ss_within, ss_total=total,
                F=f_value, p=stats.f.sf(f_value, df_between, df_within),
                eta_squared=ss_between/total if total else np.nan,
                omega_squared=(ss_between-df_between*ms_within)/(total+ms_within) if total else np.nan)


def run(output_dir):
    output_dir = Path(output_dir)
    rows = []
    for version in VERSIONS:
        for player in load_records(source_file(version, 'GEG-database.playersavedatas')):
            record = player.get('saveData', {}).get('gameRecordData', {})
            rows.append({'ID': str(player['username']), 'dataVersion': version,
                         'source_score': record.get('totalStageScore', np.nan),
                         'source_duration_seconds': record.get('totalPlayTime', np.nan)})
    source = pd.DataFrame(rows)
    # Match the established latest-snapshot rule, without the extractor's zero defaults.
    source = source.drop_duplicates('ID', keep='last')
    for col in ('source_score', 'source_duration_seconds'):
        source[col] = pd.to_numeric(source[col], errors='coerce')
    source['source_duration_minutes'] = source.source_duration_seconds / 60
    source['recalculated_efficiency'] = source.source_score.div(source.source_duration_minutes).where(
        source.source_duration_minutes.gt(0))
    assignments = pd.read_csv(output_dir / 'analysis_kmeans_assignments.csv', dtype={'ID': str})
    audit = assignments[['ID', 'Cluster', 'LearningEfficiency']].merge(source, on='ID', how='left', validate='one_to_one')
    audit['matches_saved_feature'] = np.isclose(audit.LearningEfficiency, audit.recalculated_efficiency,
                                               rtol=1e-10, atol=1e-8, equal_nan=True)
    audit['status'] = np.select([audit.source_score.isna(), audit.source_duration_seconds.isna(),
                                audit.source_duration_seconds.le(0)],
                               ['missing_source_score', 'missing_source_duration', 'nonpositive_duration'],
                               default='observed')
    audit['duration_under_1min'] = audit.source_duration_seconds.between(0, 60, inclusive='neither')
    audit.to_csv(output_dir / 'analysis_efficiency_source_audit.csv', index=False)
    descriptive = audit.groupby('Cluster').agg(
        cluster_n=('ID', 'size'), n_observed=('recalculated_efficiency', 'count'),
        mean=('recalculated_efficiency', 'mean'), sd=('recalculated_efficiency', 'std'),
        median=('recalculated_efficiency', 'median'), minimum=('recalculated_efficiency', 'min'),
        maximum=('recalculated_efficiency', 'max'))
    descriptive['n_missing'] = descriptive.cluster_n - descriptive.n_observed
    descriptive.to_csv(output_dir / 'analysis_efficiency_verified_descriptives.csv')
    raw_groups = [g.recalculated_efficiency.dropna().to_numpy() for _, g in audit.groupby('Cluster')]
    results = []
    for scale, groups in [('raw_points_per_minute', raw_groups),
                          ('log1p_points_per_minute', [np.log1p(g) for g in raw_groups])]:
        result = dict(scale=scale, **anova_from_groups(groups))
        result['scipy_F'], result['scipy_p'] = stats.f_oneway(*groups)
        result['manual_matches_scipy'] = bool(np.isclose(result['F'], result['scipy_F'], rtol=1e-10))
        welch = anova_oneway(groups, use_var='unequal', welch_correction=True)
        result.update(welch_F=float(welch.statistic), welch_p=float(welch.pvalue),
                      welch_df1=float(welch.df[0]), welch_df2=float(welch.df[1]),
                      kruskal_H=float(stats.kruskal(*groups).statistic),
                      kruskal_p=float(stats.kruskal(*groups).pvalue),
                      levene_median_p=float(stats.levene(*groups, center='median').pvalue))
        results.append(result)
    pd.DataFrame(results).to_csv(output_dir / 'analysis_efficiency_verified_tests.csv', index=False)
    saved_tests = pd.read_csv(output_dir / 'analysis_cluster_group_comparisons.csv')
    saved = saved_tests.loc[saved_tests.feature.eq('LearningEfficiency')].iloc[0]
    saved_profiles = pd.read_csv(output_dir / 'analysis_cluster_profiles.csv').set_index('Cluster')
    summary = {
        'definition': 'cumulative game score / (cumulative saved play time in seconds / 60)',
        'unit': 'game-score points per minute; not measured pre/post learning gain',
        'n_retained': len(audit), 'n_observed': int(audit.recalculated_efficiency.notna().sum()),
        'n_missing': int(audit.recalculated_efficiency.isna().sum()),
        'mismatched_feature_rows': int((~audit.matches_saved_feature).sum()),
        'profile_means_match': bool(np.allclose(descriptive['mean'], saved_profiles.LearningEfficiency_mean)),
        'profile_sds_match': bool(np.allclose(descriptive.sd, saved_profiles.LearningEfficiency_std)),
        'raw_F_matches_existing_output': bool(np.isclose(results[0]['F'], saved.anova_F)),
        'raw_eta_squared_matches_existing_output': bool(np.isclose(results[0]['eta_squared'], saved.eta_squared)),
        'short_duration_observations': int(audit.duration_under_1min.sum()),
        'limitations': ['The source manuscript is preserved; analysis does not edit its printed entries.',
                       'Efficiency is a clustering input; between-cluster tests are circular and exploratory.',
                       'Raw descriptive statistics require raw-scale tests; log1p tests are a separate sensitivity analysis.',
                       'Missing/nonpositive-duration efficiency values are excluded from inference, not median-imputed.',
                       'Source play-time units follow the existing code; logger implementation is not available for independent unit validation.']}
    (output_dir / 'analysis_efficiency_verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary
