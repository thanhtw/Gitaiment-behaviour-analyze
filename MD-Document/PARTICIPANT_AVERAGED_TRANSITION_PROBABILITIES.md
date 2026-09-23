# Participant-Averaged First-Order Transition Probabilities

## Implementation status

This document specifies a method that calculates transition probabilities **for each participant first, then averages them within each cluster**.

The current [transition-analysis code](../Extract-Data-Code/behavior_transition_analysis.py) instead pools transition counts within each cluster before calculating probabilities. Therefore, the existing `analysis_behavior_transitions_by_cluster.csv` does **not** contain the participant-averaged probabilities defined below. The analysis code and results must be updated before the suggested manuscript wording is used to describe the implemented analysis. This document does not change the code or results.

## 1. Notation and transition sequences

| Symbol | Definition |
|---|---|
| $i$ | Participant index |
| $k$ | Cluster index |
| $I_k$ | Participants assigned to cluster $k$ |
| $\mathcal S$ | Set of behavioral states |
| $a,b,c$ | States in $\mathcal S$ |
| $s_{i,t}$ | State of participant $i$ at position $t$ in the ordered sequence |
| $m_i$ | Number of retained state observations for participant $i$ |
| $N_i(a,b)$ | Number of observed transitions from $a$ to $b$ for participant $i$ |
| $O_i(a)$ | Total observed outgoing transitions from $a$ for participant $i$ |
| $V_{k,a}$ | Participants in cluster $k$ with $O_i(a)>0$ |
| $n_{k,a}$ | Number of participants in $V_{k,a}$ |

The behavioral states are Action (A), Exploration (E), Command manipulation (CM), Instructional material/help (IM), Failure (F), and Reward/progression (R). Exact event mappings are defined in the [state dictionary](../Analysis-Log-Results/analysis_behavior_state_dictionary.csv).

First-order transitions connect each retained state observation to the next retained observation within the same participant. Counts never cross participant boundaries. Self-transitions, such as CM to CM, are included. The final observation has no following observation and contributes no outgoing transition.

The current sequence construction sorts mapped events by timestamp, excludes unmapped events and invalid timestamps, and does not split sequences at session boundaries. Thus, “next” currently means the next retained mapped event, potentially across a session gap. Changing to within-session transitions would be a separate methodological change that should be documented.

## 2. Count transitions for each participant

$$
N_i(a,b)=\sum_{t=1}^{m_i-1}
\mathbf{1}\{s_{i,t}=a\ \text{and}\ s_{i,t+1}=b\},
\tag{1}
$$

where $\mathbf{1}\{\cdot\}$ equals 1 when its condition holds and 0 otherwise. A sequence with fewer than two observations contributes no transitions.

Total outgoing transitions from state $a$ are:

$$
O_i(a)=\sum_{c\in\mathcal S}N_i(a,c).
\tag{2}
$$

This denominator counts observed transitions, not participants and not all occurrences of $a$. For example, an occurrence of $a$ at the end of a participant's sequence has no outgoing transition.

## 3. Calculate participant-level probabilities

$$
p_i(a\rightarrow b)=\frac{N_i(a,b)}{O_i(a)},
\qquad O_i(a)>0.
\tag{3}
$$

This is the participant's observed proportion of outgoing transitions from $a$ that lead to $b$.

- If $O_i(a)>0$ and $N_i(a,b)=0$, the probability is **zero**.
- If $O_i(a)=0$, the probability is **undefined**, not zero.
- No smoothing or pseudocount is used in this specification.

For each participant with an observed outgoing transition from $a$:

$$
\sum_{b\in\mathcal S}p_i(a\rightarrow b)=1.
$$

## 4. Average probabilities within each cluster

Define the contributing participants separately for each originating state:

$$
V_{k,a}=\{i\in I_k:O_i(a)>0\},
\qquad n_{k,a}=|V_{k,a}|.
\tag{4}
$$

The cluster-level participant-averaged transition probability is:

$$
\boxed{
\overline p_k(a\rightarrow b)=
\frac{1}{n_{k,a}}\sum_{i\in V_{k,a}}p_i(a\rightarrow b)
},\qquad n_{k,a}>0.
\tag{5}
$$

Each contributing participant has equal weight $1/n_{k,a}$, regardless of their number of outgoing transitions from $a$. A participant with one such transition receives the same weight as a participant with 100.

