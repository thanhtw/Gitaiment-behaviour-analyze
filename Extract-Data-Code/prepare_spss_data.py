"""
GiTaiment SPSS Data Preparation Script
======================================
This script creates a comprehensive CSV file optimized for SPSS analysis.
All variables are properly coded and labeled for statistical analysis.

Output: analysis_spss_ready.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_data(data_dir):
    """Load all data sources"""
    print("=" * 80)
    print("LOADING DATA FOR SPSS PREPARATION")
    print("=" * 80)
    
    events = pd.read_csv(f"{data_dir}/extracted_events.csv")
    events['eventTime'] = pd.to_datetime(events['eventTime'], format='mixed')
    
    game_records = pd.read_csv(f"{data_dir}/extracted_player_game_records.csv")
    stage_data = pd.read_csv(f"{data_dir}/extracted_player_stage_data.csv")
    per_user = pd.read_csv(f"{data_dir}/analysis_per_user_combined.csv")
    
    print(f"Loaded: {len(events)} events, {len(game_records)} players")
    
    return events, game_records, stage_data, per_user

def calculate_spss_variables(events, game_records, stage_data, per_user):
    """
    Calculate all variables needed for SPSS analysis.
    Returns a DataFrame with one row per user and all computed variables.
    """
    print("\n" + "=" * 80)
    print("CALCULATING SPSS VARIABLES")
    print("=" * 80)
    
    # Start with per-user data
    df = per_user.copy()
    
    # Rename columns for SPSS (no special characters, shorter names)
    df = df.rename(columns={
        'username': 'ID',
        'event_total_events': 'TotalEvents',
        'event_total_logins': 'TotalLogins',
        'event_total_sessions': 'TotalSessions',
        'event_stages_started': 'StagesStarted',
        'event_quests_added': 'QuestsAdded',
        'event_quests_completed': 'QuestsCompleted',
        'event_perfect_quests': 'PerfectQuests',
        'event_good_quests': 'GoodQuests',
        'event_hint_used_quests': 'HintQuests',
        'event_answer_used_quests': 'AnswerQuests',
        'event_correct_actions': 'CorrectActions',
        'event_failed_actions': 'FailedActions',
        'event_game_manual_opens': 'ManualOpens',
        'event_leaderboard_checks': 'LeaderboardChecks',
        'event_window_opens': 'WindowOpens',
        'event_last_conversations': 'Conversations',
        'event_activity_span_days': 'ActivityDays',
        'event_unique_stages_attempted': 'UniqueStages',
        'record_totalStarCount': 'TotalStars',
        'record_totalStageScore': 'TotalScore',
        'record_totalGameProgress': 'GameProgress',
        'record_totalPlayTime': 'PlayTimeSeconds',
        'record_totalTimesStageClear': 'StageClears',
        'record_totalTimesUsedGameManual': 'ManualUsed',
        'record_totalCommandExecuteTimes': 'CommandsExecuted',
        'record_totalTimesQuestClearPerfect': 'RecordPerfect',
        'record_totalTimesQuestClearGood': 'RecordGood',
        'record_totalTimesQuestClearHint': 'RecordHint',
        'record_totalTimesQuestClearAnswer': 'RecordAnswer',
        'stage_total_stages': 'TotalStagesGame',
        'stage_stages_unlocked': 'StagesUnlocked',
        'stage_stages_cleared': 'StagesCleared',
        'stage_total_clear_times': 'TotalClearTimes',
        'stage_avg_best_score': 'AvgBestScore',
        'stage_avg_clear_time': 'AvgClearTime',
        'stage_basic_stages_unlocked': 'BasicUnlocked',
        'stage_branch_stages_unlocked': 'BranchUnlocked',
        'stage_remote_stages_unlocked': 'RemoteUnlocked',
        'stage_tutorial_stages_cleared': 'TutorialCleared',
        'stage_practice_stages_cleared': 'PracticeCleared',
        'rank_progress_rank': 'ProgressRank',
        'rank_progress_percentile': 'ProgressPercentile',
        'rank_score_rank': 'ScoreRank',
        'rank_score_percentile': 'ScorePercentile'
    })
    
    # Fill NaN with 0 for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # =========================================================================
    # CALCULATED VARIABLES FOR SPSS ANALYSIS
    # =========================================================================
    
    print("\nCalculating derived variables...")
    
    # 1. HELP-SEEKING VARIABLES
    df['HelpQuests'] = df['HintQuests'] + df['AnswerQuests']
    df['HelpRatio'] = df['HelpQuests'] / df['QuestsCompleted'].replace(0, 1)
    df['HintRatio'] = df['HintQuests'] / df['QuestsCompleted'].replace(0, 1)
    df['AnswerRatio'] = df['AnswerQuests'] / df['QuestsCompleted'].replace(0, 1)
    df['PerfectRatio'] = df['PerfectQuests'] / df['QuestsCompleted'].replace(0, 1)
    df['GoodRatio'] = df['GoodQuests'] / df['QuestsCompleted'].replace(0, 1)
    
    # 2. HELP-SEEKING CATEGORY (1=Independent, 2=LowHelp, 3=ModerateHelp, 4=HighHelp)
    def categorize_help(ratio):
        if ratio <= 0.05:
            return 1  # Independent
        elif ratio <= 0.20:
            return 2  # Low Help
        elif ratio <= 0.50:
            return 3  # Moderate Help
        else:
            return 4  # High Help
    
    df['HelpCategory'] = df['HelpRatio'].apply(categorize_help)
    
    # 3. ACTION SUCCESS VARIABLES
    df['TotalActions'] = df['CorrectActions'] + df['FailedActions']
    df['ActionSuccessRate'] = df['CorrectActions'] / df['TotalActions'].replace(0, 1)
    df['FailureRate'] = df['FailedActions'] / df['TotalEvents'].replace(0, 1)
    
    # 4. ENGAGEMENT VARIABLES
    df['EventsPerSession'] = df['TotalEvents'] / df['TotalSessions'].replace(0, 1)
    df['QuestsPerSession'] = df['QuestsCompleted'] / df['TotalSessions'].replace(0, 1)
    df['PlayTimeMinutes'] = df['PlayTimeSeconds'] / 60
    df['PlayTimeHours'] = df['PlayTimeSeconds'] / 3600
    
    # 5. PROGRESS VARIABLES
    df['CompletionRate'] = df['StagesCleared'] / df['TotalStagesGame'].replace(0, 1)
    df['UnlockRate'] = df['StagesUnlocked'] / df['TotalStagesGame'].replace(0, 1)
    df['QuestCompletionRate'] = df['QuestsCompleted'] / df['QuestsAdded'].replace(0, 1)
    
    # 6. STAGE TYPE PROGRESS
    df['BasicClearRate'] = df['BasicUnlocked'] / 14  # 14 basic stages
    df['BranchClearRate'] = df['BranchUnlocked'] / 8  # 8 branch stages
    df['RemoteClearRate'] = df['RemoteUnlocked'] / 12  # 12 remote stages
    
    # 7. DROPOUT CATEGORY (1=Dropout, 2=LowProgress, 3=MediumProgress, 4=HighProgress, 5=Complete)
    def categorize_progress(progress):
        if progress < 10:
            return 1  # Dropout
        elif progress < 25:
            return 2  # Low Progress
        elif progress < 50:
            return 3  # Medium Progress
        elif progress < 100:
            return 4  # High Progress
        else:
            return 5  # Complete
    
    df['ProgressCategory'] = df['GameProgress'].apply(categorize_progress)
    
    # 8. BINARY DROPOUT (0=Active, 1=Dropout)
    df['IsDropout'] = (df['GameProgress'] < 20).astype(int)
    
    # 9. LEARNING TRAJECTORY (calculate from events)
    print("Calculating learning trajectories...")
    trajectories = {}
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        quest_completions = user_events[user_events['eventName'] == 'Complete Quest']
        
        if len(quest_completions) >= 5:
            performance = []
            for _, row in quest_completions.iterrows():
                detail = str(row['eventDetail'])
                score = 4 if 'Perfect' in detail else 3 if 'Good' in detail else 2 if 'Hint' in detail else 1
                performance.append(score)
            
            n = len(performance)
            early = np.mean(performance[:n//3]) if n >= 3 else np.mean(performance)
            late = np.mean(performance[-n//3:]) if n >= 3 else np.mean(performance)
            improvement = late - early
            
            trajectories[username] = {
                'EarlyScore': early,
                'LateScore': late,
                'ScoreImprovement': improvement,
                'TrajectoryType': 1 if improvement > 0.3 else 3 if improvement < -0.3 else 2  # 1=Improving, 2=Stable, 3=Declining
            }
    
    # Merge trajectory data
    traj_df = pd.DataFrame(trajectories).T.reset_index()
    traj_df.columns = ['ID', 'EarlyScore', 'LateScore', 'ScoreImprovement', 'TrajectoryType']
    df = df.merge(traj_df, on='ID', how='left')
    
    # Fill trajectory NaN
    df['EarlyScore'] = df['EarlyScore'].fillna(0)
    df['LateScore'] = df['LateScore'].fillna(0)
    df['ScoreImprovement'] = df['ScoreImprovement'].fillna(0)
    df['TrajectoryType'] = df['TrajectoryType'].fillna(2)  # Default to Stable
    
    # 10. HINT TIMING (quests before first hint)
    print("Calculating hint timing...")
    hint_timing = {}
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        hint_events = user_events[user_events['eventDetail'].str.contains('Hint|Answer', na=False)]
        quest_events = user_events[user_events['eventName'] == 'Complete Quest']
        
        if len(hint_events) > 0 and len(quest_events) > 0:
            quests_before = len(quest_events[quest_events['eventTime'] < hint_events['eventTime'].iloc[0]])
            hint_timing[username] = quests_before
        else:
            hint_timing[username] = -1  # Never used hint
    
    df['QuestsBeforeFirstHint'] = df['ID'].map(hint_timing).fillna(-1)
    
    # Hint timing category (1=Early, 2=Late, 0=Never)
    median_hint = df[df['QuestsBeforeFirstHint'] > 0]['QuestsBeforeFirstHint'].median()
    def categorize_hint_timing(quests):
        if quests < 0:
            return 0  # Never used
        elif quests < median_hint:
            return 1  # Early
        else:
            return 2  # Late
    
    df['HintTimingCategory'] = df['QuestsBeforeFirstHint'].apply(categorize_hint_timing)
    
    # 11. CASCADE FAILURE COUNT
    print("Calculating cascade failures...")
    cascade_failures = {}
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        event_names = user_events['eventName'].tolist()
        
        cascade_count = 0
        for i in range(len(event_names) - 2):
            if event_names[i] == 'Failed Action' and event_names[i+1] == 'Failed Action' and event_names[i+2] == 'Failed Action':
                cascade_count += 1
        
        cascade_failures[username] = cascade_count
    
    df['CascadeFailures'] = df['ID'].map(cascade_failures).fillna(0)
    
    # 12. STANDARDIZED SCORES (Z-scores for key variables)
    for col in ['GameProgress', 'TotalScore', 'QuestsCompleted', 'PlayTimeMinutes', 'HelpRatio']:
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val > 0:
            df[f'{col}_Z'] = (df[col] - mean_val) / std_val
        else:
            df[f'{col}_Z'] = 0
    
    return df

def export_for_spss(df, output_dir):
    """Export data in SPSS-ready format"""
    print("\n" + "=" * 80)
    print("EXPORTING SPSS-READY DATA")
    print("=" * 80)
    
    # Select and order columns for SPSS
    spss_columns = [
        # Identifiers
        'ID',
        
        # Demographic/Engagement (Independent Variables)
        'TotalEvents', 'TotalLogins', 'TotalSessions', 'ActivityDays',
        'PlayTimeSeconds', 'PlayTimeMinutes', 'PlayTimeHours',
        'EventsPerSession', 'QuestsPerSession',
        
        # Help-Seeking Variables (Independent Variables)
        'HelpQuests', 'HintQuests', 'AnswerQuests',
        'HelpRatio', 'HintRatio', 'AnswerRatio',
        'HelpCategory',  # Categorical: 1=Independent, 2=LowHelp, 3=ModerateHelp, 4=HighHelp
        'QuestsBeforeFirstHint', 'HintTimingCategory',  # 0=Never, 1=Early, 2=Late
        
        # Action Variables (Process Variables)
        'CorrectActions', 'FailedActions', 'TotalActions',
        'ActionSuccessRate', 'FailureRate',
        'CascadeFailures',
        
        # Quest Variables
        'QuestsAdded', 'QuestsCompleted', 'QuestCompletionRate',
        'PerfectQuests', 'GoodQuests',
        'PerfectRatio', 'GoodRatio',
        
        # Resource Usage
        'ManualOpens', 'ManualUsed', 'LeaderboardChecks',
        'CommandsExecuted', 'Conversations', 'WindowOpens',
        
        # Stage Progress Variables
        'StagesStarted', 'UniqueStages',
        'StagesUnlocked', 'StagesCleared',
        'UnlockRate', 'CompletionRate',
        'BasicUnlocked', 'BranchUnlocked', 'RemoteUnlocked',
        'BasicClearRate', 'BranchClearRate', 'RemoteClearRate',
        'TutorialCleared', 'PracticeCleared',
        'TotalClearTimes', 'AvgBestScore', 'AvgClearTime',
        
        # Performance Outcomes (Dependent Variables)
        'GameProgress', 'TotalScore', 'TotalStars',
        'ProgressCategory',  # 1=Dropout to 5=Complete
        'IsDropout',  # 0=Active, 1=Dropout
        
        # Learning Trajectory
        'EarlyScore', 'LateScore', 'ScoreImprovement',
        'TrajectoryType',  # 1=Improving, 2=Stable, 3=Declining
        
        # Ranking
        'ProgressRank', 'ProgressPercentile',
        'ScoreRank', 'ScorePercentile',
        
        # Standardized Scores
        'GameProgress_Z', 'TotalScore_Z', 'QuestsCompleted_Z',
        'PlayTimeMinutes_Z', 'HelpRatio_Z'
    ]
    
    # Filter to existing columns
    existing_cols = [col for col in spss_columns if col in df.columns]
    spss_df = df[existing_cols].copy()
    
    # Export to CSV
    output_path = f"{output_dir}/analysis_spss_ready.csv"
    spss_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nExported: {output_path}")
    print(f"Variables: {len(existing_cols)}")
    print(f"Cases: {len(spss_df)}")
    
    return spss_df

def create_spss_codebook(df, output_dir):
    """Create a codebook explaining all variables"""
    
    codebook = """# SPSS Variable Codebook
