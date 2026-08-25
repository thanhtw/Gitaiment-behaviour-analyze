"""Gap Statistic, K-means, and cluster profile analysis.

Input is the combined two-version ``analysis_spss_ready.csv`` produced by
``run_analysis.py``. Outputs are written beside that file.
"""

import os
from pathlib import Path

# Avoid the documented Windows MKL K-means memory leak and warning flood.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway, kruskal
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,
                             davies_bouldin_score, silhouette_score)
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
N_REFERENCES = 100
MAX_K = 10

# Only behavioral variables define the clusters. Performance outcomes are held
# out and used later to profile/compare the discovered groups.
FEATURES = [
    "ActivitySpanDays", "TotalSessions", "EventsPerSession", "QuestsPerSession",
    "HelpRatio", "ActionSuccessRate", "QuestCompletionRate", "PerfectRatio",
    "ManualOpens", "LeaderboardChecks", "CommandsExecuted", "StagesAttempted",
]
OUTCOMES = [
    "GameProgress", "TotalScore", "TotalStars", "StagesCleared",
    "AvgBestScore", "AvgClearTime",
]


def build_python_feature_table(source):
    """Derive clustering variables directly from the combined per-user CSV."""
    raw = pd.read_csv(source)
    number = lambda name: pd.to_numeric(raw.get(name, 0), errors="coerce").fillna(0)
    safe_ratio = lambda top, bottom: np.divide(
        top, bottom, out=np.zeros(len(raw), dtype=float), where=np.asarray(bottom) != 0
    )
    quests = number("event_quests_added")
    actions = number("event_correct_actions") + number("event_failed_actions")
    table = pd.DataFrame({
        "ID": raw["username"],
        "ActivitySpanDays": number("event_activity_span_days"),
        "TotalSessions": number("event_total_sessions"),
        "EventsPerSession": safe_ratio(number("event_total_events"), number("event_total_sessions")),
        "QuestsPerSession": safe_ratio(quests, number("event_total_sessions")),
        "HelpRatio": safe_ratio(number("event_hint_used_quests") + number("event_answer_used_quests"), quests),
        "ActionSuccessRate": safe_ratio(number("event_correct_actions"), actions),
        "QuestCompletionRate": safe_ratio(number("event_quests_completed"), quests),
        "PerfectRatio": safe_ratio(number("event_perfect_quests"), number("event_quests_completed")),
        "ManualOpens": number("event_game_manual_opens"),
        "LeaderboardChecks": number("event_leaderboard_checks"),
        "CommandsExecuted": number("record_totalCommandExecuteTimes"),
        "StagesAttempted": number("event_unique_stages_attempted"),
        "GameProgress": number("record_totalGameProgress"),
        "TotalScore": number("record_totalStageScore"),
        "TotalStars": number("record_totalStarCount"),
        "StagesCleared": number("record_totalTimesStageClear"),
        "AvgBestScore": number("stage_avg_best_score"),
        "AvgClearTime": number("stage_avg_clear_time"),
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
    scaled = StandardScaler().fit_transform(imputed)
    return numeric.columns.tolist(), imputed, scaled


def _dispersion(values, labels, centers):
    return sum(np.square(values[labels == cluster] - centers[cluster]).sum()
               for cluster in range(len(centers)))


def calculate_gap_statistic(values, max_k=MAX_K, references=N_REFERENCES):
    """Calculate Gap(k) and select a profileable k with the one-SE rule."""
    rng = np.random.default_rng(RANDOM_STATE)
    lower, upper = values.min(axis=0), values.max(axis=0)
    max_k = min(max_k, len(values) - 1)
    rows = []
    for k in range(1, max_k + 1):
        model = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit(values)
        observed = max(_dispersion(values, model.labels_, model.cluster_centers_), 1e-12)
        reference_logs = []
        for index in range(references):
            reference = rng.uniform(lower, upper, size=values.shape)
            ref_model = KMeans(
                n_clusters=k, n_init=10, random_state=RANDOM_STATE + index
            ).fit(reference)
            dispersion = max(
                _dispersion(reference, ref_model.labels_, ref_model.cluster_centers_),
                1e-12,
            )
            reference_logs.append(np.log(dispersion))
        gap = np.mean(reference_logs) - np.log(observed)
        standard_error = np.std(reference_logs, ddof=1) * np.sqrt(1 + 1 / references)
        cluster_sizes = np.bincount(model.labels_, minlength=k)
        minimum_required = max(2, int(np.ceil(len(values) * 0.05)))
        rows.append({
            "k": k,
            "gap": gap,
            "standard_error": standard_error,
            "observed_log_dispersion": np.log(observed),
            "reference_log_dispersion": np.mean(reference_logs),
            "minimum_cluster_size": int(cluster_sizes.min()),
            "eligible": bool(cluster_sizes.min() >= minimum_required),
        })
    result = pd.DataFrame(rows)
    eligible_indices = result.index[result["eligible"] & result["k"].gt(1)].tolist()
    if not eligible_indices:
        raise ValueError("No k produced clusters large enough for profile comparison")
    selected_index = result.loc[eligible_indices, "gap"].idxmax()
    for current, following in zip(eligible_indices, eligible_indices[1:]):
        if result.loc[current, "gap"] >= (
            result.loc[following, "gap"] - result.loc[following, "standard_error"]
        ):
            selected_index = current
            break
    selected_k = int(result.loc[selected_index, "k"])
    result["selected"] = result["k"].eq(selected_k)
    return result, selected_k


def calculate_cluster_validity(values, max_k=MAX_K):
    """Compare k using elbow, Silhouette, Calinski-Harabasz, Davies-Bouldin and stability."""
    rows = []
    max_k = min(max_k, len(values) - 1)
    minimum_required = max(2, int(np.ceil(len(values) * 0.05)))
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, n_init=50, random_state=RANDOM_STATE).fit(values)
        seed_labels = [KMeans(n_clusters=k, n_init=1, random_state=seed).fit_predict(values)
                       for seed in range(RANDOM_STATE, RANDOM_STATE + 20)]
        stability = np.mean([
            adjusted_rand_score(seed_labels[i], seed_labels[j])
            for i in range(len(seed_labels)) for j in range(i + 1, len(seed_labels))
        ])
        smallest = int(np.bincount(model.labels_, minlength=k).min())
        rows.append({
            'k': k, 'inertia': model.inertia_,
            'silhouette': silhouette_score(values, model.labels_),
            'calinski_harabasz': calinski_harabasz_score(values, model.labels_),
            'davies_bouldin': davies_bouldin_score(values, model.labels_),
            'stability_ARI': stability, 'smallest_group_n': smallest,
            'eligible': smallest >= minimum_required,
        })
    result = pd.DataFrame(rows)
    eligible = result[result['eligible']]
    recommendations = {
        'silhouette': int(eligible.loc[eligible['silhouette'].idxmax(), 'k']),
        'calinski_harabasz': int(eligible.loc[eligible['calinski_harabasz'].idxmax(), 'k']),
        'davies_bouldin': int(eligible.loc[eligible['davies_bouldin'].idxmin(), 'k']),
        'stability_ARI': int(eligible.loc[eligible['stability_ARI'].idxmax(), 'k']),
    }
    for method, k in recommendations.items():
        result[f'recommended_{method}'] = result['k'].eq(k)
    return result, recommendations


def profile_clusters(df, feature_names, imputed, scaled, labels):
    raw = pd.DataFrame(imputed, columns=feature_names, index=df.index)
    for outcome in OUTCOMES:
        raw[outcome] = pd.to_numeric(df[outcome], errors="coerce")
    zscores = pd.DataFrame(scaled, columns=feature_names, index=df.index)
    raw["Cluster"] = labels
    zscores["Cluster"] = labels

    profiles = raw.groupby("Cluster").agg(["count", "mean", "std", "median"])
    profiles.columns = [f"{feature}_{stat}" for feature, stat in profiles.columns]
    profiles = profiles.reset_index()
    standardized_profiles = zscores.groupby("Cluster").mean().reset_index()

    comparisons = []
    clusters = sorted(np.unique(labels))
    for feature in feature_names + OUTCOMES:
        groups = [raw.loc[raw["Cluster"] == cluster, feature].values for cluster in clusters]
        valid = all(len(group) >= 2 for group in groups)
        anova_f, anova_p = f_oneway(*groups) if valid else (np.nan, np.nan)
        kw_h, kw_p = kruskal(*groups) if valid else (np.nan, np.nan)
        grand_mean = raw[feature].mean()
        ss_between = sum(len(group) * (group.mean() - grand_mean) ** 2 for group in groups)
        ss_total = np.square(raw[feature] - grand_mean).sum()
        comparisons.append({
            "feature": feature,
            "anova_F": anova_f,
            "anova_p": anova_p,
            "kruskal_H": kw_h,
            "kruskal_p": kw_p,
            "eta_squared": ss_between / ss_total if ss_total else np.nan,
        })
    comparisons = pd.DataFrame(comparisons).sort_values(
        ["anova_p", "eta_squared"], ascending=[True, False]
    )
    return profiles, standardized_profiles, comparisons


def create_visualizations(data_dir, gaps, validity, selected_k, scaled, labels,
                          standardized_profiles, comparisons):
    """Create publication-ready visual summaries of clustering results."""
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(gaps["k"], gaps["gap"], yerr=gaps["standard_error"], marker="o", capsize=4)
    ax.axvline(selected_k, color="crimson", linestyle="--", label=f"Selected k = {selected_k}")
    ax.set(xlabel="Number of clusters (k)", ylabel="Gap Statistic", title="Gap Statistic Cluster Selection")
    ax.legend()
    fig.tight_layout(); fig.savefig(data_dir / "figure_gap_statistic.png", dpi=300); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    metrics = [('inertia', 'Elbow / inertia', False), ('silhouette', 'Silhouette', True),
               ('calinski_harabasz', 'Calinski–Harabasz', True),
               ('davies_bouldin', 'Davies–Bouldin (lower is better)', False)]
    for ax, (column, title, _) in zip(axes.flat, metrics):
        ax.plot(validity['k'], validity[column], marker='o')
        ax.axvline(selected_k, color='crimson', linestyle='--')
        ax.set(xlabel='k', ylabel=column.replace('_', ' ').title(), title=title)
    fig.suptitle('Comparison of Cluster-Selection Diagnostics')
    fig.tight_layout(); fig.savefig(data_dir / 'figure_cluster_selection_methods.png', dpi=300); plt.close(fig)

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
    fig.colorbar(image, ax=ax, label="Mean z-score")
    fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_profile_heatmap.png", dpi=300); plt.close(fig)

    top = comparisons.nlargest(12, "eta_squared").sort_values("eta_squared")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["feature"], top["eta_squared"], color="#F58518")
    ax.set(xlabel="Eta-squared", title="Largest Differences Between Cluster Profiles")
    fig.tight_layout(); fig.savefig(data_dir / "figure_cluster_group_effects.png", dpi=300); plt.close(fig)


