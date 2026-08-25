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

`StagesCleared`, `GameProgress`, and `TotalScore` are profile-only outcomes excluded from K-means fitting.

For transition tables, `state` is the current behavior, `next_state` is the following behavior, `count` is frequency, `outgoing_total` is all transitions leaving the current state, and `probability = count / outgoing_total`.

See [PYTHON_ANALYSIS_RESEARCH_GUIDE.md](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) for complete definitions.