# ======================
# File: analysis_spss_ready.csv

## Variable Definitions

### IDENTIFICATION
| Variable | Type | Description |
|----------|------|-------------|
| ID | String | Unique player identifier |

### ENGAGEMENT VARIABLES (Independent)
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| TotalEvents | Scale | 0-∞ | Total number of logged events |
| TotalLogins | Scale | 0-∞ | Number of login events |
| TotalSessions | Scale | 0-∞ | Number of play sessions (>30min gap) |
| ActivityDays | Scale | 0-∞ | Days between first and last activity |
| PlayTimeSeconds | Scale | 0-∞ | Total play time in seconds |
| PlayTimeMinutes | Scale | 0-∞ | Total play time in minutes |
| PlayTimeHours | Scale | 0-∞ | Total play time in hours |
| EventsPerSession | Scale | 0-∞ | Average events per session |
| QuestsPerSession | Scale | 0-∞ | Average quests completed per session |

### HELP-SEEKING VARIABLES (Independent/Mediator)
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| HelpQuests | Scale | 0-∞ | Quests completed using hint or answer |
| HintQuests | Scale | 0-∞ | Quests completed using hint |
| AnswerQuests | Scale | 0-∞ | Quests completed using answer |
| HelpRatio | Scale | 0-1 | Proportion of quests using help |
| HintRatio | Scale | 0-1 | Proportion of quests using hints |
| AnswerRatio | Scale | 0-1 | Proportion of quests using answers |
| HelpCategory | Ordinal | 1-4 | 1=Independent, 2=LowHelp, 3=ModerateHelp, 4=HighHelp |
| QuestsBeforeFirstHint | Scale | -1 to ∞ | Quests completed before first hint (-1=never used) |
| HintTimingCategory | Nominal | 0-2 | 0=Never used, 1=Early adopter, 2=Late adopter |

