# GiTaiment Per-User Combined Data - Column Dictionary
# ======================================================
# File: analysis_per_user_combined.csv
# Total Columns: 55
# Total Users: 51

---

## Overview

This document explains each column in `analysis_per_user_combined.csv`, including:
- **Meaning**: What the column represents
- **Data Source**: Which JSON file the data comes from
- **Calculation**: How the value is computed

---

## Key Game Concepts

### What is a Stage?
A **Stage** is a learning module (level) in GiTaiment that teaches specific Git concepts. The game has **34 stages** organized into:

| Stage Type | Description | Git Topics Covered |
|------------|-------------|-------------------|
| **Basic** | Fundamental Git operations | Repository creation, staging area, commits, version switching |
| **Branch** | Branching and merging | Branch creation, fast-forward merge, auto merge, merge conflicts |
| **Remote** | Remote collaboration | Remote repos, push, sync, pull requests |

Each topic has two modes:
- **Tutorial**: Guided instruction with explanations
- **Practice**: Self-directed practice without guidance

**Example Stages:**
- `Game Introduction (Tutorial)` - First stage introducing the game interface
- `Create Local Repository (Practice)` - Practice creating git init
- `Merge Conflicts (Tutorial)` - Learn to resolve merge conflicts

### What is a Quest?
A **Quest** is a specific task within a Stage. Each stage contains multiple quests (Quest1, Quest2, Quest3, etc.) that the player must complete.

**Quest Completion Ratings:**
| Rating | Meaning |
|--------|---------|
| **Perfect** | Completed without any mistakes or help |
| **Good** | Completed with minor mistakes but no help used |
| **Hint** | Completed using the hint system |
| **Answer** | Completed by viewing the answer |

### What are Actions?
**Actions** are the interactive operations players perform during quests, simulating Git commands through the game UI.

**Action Types in eventDetail:**
| Action | Simulated Git Operation |
|--------|------------------------|
| `<File/FileFunctionSelection>` | Selecting a file operation |
| `<FileContentWindow/AddButtonSelection>` | `git add` (staging a file) |
| `<FileContentWindow/DeleteButtonSelection>` | `rm` or `git rm` (removing a file) |
| `<FileContentWindow/RenameButtonSelection>` | `mv` or `git mv` (renaming a file) |
| `<FileContentWindow/ModifyButtonSelection>` | Modifying file content |

---

## Understanding Failed Actions

A **Failed Action** occurs when a player performs an incorrect operation during a quest. The `eventDetail` field reveals the exact cause:

### Failed Action Format
```
<UI_Element/Action> - <UI_Element/Action/Error_Type>
```

### Error Types and Their Meanings

| Error Type | Meaning | Example Scenario |
|------------|---------|------------------|
| **Wrong Quest** | Player performed the action on the wrong quest/target | Tried to delete File A when Quest asked to delete File B |
| **Wrong Content** | Player modified content incorrectly | Changed file content to wrong value |
| **Wrong File** | Player selected the wrong file | Staged wrong file instead of the requested one |
| **Wrong Command** | Player used incorrect Git command type | Used `add` when should have used `commit` |

### Real Examples from Data

| eventDetail | Explanation |
|-------------|-------------|
| `<FileContentWindow/DeleteButtonSelection>-<Wrong Quest>` | Player clicked delete button but targeted wrong file/quest |
| `<FileContentWindow/AddButtonSelection>-<Wrong Quest>` | Player tried to add/stage wrong file |
| `<FileContentWindow/RenameButtonSelection>-<Wrong Quest>` | Player attempted to rename wrong file |
| `<FileContentWindow/ModifyButtonSelection>-<Wrong Quest>` | Player modified wrong file content |
| `<FileContentWindow/DeleteButtonSelection>-<Wrong Content>` | Player deleted with incorrect parameters |

### Research Implications
- High `event_failed_actions` indicates learning difficulty or trial-and-error behavior
- Compare `event_correct_actions` vs `event_failed_actions` for **action success rate**
- `Wrong Quest` errors suggest confusion about task requirements
- `Wrong Content` errors suggest misunderstanding of Git concepts

---

## Column Categories