def main(data_dir="."):
    data_dir = Path(data_dir)
    df = build_python_feature_table(data_dir / "analysis_per_user_combined.csv")
    feature_names, imputed, scaled = prepare_features(df)
    gaps, selected_k = calculate_gap_statistic(scaled)
    validity, recommendations = calculate_cluster_validity(scaled)
    model = KMeans(n_clusters=selected_k, n_init=50, random_state=RANDOM_STATE)
    labels = model.fit_predict(scaled) + 1  # human-readable cluster numbering

    assignments = df.copy()
    assignments.insert(1, "Cluster", labels)
    profiles, standardized_profiles, comparisons = profile_clusters(
        df, feature_names, imputed, scaled, labels
    )

    gaps.to_csv(data_dir / "analysis_gap_statistic.csv", index=False, encoding="utf-8-sig")
    validity.to_csv(data_dir / "analysis_cluster_selection_methods.csv", index=False, encoding="utf-8-sig")
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
    create_visualizations(data_dir, gaps, validity, selected_k, scaled, labels,
                          standardized_profiles, comparisons)

    print("=" * 80)
    print("GAP STATISTIC, K-MEANS, AND PROFILE ANALYSIS")
    print("=" * 80)
    print(f"Cases: {len(df)} | Clustering features: {len(feature_names)} | Selected k: {selected_k}")
    print("Cluster sizes:")
    print(pd.Series(labels).value_counts().sort_index().to_string())
    print(f"Other selection methods: {recommendations}")
    print("\nStrongest group differences (eta-squared):")
    print(comparisons.nlargest(10, "eta_squared")[
        ["feature", "anova_p", "kruskal_p", "eta_squared"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