### ACTION VARIABLES (Process/Mediator)
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| CorrectActions | Scale | 0-∞ | Number of correct game actions |
| FailedActions | Scale | 0-∞ | Number of failed game actions |
| TotalActions | Scale | 0-∞ | Total actions (correct + failed) |
| ActionSuccessRate | Scale | 0-1 | Proportion of correct actions |
| FailureRate | Scale | 0-1 | Failed actions / Total events |
| CascadeFailures | Scale | 0-∞ | Count of 3+ consecutive failures |

### QUEST VARIABLES
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| QuestsAdded | Scale | 0-∞ | Total quests started |
| QuestsCompleted | Scale | 0-∞ | Total quests completed |
| QuestCompletionRate | Scale | 0-1 | Completed / Added quests |
| PerfectQuests | Scale | 0-∞ | Quests with Perfect rating |
| GoodQuests | Scale | 0-∞ | Quests with Good rating |
| PerfectRatio | Scale | 0-1 | Proportion of Perfect completions |
| GoodRatio | Scale | 0-1 | Proportion of Good completions |

### RESOURCE USAGE VARIABLES
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| ManualOpens | Scale | 0-∞ | Times game manual was opened (event) |
| ManualUsed | Scale | 0-∞ | Times game manual was used (record) |
| LeaderboardChecks | Scale | 0-∞ | Times leaderboard was checked |
| CommandsExecuted | Scale | 0-∞ | Git commands executed |
| Conversations | Scale | 0-∞ | In-game conversation events |
| WindowOpens | Scale | 0-∞ | Window open events |