| Prefix | Data Source | Description |
|--------|-------------|-------------|
| `event_` | GEG-database.eventdatas.json | Real-time player action logs |
| `record_` | GEG-database.playersavedatas.json → gameRecordData | Cumulative game statistics |
| `stage_` | GEG-database.playersavedatas.json → stageData | Per-stage progression data |
| `rank_` | GEG-database.globalleaderboarddatas.json | Leaderboard rankings |

---

## 1. IDENTIFIER COLUMN

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `username` | Unique player identifier | Direct from player field in all data sources |

---

## 2. EVENT-BASED COLUMNS (from eventdatas.json)

These columns are calculated from the real-time event logs that capture every player action.

### 2.1 Activity Summary

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_total_events` | Total number of events recorded | `COUNT(*)` for all events where `player = username` |
| `event_first_activity` | Timestamp of first recorded action | `MIN(eventTime)` for the user |
| `event_last_activity` | Timestamp of last recorded action | `MAX(eventTime)` for the user |
| `event_activity_span_days` | Days between first and last activity | `(last_activity - first_activity).days` |

### 2.2 Login & Session Data

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_total_logins` | Number of times player logged in | `COUNT(*)` where `eventName = 'Login'` |
| `event_total_sessions` | Number of distinct play sessions | Count of login events with gap > 30 minutes from previous event |

### 2.3 Stage & Quest Progress

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_stages_started` | Number of times player started a stage | `COUNT(*)` where `eventName = 'Start Stage'` |
| `event_unique_stages_attempted` | Number of distinct stages attempted | `COUNT(DISTINCT gameScene)` where `eventName = 'Start Stage'` |
| `event_quests_added` | Number of quests initiated | `COUNT(*)` where `eventName = 'Add New Quest'` |
| `event_quests_completed` | Total quests completed (any rating) | `COUNT(*)` where `eventName = 'Complete Quest'` |
| `event_perfect_quests` | Quests completed with Perfect rating | `COUNT(*)` where `eventName = 'Complete Quest'` AND `eventDetail` contains `'Perfect'` |
| `event_good_quests` | Quests completed with Good rating | `COUNT(*)` where `eventName = 'Complete Quest'` AND `eventDetail` contains `'Good'` |
| `event_hint_used_quests` | Quests completed using hints | `COUNT(*)` where `eventName = 'Complete Quest'` AND `eventDetail` contains `'Hint'` |
| `event_answer_used_quests` | Quests completed using answers | `COUNT(*)` where `eventName = 'Complete Quest'` AND `eventDetail` contains `'Answer'` |

### 2.4 Player Actions

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_correct_actions` | Number of correct Git commands executed | `COUNT(*)` where `eventName = 'Correct Action'` |
| `event_failed_actions` | Number of incorrect Git commands executed | `COUNT(*)` where `eventName = 'Failed Action'` |

