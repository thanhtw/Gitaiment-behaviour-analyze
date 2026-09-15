# Current Analysis Results

Updated 2026-09-15. See [methods](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) and [data provenance](DATA_DICTIONARY.md).

## Sample

- Combined per-user profiles: **115**.
- Excluded for no observed activity: **11**.
- Retained for clustering: **104**.
- Active profiles excluded as statistical outliers: **0**.

## Selected cluster count

**K=3 maximizes both silhouette and Calinski-Harabasz among the tested K=2 through 10.** These are the only scores used to identify K.

| Score | Value at K=3 | Preferred K |
|---|---:|---:|
| Silhouette | 0.3093 | 3 |
| Calinski-Harabasz | 39.5391 | 3 |

Both scores agree, so no compromise or tie-break is needed for this dataset. The same K is selected before statistical outlier filtering. This is the best tested solution under the stated rule, not proof of a unique population partition.

### Separate selection figures

- [Silhouette score](../Analysis-Log-Results/figure_cluster_silhouette.png)
- [Calinski-Harabasz score](../Analysis-Log-Results/figure_cluster_calinski_harabasz.png)

### Cluster sizes

| Cluster | Participants |
|---|---:|
| 1 | 57 |
| 2 | 32 |
| 3 | 15 |

## Output reference

All files are in `Analysis-Log-Results`.

| Output | Purpose |
|---|---|
| `analysis_cluster_selection_summary.json` | Selection rule, both recommendations, scores, and sample counts |
| `analysis_cluster_selection_methods.csv` | Scores, ranks, eligibility, and final selection for each K |
| `analysis_cluster_selection_unfiltered.csv` | Same two-score analysis before statistical outlier exclusions |
| `analysis_cluster_noise_audit.csv` | Inclusion decisions and exclusion reasons for every participant |
| `analysis_cluster_cleaned_features.csv` | Retained features before imputation and transformation |
| `analysis_kmeans_assignments.csv` | Participant membership and raw variables |
| `analysis_cluster_profiles.csv` | Raw cluster summaries |
| `analysis_cluster_profiles_standardized.csv` | Mean transformed and standardized features |
| `analysis_cluster_group_comparisons.csv` | Descriptive group comparisons and effect sizes |
| `analysis_behavior_sequences.csv` | Frequent sequences around success, help, and failure |
| `analysis_behavior_transitions_by_cluster.csv` | Cluster-specific transition counts and probabilities |