### STAGE PROGRESS VARIABLES
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| StagesStarted | Scale | 0-∞ | Times stages were started |
| UniqueStages | Scale | 0-34 | Unique stages attempted |
| StagesUnlocked | Scale | 0-34 | Stages unlocked |
| StagesCleared | Scale | 0-34 | Stages completed at least once |
| UnlockRate | Scale | 0-1 | Proportion of stages unlocked |
| CompletionRate | Scale | 0-1 | Proportion of stages cleared |
| BasicUnlocked | Scale | 0-14 | Basic stages unlocked |
| BranchUnlocked | Scale | 0-8 | Branch stages unlocked |
| RemoteUnlocked | Scale | 0-12 | Remote stages unlocked |
| BasicClearRate | Scale | 0-1 | Basic stages unlock rate |
| BranchClearRate | Scale | 0-1 | Branch stages unlock rate |
| RemoteClearRate | Scale | 0-1 | Remote stages unlock rate |
| TutorialCleared | Scale | 0-17 | Tutorial stages cleared |
| PracticeCleared | Scale | 0-17 | Practice stages cleared |
| TotalClearTimes | Scale | 0-∞ | Total stage clear count (including replays) |
| AvgBestScore | Scale | 0-∞ | Average best score per stage |
| AvgClearTime | Scale | 0-∞ | Average clear time in seconds |

