# Indicator Formulas and Cluster-Level Aggregation

This reference defines all **11 clustering indicators** and **three profile outcomes** in the current analysis. It separates each learner's measurement from the mean reported for a cluster.

The formulas follow [feature construction](../Extract-Data-Code/cluster_profile_analysis.py) and [event aggregation](../Extract-Data-Code/extract_per_user_data.py). For examples and interpretation, see [Behavioral Features: Definitions and Interpretation](BEHAVIORAL_FEATURE_EXPLANATION.md).

## 1. Notation and counting rules

| Symbol | Meaning |
|---|---|
| $i$ | Learner index |
| $k$ | Cluster index |
| $N_k$ | Total learners assigned to cluster $k$ |
| $\mathcal{E}_i$ | Available event records for learner $i$ |
| $\mathbf{1}\{B\}$ | Indicator function: 1 when condition $B$ is true, otherwise 0 |
| $\operatorname{name}(e)$ | Event name of record $e$ |
| $\operatorname{detail}(e)$ | Event-detail text of record $e$ |
| $V_{k,X}$ | Learners in cluster $k$ with a valid observed value for indicator $X$ |
| $n_{k,X}=|V_{k,X}|$ | Valid observed sample size for indicator $X$ in cluster $k$ |

Saved counters are read from the selected player-save record; cumulative snapshots are not added across versions. Event counts are calculated from the combined available event records. Repeated matching events count separately.

When an event profile is available, an event count is zero if no records satisfy its counting rule. When an entire source profile is unavailable, its fields remain missing rather than being interpreted as evidence of zero activity.

## 2. Four derived indicators: calculate for each learner first

### Equation (1): score per recorded play minute

Code column: `LearningEfficiency`.

$$
E_i=\frac{S_i}{T_i},\qquad T_i>0.
\tag{1}
$$

$S_i$ is the saved total stage score and $T_i$ is recorded play duration in minutes. The unit is **score units per minute**. This is a rate of score accumulation, not a direct measure of learning gain. Prefer the reporting label **Score per recorded play minute**.

### Equation (2): recorded game-action success proportion

Code column: `AccuracyRate`.

$$
R_i=\frac{A_i}{A_i+F_i},\qquad A_i+F_i>0.
\tag{2}
$$

$A_i$ and $F_i$ count logged `Correct Action` and `Failed Action` events, respectively. These are game-action categories and can include tutorial interface actions. They are not verified counts of successful and unsuccessful Git commands. Multiply the resulting proportion by 100 to report a percentage.

### Equation (3): perfect-labelled events per quest completion

Code column: `PerfectQuestRate`.

$$
R_i^{\mathrm{perfect}}=\frac{P_i}{Q_i},\qquad Q_i>0.
\tag{3}
$$

$P_i$ counts event records whose details contain `Perfect`; $Q_i$ counts events named `Complete Quest`:

$$
P_i=\sum_{e\in\mathcal{E}_i}\mathbf{1}\{\operatorname{detail}(e)\text{ contains Perfect}\},
\qquad
Q_i=\sum_{e\in\mathcal{E}_i}\mathbf{1}\{\operatorname{name}(e)=\text{Complete Quest}\}.
$$

The numerator is not additionally restricted to completion events or deduplicated by quest ID. Interpreting it as quests completed without errors or assistance requires validation of the game's event labels; that interpretation is not independently established by the extraction code.

### Equation (4): help-labelled events per quest completion

Code column: `HelpDependencyRatio`.

$$
D_i=\frac{H_i+B_i}{Q_i},\qquad Q_i>0.
\tag{4}
$$

$H_i$ and $B_i$ count event details containing `Hint` and `Answer`, respectively. Their definitions are Equations (8) and (9). This is an operational ratio of labelled events, not a validated measure of psychological dependence. The numerator is not a deduplicated count of distinct assisted quests.

**Missing-value rule for (1)-(4):** a ratio is missing if a required input is missing or the denominator is zero. Missing ratios are excluded from descriptive summaries and statistical tests. Under the current cleaning rules, profiles with negative feature values, infinite feature values, or rate features above one are excluded before clustering; values are not silently clipped into range.

## 3. Other clustering indicators

### Equation (5): saved Git-command count

Code column: `CommandsExecuted`.

$$
C_i=\operatorname{record\_totalCommandExecuteTimes}_i.
\tag{5}
$$

This is the cumulative command count in the player-save record. It is not divided by duration and is not calculated by counting `Execute Git Command` event rows. Its unit is **recorded commands per learner**.

### Equation (6): correct game-action count

Code column: `CorrectActions`.

$$
A_i=\sum_{e\in\mathcal{E}_i}
\mathbf{1}\{\operatorname{name}(e)=\text{Correct Action}\}.
\tag{6}
$$

Count every event with the specified name. Observed details include file/function selection and rename, delete, modify, and add-button selections. Therefore $A_i$ can exceed $C_i$ without a mathematical contradiction: the two variables count different activities.