The denominator $n_{k,a}$ is not necessarily the cluster's total membership. It can differ by originating state, but must be the **same for all destination states in a given originating-state row**. Include zero-probability destinations for contributing participants; do not average only participants who exhibited the particular pair $a\rightarrow b$.

If no participant has an outgoing transition from $a$, the entire cluster row for $a$ is undefined and should be reported as unavailable, not as a row of zeros.

For a cluster row with at least one contributing participant:

$$
\sum_{b\in\mathcal S}\overline p_k(a\rightarrow b)=1.
$$

Multiply $\overline p_k(a\rightarrow b)$ by 100 to report a percentage.

## 5. Difference from pooling transition counts

The current code calculates:

$$
p_k^{\mathrm{pooled}}(a\rightarrow b)=
\frac{\sum_{i\in I_k}N_i(a,b)}
{\sum_{i\in I_k}O_i(a)},
\tag{6}
$$

when the denominator is positive. Equivalently:

$$
p_k^{\mathrm{pooled}}(a\rightarrow b)=
\sum_{i\in V_{k,a}}
\frac{O_i(a)}{\sum_{j\in V_{k,a}}O_j(a)}
p_i(a\rightarrow b).
$$

Pooling weights participants by their number of outgoing transitions from the originating state. Participant averaging weights contributing participants equally. These methods answer different questions and generally give different values.

### Illustrative example

| Participant | Transitions $a\rightarrow b$ | All outgoing transitions from $a$ | Participant probability |
|---|---:|---:|---:|
| 1 | 9 | 10 | 0.90 |
| 2 | 1 | 2 | 0.50 |
| 3 | 0 | 0 | Undefined; excluded for state $a$ |

Participant-averaged probability:

$$
\overline p_k(a\rightarrow b)=\frac{0.90+0.50}{2}=0.70.
$$

Pooled probability:

$$
p_k^{\mathrm{pooled}}(a\rightarrow b)=\frac{9+1}{10+2}
=0.8333.
$$

The participant-averaged result is **70.00%**; the pooled result is **83.33%**. Participant 3 is excluded because no conditional probability from $a$ can be estimated for that participant. If a participant instead had outgoing transitions from $a$ but none to $b$, that participant would contribute zero to the average.

## 6. Suggested manuscript wording

**Use this wording only after implementing and regenerating participant-averaged results:**

> First-order transition probabilities were calculated separately for each participant by dividing the frequency of each state-to-state transition by the participant's total observed outgoing transitions from the originating state. These probabilities were then averaged within each cluster, giving equal weight to participants with at least one observed outgoing transition from that state. Participants without outgoing transitions from a given state were excluded from that state's average. For contributing participants, unobserved destination transitions were assigned probability zero. The number of contributing participants was reported for each originating state.

Suggested interpretation:

> The reported probability represents the mean participant-level conditional transition probability among cluster members with observed outgoing transitions from the originating state.

This is not the percentage of participants who ever performed the transition. It is also not the proportion of all pooled transitions unless the two averaging procedures happen to coincide.

## 7. Reporting and implementation requirements

To implement this method, calculate participant-level transition counts before aggregating by cluster, include all destination states for each observed participant-originating-state combination, and average the resulting probabilities using Equation (5).

Recommended cluster output fields are:

| Field | Meaning |
|---|---|
| `Cluster` | Cluster label |
| `state` | Originating state $a$ |
| `next_state` | Destination state $b$ |
| `participants_with_outgoing` | $n_{k,a}$, contributing participants for this originating state |
| `mean_participant_probability` | $\overline p_k(a\rightarrow b)$ |
| `count` | Pooled transition count, retained as descriptive context |
| `outgoing_total` | Pooled outgoing count, retained as descriptive context |

Under this method, `mean_participant_probability` must **not** be calculated as `count / outgoing_total`; that division remains the pooled probability. Store both under distinct names if both are reported.

Before reporting results, verify that defined participant and cluster rows sum to one, undefined rows remain unavailable, and the participant denominator is constant across destinations for the same cluster and originating state. Construct probabilities before applying display thresholds. If a diagram omits low-probability edges, its displayed edges need not sum to one; do not renormalize them without explicitly defining a different measure.

Averages from participants with very few transitions can be variable. Report the contributing participant counts and transition counts with the probabilities. These descriptive transitions do not by themselves establish causality or statistically significant cluster differences.
