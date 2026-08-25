# GiTaiment Behavioral Analysis: Research Guide

## Scope and execution

The Python workflow combines the Version-1 JSON exports and Version-2 CSV exports before analysis. The `dataVersion` field preserves provenance. SPSS is not required.

```powershell
conda activate NLP
python Extract-Data-Code\run_analysis.py
```

Tables and figures are written to `Analysis-Log-Results`.

## Behavioral sequence analysis

Events are ordered by player and timestamp. Event sequences preceding perfect completion, hint/answer-assisted completion, and failed actions are counted. These frequencies identify recurring pathways; they do not establish causality. Highly active players produce more sequences, so frequency should be interpreted alongside engagement.

Outputs include `analysis_behavior_sequences.csv`, three outcome-specific sequence charts, and `figure_sequence_category_comparison.png`.

### Cluster-specific transition diagrams

The workflow also reduces events to six interpretable states: **A** (action), **E** (exploration), **CM** (command manipulation), **IM** (instructional material/help), **F** (failure), and **R** (reward/progression). For each player, consecutive state pairs are counted after ordering events by timestamp. Counts are pooled within clusters and converted to conditional probabilities, where each value means the probability of the next state given the current state.

The diagrams display transitions with probability at least .15 and at least five observations to control visual clutter. All transitions, including those omitted visually, remain in `analysis_behavior_transitions_by_cluster.csv`. Node size represents state frequency and arrow width represents transition probability. The accompanying heatmaps show the complete numerical transition matrices.

Suggested methods text:

> Event records were mapped to six behavioral states and ordered within player by timestamp. First-order transition matrices were estimated separately for each behavioral cluster. Transition probabilities were calculated conditionally on the current state. Diagrams retained transitions with probability ≥ .15 and frequency ≥ 5, while analytical tables retained all observed transitions.

These figures support descriptions such as “Cluster 1 showed repeated command manipulation followed by progression,” but differences should not be called statistically significant unless they are tested explicitly. Transition probabilities are descriptive and repeated transitions within players are not independent.

Suggested methods text:

> Sequential pattern analysis was applied to timestamp-ordered event logs. Event n-grams preceding perfect completion, help-assisted completion, and failed actions were counted to identify recurring behavioral pathways. Frequencies were interpreted descriptively rather than causally.

## Cluster construction

Clusters use 12 behavioral features: activity span, sessions, events per session, quests per session, help ratio, action success rate, quest completion rate, perfect ratio, manual opens, leaderboard checks, commands executed, and stages attempted. Missing values are median-imputed and features are standardized. Performance outcomes are withheld from fitting and used afterward for profile interpretation, reducing circularity.

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
