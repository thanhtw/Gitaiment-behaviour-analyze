# Current Column and Feature Dictionary

The generated sources of truth are:

- `Analysis-Log-Results/analysis_cluster_feature_dictionary.csv`
- `Analysis-Log-Results/analysis_behavior_state_dictionary.csv`
- `Analysis-Log-Results/analysis_sequence_feature_dictionary.csv`

## Cluster inputs

| Feature | Definition |
|---|---|
| CommandsExecuted | Cumulative Git commands executed |
| CorrectActions | Correct game-action events |
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

For transition tables, `state` is the current behavior, `next_state` is the following behavior, `count` is frequency, `outgoing_total` is all transitions leaving the current state, and `probability = count / outgoing_total`.

See [PYTHON_ANALYSIS_RESEARCH_GUIDE.md](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) for complete definitions.
