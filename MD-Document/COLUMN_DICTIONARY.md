# Current Column and Feature Dictionary

The generated sources of truth are:

- `Analysis-Log-Results/analysis_cluster_feature_dictionary.csv`
- `Analysis-Log-Results/analysis_behavior_state_dictionary.csv`
- `Analysis-Log-Results/analysis_sequence_feature_dictionary.csv`

## Cluster inputs

| Feature | Definition |
|---|---|
| CommandsExecuted | Cumulative Git commands executed |
| CorrectActions | Logged correct game-action events, including tutorial UI actions; not successful Git commands |
| FailedActions | Failed game-action events |
| HintQuests | Quests completed using a hint |
| AnswerQuests | Quests completed using an answer |
| PlayDurationMinutes | Total active game time in minutes |
| LeaderboardInteractions | Leaderboard/ranking checks |
| LearningEfficiency | Total score / play duration in minutes |
| AccuracyRate | Correct / (correct + failed actions) |
| PerfectQuestRate | Perfect / completed quests |
| HelpDependencyRatio | (Hint + answer quests) / completed quests |

`StagesCleared`, `GameProgress`, and `TotalScore` are reported as profile outcomes. Total score also enters the derived input `LearningEfficiency`, so comparisons of score are not independent of cluster construction.

## Cluster-selection output

| Column | Meaning |
|---|---|
| `k` | Number of clusters tested |
| `silhouette` | Silhouette score; higher is better |
| `calinski_harabasz` | Calinski-Harabasz score; higher is better |
| `smallest_group_n` | Participants in the smallest cluster |
| `eligible` | Every cluster has at least two participants |
| `silhouette_rank`, `calinski_harabasz_rank` | Descending ranks within eligible solutions; tied scores share a rank |
| `combined_rank` | Sum of the two ranks; lower is better |
| `recommended_silhouette`, `recommended_calinski_harabasz` | Each score's preferred K; ties choose smaller K |
| `selected` | Final selection under the two-score rule |

The noise audit records `ID`, `reason`, `lof_score`, and `included`. The cleaned-feature CSV contains retained observations before imputation and transformation.

## Profile and test counts

In `analysis_cluster_profiles.csv`, `cluster_n` is total cluster membership. Each indicator's `_count` is its observed sample size and `_missing` is the number without a finite observed value; mean, median, and standard deviation use only observed values. Standardized profiles describe the imputed clustering representation instead.

In `analysis_cluster_group_comparisons.csv`, `n_observed`, `n_missing`, and `cluster_<label>_n` document the observations used. `test_status` is `ok`, `constant_indicator`, or `insufficient_observed_values`. ANOVA and Kruskal-Wallis use those same observed values. `levene_F`/`levene_p` provide a median-centered equal-variance diagnostic; `variance_heterogeneity_flag` is true when its p-value is below 0.05. `kruskal_small_group` flags a group with fewer than five observed values. These flags do not validate inferential assumptions or adjust p-values.

`analysis_cluster_profile_audit.csv` records missing observations, their clustering-only imputed values, and saved counters flagged for manual review. `StagesCleared` counts repeat clears as well as first clears.

`welch_F`, `welch_p`, `welch_df_between`, and `welch_df_within` provide the supplementary Welch ANOVA result and degrees of freedom. `welch_status` identifies unavailable results, including groups with zero sample variance. The ordinary ANOVA columns retain their original meaning; no p-value is silently replaced by another test.

For transition tables, `state` is the current behavior, `next_state` is the following behavior, `count` is frequency, `outgoing_total` is all transitions leaving the current state, and `probability = count / outgoing_total`.

See [PYTHON_ANALYSIS_RESEARCH_GUIDE.md](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) for complete definitions.