### PERFORMANCE OUTCOMES (Dependent Variables)
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| GameProgress | Scale | 0-100 | Overall game progress percentage |
| TotalScore | Scale | 0-∞ | Cumulative game score |
| TotalStars | Scale | 0-∞ | Total stars earned |
| ProgressCategory | Ordinal | 1-5 | 1=Dropout, 2=Low, 3=Medium, 4=High, 5=Complete |
| IsDropout | Nominal | 0-1 | 0=Active (≥20%), 1=Dropout (<20%) |

### LEARNING TRAJECTORY VARIABLES
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| EarlyScore | Scale | 1-4 | Avg score in first third of quests |
| LateScore | Scale | 1-4 | Avg score in last third of quests |
| ScoreImprovement | Scale | -3 to 3 | LateScore - EarlyScore |
| TrajectoryType | Nominal | 1-3 | 1=Improving, 2=Stable, 3=Declining |

### RANKING VARIABLES
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| ProgressRank | Ordinal | 1-∞ | Rank by game progress (1=best) |
| ProgressPercentile | Scale | 0-100 | Percentile by progress |
| ScoreRank | Ordinal | 1-∞ | Rank by total score (1=best) |
| ScorePercentile | Scale | 0-100 | Percentile by score |

### STANDARDIZED SCORES (Z-Scores)
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| GameProgress_Z | Scale | -∞ to ∞ | Standardized game progress |
| TotalScore_Z | Scale | -∞ to ∞ | Standardized total score |
| QuestsCompleted_Z | Scale | -∞ to ∞ | Standardized quests completed |
| PlayTimeMinutes_Z | Scale | -∞ to ∞ | Standardized play time |
| HelpRatio_Z | Scale | -∞ to ∞ | Standardized help ratio |

