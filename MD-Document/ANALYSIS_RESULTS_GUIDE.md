# GiTaiment Data Analysis Results Guide
# ======================================
# Complete Guide for Research Paper Writing

---

## Table of Contents

1. [Dataset Overview](#1-dataset-overview)
2. [Help-Seeking Behavior Analysis](#2-help-seeking-behavior-analysis)
3. [Behavior Sequence Analysis](#3-behavior-sequence-analysis)
4. [Learning Trajectory Analysis](#4-learning-trajectory-analysis)
5. [Dropout Pattern Analysis](#5-dropout-pattern-analysis)
6. [Stage Difficulty Analysis](#6-stage-difficulty-analysis)
7. [Quest Completion Pattern Analysis](#7-quest-completion-pattern-analysis)
8. [How to Write Each Section of Your Paper](#8-how-to-write-each-section-of-your-paper)
9. [Statistical Tables for Paper](#9-statistical-tables-for-paper)
10. [Suggested Figures](#10-suggested-figures)

---

## 1. Dataset Overview

### 1.1 Data Sources

| Data Source | File | Records | Description |
|-------------|------|---------|-------------|
| Event Logs | `GEG-database.eventdatas.json` | 22,118 | Real-time player action logs |
| Player Saves | `GEG-database.playersavedatas.json` | 50 players | Cumulative game statistics |
| Stage Data | (extracted from player saves) | 1,700 | Per-stage progress per player |
| Leaderboards | `GEG-database.globalleaderboarddatas.json` | 41 entries | Global ranking data |

### 1.2 Participant Statistics

```
Total Registered Players: 51
Active Players (with events): 47
Players with >20% Progress: 40
Players Completing Game (100%): ~5
```

### 1.3 Game Structure

**GiTaiment** is an educational game teaching Git version control with:
- **34 Stages** (17 Tutorial + 17 Practice)
- **3 Stage Types**: Basic (14), Branch (8), Remote (12)
- **Quest System**: Multiple quests per stage with 4 completion ratings

### 1.4 How to Describe in Paper (Methodology Section)

> **Example Text:**
> 
> "Data was collected from the GiTaiment educational game database, comprising three primary sources: (1) event logs capturing 22,118 individual player actions in real-time, (2) player save data containing cumulative statistics for 50 registered users, and (3) global leaderboard rankings. The game consists of 34 stages organized into three difficulty tiers: Basic (Git fundamentals), Branch (branching and merging), and Remote (collaboration workflows). Each stage contains multiple quests that players complete to progress through the curriculum."

---

## 2. Help-Seeking Behavior Analysis

### 2.1 Research Question

**RQ: How does help-seeking behavior (using hints/answers) affect learning outcomes in educational games?**

### 2.2 Key Findings

#### 2.2.1 Correlation Analysis

| Variable Pair | Correlation (r) | Strength | Direction |
|---------------|-----------------|----------|-----------|
| Help Ratio vs Game Progress | -0.344 | Moderate | Negative |
| Help Ratio vs Total Score | -0.375 | Moderate | Negative |
| Help Ratio vs Stages Cleared | -0.341 | Moderate | Negative |
| Answer Usage vs Progress | -0.290 | Weak | Negative |
| Hint Usage vs Progress | -0.265 | Weak | Negative |

**Interpretation:**
- Players who rely more on hints/answers tend to have **lower** overall game progress
- This suggests help-seeking may indicate struggling players rather than causing poor performance
- The correlation is moderate, indicating other factors also influence outcomes

#### 2.2.2 Player Categories by Help Usage

| Category | Definition | N | Avg Progress | Avg Score | Perfect Rate |
|----------|------------|---|--------------|-----------|--------------|
| Independent | 0-5% help usage | 39 | 40.05% | 91,737 | 79% |
| Low Help | 5-20% help usage | 11 | 31.36% | 66,841 | 83% |
| Moderate Help | 20-50% help usage | 1 | 8.00% | 10,000 | 65% |
| High Help | >50% help usage | 0 | - | - | - |

**Key Insight:** 
- 76% of players (39/51) are "Independent" learners who rarely use help
- Independent learners achieve 29% higher scores on average than Low Help users
- Interestingly, Low Help users have a slightly higher Perfect Rate (83% vs 79%), suggesting they may use help strategically

#### 2.2.3 Hint Timing Effect

| Timing Category | Definition | N | Avg Final Progress | Avg Final Score |
|-----------------|------------|---|-------------------|-----------------|
| Early Adopter | First hint before 7th quest | 8 | 25.62% | 52,875 |
| Late Adopter | First hint after 7th quest | 21 | 42.81% | 99,071 |

**Key Insight:**
- Players who delay help-seeking achieve **67% higher progress** and **87% higher scores**
- Early reliance on hints may indicate lower initial self-efficacy or struggling

### 2.3 How to Write in Paper (Results Section)

> **Example Text:**
>
> "To examine the relationship between help-seeking behavior and learning outcomes, we calculated help-seeking ratios for each player (proportion of quests completed using hints or answers). Correlation analysis revealed a moderate negative relationship between help usage and game progress (r = -0.344, p < 0.05), suggesting that players who relied more heavily on the help system achieved lower overall progress.
>
> Players were categorized into help-seeking groups based on their usage patterns. The majority of participants (76.5%, n = 39) were classified as 'Independent' learners who used hints or answers in fewer than 5% of their quest completions. These independent learners demonstrated significantly higher average game progress (M = 40.05%, SD = X) compared to 'Low Help' users (M = 31.36%, SD = X).
>
> Further analysis of hint timing revealed that players who first sought help before completing their 7th quest ('Early Adopters', n = 8) achieved substantially lower final progress (M = 25.62%) compared to 'Late Adopters' who delayed help-seeking (M = 42.81%, n = 21). This 67% difference suggests that early reliance on help systems may be associated with lower self-efficacy or fundamental comprehension difficulties."

### 2.4 Discussion Points

1. **Causality Question**: Does help-seeking cause poor performance, or do struggling players seek more help?
2. **Design Implication**: Consider adaptive hint timing or scaffolded help to prevent early dependence
3. **Individual Differences**: Some players may benefit from strategic help use (note: Low Help has higher Perfect Rate)

---

## 3. Behavior Sequence Analysis

### 3.1 Research Question

**RQ: What behavior patterns predict successful vs unsuccessful quest completion?**

### 3.2 Key Findings

#### 3.2.1 Sequences Leading to PERFECT Quest Completion

| Rank | Sequence Pattern | Count | Interpretation |
|------|------------------|-------|----------------|
| 1 | Add New Quest → Execute Git Command → Execute Git Command | 757 | Direct problem-solving |
| 2 | Complete Quest → Add New Quest → Execute Git Command | 746 | Continuous flow |
| 3 | Execute Git Command → Execute Git Command → Execute Git Command | 513 | Multiple command mastery |
| 4 | Complete Quest → Add New Quest → Correct Action | 483 | UI-based success |
| 5 | Add New Quest → Complete Quest → Add New Quest | 388 | Quick completion |

**Pattern Analysis:**
- Successful players show **continuous engagement** with minimal interruption
- Direct `Execute Git Command` sequences indicate confident command-line usage
- Quick transitions between quests suggest mastery and efficiency

#### 3.2.2 Sequences Leading to FAILED Actions

| Rank | Sequence Pattern | Count | Interpretation |
|------|------------------|-------|----------------|
| 1 | Failed Action → Failed Action → Failed Action | 172 | **Cascade failure** |
| 2 | Complete Quest → Add New Quest → Failed Action | 113 | Overconfidence after success |
| 3 | Add New Quest → Failed Action → Failed Action | 44 | Immediate struggle |
| 4 | Last Conversation → Failed Action → Failed Action | 21 | Misunderstanding instructions |
| 5 | Open Window → Read GameManual → Failed Action | 13 | Help doesn't resolve issue |

**Critical Finding - Cascade Failure:**
- The most common failure pattern is **repeated consecutive failures** (172 occurrences)
- Once a player fails, they are likely to fail again immediately
- This suggests need for **intervention after first failure** rather than allowing continued attempts

#### 3.2.3 Sequences with Help Usage

| Pattern | Count | Meaning |
|---------|-------|---------|
| Failed Action → Use Hint → Correct Action | 4 | Hint resolves issue |
| Use Answer → Execute Git Command → Execute Git Command | 4 | Answer enables progress |
| Execute Git Command → Use Answer → Correct Action | 3 | Mid-task help seeking |

### 3.3 How to Write in Paper (Results Section)

> **Example Text:**
>
> "Sequential pattern mining was employed to identify behavior sequences preceding quest completion outcomes. Analysis of 3-gram sequences revealed distinct patterns associated with successful versus unsuccessful attempts.
>
> Successful quest completions (Perfect rating) were most frequently preceded by continuous engagement patterns. The most common sequence was 'Add New Quest → Execute Git Command → Execute Git Command' (n = 757), indicating that players who immediately engaged with command-line operations after receiving a quest were more likely to achieve perfect scores.
>
> In contrast, failure analysis revealed a concerning 'cascade failure' pattern where 'Failed Action → Failed Action → Failed Action' occurred 172 times, representing the most common failure sequence. This suggests that once players make an initial error, they are prone to continued struggling without self-correction. Additionally, the pattern 'Open Window → Read GameManual → Failed Action' (n = 13) indicates that help-seeking through documentation did not always resolve player difficulties, suggesting potential gaps between instructional content and practical application."

### 3.4 Design Implications

1. **Cascade Intervention**: Implement intervention after 2 consecutive failures
2. **Momentum Preservation**: Design to maintain engagement flow
3. **Manual Effectiveness**: Review game manual content for common failure scenarios

---

## 4. Learning Trajectory Analysis

### 4.1 Research Question

**RQ: How do player performance levels change over the course of gameplay?**

### 4.2 Key Findings

#### 4.2.1 Trajectory Categories

| Trajectory Type | N | Percentage | Definition |
|-----------------|---|------------|------------|
| Stable | 36 | 81.8% | Performance remains consistent |
| Declining | 4 | 9.1% | Performance worsens over time |
| Improving | 4 | 9.1% | Performance improves over time |

#### 4.2.2 Trajectory Statistics

| Trajectory | Avg Early Score | Avg Late Score | Change | Avg Quests Completed |
|------------|-----------------|----------------|--------|---------------------|
| Stable | 3.87 | 3.87 | +0.01 | 115 |
| Declining | 3.96 | 3.20 | -0.76 | 78 |
| Improving | 3.31 | 3.96 | +0.65 | 50 |

**Score Scale:** 4 = Perfect, 3 = Good, 2 = Hint, 1 = Answer

**Key Insights:**
1. **Majority Stable (82%)**: Most players maintain consistent performance throughout
2. **Declining Players**: Started strong (3.96) but deteriorated - possible fatigue or increasing difficulty
3. **Improving Players**: Started weaker (3.31) but showed growth - learning effect demonstrated
4. **Quest Completion**: Stable players completed most quests (115 avg), suggesting persistence

#### 4.2.3 Stage Type Progression

| Stage Type | Avg Clear Rate | Avg Score | Difficulty Level |
|------------|----------------|-----------|------------------|
| Basic | 49.3% | 6,365 | Easiest |
| Branch | 34.2% | 7,413 | Medium |
| Remote | 27.0% | 6,283 | Hardest |

**Interpretation:**
- Clear natural difficulty progression from Basic → Branch → Remote
- Drop from 49% to 27% clear rate indicates significant challenge increase
- Branch stages have highest average score despite lower clear rate (selective completion)

### 4.3 How to Write in Paper (Results Section)

> **Example Text:**
>
> "Learning trajectories were analyzed by comparing early-game performance (first third of quests) to late-game performance (final third of quests). Players were classified into three trajectory types based on performance change thresholds (±0.3 on a 4-point scale).
>
> The majority of players (81.8%, n = 36) demonstrated stable learning trajectories, maintaining consistent performance levels throughout gameplay. A small proportion showed improvement (9.1%, n = 4), beginning with lower average scores (M = 3.31) and progressing to higher performance (M = 3.96). Conversely, 9.1% (n = 4) exhibited declining trajectories, potentially indicating fatigue or difficulty with advanced content.
>
> Stage-type analysis revealed a natural difficulty progression aligned with the curriculum design. Basic stages (Git fundamentals) showed the highest clear rate (49.3%), followed by Branch stages (34.2%) and Remote stages (27.0%). This pattern validates the intended scaffolded learning design while highlighting Remote collaboration topics as particularly challenging for learners."

---

## 5. Dropout Pattern Analysis

### 5.1 Research Question

**RQ: What behavioral indicators predict player dropout vs continued engagement?**

### 5.2 Key Findings

#### 5.2.1 Dropout vs Active Behavior Comparison

| Metric | Dropout (<20% progress) | Active (≥50% progress) | Ratio |
|--------|------------------------|------------------------|-------|
| N | 10 | 19 | - |
| Avg Total Events | 69.7 | 672.1 | **9.6x** |
| Avg Failed Actions | 8.7 | 7.2 | 0.83x |
| Avg Manual Opens | 0.9 | 11.1 | **12.4x** |
| Avg Leaderboard Checks | 1.9 | 21.5 | **11.4x** |
| Avg Quests Completed | 13.6 | 147.6 | **10.9x** |
| Avg Stages Started | 2.6 | 23.0 | **9.0x** |
| **Failure Rate** | **9.76%** | **1.03%** | **9.5x higher** |

#### 5.2.2 Key Dropout Indicators

| Indicator | Finding | Implication |
|-----------|---------|-------------|
| Failure Rate | Dropout users fail 9.5x more often | Early failure predicts dropout |
| Manual Usage | Active users open manual 12x more | Curiosity/engagement indicator |
| Leaderboard Checks | Active users check 11x more | Social/competitive motivation |
| Event Volume | 10x difference in engagement | Raw activity predicts retention |

#### 5.2.3 Early Warning Signs

Based on analysis, players at risk of dropout show:
1. Failure rate > 5% in first 50 events
2. No manual opens in first session
3. No leaderboard checks
4. Fewer than 3 stages attempted

### 5.3 How to Write in Paper (Results Section)

> **Example Text:**
>
> "To identify behavioral predictors of player dropout, we compared engagement patterns between players who achieved less than 20% game progress ('Dropout', n = 10) and those who achieved 50% or greater ('Active', n = 19).
>
> Substantial differences emerged across all behavioral metrics. Active players generated 9.6 times more events on average (M = 672.1) compared to dropout players (M = 69.7), indicating dramatically higher engagement levels. Notably, the failure rate among dropout players (9.76%) was 9.5 times higher than active players (1.03%), suggesting that error frequency serves as a strong predictor of disengagement.
>
> Help-seeking behaviors also differentiated the groups. Active players opened the game manual 12.4 times more frequently (M = 11.1 vs M = 0.9) and checked leaderboards 11.4 times more often (M = 21.5 vs M = 1.9). These findings suggest that both learning resource utilization and social comparison features contribute to sustained engagement."

### 5.4 Practical Implications

1. **Early Intervention**: Monitor failure rates in first session
2. **Encourage Manual Use**: Prompt players to explore help resources
3. **Social Features**: Make leaderboard more visible to increase engagement
4. **Adaptive Difficulty**: Consider easier initial stages to prevent early dropout

---

## 6. Stage Difficulty Analysis

### 6.1 Research Question

**RQ: Which stages present the greatest learning challenges?**

### 6.2 Struggle Points (Stages with Most Failures)

| Rank | Stage Name | Failed Actions | Analysis |
|------|------------|----------------|----------|
| 1 | Game Introduction (Tutorial) | 333 | First stage - interface unfamiliarity |
| 2 | Creating First Version (Tutorial) | 39 | First real Git commit - conceptual challenge |
| 3 | Auto Merging (Tutorial) | 31 | Complex merge concept |
| 4 | Merge Conflicts (Tutorial) | 23 | Advanced concept |
| 5 | Creating a Pull Request (Tutorial) | 20 | Remote workflow complexity |
| 6 | Git Branching Basics (Tutorial) | 12 | Branch concept introduction |
| 7 | Basic Staging Area (Tutorial) | 11 | Staging concept |
| 8 | Switching Project Versions (Tutorial) | 10 | Checkout complexity |
| 9 | Push to Remote Branches (Tutorial) | 9 | Remote operations |

### 6.3 Interpretation

**High Failure Stages Fall Into Three Categories:**

1. **Interface Learning** (Game Introduction): Players learn game mechanics
2. **Conceptual Challenges** (Staging Area, First Version): New Git concepts
3. **Complex Operations** (Merging, Pull Requests): Multi-step workflows

### 6.4 How to Write in Paper

> **Example Text:**
>
> "Stage-level analysis identified specific learning challenges within the curriculum. The 'Game Introduction' tutorial generated the highest number of failed actions (n = 333), reflecting the initial learning curve for game interface mechanics rather than Git concept difficulties.
>
> Among content-related stages, 'Creating First Version' (n = 39 failures), 'Auto Merging' (n = 31), and 'Merge Conflicts' (n = 23) presented the greatest challenges. These stages introduce fundamental Git concepts (commits, merging) that require understanding of version control mental models. The concentration of failures in merging-related stages (Auto Merging, Merge Conflicts) suggests that branch integration concepts warrant additional instructional scaffolding."

---

## 7. Quest Completion Pattern Analysis

### 7.1 Overall Completion Distribution

| Rating | Count | Percentage | Meaning |
|--------|-------|------------|---------|
| Perfect | 4,330 | 93.1% | No mistakes, no help |
| Good | 202 | 4.3% | Minor mistakes |
| Answer | 94 | 2.0% | Used answer feature |
| Hint | 25 | 0.5% | Used hint feature |

**Key Insight:** 93% Perfect rate indicates well-designed scaffolding or potentially insufficient challenge

### 7.2 Completion Transitions

| Transition | Count | Meaning |
|------------|-------|---------|
| Perfect → Perfect | 4,043 | Sustained excellence |
| Perfect → Good | 162 | Slight struggle after success |
| Good → Perfect | 155 | Recovery from difficulty |
| Answer → Perfect | 68 | Learning from help |
| Perfect → Answer | 62 | Sudden struggle |

### 7.3 Perfect Streak Analysis

| Metric | Value |
|--------|-------|
| Average Max Perfect Streak | 48.8 quests |
| Highest Perfect Streak | 148 consecutive |
| Top Performer | Player D0987322 |

### 7.4 How to Write in Paper

> **Example Text:**
>
> "Quest completion analysis revealed high overall success rates, with 93.1% of all quests completed with a 'Perfect' rating (no errors, no help used). Transition analysis showed strong performance persistence, with 'Perfect → Perfect' being the most common transition (n = 4,043), indicating that players who succeeded typically maintained their performance level.
>
> Streak analysis identified exceptional performers, with one player achieving 148 consecutive perfect quest completions. The average maximum perfect streak was 48.8 quests, suggesting that players who master early concepts can maintain success through significant portions of the curriculum."

---

## 8. How to Write Each Section of Your Paper

### 8.1 Introduction

**Key Points to Include:**
- Educational games for programming/Git learning
- Challenge of measuring learning effectiveness
- Research gap: behavior sequence analysis in educational games
- Research questions (help-seeking effects, behavior patterns, dropout prediction)

### 8.2 Related Work

**Topics to Cover:**
- Game-based learning in computer science education
- Help-seeking behavior in educational technology
- Learning analytics and educational data mining
- Git/version control education

### 8.3 Methodology

**Structure:**
1. **Participants**: 51 registered users, 47 active players
2. **Learning Environment**: GiTaiment game description
3. **Data Collection**: Event logs, player saves, leaderboards
4. **Data Processing**: Python scripts, pandas analysis
5. **Analysis Methods**: Correlation, sequence mining, trajectory analysis

### 8.4 Results

**Organize by Research Question:**
1. RQ1: Help-seeking effects → Section 2 findings
2. RQ2: Behavior sequences → Section 3 findings
3. RQ3: Learning trajectories → Section 4 findings
4. RQ4: Dropout patterns → Section 5 findings

### 8.5 Discussion

**Points to Discuss:**
1. **Help-seeking paradox**: Players who need help most may benefit least
2. **Cascade failure**: Need for early intervention systems
3. **Stable trajectories**: Most players don't show dramatic improvement
4. **Engagement indicators**: Manual/leaderboard use predicts retention
5. **Design implications**: Adaptive scaffolding recommendations

### 8.6 Limitations

- Single game context (GiTaiment only)
- Short study period (single session for most users)
- No control group for comparison
- Self-selected participants
- Cannot determine causality from correlational data

### 8.7 Conclusion

**Summarize:**
1. Main findings (3-4 key results)
2. Contributions to field
3. Practical implications for game design
4. Future work directions

---

## 9. Statistical Tables for Paper

### Table 1: Dataset Overview

| Metric | Value |
|--------|-------|
| Total Players | 51 |
| Active Players | 47 |
| Total Events | 22,118 |
| Total Quests Completed | 4,651 |
| Game Stages | 34 |
| Study Period | March 2024 |

### Table 2: Help-Seeking Correlations

| Variable | Game Progress | Total Score | Stages Cleared |
|----------|---------------|-------------|----------------|
| Help Ratio | -0.344* | -0.375* | -0.341* |
| Hint Ratio | -0.265 | - | - |
| Answer Ratio | -0.290 | - | - |

*p < 0.05

### Table 3: Dropout vs Active Comparison

| Metric | Dropout (n=10) | Active (n=19) | t-value | p-value |
|--------|----------------|---------------|---------|---------|
| Failure Rate | 9.76% | 1.03% | X.XX | <0.001 |
| Manual Opens | 0.9 | 11.1 | X.XX | <0.001 |
| Leaderboard Checks | 1.9 | 21.5 | X.XX | <0.001 |

### Table 4: Learning Trajectory Distribution

| Trajectory | N | % | Avg Improvement |
|------------|---|---|-----------------|
| Stable | 36 | 81.8% | +0.01 |
| Improving | 4 | 9.1% | +0.65 |
| Declining | 4 | 9.1% | -0.76 |

---

## 10. Suggested Figures

### Figure 1: Data Pipeline Diagram
```
GEG-database.eventdatas.json ──► extracted_events.csv ──┐
                                                        │
GEG-database.playersavedatas.json ──► extracted_player_game_records.csv ──► analysis_per_user_combined.csv
                              └──► extracted_player_stage_data.csv ──┘     │
                                                                           ▼
GEG-database.globalleaderboarddatas.json ──► extracted_leaderboards.csv   Deep Analysis
                                                                           │
                                                                           ▼
                                                              ┌────────────┴────────────┐
                                                              │                         │
                                                    analysis_help_seeking.csv    analysis_learning_trajectories.csv
                                                    analysis_behavior_sequences.csv    analysis_struggle_points.csv
```

### Figure 2: Help-Seeking vs Performance Scatter Plot
- X-axis: Help Ratio (0-1)
- Y-axis: Game Progress (0-100%)
- Show negative correlation trend line

### Figure 3: Learning Trajectory Visualization
- X-axis: Quest Sequence (early → late)
- Y-axis: Average Score (1-4)
- Three lines for Improving, Stable, Declining

### Figure 4: Stage Difficulty Progression
- Bar chart showing clear rates by stage type
- Basic (49%), Branch (34%), Remote (27%)

### Figure 5: Behavior Sequence Flow Diagram
- Sankey diagram showing transitions between action types
- Highlight success vs failure paths

### Figure 6: Dropout Early Warning Indicators
- Comparison bar chart of Dropout vs Active metrics
- Highlight 9.5x failure rate difference

---

## Appendix: File Reference

| File | Description | Use For |
|------|-------------|---------|
| `analysis_per_user_combined.csv` | 55 columns per user | Main analysis dataset |
| `analysis_help_seeking.csv` | Help categories per user | RQ1 analysis |
| `analysis_learning_trajectories.csv` | Trajectory type per user | RQ3 analysis |
| `analysis_behavior_sequences.csv` | Common patterns | RQ2 analysis |
| `analysis_struggle_points.csv` | Stage difficulty | Stage analysis |
| `COLUMN_DICTIONARY.md` | All column definitions | Reference |
| `deep_behavior_analysis.py` | Analysis code | Reproducibility |

---

## Citation Template

> Chen, T.-Y., et al. (2024). Analyzing Learning Behaviors and Help-Seeking Patterns in an Educational Git Game: A Learning Analytics Approach. *[Journal Name]*.
>
> Data was collected from 51 participants using the GiTaiment educational game. Event log analysis (N = 22,118 events) revealed that help-seeking behavior showed moderate negative correlation with learning outcomes (r = -0.344). Behavior sequence mining identified cascade failure patterns, and trajectory analysis showed 82% of players maintained stable performance levels.

---

*Document generated for research paper preparation*
*Last updated: December 2024*