### Equation (7): failed game-action count

Code column: `FailedActions`.

$$
F_i=\sum_{e\in\mathcal{E}_i}
\mathbf{1}\{\operatorname{name}(e)=\text{Failed Action}\}.
\tag{7}
$$

This counts the logged failure category. It should not automatically be described as the number of incorrect Git commands or failed quests.

### Equation (8): hint-labelled event count

Code column: `HintQuests`.

$$
H_i=\sum_{e\in\mathcal{E}_i}
\mathbf{1}\{\operatorname{detail}(e)\text{ contains Hint}\}.
\tag{8}
$$

The implementation counts matching event-detail rows, without a separate completion-event filter or distinct-quest check. The matching is case-sensitive; a missing event detail does not match.

### Equation (9): answer-labelled event count

Code column: `AnswerQuests`.

$$
B_i=\sum_{e\in\mathcal{E}_i}
\mathbf{1}\{\operatorname{detail}(e)\text{ contains Answer}\}.
\tag{9}
$$

The same counting qualifications as Equation (8) apply. A record containing both strings could contribute to both counts under these rules; the extraction does not enforce mutually exclusive categories.

### Equation (10): recorded play duration in minutes

Code column: `PlayDurationMinutes`.

$$
T_i=\frac{\operatorname{record\_totalPlayTime}_i}{60}.
\tag{10}
$$

The saved duration is expressed in seconds and converted to minutes. The analysis does not reconstruct this duration from event timestamps or independently verify the exclusion of idle time. A recorded duration of zero can appear in the duration summary, but does not produce a valid score-per-minute ratio.

### Equation (11): global leaderboard-check count

Code column: `LeaderboardInteractions`.

$$
L_i=\sum_{e\in\mathcal{E}_i}
\mathbf{1}\{\operatorname{name}(e)=\text{Check GlobalLeaderBoard}\}.
\tag{11}
$$

Repeated checks count separately. This is not the count of distinct leaderboard pages, and the code does not include other event names merely because they concern rankings.

## 4. Outcomes used to describe clusters

### Equation (12): total recorded stage-clear occurrences

Code column: `StageClearOccurrences`.

$$
G_i=\operatorname{record\_totalTimesStageClear}_i.
\tag{12}
$$

The saved counter includes repeated clear occurrences. It is **not the number of distinct stages completed out of 16**, and it can exceed 16. Do not cap it at 16 or use $G_i/16$ as a completion percentage. A separate distinct-stage measure requires the confirmed study-stage list and Tutorial/Practice completion rule.

### Equation (13): saved game progress

Code column: `GameProgress`.

$$
U_i=\operatorname{record\_totalGameProgress}_i.
\tag{13}
$$

The pipeline reports this saved value as a percentage. It does not recompute progress from stage-clear occurrences or reconstruct the game's progress algorithm. Averaging values already on a 0-100 scale does not require multiplying them by 100 again.

### Equation (14): saved total stage score

Code column: `TotalScore`.

$$
S_i=\operatorname{record\_totalStageScore}_i.
\tag{14}
$$

This is the cumulative saved score; the analysis does not reconstruct the game's scoring algorithm. Although this column is a profile outcome, it also enters Equation (1), so it is not independent of cluster construction.

## 5. Cluster aggregation: applies to all 14 indicators

For any indicator $X$, the cluster-level mean is:

$$
\boxed{\overline{X}_k=
\frac{1}{n_{k,X}}\sum_{i\in V_{k,X}}X_i.}
\tag{15}
$$

Each learner with an observed indicator value receives equal weight. Recorded zeros are included; missing values are excluded separately for each indicator. If there are no observed values, the mean is missing. Thus $n_{k,X}$ need not equal $N_k$ and can differ between indicators.

### Explicit forms for the four derived indicators

$$
\overline{E}_k=\frac{1}{n_{k,E}}\sum_{i\in V_{k,E}}\frac{S_i}{T_i},
\qquad
\overline{R}_k=\frac{1}{n_{k,R}}\sum_{i\in V_{k,R}}\frac{A_i}{A_i+F_i},
$$

$$
\overline{R^{\mathrm{perfect}}}_k=
\frac{1}{n_{k,R^{\mathrm{perfect}}}}\sum_{i\in V_{k,R^{\mathrm{perfect}}}}\frac{P_i}{Q_i},
\qquad
\overline{D}_k=\frac{1}{n_{k,D}}\sum_{i\in V_{k,D}}\frac{H_i+B_i}{Q_i}.
$$

These are **means of individual ratios**, not ratios of cluster means or totals. In general:

$$
\frac{1}{n_{k,E}}\sum_{i\in V_{k,E}}\frac{S_i}{T_i}
\ne
\frac{\sum_{i\in V_{k,E}}S_i}{\sum_{i\in V_{k,E}}T_i}.
$$

