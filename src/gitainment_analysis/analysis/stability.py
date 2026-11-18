"""Explore fixed-k initialization, resampling, method, and feature sensitivity."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from .clustering import RATE_FEATURES, N_INIT, RANDOM_STATE, prepare_features


def transform_bootstrap(train, full, features):
    """Refit preprocessing on sampled learners, then transform the retained cohort."""
    imputer = SimpleImputer(strategy='median')
    train_values = imputer.fit_transform(train[features])
    full_values = imputer.transform(full[features])
    log_indices = [i for i, name in enumerate(features) if name not in RATE_FEATURES]
    train_values[:, log_indices] = np.log1p(train_values[:, log_indices])
    full_values[:, log_indices] = np.log1p(full_values[:, log_indices])
    scaler = StandardScaler().fit(train_values)
    return scaler.transform(train_values), scaler.transform(full_values)


def matched_jaccard(reference, candidate):
    """One-to-one matching of arbitrary labels by maximum total Jaccard overlap."""
    refs, candidates = np.unique(reference), np.unique(candidate)
    scores = np.array([[np.sum((reference == a) & (candidate == b)) /
                        np.sum((reference == a) | (candidate == b))
                        for b in candidates] for a in refs])
    rows, cols = linear_sum_assignment(-scores)
    result = {int(a): 0.0 for a in refs}
    result.update({int(refs[r]): float(scores[r, c]) for r, c in zip(rows, cols)})
    return result


def run(output_dir, n_boot=500, n_seeds=100):
    output_dir = Path(output_dir)
    data = pd.read_csv(output_dir / 'analysis_kmeans_assignments.csv', dtype={'ID': str})
    features, _, scaled = prepare_features(data)
    reference = data.Cluster.to_numpy()
    k = len(np.unique(reference))
    settings = dict(n_clusters=k, init='k-means++', n_init=N_INIT, algorithm='lloyd',
                    max_iter=300, tol=1e-4)
    pca = PCA(svd_solver='full').fit(scaled)
    pd.DataFrame({'component': np.arange(1, len(pca.explained_variance_ratio_) + 1),
                  'explained_variance_ratio': pca.explained_variance_ratio_,
                  'cumulative_explained_variance': np.cumsum(pca.explained_variance_ratio_)}).to_csv(
                      output_dir / 'analysis_pca_variance.csv', index=False)
    pd.DataFrame(pca.components_.T, index=features,
                 columns=[f'PC{i+1}' for i in range(len(features))]).rename_axis('feature').to_csv(
                     output_dir / 'analysis_pca_loadings.csv')
    seed_rows, bootstrap_rows, alternatives = [], [], []
    rng = np.random.default_rng(RANDOM_STATE)
    with threadpool_limits(limits=1):
        baseline = KMeans(**settings, random_state=RANDOM_STATE).fit(scaled)
        if adjusted_rand_score(reference, baseline.labels_) < .999999:
            raise ValueError('Saved assignments do not reproduce from current features and settings')
        for n_init in (1, N_INIT):
            for seed in range(n_seeds):
                options = dict(settings, n_init=n_init)
                model = KMeans(**options, random_state=seed).fit(scaled)
                seed_rows.append(dict(seed=seed, n_init=n_init,
                    ari=adjusted_rand_score(reference, model.labels_), inertia=model.inertia_,
                    silhouette=silhouette_score(scaled, model.labels_)))
        for replicate in range(n_boot):
            sample = rng.integers(len(data), size=len(data))
            train, full = transform_bootstrap(data.iloc[sample], data, features)
            model = KMeans(**settings, random_state=replicate).fit(train)
            predicted = model.predict(full)
            in_bag = np.zeros(len(data), dtype=bool)
            in_bag[np.unique(sample)] = True
            oob = ~in_bag
            row = dict(replicate=replicate, ari=adjusted_rand_score(reference, predicted),
                       oob_n=int(oob.sum()), oob_ari=adjusted_rand_score(reference[oob], predicted[oob])
                       if oob.sum() >= 2 else np.nan)
            row.update({f'cluster_{c}_jaccard': value for c, value in matched_jaccard(reference, predicted).items()})
            bootstrap_rows.append(row)
        # These comparisons fix k; agreement measures method dependence, not ground truth.
        alternative_models = {
            'ward_agglomerative': AgglomerativeClustering(n_clusters=k, linkage='ward'),
            'gaussian_mixture_full': GaussianMixture(n_components=k, covariance_type='full',
                                                    n_init=20, random_state=RANDOM_STATE),
        }
        for name, model in alternative_models.items():
            labels = model.fit_predict(scaled)
            alternatives.append(dict(method=name, features_used='all', dimensions=len(features),
                ari=adjusted_rand_score(reference, labels), silhouette=silhouette_score(scaled, labels),
                smallest_cluster_n=int(np.bincount(labels).min())))
        for removed in ('LearningEfficiency', *[x for x in features if x != 'LearningEfficiency']):
            reduced = data.drop(columns=removed)
            names, _, values = prepare_features(reduced)
            labels = KMeans(**settings, random_state=RANDOM_STATE).fit_predict(values)
            alternatives.append(dict(method=f'kmeans_without_{removed}', features_used=';'.join(names),
                dimensions=len(names), ari=adjusted_rand_score(reference, labels),
                silhouette=silhouette_score(values, labels), smallest_cluster_n=int(np.bincount(labels).min())))
    seeds, boot, alternate = map(pd.DataFrame, (seed_rows, bootstrap_rows, alternatives))
    seeds.to_csv(output_dir / 'analysis_cluster_seed_sensitivity.csv', index=False)
    boot.to_csv(output_dir / 'analysis_cluster_bootstrap_stability.csv', index=False)
    alternate.to_csv(output_dir / 'analysis_cluster_alternative_solutions.csv', index=False)
    summary = {
        'settings': {**settings, 'random_state': RANDOM_STATE, 'distance': 'Euclidean',
                     'input_features': features, 'n_learners': len(data),
                     'preprocessing': 'median imputation; log1p non-rate variables; standard scaling',
                     'components_used_for_original_clustering': 0,
                     'clustering_space': 'all standardized behavioral features; PCA is visualization only',
                     'pca_visualization_components': 2,
                     'pca_visualization_explained_variance': float(pca.explained_variance_ratio_[:2].sum())},
        'seed_sensitivity': {str(init): {'n_runs': len(group), 'ari_min': float(group.ari.min()),
                     'ari_median': float(group.ari.median()), 'ari_max': float(group.ari.max()),
                     'identical_partition_fraction': float(np.isclose(group.ari, 1).mean())}
                     for init, group in seeds.groupby('n_init')},
        'bootstrap': {'replicates': n_boot, 'seed': RANDOM_STATE,
                      'method': 'resample retained learners; refit imputation, transformations, scaling and fixed-k KMeans; predict full cohort',
                      'scope': 'conditional on retained cohort, feature set, and selected k; no new k selection or LOF within replicates',
                      'quantiles_are': 'empirical resampling stability ranges, not parameter confidence intervals',
                      'metrics': {col: {'mean': float(boot[col].mean()), 'median': float(boot[col].median()),
                          'q025': float(boot[col].quantile(.025)), 'q975': float(boot[col].quantile(.975))}
                          for col in ['ari', 'oob_ari'] + [c for c in boot if c.endswith('_jaccard')]}},
        'interpretation': 'Exploratory profiles; reproducible initialization does not establish separated or definitive learner types.'}
    (output_dir / 'analysis_cluster_stability_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary
