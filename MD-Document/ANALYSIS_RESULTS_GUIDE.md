# Current Analysis Results

Profile reporting corrected 2026-09-23; cluster assignments remain unchanged. See [methods](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) and [data provenance](DATA_DICTIONARY.md).

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

### Observed profile values

Descriptive statistics and tests now exclude missing observations separately for each indicator, rather than using clustering-imputed values. Cluster membership remains 104; statistical sample sizes can be smaller and are exported with every result.

For Cluster 2 (32 members):

| Indicator | Observed mean | Observed n | Missing n |
|---|---:|---:|---:|
| CommandsExecuted | 0.1290 | 31 | 1 |
| CorrectActions | 5.6129 | 31 | 1 |
| StagesCleared | 3.5484 | 31 | 1 |

Correct actions include tutorial UI interactions. Stage clears include repetitions; they are not constrained to the saved command count. In the extracted data, `NewPlayer` and `clear` each have 38 saved stage clears, matching their per-stage clear totals. These accounts remain included pending confirmation of participant eligibility. The profile audit flags source-review cases without automatically excluding them.

Median-centered Levene checks flag unequal variances at p<0.05 for 11 of 14 indicators. The test table therefore includes supplementary Welch ANOVA, alongside ordinary ANOVA and Kruskal-Wallis. These are exploratory comparisons; ordinary ANOVA assumptions are not certified by successful computation.

All files are in `Analysis-Log-Results`.

| Output | Purpose |
|---|---|
| `analysis_cluster_selection_summary.json` | Selection rule, both recommendations, scores, and sample counts |
| `analysis_cluster_selection_methods.csv` | Scores, ranks, eligibility, and final selection for each K |
| `analysis_cluster_selection_unfiltered.csv` | Same two-score analysis before statistical outlier exclusions |
| `analysis_cluster_noise_audit.csv` | Inclusion decisions and exclusion reasons for every participant |
| `analysis_cluster_profile_audit.csv` | Missing observations, clustering-only imputations, and source-review flags |
| `analysis_cluster_cleaned_features.csv` | Retained features before imputation and transformation |
| `analysis_kmeans_assignments.csv` | Participant membership and raw variables |
| `analysis_cluster_profiles.csv` | Observed cluster summaries with valid/missing counts and total membership |
| `analysis_cluster_profiles_standardized.csv` | Mean transformed and standardized features |
| `analysis_cluster_group_comparisons.csv` | Descriptive group comparisons and effect sizes |
| `analysis_behavior_sequences.csv` | Frequent sequences around success, help, and failure |
| `analysis_behavior_transitions_by_cluster.csv` | Cluster-specific transition counts and probabilities |