Even when the same learners contribute to both calculations, the first gives equal weight to learners and the second weights their individual score rates by duration.

### Explicit forms for the remaining indicators

| Reported cluster indicator | Mean formula |
|---|---|
| Commands executed | $\overline C_k=\sum_{i\in V_{k,C}}C_i/n_{k,C}$ |
| Correct actions | $\overline A_k=\sum_{i\in V_{k,A}}A_i/n_{k,A}$ |
| Failed actions | $\overline F_k=\sum_{i\in V_{k,F}}F_i/n_{k,F}$ |
| Hint-labelled events | $\overline H_k=\sum_{i\in V_{k,H}}H_i/n_{k,H}$ |
| Answer-labelled events | $\overline B_k=\sum_{i\in V_{k,B}}B_i/n_{k,B}$ |
| Recorded play duration | $\overline T_k=\sum_{i\in V_{k,T}}T_i/n_{k,T}$ |
| Leaderboard checks | $\overline L_k=\sum_{i\in V_{k,L}}L_i/n_{k,L}$ |
| Stage-clear occurrences | $\overline G_k=\sum_{i\in V_{k,G}}G_i/n_{k,G}$ |
| Saved game progress | $\overline U_k=\sum_{i\in V_{k,U}}U_i/n_{k,U}$ |
| Saved total score | $\overline S_k=\sum_{i\in V_{k,S}}S_i/n_{k,S}$ |

A mean command count is therefore **commands per learner**, not the cluster's total commands. A mean duration is **minutes per learner**, not the total time spent by the cluster.

## 6. Standard deviation, median, and missing counts

The sample standard deviation is:

$$
s_{k,X}=\sqrt{\frac{\sum_{i\in V_{k,X}}(X_i-\overline X_k)^2}{n_{k,X}-1}},
\qquad n_{k,X}\ge2.
\tag{16}
$$

Standard deviation is missing when fewer than two observed values are available. The median is the middle ordered observed value, or the average of the two middle values when the observed sample size is even.

$$
m_{k,X}=N_k-n_{k,X}
\tag{17}
$$

$m_{k,X}$ is the number of learners with missing values for that indicator. In `analysis_cluster_profiles.csv`, these quantities correspond to:

| Output column | Quantity |
|---|---|
| `cluster_n` | $N_k$ |
| `<feature>_count` | $n_{k,X}$ |
| `<feature>_missing` | $m_{k,X}$ |
| `<feature>_mean` | $\overline X_k$ |
| `<feature>_std` | $s_{k,X}$ |
| `<feature>_median` | Median observed value |

## 7. Worked examples from the current report

- **Cluster 2 commands:** 4 observed commands across 31 learners with available counters gives $4/31=0.1290$ commands per learner. The cluster contains 32 learners, but one command count is missing.
- **Cluster 2 correct actions:** 174 events across 31 learners with available counts gives $174/31=5.6129$ events per learner. The learner missing this indicator is not necessarily the learner missing a command count.
- **Cluster 1 stage clears:** 925 saved clear occurrences across 57 learners gives $925/57=16.2281$, reported as 16.23 clear occurrences per learner, including repetitions.
- **Illustrative efficiency calculation:** learners scoring 1,000 points in 10 and 100 minutes have individual efficiencies of 100 and 10 points/minute. Their mean individual efficiency is 55 points/minute; the ratio of total score to total duration is $2,000/110=18.18$ points/minute. These are different summaries.

## 8. Suggested manuscript wording

> Eleven participant-level indicators were used for clustering: saved Git-command count, correct and failed game-action counts, hint- and answer-labelled event counts, recorded play duration, global leaderboard-check count, score per recorded play minute, recorded game-action success proportion, perfect-labelled events per quest completion, and help-labelled events per quest completion. Four derived ratios were calculated separately for each participant using Equations (1)-(4). Saved stage-clear occurrences, game progress, and total stage score were reported as profile outcomes. Cluster-level summaries were calculated as the arithmetic means and sample standard deviations of observed participant-level values using Equations (15)-(16). Ratios with missing inputs or zero denominators were treated as missing, and valid sample sizes were reported separately for each indicator. This procedure gives equal weight to each participant with an observed value for the corresponding indicator. Missing features were median-imputed for clustering only, not for descriptive summaries or group comparisons.

> Correct game actions include tutorial interface interactions and should not be interpreted as successful Git commands. Stage-clear occurrences include repeated completions and are not counts of distinct study stages. The perfect-, hint-, and answer-related indicators use event-detail matching; interpreting them as distinct completed quests requires validation of the logging semantics.

The original code column names can be retained in a supplementary data dictionary while using the more explicit labels above in paper tables. Statistical tests compare each indicator across clusters; comparisons of the indicators used to form those clusters remain exploratory rather than independent validation. See [analysis methods](PYTHON_ANALYSIS_RESEARCH_GUIDE.md) for testing and preprocessing details.
