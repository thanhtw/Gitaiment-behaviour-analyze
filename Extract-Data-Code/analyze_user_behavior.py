"""
GiTaiment Game Analytics - User Behavior Data Mining
=====================================================
This script combines and analyzes player data from multiple sources to understand
user behavior patterns during game progression in a Git learning game.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DATA LOADING
# =============================================================================

def load_all_data(data_dir):
    """Load all extracted CSV files"""
    print("=" * 80)
    print("LOADING DATA FILES")
    print("=" * 80)
    
    # Load player game records
    game_records = pd.read_csv(f"{data_dir}/extracted_player_game_records.csv")
    print(f"Player Game Records: {len(game_records)} players")
    
    # Load player stage data
    stage_data = pd.read_csv(f"{data_dir}/extracted_player_stage_data.csv")
    print(f"Player Stage Data: {len(stage_data)} records")
    
    # Load global leaderboards
    leaderboards = pd.read_csv(f"{data_dir}/extracted_leaderboards.csv")
    print(f"Global Leaderboards: {len(leaderboards)} entries")
    
    # Load stage leaderboards
    stage_leaderboards = pd.read_csv(f"{data_dir}/extracted_stage_leaderboards.csv")
    print(f"Stage Leaderboards: {len(stage_leaderboards)} entries")
    
    return game_records, stage_data, leaderboards, stage_leaderboards

# =============================================================================
# DATA PREPROCESSING
# =============================================================================

def preprocess_data(game_records, stage_data, leaderboards, stage_leaderboards):
    """Clean and preprocess all data"""
    print("\n" + "=" * 80)
    print("PREPROCESSING DATA")
    print("=" * 80)
    
    # Remove players with no activity
    active_players = game_records[game_records['totalPlayTime'] > 0].copy()
    print(f"Active players (with play time > 0): {len(active_players)}")
    
    # Calculate derived metrics for game records
    active_players['avgScorePerStage'] = active_players['totalStageScore'] / active_players['totalTimesStageClear'].replace(0, 1)
    active_players['avgTimePerStage'] = active_players['totalPlayTime'] / active_players['totalTimesStageClear'].replace(0, 1)
    active_players['playTimeHours'] = active_players['totalPlayTime'] / 3600
    
    # Quest completion metrics
    active_players['totalQuestClears'] = (
        active_players['totalTimesQuestClearPerfect'] + 
        active_players['totalTimesQuestClearGood'] + 
        active_players['totalTimesQuestClearHint'] + 
        active_players['totalTimesQuestClearAnswer']
    )
    
    active_players['perfectClearRate'] = (
        active_players['totalTimesQuestClearPerfect'] / 
        active_players['totalQuestClears'].replace(0, 1) * 100
    )
    
    active_players['hintUsageRate'] = (
        (active_players['totalTimesQuestClearHint'] + active_players['totalTimesQuestClearAnswer']) / 
        active_players['totalQuestClears'].replace(0, 1) * 100
    )
    
    # Efficiency score (progress per hour played)
    active_players['efficiencyScore'] = (
        active_players['totalGameProgress'] / 
        active_players['playTimeHours'].replace(0, 1)
    )
    
    return active_players, stage_data, leaderboards, stage_leaderboards

# =============================================================================
# PLAYER SEGMENTATION
# =============================================================================

def segment_players(game_records):
    """Segment players based on behavior patterns"""
    print("\n" + "=" * 80)
    print("PLAYER SEGMENTATION ANALYSIS")
    print("=" * 80)
    
    df = game_records.copy()
    
    # Define player segments based on progress
    def get_progress_segment(progress):
        if progress >= 80:
            return 'Completionist'
        elif progress >= 50:
            return 'Advanced'
        elif progress >= 25:
            return 'Intermediate'
        elif progress > 0:
            return 'Beginner'
        else:
            return 'Inactive'
    
    df['progressSegment'] = df['totalGameProgress'].apply(get_progress_segment)
    
    # Define learning style based on hint usage
    def get_learning_style(row):
        if row['totalQuestClears'] == 0:
            return 'Unknown'
        hint_rate = row['hintUsageRate']
        perfect_rate = row['perfectClearRate']
        
        if perfect_rate >= 80:
            return 'Master'
        elif hint_rate <= 5:
            return 'Independent'
        elif hint_rate <= 20:
            return 'Balanced'
        else:
            return 'Hint-Dependent'
    
    df['learningStyle'] = df.apply(get_learning_style, axis=1)
    
    # Define engagement level based on play time and activity
    def get_engagement_level(row):
        if row['playTimeHours'] >= 2:
            return 'High'
        elif row['playTimeHours'] >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    df['engagementLevel'] = df.apply(get_engagement_level, axis=1)
    
    # Print segment distributions
    print("\n--- Progress Segment Distribution ---")
    print(df['progressSegment'].value_counts())
    
    print("\n--- Learning Style Distribution ---")
    print(df['learningStyle'].value_counts())
    
    print("\n--- Engagement Level Distribution ---")
    print(df['engagementLevel'].value_counts())
    
    return df

# =============================================================================
# STAGE PROGRESSION ANALYSIS
# =============================================================================

def analyze_stage_progression(stage_data, game_records):
    """Analyze how players progress through stages"""
    print("\n" + "=" * 80)
    print("STAGE PROGRESSION ANALYSIS")
    print("=" * 80)
    
    # Get active usernames
    active_usernames = game_records['username'].tolist()
    active_stage_data = stage_data[stage_data['username'].isin(active_usernames)].copy()
    
    # Stage unlock rates
    stage_unlock_rates = active_stage_data.groupby('stageName').agg({
        'isStageUnlock': ['sum', 'count'],
        'stageClearTimes': 'sum',
        'bestPlayerScore': 'mean'
    }).reset_index()
    
    stage_unlock_rates.columns = ['stageName', 'timesUnlocked', 'totalPlayers', 'totalClears', 'avgBestScore']
    stage_unlock_rates['unlockRate'] = (stage_unlock_rates['timesUnlocked'] / stage_unlock_rates['totalPlayers'] * 100).round(2)
    stage_unlock_rates['clearRate'] = (stage_unlock_rates['totalClears'] / stage_unlock_rates['timesUnlocked'].replace(0, 1)).round(2)
    
    # Define stage order for proper sorting
    stage_order = [
        'Game Introduction (Tutorial)', 'Version Control and Git (Tutorial)',
        'Create Local Repository (Tutorial)', 'Basic Staging Area (Tutorial)',
        'Advanced Staging Area (Tutorial)', 'Creating First Version (Tutorial)',
        'Switching Project Versions (Tutorial)', 'Git Branching Basics (Tutorial)',
        'Fast-Forward Merging (Tutorial)', 'Auto Merging (Tutorial)',
        'Merge Conflicts (Tutorial)', 'Create Remote Repository (Tutorial)',
        'Push to Remote Branches (Tutorial)', 'Keep Branches in Sync (Tutorial)',
        'Preparation for Merging (Tutorial)', 'Creating a Pull Request (Tutorial)',
        'Review and Merge Pull Requests (Tutorial)'
    ]
    
    # Filter and sort tutorial stages
    tutorial_stages = stage_unlock_rates[stage_unlock_rates['stageName'].str.contains('Tutorial')]
    tutorial_stages['stageOrder'] = tutorial_stages['stageName'].apply(
        lambda x: stage_order.index(x) if x in stage_order else 999
    )
    tutorial_stages = tutorial_stages.sort_values('stageOrder')
    
    print("\n--- Tutorial Stage Progression (Ordered) ---")
    print(tutorial_stages[['stageName', 'unlockRate', 'clearRate', 'avgBestScore']].to_string(index=False))
    
    # Calculate dropout points (where unlock rate drops significantly)
    print("\n--- Dropout Analysis ---")
    prev_rate = 100
    for _, row in tutorial_stages.iterrows():
        drop = prev_rate - row['unlockRate']
        if drop > 10:
            print(f"  Significant drop at '{row['stageName']}': {drop:.1f}% decrease")
        prev_rate = row['unlockRate']
    
    return stage_unlock_rates, tutorial_stages

# =============================================================================
# PERFORMANCE ANALYSIS
# =============================================================================

def analyze_performance(game_records, stage_data):
    """Analyze player performance patterns"""
    print("\n" + "=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    df = game_records.copy()
    
    # Performance metrics
    print("\n--- Overall Performance Statistics ---")
    metrics = ['totalStageScore', 'totalGameProgress', 'totalPlayTime', 
               'perfectClearRate', 'efficiencyScore', 'totalCommandExecuteTimes']
    
    for metric in metrics:
        if metric in df.columns:
            print(f"\n{metric}:")
            print(f"  Mean: {df[metric].mean():.2f}")
            print(f"  Median: {df[metric].median():.2f}")
            print(f"  Std Dev: {df[metric].std():.2f}")
            print(f"  Min: {df[metric].min():.2f}")
            print(f"  Max: {df[metric].max():.2f}")
    
    # Correlation analysis
    print("\n--- Correlation Analysis ---")
    correlation_cols = ['totalStageScore', 'totalGameProgress', 'totalPlayTime',
                        'totalTimesStageClear', 'totalCommandExecuteTimes',
                        'perfectClearRate', 'hintUsageRate']
    
    correlation_cols = [c for c in correlation_cols if c in df.columns]
    correlation_matrix = df[correlation_cols].corr()
    
    print("\nKey Correlations:")
    print(f"  Score vs Progress: {correlation_matrix.loc['totalStageScore', 'totalGameProgress']:.3f}")
    print(f"  Score vs PlayTime: {correlation_matrix.loc['totalStageScore', 'totalPlayTime']:.3f}")
    print(f"  Progress vs Commands: {correlation_matrix.loc['totalGameProgress', 'totalCommandExecuteTimes']:.3f}")
    print(f"  Perfect Rate vs Progress: {correlation_matrix.loc['perfectClearRate', 'totalGameProgress']:.3f}")
    
    # Top performers
    print("\n--- Top 10 Performers by Score ---")
    top_by_score = df.nlargest(10, 'totalStageScore')[
        ['username', 'totalStageScore', 'totalGameProgress', 'perfectClearRate', 'playTimeHours']
    ]
    print(top_by_score.to_string(index=False))
    
    # Most efficient players
    print("\n--- Top 10 Most Efficient Players (Progress per Hour) ---")
    top_efficient = df.nlargest(10, 'efficiencyScore')[
        ['username', 'efficiencyScore', 'totalGameProgress', 'playTimeHours']
    ]
    print(top_efficient.to_string(index=False))
    
    return correlation_matrix

# =============================================================================
# LEARNING BEHAVIOR ANALYSIS
# =============================================================================

def analyze_learning_behavior(game_records):
    """Analyze how players learn and use help features"""
    print("\n" + "=" * 80)
    print("LEARNING BEHAVIOR ANALYSIS")
    print("=" * 80)
    
    df = game_records.copy()
    
    # Quest completion breakdown
    print("\n--- Quest Completion Methods ---")
    total_perfect = df['totalTimesQuestClearPerfect'].sum()
    total_good = df['totalTimesQuestClearGood'].sum()
    total_hint = df['totalTimesQuestClearHint'].sum()
    total_answer = df['totalTimesQuestClearAnswer'].sum()
    total_all = total_perfect + total_good + total_hint + total_answer
    
    print(f"  Perfect Clears: {total_perfect} ({total_perfect/total_all*100:.1f}%)")
    print(f"  Good Clears: {total_good} ({total_good/total_all*100:.1f}%)")
    print(f"  With Hints: {total_hint} ({total_hint/total_all*100:.1f}%)")
    print(f"  With Answers: {total_answer} ({total_answer/total_all*100:.1f}%)")
    
    # Game manual usage
    print("\n--- Game Manual Usage Statistics ---")
    manual_users = df[df['totalTimesUsedGameManual'] > 0]
    print(f"  Players who used manual: {len(manual_users)} ({len(manual_users)/len(df)*100:.1f}%)")
    print(f"  Average uses per player: {df['totalTimesUsedGameManual'].mean():.1f}")
    print(f"  Max uses: {df['totalTimesUsedGameManual'].max()}")
    
    # Command execution analysis
    print("\n--- Command Execution Analysis ---")
    cmd_users = df[df['totalCommandExecuteTimes'] > 0]
    print(f"  Players who executed commands: {len(cmd_users)} ({len(cmd_users)/len(df)*100:.1f}%)")
    print(f"  Average commands per player: {df['totalCommandExecuteTimes'].mean():.1f}")
    print(f"  Commands per stage clear: {(df['totalCommandExecuteTimes'].sum() / df['totalTimesStageClear'].sum()):.1f}")
    
    # Learning style impact on progress
    print("\n--- Learning Style Impact on Progress ---")
    style_progress = df.groupby('learningStyle').agg({
        'totalGameProgress': 'mean',
        'totalStageScore': 'mean',
        'playTimeHours': 'mean',
        'username': 'count'
    }).round(2)
    style_progress.columns = ['avgProgress', 'avgScore', 'avgPlayTimeHours', 'playerCount']
    print(style_progress.to_string())
    
    return df

# =============================================================================
# TIME-BASED ANALYSIS
# =============================================================================

def analyze_time_patterns(game_records, stage_data):
    """Analyze time-related patterns"""
    print("\n" + "=" * 80)
    print("TIME-BASED ANALYSIS")
    print("=" * 80)
    
    df = game_records.copy()
    
    # Play time distribution
    print("\n--- Play Time Distribution ---")
    time_bins = [0, 0.5, 1, 1.5, 2, 3, 5, float('inf')]
    time_labels = ['0-30min', '30-60min', '1-1.5hr', '1.5-2hr', '2-3hr', '3-5hr', '5hr+']
    df['playTimeBin'] = pd.cut(df['playTimeHours'], bins=time_bins, labels=time_labels)
    
    time_dist = df['playTimeBin'].value_counts().sort_index()
    for bin_name, count in time_dist.items():
        print(f"  {bin_name}: {count} players ({count/len(df)*100:.1f}%)")
    
    # Average time per stage type
    print("\n--- Average Clear Time by Stage Type ---")
    active_usernames = df['username'].tolist()
    active_stages = stage_data[
        (stage_data['username'].isin(active_usernames)) & 
        (stage_data['stageClearTimes'] > 0)
    ].copy()
    
    stage_type_times = active_stages.groupby('stageType').agg({
        'bestPlayerClearTime': 'mean',
        'bestPlayerScore': 'mean',
        'stageClearTimes': 'sum'
    }).round(2)
    stage_type_times.columns = ['avgClearTime', 'avgScore', 'totalClears']
    print(stage_type_times.to_string())
    
    # Efficiency analysis by progress segment
    print("\n--- Efficiency by Progress Segment ---")
    segment_efficiency = df.groupby('progressSegment').agg({
        'avgTimePerStage': 'mean',
        'avgScorePerStage': 'mean',
        'efficiencyScore': 'mean',
        'username': 'count'
    }).round(2)
    segment_efficiency.columns = ['avgTimePerStage', 'avgScorePerStage', 'avgEfficiency', 'playerCount']
    print(segment_efficiency.to_string())
    
    return df

# =============================================================================
# CHURN AND RETENTION ANALYSIS
# =============================================================================

def analyze_retention(game_records, stage_data):
    """Analyze player retention and churn patterns"""
    print("\n" + "=" * 80)
    print("RETENTION AND CHURN ANALYSIS")
    print("=" * 80)
    
    df = game_records.copy()
    
    # Retention by progress milestones
    print("\n--- Retention by Progress Milestones ---")
    milestones = [0, 10, 25, 50, 75, 100]
    for i in range(len(milestones) - 1):
        start, end = milestones[i], milestones[i+1]
        count = len(df[(df['totalGameProgress'] >= start) & (df['totalGameProgress'] < end)])
        print(f"  {start}%-{end}%: {count} players ({count/len(df)*100:.1f}%)")
    
    # Completion rate
    completed = len(df[df['totalGameProgress'] >= 100])
    print(f"\n  100% Completion: {completed} players ({completed/len(df)*100:.1f}%)")
    
    # Churn analysis - find where players stopped
    print("\n--- Stage Dropout Analysis ---")
    active_usernames = df['username'].tolist()
    active_stages = stage_data[stage_data['username'].isin(active_usernames)].copy()
    
    # Find last unlocked stage for each player
    last_stages = active_stages[active_stages['isStageUnlock']].groupby('username').agg({
        'stageName': 'last'
    }).reset_index()
    
    dropout_stages = last_stages['stageName'].value_counts().head(10)
    print("\nMost common 'last stage' (potential dropout points):")
    print(dropout_stages.to_string())
    
    # Analyze players who didn't progress past first few stages
    early_dropout = df[df['totalGameProgress'] <= 10]
    print(f"\n--- Early Dropout Analysis (Progress <= 10%) ---")
    print(f"  Count: {len(early_dropout)} players ({len(early_dropout)/len(df)*100:.1f}%)")
    print(f"  Average play time: {early_dropout['playTimeHours'].mean():.2f} hours")
    print(f"  Average stages cleared: {early_dropout['totalTimesStageClear'].mean():.1f}")
    
    return df

# =============================================================================
# COMBINED INSIGHTS
# =============================================================================

def generate_combined_insights(game_records, stage_data, leaderboards, stage_leaderboards):
    """Generate combined insights from all data sources"""
    print("\n" + "=" * 80)
    print("COMBINED DATA INSIGHTS")
    print("=" * 80)
    
    # Merge leaderboard data with game records
    print("\n--- Leaderboard vs Game Records Comparison ---")
    
    # Get GameProgress from leaderboards
    lb_progress = leaderboards[leaderboards['leaderBoardType'] == 'GameProgress'][
        ['playerName', 'gameProgress', 'playTime']
    ].copy()
    lb_progress.columns = ['username', 'lb_gameProgress', 'lb_playTime']
    
    # Get TotalScore from leaderboards
    lb_score = leaderboards[leaderboards['leaderBoardType'] == 'TotalScore'][
        ['playerName', 'totalScore', 'playTime']
    ].copy()
    lb_score.columns = ['username', 'lb_totalScore', 'lb_playTime_score']
    
    # Merge with game records
    merged = game_records.merge(lb_progress, on='username', how='left')
    merged = merged.merge(lb_score, on='username', how='left')
    
    # Check data consistency
    matched = merged[merged['lb_gameProgress'].notna()]
    print(f"  Players matched with leaderboard: {len(matched)}")
    
    # Stage difficulty analysis using stage leaderboards
    print("\n--- Stage Difficulty Analysis (from clear times) ---")
    stage_difficulty = stage_leaderboards.groupby('stageName').agg({
        'playerClearTime': ['mean', 'std', 'count'],
        'playerScore': 'mean',
        'playerStar': 'mean'
    }).round(2)
    stage_difficulty.columns = ['avgClearTime', 'stdClearTime', 'attempts', 'avgScore', 'avgStars']
    
    # Most difficult stages (highest avg clear time)
    print("\nHardest stages by clear time:")
    print(stage_difficulty.nlargest(10, 'avgClearTime')[['avgClearTime', 'attempts', 'avgScore']].to_string())
    
    # Easiest stages
    print("\nEasiest stages by clear time:")
    print(stage_difficulty.nsmallest(10, 'avgClearTime')[['avgClearTime', 'attempts', 'avgScore']].to_string())
    
    return merged, stage_difficulty

# =============================================================================
# EXPORT RESULTS
# =============================================================================

def export_analysis_results(game_records, stage_unlock_rates, correlation_matrix, output_dir):
    """Export analysis results to CSV files"""
    print("\n" + "=" * 80)
    print("EXPORTING ANALYSIS RESULTS")
    print("=" * 80)
    
    # Export segmented player data
    export_cols = [
        'username', 'totalStageScore', 'totalGameProgress', 'totalPlayTime',
        'playTimeHours', 'totalTimesStageClear', 'totalCommandExecuteTimes',
        'perfectClearRate', 'hintUsageRate', 'efficiencyScore',
        'progressSegment', 'learningStyle', 'engagementLevel'
    ]
    available_cols = [c for c in export_cols if c in game_records.columns]
    game_records[available_cols].to_csv(
        f"{output_dir}/analysis_player_segments.csv", 
        index=False, 
        encoding='utf-8-sig'
    )
    print(f"Exported: analysis_player_segments.csv")
    
    # Export stage unlock rates
    stage_unlock_rates.to_csv(
        f"{output_dir}/analysis_stage_unlock_rates.csv",
        index=False,
        encoding='utf-8-sig'
    )
    print(f"Exported: analysis_stage_unlock_rates.csv")
    
    # Export correlation matrix
    correlation_matrix.to_csv(
        f"{output_dir}/analysis_correlation_matrix.csv",
        encoding='utf-8-sig'
    )
    print(f"Exported: analysis_correlation_matrix.csv")
    
    # Generate summary report
    summary_report = f"""
