"""Audited noise filtering, two-score K selection, and cluster profile analysis.

Input is the combined two-version ``analysis_per_user_combined.csv`` produced by
``run_analysis.py``. Outputs are written beside that file.
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Avoid the documented Windows MKL K-means memory leak and warning flood.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway, kruskal, levene
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from statsmodels.stats.oneway import anova_oneway

RANDOM_STATE = 42
MAX_K = 10
N_INIT = 50
LOF_NEIGHBORS = 20
LOF_THRESHOLD = 2.0
RATE_FEATURES = ["AccuracyRate", "PerfectQuestRate", "HelpDependencyRatio"]

# Behavioral and derived variables define the clusters. LearningEfficiency
# contains score, so subsequent TotalScore comparisons are not independent.
FEATURES = [
    "CommandsExecuted", "CorrectActions", "FailedActions", "HintQuests",
    "AnswerQuests", "PlayDurationMinutes", "LeaderboardInteractions",
    "LearningEfficiency", "AccuracyRate", "PerfectQuestRate",
    "HelpDependencyRatio",
]
OUTCOMES = [
    "StagesCleared", "GameProgress", "TotalScore",
]

FEATURE_DEFINITIONS = {
    "CommandsExecuted": "Cumulative number of Git commands executed.",
    "CorrectActions": "Logged Correct Action events, including tutorial UI actions; not a count of successful Git commands.",
    "FailedActions": "Number of failed game-action events.",
    "HintQuests": "Number of quests completed using a hint.",
    "AnswerQuests": "Number of quests completed using an answer.",
    "PlayDurationMinutes": "Total active game time in minutes.",
    "LeaderboardInteractions": "Number of leaderboard or ranking checks.",
    "LearningEfficiency": "Total score divided by play duration in minutes.",
    "AccuracyRate": "Correct actions divided by correct plus failed actions.",
    "PerfectQuestRate": "Perfect quest completions divided by completed quests.",
    "HelpDependencyRatio": "Hint-assisted plus answer-assisted quests divided by completed quests.",
}
OUTCOME_DEFINITIONS = {
    "StagesCleared": "Saved cumulative stage-clear count, including repeat clears; not unique stages.",
    "GameProgress": "Cumulative game-progress percentage; used only for profiling.",
    "TotalScore": "Cumulative stage score; used only for profiling.",
}


def build_python_feature_table(source):
    """Derive clustering variables directly from the combined per-user CSV."""
    raw = pd.read_csv(source)
    number = lambda name: pd.to_numeric(raw[name], errors="coerce")
    safe_ratio = lambda top, bottom: np.divide(
        top, bottom, out=np.full(len(raw), np.nan), where=np.asarray(bottom) > 0
    )
    completed = number("event_quests_completed")
    actions = number("event_correct_actions") + number("event_failed_actions")
    duration_minutes = number("record_totalPlayTime") / 60
    total_score = number("record_totalStageScore")
    table = pd.DataFrame({
        "ID": raw["username"],
        "CommandsExecuted": number("record_totalCommandExecuteTimes"),
        "CorrectActions": number("event_correct_actions"),
        "FailedActions": number("event_failed_actions"),
        "HintQuests": number("event_hint_used_quests"),
        "AnswerQuests": number("event_answer_used_quests"),
        "PlayDurationMinutes": duration_minutes,
        "LeaderboardInteractions": number("event_leaderboard_checks"),
        "LearningEfficiency": safe_ratio(total_score, duration_minutes),
        "AccuracyRate": safe_ratio(number("event_correct_actions"), actions),
        "PerfectQuestRate": safe_ratio(number("event_perfect_quests"), completed),
        "HelpDependencyRatio": safe_ratio(
            number("event_hint_used_quests") + number("event_answer_used_quests"), completed
        ),
        "StagesCleared": number("record_totalTimesStageClear"),
        "GameProgress": number("record_totalGameProgress"),
        "TotalScore": total_score,
    })
    return table


def prepare_features(df):
    selected = [name for name in FEATURES if name in df.columns]
    numeric = df[selected].apply(pd.to_numeric, errors="coerce")
    # A constant variable carries no clustering information.
    numeric = numeric.loc[:, numeric.nunique(dropna=True) > 1]
    if numeric.shape[1] < 2:
        raise ValueError("At least two non-constant numeric features are required")
    imputed = SimpleImputer(strategy="median").fit_transform(numeric)
    transformed = pd.DataFrame(imputed, columns=numeric.columns)
    log_columns = [name for name in numeric.columns if name not in RATE_FEATURES]
    transformed[log_columns] = np.log1p(transformed[log_columns])
    scaled = StandardScaler().fit_transform(transformed)
    return numeric.columns.tolist(), imputed, scaled


def filter_noise(df):
    """Audit invalid/inactive rows and conservative local outliers before choosing k.

    LOF > 2 is fixed independently of cluster scores; no removal fraction is forced.
    Statistical outliers are candidate noise, not proven erroneous participants.
    """
    numeric = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    invalid = ((numeric < 0).any(axis=1) | np.isinf(numeric).any(axis=1)
               | (numeric[RATE_FEATURES] > 1).any(axis=1))
    activity = ["CommandsExecuted", "CorrectActions", "FailedActions", "HintQuests",
                "AnswerQuests", "PlayDurationMinutes", "LeaderboardInteractions"]
    inactive = numeric[activity].fillna(0).eq(0).all(axis=1)
    audit = pd.DataFrame({"ID": df["ID"], "reason": "retained", "lof_score": np.nan})
    audit.loc[inactive, "reason"] = "no_observed_activity"
    audit.loc[invalid, "reason"] = "invalid_feature_value"
    valid = df.loc[~(invalid | inactive)].copy()
    if len(valid) < 4:
        raise ValueError("Too few valid active participants for clustering")
    _, _, scaled = prepare_features(valid)
    detector = LocalOutlierFactor(n_neighbors=min(LOF_NEIGHBORS, len(valid) - 1))
    detector.fit_predict(scaled)
    scores = -detector.negative_outlier_factor_
    audit.loc[valid.index, "lof_score"] = scores
    audit.loc[valid.index[scores > LOF_THRESHOLD], "reason"] = "local_outlier"
    audit["included"] = audit["reason"].eq("retained")
    cleaned = df.loc[audit["included"]].copy()
    if len(cleaned) < 4:
        raise ValueError("Too few participants remain after noise filtering")
    return cleaned, audit, valid


def calculate_cluster_validity(values, max_k=MAX_K):
    """Evaluate only silhouette and Calinski-Harabasz on the same K-means fits."""
    rows = []
    max_k = min(max_k, len(values) - 1, len(np.unique(values, axis=0)))
    if max_k < 2:
        raise ValueError("At least two distinct feature vectors are required")
    for k in range(2, max_k + 1):
        print(f"Silhouette and Calinski-Harabasz: k={k}/{max_k}", flush=True)
        model = KMeans(n_clusters=k, n_init=N_INIT, random_state=RANDOM_STATE).fit(values)
        smallest = int(np.bincount(model.labels_, minlength=k).min())
        rows.append({
            'k': k,
            'silhouette': silhouette_score(values, model.labels_),
            'calinski_harabasz': calinski_harabasz_score(values, model.labels_),
            'smallest_group_n': smallest,
            'eligible': smallest >= 2,
        })
    result = pd.DataFrame(rows)
    eligible = result[result['eligible']]
    if eligible.empty:
        raise ValueError("No candidate k avoids singleton clusters; inspect the data")
    recommendations = {}
    for metric in ('silhouette', 'calinski_harabasz'):
        best_k = int(eligible.sort_values([metric, 'k'], ascending=[False, True]).iloc[0]['k'])
        recommendations[metric] = best_k
        result[f'recommended_{metric}'] = result['k'].eq(best_k)
    return result, recommendations


def select_cluster_count(validity):
    """Equal rank weight for both scores; silhouette then smaller K break ties."""
    result = validity.copy()
    eligible = result['eligible']
    if not eligible.any():
        raise ValueError("No eligible cluster counts")
    for metric in ('silhouette', 'calinski_harabasz'):
        result.loc[eligible, f'{metric}_rank'] = result.loc[eligible, metric].rank(
            ascending=False, method='min')
    result['combined_rank'] = result['silhouette_rank'] + result['calinski_harabasz_rank']
    best = result.loc[eligible].sort_values(
        ['combined_rank', 'silhouette', 'k'], ascending=[True, False, True]).iloc[0]
    selected_k = int(best['k'])
    agreement = bool(best['silhouette_rank'] == 1 and best['calinski_harabasz_rank'] == 1)
    result['selected'] = result['k'].eq(selected_k)
    return result, selected_k, agreement


def profile_clusters(df, feature_names, scaled, labels):
    """Use observed values for summaries/tests; imputation is only for clustering."""
    raw = df[feature_names + OUTCOMES].apply(pd.to_numeric, errors="coerce").replace(
        [np.inf, -np.inf], np.nan)
    zscores = pd.DataFrame(scaled, columns=feature_names, index=df.index)
    raw["Cluster"] = labels
    zscores["Cluster"] = labels

    profiles = raw.groupby("Cluster").agg(["count", "mean", "std", "median"])
    profiles.columns = [f"{feature}_{stat}" for feature, stat in profiles.columns]
    cluster_sizes = raw.groupby("Cluster").size()
    profiles.insert(0, "cluster_n", cluster_sizes)
    for feature in feature_names + OUTCOMES:
        profiles[f"{feature}_missing"] = cluster_sizes - profiles[f"{feature}_count"]
    profiles = profiles.reset_index()
    standardized_profiles = zscores.groupby("Cluster").mean().reset_index()

    comparisons = []
    clusters = sorted(np.unique(labels))
    for feature in feature_names + OUTCOMES:
        groups = [raw.loc[raw["Cluster"] == cluster, feature].dropna().to_numpy() for cluster in clusters]
        valid = len(groups) >= 2 and all(len(group) >= 2 for group in groups)
        constant = valid and np.ptp(np.concatenate(groups)) == 0
        status = 'insufficient_observed_values' if not valid else ('constant_indicator' if constant else 'ok')
        anova_f, anova_p = f_oneway(*groups) if valid and not constant else (np.nan, np.nan)
        kw_h, kw_p = kruskal(*groups) if valid and not constant else (np.nan, np.nan)
        # Median-centered Levene is a variance diagnostic, not automatic test selection.
        deviations = [np.abs(group - np.median(group)) for group in groups] if valid else []
        variance_check_defined = valid and any(np.var(group) > 0 for group in deviations)
        levene_f, levene_p = levene(*groups, center='median') if variance_check_defined else (np.nan, np.nan)
        welch_status = status
        welch_f = welch_p = welch_df1 = welch_df2 = np.nan
        if valid and not constant:
            if all(np.var(group, ddof=1) > 0 for group in groups):
                welch = anova_oneway(groups, use_var='unequal', welch_correction=True)
                welch_f, welch_p = welch.statistic, welch.pvalue
                welch_df1, welch_df2 = welch.df
            else:
                welch_status = 'zero_variance_group'
        grand_mean = raw[feature].mean()
        ss_between = sum(len(group) * (group.mean() - grand_mean) ** 2 for group in groups if len(group))
        ss_total = np.square(raw[feature] - grand_mean).sum()
        comparisons.append({
            "feature": feature,
            "n_observed": int(raw[feature].count()),
            "n_missing": int(raw[feature].isna().sum()),
            **{f"cluster_{cluster}_n": len(group) for cluster, group in zip(clusters, groups)},
            "test_status": status,
            "kruskal_small_group": any(len(group) < 5 for group in groups),
            "anova_F": anova_f,
            "anova_p": anova_p,
            "welch_F": welch_f,
            "welch_p": welch_p,
            "welch_df_between": welch_df1,
            "welch_df_within": welch_df2,
            "welch_status": welch_status,
            "levene_F": levene_f,
            "levene_p": levene_p,
            "variance_heterogeneity_flag": bool(np.isfinite(levene_p) and levene_p < .05),
            "kruskal_H": kw_h,
            "kruskal_p": kw_p,
            "eta_squared": ss_between / ss_total if ss_total else np.nan,
        })
    comparisons = pd.DataFrame(comparisons).sort_values(
        ["anova_p", "eta_squared"], ascending=[True, False]
    )
    return profiles, standardized_profiles, comparisons


def create_profile_audit(df, feature_names, imputed, labels):
    """Record missing observations and saved counters needing source review."""
    rows = []
    filled = pd.DataFrame(imputed, columns=feature_names, index=df.index)
    for position, (index, row) in enumerate(df.iterrows()):
        for feature in feature_names + OUTCOMES:
            if pd.isna(row[feature]) or not np.isfinite(row[feature]):
                rows.append({'ID': row['ID'], 'Cluster': labels[position], 'feature': feature,
                             'issue': 'missing_observation', 'observed_value': row[feature],
                             'clustering_imputed_value': filled.loc[index, feature] if feature in feature_names else np.nan})
        if row['CommandsExecuted'] == 0 and row['StagesCleared'] > 0:
            rows.append({'ID': row['ID'], 'Cluster': labels[position], 'feature': 'StagesCleared',
                         'issue': 'stage_clears_with_zero_saved_commands_review_only',
                         'observed_value': row['StagesCleared'], 'clustering_imputed_value': np.nan})
    return pd.DataFrame(rows, columns=['ID', 'Cluster', 'feature', 'issue', 'observed_value', 'clustering_imputed_value'])


def create_visualizations(data_dir, validity, selected_k, scaled, labels,
                          standardized_profiles, comparisons):
    """Export each selection score as its own figure, plus cluster profiles."""
    plt.style.use("seaborn-v0_8-whitegrid")
    for metric, title in [('silhouette', 'Silhouette Score'),
                          ('calinski_harabasz', 'Calinski-Harabasz Score')]:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(validity['k'], validity[metric], marker='o', color='#4C78A8')
        ax.axvline(selected_k, color='crimson', linestyle='--', label=f'Selected k = {selected_k} (two-score rule)')
        eligible = validity.loc[validity['eligible']]
        best = eligible.loc[eligible[metric].eq(eligible[metric].max())]
        ax.scatter(best['k'], best[metric], color='green', marker='*', s=170,
                   label='Highest eligible score (ties shown)', zorder=5)
        excluded = validity.loc[~validity['eligible']]
        if len(excluded):
            ax.scatter(excluded['k'], excluded[metric], color='black', marker='x', s=80,
                       label='Singleton solution (excluded)')
        ax.set(xlabel='Number of clusters (k)', ylabel=f'{title} (higher is better)', title=f'{title} by Cluster Count')
        ax.set_xticks(validity['k'])
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(data_dir / f'figure_cluster_{metric}.png', dpi=300)
        plt.close(fig)

    counts = pd.Series(labels).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(counts.index.astype(str), counts.values, color="#4C78A8")
    ax.bar_label(bars); ax.set(xlabel="Cluster", ylabel="Players", title="K-means Cluster Membership")
    fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_sizes.png", dpi=300); plt.close(fig)

    coordinates = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(scaled)
    fig, ax = plt.subplots(figsize=(8, 6))
    for cluster in sorted(np.unique(labels)):
        mask = labels == cluster
        ax.scatter(coordinates[mask, 0], coordinates[mask, 1], label=f"Cluster {cluster}", alpha=.8)
    ax.set(xlabel="Principal component 1", ylabel="Principal component 2", title="Player Clusters (PCA Projection)")
    ax.legend(); fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_pca.png", dpi=300); plt.close(fig)

    matrix = standardized_profiles.set_index("Cluster")
    fig, ax = plt.subplots(figsize=(12, max(3, len(matrix) * .8)))
    image = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=55, ha="right")
    ax.set_yticks(range(len(matrix.index)), [f"Cluster {i}" for i in matrix.index])
    ax.set_title("Standardized Behavioral Cluster Profiles")
    fig.colorbar(image, ax=ax, label="Mean standardized feature (counts log-transformed)")
    fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_profile_heatmap.png", dpi=300); plt.close(fig)

    top = comparisons.nlargest(12, "eta_squared").sort_values("eta_squared")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["feature"], top["eta_squared"], color="#F58518")
    ax.set(xlabel="Eta-squared", title="Largest Differences Between Cluster Profiles")
    fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_group_effects.png", dpi=300); plt.close(fig)


def _run_analysis(data_dir="."):
    data_dir = Path(data_dir)
    df = build_python_feature_table(data_dir / "analysis_per_user_combined.csv")
    original_n = len(df)
    df, noise_audit, unfiltered = filter_noise(df)
    feature_names, imputed, scaled = prepare_features(df)
    validity, recommendations = calculate_cluster_validity(scaled)
    validity, selected_k, agreement = select_cluster_count(validity)
    if df.equals(unfiltered):
        baseline_validity, baseline_recommendations = validity.copy(), recommendations.copy()
    else:
        _, _, baseline_scaled = prepare_features(unfiltered)
        baseline_validity, baseline_recommendations = calculate_cluster_validity(baseline_scaled)
    baseline_validity, baseline_k, _ = select_cluster_count(baseline_validity)
    baseline_validity.to_csv(data_dir / 'analysis_cluster_selection_unfiltered.csv', index=False, encoding='utf-8-sig')
    noise_audit.to_csv(data_dir / 'analysis_cluster_noise_audit.csv', index=False, encoding='utf-8-sig')
    df.to_csv(data_dir / 'analysis_cluster_cleaned_features.csv', index=False, encoding='utf-8-sig')
    warnings = []
    if selected_k == int(validity['k'].max()):
        warnings.append('Selected k is at the search boundary; a global optimum is not established.')
    if not agreement:
        warnings.append('Silhouette and Calinski-Harabasz disagree; selected k is a combined-rank compromise.')
    if selected_k != baseline_k:
        warnings.append('Selection changes when statistical outliers are retained.')
    summary = {
        'input_n': original_n, 'retained_n': len(df), 'excluded_n': original_n - len(df),
        'exclusion_reasons': noise_audit.loc[~noise_audit['included'], 'reason'].value_counts().to_dict(),
        'noise_rule': f'LOF > {LOF_THRESHOLD}, neighbors={LOF_NEIGHBORS}; fixed before selecting k',
        'preprocessing': 'Undefined ratios are median-imputed; log1p non-rate features; standard scaling refit after filtering.',
        'selection_rule': 'Minimum sum of descending silhouette and Calinski-Harabasz ranks among non-singleton solutions; ties use higher silhouette, then smaller k.',
        'selected_k': selected_k, 'metrics_agree': agreement,
        'selected_scores': {metric: float(validity.loc[validity.selected, metric].iloc[0])
                            for metric in ('silhouette', 'calinski_harabasz')},
        'unfiltered_selected_k': baseline_k,
        'recommendations': recommendations, 'unfiltered_recommendations': baseline_recommendations,
        'warnings': warnings,
    }
    (data_dir / 'analysis_cluster_selection_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    model = KMeans(n_clusters=selected_k, n_init=N_INIT, random_state=RANDOM_STATE)
    labels = model.fit_predict(scaled) + 1  # human-readable cluster numbering

    assignments = df.copy()
    assignments.insert(1, "Cluster", labels)
    profiles, standardized_profiles, comparisons = profile_clusters(
        df, feature_names, scaled, labels
    )
    create_profile_audit(df, feature_names, imputed, labels).to_csv(
        data_dir / 'analysis_cluster_profile_audit.csv', index=False, encoding='utf-8-sig')

    validity.to_csv(data_dir / "analysis_cluster_selection_methods.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [{"feature": name, "role": "clustering input", "definition": FEATURE_DEFINITIONS[name]}
         for name in FEATURES] +
        [{"feature": name, "role": "profile outcome", "definition": OUTCOME_DEFINITIONS[name]}
         for name in OUTCOMES]
    ).to_csv(data_dir / "analysis_cluster_feature_dictionary.csv", index=False, encoding="utf-8-sig")
    assignments.to_csv(data_dir / "analysis_kmeans_assignments.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(data_dir / "analysis_cluster_profiles.csv", index=False, encoding="utf-8-sig")
    standardized_profiles.to_csv(
        data_dir / "analysis_cluster_profiles_standardized.csv", index=False, encoding="utf-8-sig"
    )
    comparisons.to_csv(
        data_dir / "analysis_cluster_group_comparisons.csv", index=False, encoding="utf-8-sig"
    )
    centers = pd.DataFrame(model.cluster_centers_, columns=feature_names)
    centers.insert(0, "Cluster", np.arange(1, selected_k + 1))
    centers.to_csv(data_dir / "analysis_kmeans_centers.csv", index=False, encoding="utf-8-sig")
    create_visualizations(data_dir, validity, selected_k, scaled, labels,
                          standardized_profiles, comparisons)

    obsolete = [data_dir / name for name in (
        'analysis_gap_statistic.csv', 'figure_gap_statistic.png',
        'figure_cluster_selection_methods.png') if (data_dir / name).exists()]
    if obsolete:
        archive = data_dir / 'previous_cluster_selection' / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        archive.mkdir(parents=True, exist_ok=True)
        for old_output in obsolete:
            old_output.replace(archive / old_output.name)

    print("=" * 80)
    print("NOISE FILTERING, K-MEANS, AND PROFILE ANALYSIS")
    print("=" * 80)
    print(f"Cases: {len(df)} | Clustering features: {len(feature_names)} | Selected k: {selected_k}")
    print("Cluster sizes:")
    print(pd.Series(labels).value_counts().sort_index().to_string())
    print(f"Selection scores: {recommendations}")
    print(json.dumps(summary, indent=2))
    print("\nStrongest group differences (eta-squared):")
    print(comparisons.nlargest(10, "eta_squared")[
        ["feature", "anova_p", "kruskal_p", "eta_squared"]
    ].to_string(index=False))


def main(data_dir="."):
    # run_analysis.py can import NumPy before this module sets OMP_NUM_THREADS.
    # Limit already-loaded native thread pools as well as fresh processes.
    with threadpool_limits(limits=1):
        return _run_analysis(data_dir)


if __name__ == "__main__":
    main()