### 2.5 Learning Resources Usage

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_game_manual_opens` | Times player opened the game manual | `COUNT(*)` where `eventName = 'Read GameManual'` |
| `event_manual_pages_read` | Specific manual pages viewed | `COUNT(*)` where `eventName = 'Read GameManual'` AND `eventDetail` is not empty |
| `event_window_opens` | Times player opened game windows | `COUNT(*)` where `eventName = 'Open Window'` |

### 2.6 Social/Competitive Features

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `event_leaderboard_checks` | Times player viewed leaderboard | `COUNT(*)` where `eventName = 'Check GlobalLeaderBoard'` |
| `event_leaderboard_score_checks` | Times player checked score ranking | `COUNT(*)` where `eventName = 'Check GlobalLeaderBoard'` AND `eventDetail` contains `'TotalScore'` |
| `event_leaderboard_progress_checks` | Times player checked progress ranking | `COUNT(*)` where `eventName = 'Check GlobalLeaderBoard'` AND `eventDetail` contains `'GameProgress'` |
| `event_player_records_viewed` | Times player viewed own records | `COUNT(*)` where `eventName = 'Open Window'` AND `eventDetail = 'PlayerRecord'` |
| `event_last_conversations` | Conversation completion events | `COUNT(*)` where `eventName = 'Last Conversation'` |

---

## 3. GAME RECORD COLUMNS (from playersavedatas.json → gameRecordData)

These columns come directly from the player's saved game record, representing cumulative statistics.

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `record_totalStarCount` | Total stars earned across all stages | Direct from `gameRecordData.totalStarCount` |
| `record_totalStageScore` | Cumulative score from all stages | Direct from `gameRecordData.totalStageScore` |
| `record_totalGameProgress` | Overall game completion percentage (0-100) | Direct from `gameRecordData.totalGameProgress` |
| `record_totalPlayTime` | Total time played in seconds | Direct from `gameRecordData.totalPlayTime` |
| `record_totalTimesStageClear` | Total number of stage completions | Direct from `gameRecordData.totalTimesStageClear` |
| `record_totalTimesUsedGameManual` | Times game manual was used | Direct from `gameRecordData.totalTimesUsedGameManual` |
| `record_totalCommandExecuteTimes` | Total Git commands executed | Direct from `gameRecordData.totalCommandExecuteTimes` |
| `record_totalTimesQuestClearPerfect` | Quest completions with Perfect rating | Direct from `gameRecordData.totalTimesQuestClearPerfect` |
| `record_totalTimesQuestClearGood` | Quest completions with Good rating | Direct from `gameRecordData.totalTimesQuestClearGood` |
| `record_totalTimesQuestClearHint` | Quest completions using hints | Direct from `gameRecordData.totalTimesQuestClearHint` |
| `record_totalTimesQuestClearAnswer` | Quest completions using answers | Direct from `gameRecordData.totalTimesQuestClearAnswer` |

---

## 4. STAGE PROGRESS COLUMNS (from playersavedatas.json → stageData)

These columns summarize the player's progress across all 34 game stages.

### Complete Stage List (34 Stages)

**Basic Type - Git Fundamentals (14 stages):**
| Tutorial Stage | Practice Stage |
|----------------|----------------|
| Game Introduction (Tutorial) | Game Introduction (Practice) |
| Version Control and Git (Tutorial) | Version Control and Git (Practice) |
| Create Local Repository (Tutorial) | Create Local Repository (Practice) |
| Basic Staging Area (Tutorial) | Basic Staging Area (Practice) |
| Advanced Staging Area (Tutorial) | Advanced Staging Area (Practice) |
| Creating First Version (Tutorial) | Creating First Version (Practice) |
| Switching Project Versions (Tutorial) | Switching Project Versions (Practice) |

**Branch Type - Branching & Merging (8 stages):**
| Tutorial Stage | Practice Stage |
|----------------|----------------|
| Git Branching Basics (Tutorial) | Git Branching Basics (Practice) |
| Fast-Forward Merging (Tutorial) | Fast-Forward Merging (Practice) |
| Auto Merging (Tutorial) | Auto Merging (Practice) |
| Merge Conflicts (Tutorial) | Merge Conflicts (Practice) |

**Remote Type - Collaboration (12 stages):**
| Tutorial Stage | Practice Stage |
|----------------|----------------|
| Create Remote Repository (Tutorial) | Create Remote Repository (Practice) |
| Push to Remote Branches (Tutorial) | Push to Remote Branches (Practice) |
| Keep Branches in Sync (Tutorial) | Keep Branches in Sync (Practice) |
| Preparation for Merging (Tutorial) | Preparation for Merging (Practice) |
| Creating a Pull Request (Tutorial) | Creating a Pull Request (Practice) |
| Review and Merge Pull Requests (Tutorial) | Review and Merge Pull Requests (Practice) |

### 4.1 Overall Stage Progress

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `stage_total_stages` | Total stages in the game | `COUNT(*)` of stage records for the user (should be 34) |
| `stage_stages_unlocked` | Number of stages unlocked | `SUM(isStageUnlock)` where `isStageUnlock = True` |
| `stage_stages_cleared` | Number of stages completed at least once | `COUNT(*)` where `stageClearTimes > 0` |
| `stage_total_clear_times` | Total stage completions (including replays) | `SUM(stageClearTimes)` across all stages |

### 4.2 Performance Metrics

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `stage_avg_best_score` | Average best score on cleared stages | `AVG(bestPlayerScore)` where `bestPlayerScore > 0` |
| `stage_avg_clear_time` | Average best clear time (seconds) | `AVG(bestPlayerClearTime)` where `bestPlayerClearTime > 0` |

### 4.3 Progress by Stage Type

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `stage_basic_stages_unlocked` | Basic (Git basics) stages unlocked | `SUM(isStageUnlock)` where `stageType = 'Basic'` |
| `stage_branch_stages_unlocked` | Branch (branching) stages unlocked | `SUM(isStageUnlock)` where `stageType = 'Branch'` |
| `stage_remote_stages_unlocked` | Remote (collaboration) stages unlocked | `SUM(isStageUnlock)` where `stageType = 'Remote'` |

### 4.4 Progress by Stage Category

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `stage_tutorial_stages_cleared` | Tutorial stages completed | `COUNT(*)` where `stageName` contains `'Tutorial'` AND `stageClearTimes > 0` |
| `stage_practice_stages_cleared` | Practice stages completed | `COUNT(*)` where `stageName` contains `'Practice'` AND `stageClearTimes > 0` |

---

## 5. RANKING COLUMNS (from globalleaderboarddatas.json)

These columns show the player's position on global leaderboards.

### 5.1 Progress Leaderboard

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `rank_progress_rank` | Player's rank by game progress | Position in `GameProgress` leaderboard (1 = highest) |
| `rank_progress_value` | Player's game progress value | `gameProgress` value from leaderboard entry |
| `rank_progress_total_players` | Total players on progress leaderboard | `COUNT(*)` of players in `GameProgress` leaderboard |
| `rank_progress_percentile` | Percentile ranking (higher = better) | `(1 - (rank - 1) / total_players) × 100` |

### 5.2 Score Leaderboard

| Column | Meaning | Calculation |
|--------|---------|-------------|
| `rank_score_rank` | Player's rank by total score | Position in `TotalScore` leaderboard (1 = highest) |
| `rank_score_value` | Player's total score value | `totalScore` value from leaderboard entry |
| `rank_score_total_players` | Total players on score leaderboard | `COUNT(*)` of players in `TotalScore` leaderboard |
| `rank_score_percentile` | Percentile ranking (higher = better) | `(1 - (rank - 1) / total_players) × 100` |

---

## Data Quality Notes

### Missing Values (NaN)
- A `NaN` value indicates the player was not found in that particular data source
- Example: A player may have event data but no leaderboard entry

### Event vs Record Discrepancies
- `event_*` columns are calculated from real-time logs (may miss some actions)
- `record_*` columns are from saved game state (authoritative cumulative values)
- Small differences are normal; use `record_*` for accurate totals

### Time Values
- `event_first_activity` and `event_last_activity` are in UTC timezone
- `record_totalPlayTime` is in seconds
- `stage_avg_clear_time` is in seconds

---

## Example Calculations

### Quest Completion Rate
```
quest_completion_rate = event_quests_completed / event_quests_added
```

### Perfect Quest Rate  
```
perfect_rate = event_perfect_quests / event_quests_completed
```

### Action Success Rate
```
success_rate = event_correct_actions / (event_correct_actions + event_failed_actions)
```
**Interpretation:**
- `success_rate > 0.9` = High proficiency, few mistakes
- `success_rate 0.7-0.9` = Moderate learning curve
- `success_rate < 0.7` = Struggling or exploring trial-and-error

### Learning Style (Help-seeking)
```
help_seeking_ratio = (event_hint_used_quests + event_answer_used_quests) / event_quests_completed
```
**Interpretation:**
- `ratio = 0` = Independent learner, never uses help
- `ratio < 0.2` = Mostly self-reliant
- `ratio > 0.5` = Relies heavily on help system

### Self-Learning vs Guided Learning
```
self_learning_rate = event_perfect_quests / event_quests_completed
guided_learning_rate = (event_hint_used_quests + event_answer_used_quests) / event_quests_completed
```

### Engagement Level
```
avg_events_per_session = event_total_events / event_total_sessions
```

### Game Completion
```
completion_rate = stage_stages_cleared / stage_total_stages
```

### Learning Progression Analysis
```python
# Early dropout: Started but completed few stages
early_dropout = (event_stages_started > 0) and (stage_stages_cleared < 5)

