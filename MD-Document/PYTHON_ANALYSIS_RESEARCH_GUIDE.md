# GiTaiment Behavioral Analysis: Research Guide

## Scope and execution

The Python workflow combines the Version-1 JSON exports and Version-2 CSV exports before analysis. The `dataVersion` field preserves provenance. SPSS is not required.

```powershell
conda activate NLP
python Extract-Data-Code\run_analysis.py
```

Tables and figures are written to `Analysis-Log-Results`.

### Data used in the current combined analysis

| Combined table | Version-1 | Version-2 | Total |
|---|---:|---:|---:|
| Events | 22,118 | 9,512 | 31,630 |
| Player game records | 50 | 54 | 104 |
| Player-stage records | 1,700 | 1,836 | 3,536 |
| Player-owned stage leaderboard entries | 741 | 254 | 995 |
| Global leaderboard entries | 637 | 293 | 930 |

After sources are combined, the per-user table contains 105 distinct usernames observed in at least one source. Cluster and profile analyses use these 105 cases. Transition and sequence analyses use the 31,630 combined timestamped events. Event histories are concatenated across versions. One player-save username (`Le Trung Hieu`) occurs in both versions; because save and stage fields are cumulative snapshots, its latest Version-2 snapshot is retained rather than summing both snapshots and double-counting progress.

## Behavioral sequence analysis

Events are ordered by player and timestamp. Event sequences preceding perfect completion, hint/answer-assisted completion, and failed actions are counted. These frequencies identify recurring pathways; they do not establish causality. Highly active players produce more sequences, so frequency should be interpreted alongside engagement.

Sequence output fields are:

| Field/type | Meaning |
|---|---|
| `sequence` | Ordered event names forming the observed pattern. |
| `count` | Frequency across the combined Version-1 and Version-2 event logs. |
| `success_perfect` | Three events immediately before a `Complete Quest` event marked `Perfect`. |
| `with_help` | Three events immediately before a `Complete Quest` event marked `Hint` or `Answer`. |
| `failed_action` | Two events before `Failed Action`, followed by the failure event. |

Sequences are calculated within players and never cross from one player to another. Only the 50 most frequent patterns per outcome are exported and visualized. The sequence features are raw event categories and local temporal order; cluster labels and performance outcomes are not used to create these patterns.

Outputs include `analysis_behavior_sequences.csv`, three outcome-specific sequence charts, and `figure_sequence_category_comparison.png`.

### Cluster-specific transition diagrams

The workflow also reduces events to six interpretable states: **A** (action), **E** (exploration), **CM** (command manipulation), **IM** (instructional material/help), **F** (failure), and **R** (reward/progression). For each player, consecutive state pairs are counted after ordering events by timestamp. Counts are pooled within clusters and converted to conditional probabilities, where each value means the probability of the next state given the current state.

| State | Meaning | Included game events |
|---|---|---|
| A — Action | Successful task-level action | `Correct Action` |
| E — Exploration | Navigation or information exploration | `Open Window`, `Check GlobalLeaderBoard`, `Login` |
| CM — Command manipulation | Direct Git command activity | `Execute Git Command` |
| IM — Instructional material/help | Instructional, hint, answer, or conversational support | `Read GameManual`, `Use Hint`, `Use Answer`, `Last Conversation` |
| F — Failure | Unsuccessful action or unresolved stage exit | `Failed Action`, `Restart Stage(Not Clear)`, `Back To Stage Select(Not Clear)` |
| R — Reward/progression | Quest or stage progression and clear-related activity | `Add New Quest`, `Complete Quest`, `Start Stage`, `Complete Stage`, `Back To Stage Select(Clear)`, `Restart Stage(Clear)` |

These are operational categories created for this study, not labels stored in the original database. If the paper uses different theoretical definitions, revise `EVENT_TO_STATE` in `behavior_transition_analysis.py` and rerun the workflow.

The diagrams display transitions with probability at least .15 and at least five observations to control visual clutter. All transitions, including those omitted visually, remain in `analysis_behavior_transitions_by_cluster.csv`. Node size represents state frequency and arrow width represents transition probability. The accompanying heatmaps show the complete numerical transition matrices.

Suggested methods text:

> Event records were mapped to six behavioral states and ordered within player by timestamp. First-order transition matrices were estimated separately for each behavioral cluster. Transition probabilities were calculated conditionally on the current state. Diagrams retained transitions with probability ≥ .15 and frequency ≥ 5, while analytical tables retained all observed transitions.

These figures support descriptions such as “Cluster 1 showed repeated command manipulation followed by progression,” but differences should not be called statistically significant unless they are tested explicitly. Transition probabilities are descriptive and repeated transitions within players are not independent.

Suggested methods text:

> Sequential pattern analysis was applied to timestamp-ordered event logs. Event n-grams preceding perfect completion, help-assisted completion, and failed actions were counted to identify recurring behavioral pathways. Frequencies were interpreted descriptively rather than causally.

