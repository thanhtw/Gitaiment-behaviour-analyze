# Behavioral Features: Definitions and Interpretation

Updated: 2026-09-23. This reference describes the current extraction and analysis code, including the distinction between Git commands, correct game actions, and stage clears.

## 1. Where the measurements come from

The clustering input is [analysis_per_user_combined.csv](../Analysis-Log-Results/analysis_per_user_combined.csv), with one row per username. Its fields combine two types of measurement:

- **Saved counters (`record_...`):** cumulative values from player-save records. Where both versions contain a player, the extraction uses the Version-2 save rather than adding cumulative snapshots.
- **Event counts (`event_...`):** counts of matching rows in the combined event logs for that player.

Saved counters and event logs are different sources. Their coverage and definitions should be checked before treating them as interchangeable. The analysis does not require their counts to match.

Implementation references: [per-user extraction](../Extract-Data-Code/extract_per_user_data.py) and [feature construction and analysis](../Extract-Data-Code/cluster_profile_analysis.py).

## 2. Features used to form clusters

All 11 features below enter clustering when they are nonconstant and have available values.

| Code name | Suggested reporting label | Source or calculation | Unit and interpretation |
|---|---|---|---|
| `CommandsExecuted` | Saved Git-command count | `record_totalCommandExecuteTimes` | Commands recorded by the saved counter. This is not a count of successful commands and is not calculated by counting `Execute Git Command` events. |
| `CorrectActions` | Correct game-action events | `event_correct_actions`: number of rows with `eventName == 'Correct Action'` | Events, including tutorial and practice interface actions. Not successful Git commands. |
| `FailedActions` | Failed game-action events | `event_failed_actions`: number of rows with `eventName == 'Failed Action'` | Events recorded under this label. The analysis does not establish that each event is a failed Git command. |
| `HintQuests` | Hint-labelled event count | `event_hint_used_quests`: event details containing `Hint` | Matching event rows. Intended to represent hint-associated quest activity; see the extraction qualification below. |
| `AnswerQuests` | Answer-labelled event count | `event_answer_used_quests`: event details containing `Answer` | Matching event rows. Intended to represent answer-associated quest activity; see the extraction qualification below. |
| `PlayDurationMinutes` | Saved play duration | `record_totalPlayTime / 60` | Minutes derived from the saved duration. It is not reconstructed from event timestamps, and this analysis does not independently verify idle-time exclusion. |
| `LeaderboardInteractions` | Global leaderboard-check events | `event_leaderboard_checks`: number of rows with `eventName == 'Check GlobalLeaderBoard'` | Repeated checks count separately. This is not the number of distinct leaderboards or a measure of competitive motivation. |
| `LearningEfficiency` | Score per recorded play minute | `record_totalStageScore / PlayDurationMinutes` | Score units per minute. A performance-rate proxy, not a direct measurement of learning gain; short recorded durations can produce high values. |
| `AccuracyRate` | Recorded game-action success proportion | `CorrectActions / (CorrectActions + FailedActions)` | Proportion; multiply by 100 for a percentage. Describes the two logged action categories, not Git-command accuracy. |
| `PerfectQuestRate` | Perfect-labelled events per quest completion | `event_perfect_quests / event_quests_completed` | Ratio intended to describe perfect quest completion. Its numerator uses the detail-matching rule below. |
| `HelpDependencyRatio` | Help-labelled events per quest completion | `(HintQuests + AnswerQuests) / event_quests_completed` | Ratio intended to describe help-associated quest activity. It does not establish a user's psychological dependence on help. |

### Qualification for quest-related indicators

The current extractor counts event details containing `Perfect`, `Hint`, or `Answer`. It does **not** additionally restrict these numerator counts to `eventName == 'Complete Quest'`, deduplicate quest IDs, or count distinct quests. The denominator `event_quests_completed` does count rows with `eventName == 'Complete Quest'`.

Consequently, labels such as “hint-assisted quests” or “perfect quest completion rate” require confirmation that those detail strings identify the intended completion events in the logging system. Matching event counts should not automatically be described as unique quest counts. This document records the implemented definitions; it does not change the extraction rules.

## 3. What counts as a correct action?

The inclusion rule is the exact event name `Correct Action`. The analysis does not infer correctness by parsing Git-command output. Examples present in the logs include:

| Logged `eventDetail` | Plain-language description |
|---|---|
| `<File/FileFunctionSelection>-<Continue>` | File/function selection recorded as a correct action |
| `<FileContentWindow/RenameButtonSelection>-<Continue>` | Rename-button selection |
| `<FileContentWindow/DeleteButtonSelection>-<Continue>` | Delete-button selection |
| `<FileContentWindow/ModifyButtonSelection>-<Continue>` | Modify-button selection |
| `<FileContentWindow/AddButtonSelection>-<Continue>` | Add-button selection |

These details occur in tutorial and practice scenes. They are examples from the available logs, not a restriction on which `Correct Action` events the code counts.