---

## Categorical Variable Codes

### HelpCategory
| Code | Label | Definition |
|------|-------|------------|
| 1 | Independent | 0-5% help usage |
| 2 | Low Help | 5-20% help usage |
| 3 | Moderate Help | 20-50% help usage |
| 4 | High Help | >50% help usage |

### HintTimingCategory
| Code | Label | Definition |
|------|-------|------------|
| 0 | Never Used | Never used hint/answer |
| 1 | Early Adopter | First hint before median quest count |
| 2 | Late Adopter | First hint after median quest count |

### ProgressCategory
| Code | Label | Definition |
|------|-------|------------|
| 1 | Dropout | <10% progress |
| 2 | Low Progress | 10-25% progress |
| 3 | Medium Progress | 25-50% progress |
| 4 | High Progress | 50-100% progress |
| 5 | Complete | 100% progress |

### TrajectoryType
| Code | Label | Definition |
|------|-------|------------|
| 1 | Improving | Score improvement > 0.3 |
| 2 | Stable | Score change between -0.3 and 0.3 |
| 3 | Declining | Score improvement < -0.3 |

### IsDropout
| Code | Label | Definition |
|------|-------|------------|
| 0 | Active | GameProgress ≥ 20% |
| 1 | Dropout | GameProgress < 20% |

---

## Missing Value Codes
- -1 for QuestsBeforeFirstHint means player never used hints
- 0 for trajectory variables means insufficient data (< 5 quests)
"""
    
    with open(f"{output_dir}/SPSS_CODEBOOK.md", 'w', encoding='utf-8') as f:
        f.write(codebook)
    
    print(f"Exported: SPSS_CODEBOOK.md")

def main():
    data_dir = "."
    
    # Load data
    events, game_records, stage_data, per_user = load_data(data_dir)
    
    # Calculate SPSS variables
    df = calculate_spss_variables(events, game_records, stage_data, per_user)
    
    # Export for SPSS
    spss_df = export_for_spss(df, data_dir)
    
    # Create codebook
    create_spss_codebook(spss_df, data_dir)
    
    print("\n" + "=" * 80)
    print("SPSS DATA PREPARATION COMPLETE")
    print("=" * 80)
    print("\nFiles created:")
    print("  1. analysis_spss_ready.csv - Main data file for SPSS")
    print("  2. SPSS_CODEBOOK.md - Variable definitions and codes")
    print("\nNext steps:")
    print("  1. Open SPSS")
    print("  2. File > Open > Data > Select analysis_spss_ready.csv")
    print("  3. Define variable properties using the codebook")
    print("  4. Run analyses as described in SPSS_ANALYSIS_GUIDE.md")

if __name__ == "__main__":
    main()