GiTaiment Game Analytics Summary Report
========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PLAYER OVERVIEW
---------------
Total Active Players: {len(game_records)}
Average Game Progress: {game_records['totalGameProgress'].mean():.1f}%
Average Play Time: {game_records['playTimeHours'].mean():.2f} hours
Average Score: {game_records['totalStageScore'].mean():.0f}

PLAYER SEGMENTS
---------------
Progress Distribution:
{game_records['progressSegment'].value_counts().to_string()}

Learning Styles:
{game_records['learningStyle'].value_counts().to_string()}

Engagement Levels:
{game_records['engagementLevel'].value_counts().to_string()}

KEY INSIGHTS
------------
1. Completion Rate: {(game_records['totalGameProgress'] >= 100).sum() / len(game_records) * 100:.1f}%
2. Average Perfect Clear Rate: {game_records['perfectClearRate'].mean():.1f}%
3. Average Hint Usage Rate: {game_records['hintUsageRate'].mean():.1f}%
4. Players using Game Manual: {(game_records['totalTimesUsedGameManual'] > 0).sum()} ({(game_records['totalTimesUsedGameManual'] > 0).sum() / len(game_records) * 100:.1f}%)
5. Average Commands per Player: {game_records['totalCommandExecuteTimes'].mean():.1f}
"""
    
    with open(f"{output_dir}/analysis_summary_report.txt", 'w', encoding='utf-8') as f:
        f.write(summary_report)
    print(f"Exported: analysis_summary_report.txt")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Data directory
    data_dir = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData"
    
    # Load all data
    game_records, stage_data, leaderboards, stage_leaderboards = load_all_data(data_dir)
    
    # Preprocess data
    game_records, stage_data, leaderboards, stage_leaderboards = preprocess_data(
        game_records, stage_data, leaderboards, stage_leaderboards
    )
    
    # Segment players
    game_records = segment_players(game_records)
    
    # Analyze stage progression
    stage_unlock_rates, tutorial_stages = analyze_stage_progression(stage_data, game_records)
    
    # Analyze performance
    correlation_matrix = analyze_performance(game_records, stage_data)
    
    # Analyze learning behavior
    game_records = analyze_learning_behavior(game_records)
    
    # Analyze time patterns
    game_records = analyze_time_patterns(game_records, stage_data)
    
    # Analyze retention
    game_records = analyze_retention(game_records, stage_data)
    
    # Generate combined insights
    merged_data, stage_difficulty = generate_combined_insights(
        game_records, stage_data, leaderboards, stage_leaderboards
    )
    
    # Export results
    export_analysis_results(game_records, stage_unlock_rates, correlation_matrix, data_dir)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