**A correct interface action can occur without a Git command.** For example, user `110122073` has six correct-action events in the Game Introduction tutorial, a logged stage completion, and zero saved Git commands. The six actions comprise two file/function selections, two rename selections, one delete selection, and one modify selection.

It is therefore inappropriate to interpret `CorrectActions / CommandsExecuted` as a command-success rate.

## 4. Outcomes used to describe the clusters

| Code name | Suggested reporting label | Source | Interpretation |
|---|---|---|---|
| `StageClearOccurrences` | Total recorded stage-clear occurrences | `record_totalTimesStageClear` | Total clear occurrences, including repeat clears. Not distinct stages completed or a completion score out of 16. |
| `GameProgress` | Saved game-progress percentage | `record_totalGameProgress` | The saved progress value, reported as a percentage by the pipeline. The analysis does not reconstruct the game's progress formula. |
| `TotalScore` | Saved total stage score | `record_totalStageScore` | Cumulative saved stage score. The analysis does not reconstruct the game's scoring rules. |

These three columns are used for profiling rather than directly included in the clustering feature list. However, `TotalScore` also supplies the numerator of `LearningEfficiency`, so score is not independent of cluster construction.

For manuscript wording, a table with valid n, mean, SD, and median, and the distinction from completion of the 16 study stages, see [paper-ready stage reporting](ANALYSIS_RESULTS_GUIDE.md#paper-ready-reporting-of-stage-completion). The former output name `StagesCleared` has been replaced with `StageClearOccurrences` to make the counting unit explicit.

For `NewPlayer` and `clear`, the saved clear count is 38 each, matching the sum of their extracted per-stage `stageClearTimes`. This supports the extracted count but does not establish whether either account is an eligible study participant. Eligibility must be confirmed from study records rather than inferred from the account name.

## 5. Worked example: Cluster 2

The current Cluster 2 contains 32 users. Its corrected descriptive statistics use observed values:

| Indicator | Observed total | Users with observed values | Missing users | Mean |
|---|---:|---:|---:|---:|
| Saved Git commands | 4 | 31 | 1 | 0.1290 |
| Correct game-action events | 174 | 31 | 1 | 5.6129 |
| Saved stage clears | 110 | 31 | 1 | 3.5484 |

The users missing a value are not necessarily the same across indicators. In this cluster, `test player` lacks the saved command and stage-clear totals, whereas `Xue` lacks the correct-action count.

All 174 observed correct-action events in this cluster occur in the Game Introduction tutorial:

| Action detail | Events |
|---|---:|
| File/function selection | 60 |
| Rename selection | 58 |
| Delete selection | 28 |
| Modify selection | 28 |
| **Total** | **174** |

The relatively high stage-clear mean is influenced by `NewPlayer` and `clear`, which together contribute 76 of the 110 clear occurrences. The cluster's stage-clear median is 1. Report the distribution and account-review limitations alongside the mean.

Suggested reporting text:

> Cluster 2 comprised 32 users. Among users with available values for each indicator (n=31), mean saved Git-command count was 0.13, mean correct game-action count was 5.61, and mean saved stage-clear count was 3.55. Correct actions in this cluster were tutorial interface events; they were not successful Git commands. Stage-clear counts included repeat completions.

## 6. Missing values and statistical interpretation

- A recorded **zero** is retained as zero. An unavailable value is **missing**, not automatically zero.
- Ratios with missing or zero denominators are missing.
- **For clustering:** missing features are median-imputed, non-rate features are log-transformed, and features are standardized.
- **For descriptive profiles and tests:** only observed values are used, separately for each indicator. Mean, median, standard deviation, and test sample size exclude missing values. The profile table provides total cluster membership, observed counts, and missing counts.
- **For standardized profiles:** values describe the imputed and transformed representation used to construct clusters, rather than raw observed means.

The former Cluster 2 means of 1.94 commands and 5.77 correct actions included substituted values. They are superseded by the observed means above. Imputation remains part of clustering, not descriptive reporting.

ANOVA, Welch ANOVA, and Kruskal-Wallis compare the **same indicator across clusters**. They do not test whether commands, correct actions, and stage clears have the same numerical value within a cluster. Comparisons of clustering inputs are exploratory because those indicators also helped define the groups. Details on variance checks, unavailable tests, and sample counts are in the [methods guide](PYTHON_ANALYSIS_RESEARCH_GUIDE.md).

## 7. Files to use

- [Observed cluster profiles](../Analysis-Log-Results/analysis_cluster_profiles.csv): means, medians, standard deviations, observed counts, and missing counts.
- [Group comparisons](../Analysis-Log-Results/analysis_cluster_group_comparisons.csv): observed sample sizes, statistical results, and diagnostic flags.
- [Profile audit](../Analysis-Log-Results/analysis_cluster_profile_audit.csv): missing observations, clustering-only substitutions, and source-review flags.
- [Column dictionary](COLUMN_DICTIONARY.md): definitions of output columns.
- [Current results](ANALYSIS_RESULTS_GUIDE.md): selected K and cluster sizes.