# Tutorial-focused: Completed tutorials but not practice
tutorial_focused = stage_tutorial_stages_cleared > stage_practice_stages_cleared

# Mastery learner: High perfect quest rate
mastery_learner = (event_perfect_quests / event_quests_completed) > 0.8
```

### Error Analysis for Research
```python
# High error rate indicates learning difficulty
error_rate = event_failed_actions / (event_correct_actions + event_failed_actions)

# If error_rate > 0.3, player may be:
# 1. Exploring through trial-and-error
# 2. Struggling with Git concepts
# 3. Not reading quest instructions carefully
```

---

## Data Source Files

| Source File | Extracted CSV | Description |
|-------------|---------------|-------------|
| GEG-database.eventdatas.json | extracted_events.csv | 22,120 event records |
| GEG-database.playersavedatas.json | extracted_player_game_records.csv | 51 player records |
| GEG-database.playersavedatas.json | extracted_player_stage_data.csv | 1,598 stage records |
| GEG-database.globalleaderboarddatas.json | extracted_leaderboards.csv | Leaderboard data |

---

## Deep Analysis Results (from deep_behavior_analysis.py)

### New Analysis Output Files

| File | Description |
|------|-------------|
| `analysis_help_seeking.csv` | Help-seeking behavior categorization per user |
| `analysis_learning_trajectories.csv` | Learning trajectory analysis (Improving/Stable/Declining) |
| `analysis_struggle_points.csv` | Stage difficulty analysis by failure rate |
| `analysis_behavior_sequences.csv` | Common behavior sequences leading to success/failure |

---

## Key Research Findings

### 1. Help-Seeking Effect on Performance

**Finding**: Negative correlation between help usage and performance

| Correlation | Value | Interpretation |
|-------------|-------|----------------|
| Help Ratio vs Game Progress | -0.344 | Moderate negative |
| Help Ratio vs Total Score | -0.375 | Moderate negative |
| Answer Ratio vs Progress | -0.290 | Weak negative |
| Hint Ratio vs Progress | -0.265 | Weak negative |

**Player Categories by Help Usage:**
| Category | Count | Avg Progress | Avg Score | Perfect Rate |
|----------|-------|--------------|-----------|--------------|
| Independent (0-5% help) | 39 | 40.05% | 91,737 | 79% |
| Low Help (5-20%) | 11 | 31.36% | 66,841 | 83% |
| Moderate Help (20-50%) | 1 | 8.00% | 10,000 | 65% |

**Hint Timing Effect:**
- Early Adopters (hint before 7 quests): Avg 25.6% progress
- Late Adopters (hint after 7 quests): Avg 42.8% progress

### 2. Behavior Sequences Analysis

**Sequences Leading to PERFECT Completion:**
1. `Add New Quest → Execute Git Command → Execute Git Command` (757 times)
2. `Complete Quest → Add New Quest → Execute Git Command` (746 times)
3. `Execute Git Command → Execute Git Command → Execute Git Command` (513 times)

**Sequences Leading to FAILED Actions:**
1. `Failed Action → Failed Action → Failed Action` (172 times) - cascade failure
2. `Complete Quest → Add New Quest → Failed Action` (113 times)
3. `Add New Quest → Failed Action → Failed Action` (44 times)

### 3. Learning Trajectories

| Trajectory | % of Players | Interpretation |
|------------|--------------|----------------|
| Stable | 81.8% | Consistent performance throughout |
| Declining | 9.1% | Performance worsened over time |
| Improving | 9.1% | Performance improved over time |

### 4. Dropout vs Active Player Comparison

| Metric | Dropout (<20%) | Active (≥50%) | Ratio |
|--------|----------------|---------------|-------|
| Avg Events | 70 | 672 | 9.6x |
| Avg Manual Opens | 0.9 | 11.1 | 12.4x |
| Avg Leaderboard Checks | 1.9 | 21.5 | 11.4x |
| Failure Rate | 9.76% | 1.03% | 9.5x higher |

### 5. Stage Difficulty Progression

| Stage Type | Clear Rate | Avg Score |
|------------|------------|-----------|
| Basic | 49.3% | 6,365 |
| Branch | 34.2% | 7,413 |
| Remote | 27.0% | 6,283 |

### 6. Quest Completion Distribution

| Rating | Count | Percentage |
|--------|-------|------------|
| Perfect | 4,330 | 93.1% |
| Good | 202 | 4.3% |
| Answer | 94 | 2.0% |
| Hint | 25 | 0.5% |

---

## Citation

When using this data in research:

> "Player behavior data was extracted from the GiTaiment educational game database, 
> comprising event logs (N=22,120 actions), player save data (N=51 players), 
> and global leaderboard rankings. Data was aggregated per-user to create 
> 55 behavioral and performance metrics."
