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

## Paper-ready reporting of stage completion

Use **Total recorded stage-clear occurrences** as the table label for `StageClearOccurrences`. This outcome is the saved cumulative counter `record_totalTimesStageClear`; it includes repeated clears. It is not the number of distinct study stages completed and is not a completion score out of 16.

| Cluster | Cluster membership | Observed n | Missing n | Mean (SD), clear occurrences | Median |
|---|---:|---:|---:|---:|---:|
| 1 | 57 | 57 | 0 | 16.23 (9.20) | 16 |
| 2 | 32 | 31 | 1 | 3.55 (9.23) | 1 |
| 3 | 15 | 15 | 0 | 1.87 (1.68) | 1 |

**Table note:** Values represent cumulative recorded clear occurrences, including repeated completions. The counter is not restricted by the number of distinct stages. Means and standard deviations use available observations only; SD denotes standard deviation. Cluster 1's mean is 925 clear occurrences / 57 participants = 16.2281, rounded to 16.23.

**Suggested Methods text**

> Total recorded stage-clear occurrences were obtained from each participant's cumulative player-save counter. This measure counts repeated clears and was treated as a measure of completion activity, rather than the number of distinct stages completed. Descriptive statistics used observed values, with valid sample sizes reported for each cluster.

**Suggested Results text**

> Mean total recorded stage-clear occurrences were 16.23 (SD = 9.20; n = 57) in Cluster 1, 3.55 (SD = 9.23; n = 31) in Cluster 2, and 1.87 (SD = 1.68; n = 15) in Cluster 3. These values include repeated stage completions and should not be interpreted as the number of distinct stages completed out of the 16 study stages.

### Distinct-stage completion is a separate, pending measure

The user identifies 16 study stages, while the exports contain 17 named topics (including Game Introduction), each with Tutorial and Practice entries. To report **Distinct study stages completed (0-16)**, first confirm the eligible stage list and whether completion requires Tutorial, Practice, either mode, or both. Then count each eligible stage once per participant using those rules. Do not substitute the existing count of completed saved stage entries, cap the cumulative counter at 16, or divide it by 16 to obtain a completion percentage.

The distinct-stage measure is not yet calculated. The cumulative counter remains explicitly labelled in current tables. Account eligibility and the interpretation limitations below still apply to manuscript use.

## Output reference

### Observed profile values

Descriptive statistics and tests now exclude missing observations separately for each indicator, rather than using clustering-imputed values. Cluster membership remains 104; statistical sample sizes can be smaller and are exported with every result.

For Cluster 2 (32 members):

| Indicator | Observed mean | Observed n | Missing n |
|---|---:|---:|---:|
| CommandsExecuted | 0.1290 | 31 | 1 |
| CorrectActions | 5.6129 | 31 | 1 |
| StageClearOccurrences | 3.5484 | 31 | 1 |

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