## Cluster construction

Clusters use 11 behavioral and derived features: commands executed, correct actions, failed actions, hint quests, answer quests, play duration, leaderboard interactions, learning efficiency, accuracy rate, perfect quest rate, and help dependency ratio. Missing values are median-imputed and features are standardized. Performance outcomes are withheld from fitting and used afterward for profile interpretation, reducing circularity.

| Clustering feature | Operational definition |
|---|---|
| CommandsExecuted | Cumulative executed Git commands |
| CorrectActions | Number of correct game actions |
| FailedActions | Number of failed game actions |
| HintQuests | Quests completed using a hint |
| AnswerQuests | Quests completed using an answer |
| PlayDurationMinutes | Total active game time in minutes |
| LeaderboardInteractions | Number of leaderboard or ranking checks |
| LearningEfficiency | Total score / play duration in minutes |
| AccuracyRate | Correct actions / (correct + failed actions) |
| PerfectQuestRate | Perfect completions / completed quests |
| HelpDependencyRatio | (Hint + answer quests) / completed quests |

Three variables—StagesCleared, GameProgress, and TotalScore—are **profile outcomes**, not K-means inputs. They help explain external performance differences after behavioral groups have been formed.

Suggested methods text:

> Players were clustered using standardized behavioral indicators. Missing values were replaced by the feature median. Performance outcomes were excluded from model estimation and subsequently used to characterize the behavioral profiles. K-means used repeated centroid initializations and a fixed random seed.

## Selecting the number of clusters

The workflow reports complementary evidence:

| Method | Preferred result |
|---|---|
| Gap Statistic | Larger value; the one-standard-error rule is applied |
| Elbow/inertia | Point where improvement begins diminishing |
| Silhouette | Higher |
| Calinski–Harabasz | Higher |
| Davies–Bouldin | Lower |
| Stability ARI | Higher |

Every accepted solution must have at least 5% of cases in its smallest cluster. This avoids unstable groups that cannot support profile comparisons. Gap Statistic is the primary criterion; other indices are sensitivity checks. In `analysis_gap_statistic.csv`, `k` means the number of clusters, whereas `minimum_cluster_size` means the player count in the smallest group for that candidate.

Suggested methods text:

> Cluster count was evaluated with the Gap Statistic, elbow criterion, silhouette coefficient, Calinski–Harabasz index, Davies–Bouldin index, and repeated-initialization stability. Solutions with a group smaller than 5% of the sample were rejected. The final solution prioritized the Gap Statistic and was checked against the remaining diagnostics.

Use `analysis_cluster_selection_methods.csv`, `figure_gap_statistic.png`, and `figure_cluster_selection_methods.png` to report this decision.

### Current selection result (2026-08-25)

Gap Statistic selected `k=4`. Final K-means membership is Cluster 1 (`n=21`), Cluster 2 (`n=44`), Cluster 3 (`n=31`), and Cluster 4 (`n=9`). All final groups satisfy the minimum-size requirement. Sensitivity indices do not unanimously agree: Silhouette recommends `k=5`, Calinski–Harabasz `k=2`, Davies–Bouldin `k=4`, and stability ARI `k=3`. The paper should report this disagreement and characterize the four-cluster solution as Gap-selected and exploratory.

## Profile analysis

`analysis_cluster_profiles.csv` gives count, mean, standard deviation, and median. The standardized profile table expresses behavioral means as z-scores: positive values are above the sample average and negative values are below it. Group comparisons include one-way ANOVA, Kruskal–Wallis tests, and eta-squared effect sizes.

Values near .01, .06, and .14 are often described as small, medium, and large eta-squared effects, but these are conventions. Interpret significance together with effect magnitude, group size, distribution, and multiple testing.

Suggested results order:

1. Report selected `k` and all group sizes.
2. Describe agreement or disagreement among validity indices.
3. Name profiles from their strongest standardized behavioral features.
4. Compare withheld outcomes such as progress, score, and stages cleared.
5. Report test statistics, p-values, and eta-squared.
6. Describe clusters as sample-dependent behavioral profiles, not fixed learner traits.

Suggested results text:

> Cluster labels were assigned after inspecting standardized feature means and were not specified in advance. Differences were evaluated using ANOVA and Kruskal–Wallis tests, with eta-squared quantifying practical separation. The clusters represent observed patterns of play rather than immutable learner types.

## Figure interpretation

- Gap and validity-index charts justify the selected `k`.
- The size chart verifies that no accepted group is extremely small.
- The PCA plot is a two-dimensional illustration, not the clustering input space.
- The heatmap supports profile naming.
- The effect-size chart identifies the strongest group differences.
- Sequence charts illustrate common pathways to success, help use, and failure.

## Limitations

This is observational analysis. K-means assumes compact groups and is sensitive to feature selection and scaling. Internal validity indices measure geometric separation, not educational importance. Sequence observations within a player are dependent, and active players contribute more events. Findings should be framed as exploratory and validated in an independent sample.
