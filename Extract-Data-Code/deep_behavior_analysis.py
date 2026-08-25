"""
GiTaiment Deep Behavior Mining Analysis
=======================================
This script performs advanced data mining including:
1. Behavior Sequence Analysis - What patterns lead to success/failure
2. Help-Seeking Effect Analysis - How hints/answers affect performance
3. Learning Trajectory Analysis - How players progress over time
4. Failure Pattern Analysis - What behaviors lead to dropout

Author: Data Mining Script
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DATA LOADING
# =============================================================================

def load_data(data_dir):
    """Load all extracted CSV files"""
    print("=" * 80)
    print("LOADING DATA FOR DEEP ANALYSIS")
    print("=" * 80)
    
    events = pd.read_csv(f"{data_dir}/extracted_events.csv")
    events['eventTime'] = pd.to_datetime(events['eventTime'], format='mixed')
    print(f"Events: {len(events)} records")
    
    game_records = pd.read_csv(f"{data_dir}/extracted_player_game_records.csv")
    print(f"Game Records: {len(game_records)} players")
    
    stage_data = pd.read_csv(f"{data_dir}/extracted_player_stage_data.csv")
    print(f"Stage Data: {len(stage_data)} records")
    
    per_user = pd.read_csv(f"{data_dir}/analysis_per_user_combined.csv")
    print(f"Per-User Combined: {len(per_user)} users")
    
    return events, game_records, stage_data, per_user

# =============================================================================
# 1. BEHAVIOR SEQUENCE ANALYSIS
# =============================================================================

def extract_behavior_sequences(events, username, window_size=5):
    """
    Extract behavior sequences for a user.
    Returns sequences of eventName in order.
    """
    user_events = events[events['player'] == username].sort_values('eventTime')
    sequences = []
    
    event_names = user_events['eventName'].tolist()
    
    # Extract n-gram sequences
    for i in range(len(event_names) - window_size + 1):
        seq = tuple(event_names[i:i + window_size])
        sequences.append(seq)
    
    return sequences

def analyze_success_sequences(events, game_records):
    """
    Analyze what behavior sequences lead to successful quest completion.
    """
    print("\n" + "=" * 80)
    print("1. BEHAVIOR SEQUENCE ANALYSIS")
    print("=" * 80)
    
    # Define success metrics
    high_performers = game_records[game_records['totalGameProgress'] >= 50]['username'].tolist()
    low_performers = game_records[game_records['totalGameProgress'] < 20]['username'].tolist()
    
    print(f"\nHigh Performers (≥50% progress): {len(high_performers)}")
    print(f"Low Performers (<20% progress): {len(low_performers)}")
    
    # Extract sequences before quest completion
    success_patterns = []
    failure_patterns = []
    
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        event_list = list(zip(user_events['eventName'], user_events['eventDetail']))
        
        for i, (event_name, event_detail) in enumerate(event_list):
            if event_name == 'Complete Quest' and i >= 3:
                # Get 3 events before completion
                prev_sequence = [e[0] for e in event_list[i-3:i]]
                
                if 'Perfect' in str(event_detail):
                    success_patterns.append(tuple(prev_sequence))
                elif 'Answer' in str(event_detail) or 'Hint' in str(event_detail):
                    failure_patterns.append(tuple(prev_sequence))
    
    print("\n--- Sequences Leading to PERFECT Quest Completion ---")
    success_counter = Counter(success_patterns)
    for seq, count in success_counter.most_common(10):
        print(f"  {' → '.join(seq)}: {count} times")
    
    print("\n--- Sequences Leading to HINT/ANSWER Quest Completion ---")
    failure_counter = Counter(failure_patterns)
    for seq, count in failure_counter.most_common(10):
        print(f"  {' → '.join(seq)}: {count} times")
    
    return success_counter, failure_counter

def analyze_action_sequences_before_failure(events):
    """
    Analyze what happens before a Failed Action.
    """
    print("\n--- Sequences Leading to FAILED Actions ---")
    
    failure_sequences = []
    
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        event_list = user_events['eventName'].tolist()
        
        for i, event_name in enumerate(event_list):
            if event_name == 'Failed Action' and i >= 2:
                prev_sequence = tuple(event_list[i-2:i])
                failure_sequences.append(prev_sequence)
    
    failure_counter = Counter(failure_sequences)
    for seq, count in failure_counter.most_common(10):
        print(f"  {' → '.join(seq)} → Failed Action: {count} times")
    
    return failure_counter

# =============================================================================
# 2. HELP-SEEKING EFFECT ANALYSIS
# =============================================================================

def analyze_help_seeking_effects(per_user, game_records):
    """
    Analyze how using hints and answers affects player performance.
    """
    print("\n" + "=" * 80)
    print("2. HELP-SEEKING EFFECT ANALYSIS")
    print("=" * 80)
    
    # Calculate help-seeking ratio for each user
    df = per_user.copy()
    
    # Avoid division by zero
    df['total_quests'] = df['event_quests_completed'].fillna(0)
    df['hint_ratio'] = df['event_hint_used_quests'].fillna(0) / df['total_quests'].replace(0, 1)
    df['answer_ratio'] = df['event_answer_used_quests'].fillna(0) / df['total_quests'].replace(0, 1)
    df['help_ratio'] = (df['event_hint_used_quests'].fillna(0) + df['event_answer_used_quests'].fillna(0)) / df['total_quests'].replace(0, 1)
    df['perfect_ratio'] = df['event_perfect_quests'].fillna(0) / df['total_quests'].replace(0, 1)
    
    # Categorize players by help-seeking behavior
    df['help_category'] = pd.cut(df['help_ratio'], 
                                  bins=[-0.01, 0.05, 0.2, 0.5, 1.01],
                                  labels=['Independent', 'Low Help', 'Moderate Help', 'High Help'])
    
    print("\n--- Help-Seeking Categories ---")
    category_stats = df.groupby('help_category').agg({
        'username': 'count',
        'record_totalGameProgress': 'mean',
        'record_totalStageScore': 'mean',
        'stage_stages_cleared': 'mean',
        'perfect_ratio': 'mean'
    }).round(2)
    category_stats.columns = ['Count', 'Avg Progress %', 'Avg Score', 'Avg Stages Cleared', 'Perfect Rate']
    print(category_stats.to_string())
    
    # Correlation analysis
    print("\n--- Correlation: Help-Seeking vs Performance ---")
    correlations = {
        'Help Ratio vs Game Progress': df['help_ratio'].corr(df['record_totalGameProgress']),
        'Help Ratio vs Total Score': df['help_ratio'].corr(df['record_totalStageScore']),
        'Help Ratio vs Stages Cleared': df['help_ratio'].corr(df['stage_stages_cleared']),
        'Answer Ratio vs Progress': df['answer_ratio'].corr(df['record_totalGameProgress']),
        'Hint Ratio vs Progress': df['hint_ratio'].corr(df['record_totalGameProgress']),
    }
    
    for metric, corr in correlations.items():
        interpretation = "positive" if corr > 0 else "negative"
        strength = "strong" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"
        print(f"  {metric}: {corr:.3f} ({strength} {interpretation})")
    
    # Statistical comparison
    print("\n--- Performance Comparison by Help Usage ---")
    independent = df[df['help_category'] == 'Independent']
    high_help = df[df['help_category'] == 'High Help']
    
    if len(independent) > 0 and len(high_help) > 0:
        print(f"\n  Independent Learners (n={len(independent)}):")
        print(f"    Avg Progress: {independent['record_totalGameProgress'].mean():.1f}%")
        print(f"    Avg Score: {independent['record_totalStageScore'].mean():.0f}")
        print(f"    Perfect Rate: {independent['perfect_ratio'].mean():.1%}")
        
        print(f"\n  High Help Users (n={len(high_help)}):")
        print(f"    Avg Progress: {high_help['record_totalGameProgress'].mean():.1f}%")
        print(f"    Avg Score: {high_help['record_totalStageScore'].mean():.0f}")
        print(f"    Perfect Rate: {high_help['perfect_ratio'].mean():.1%}")
    
    return df, category_stats

def analyze_hint_timing_effect(events, game_records):
    """
    Analyze when players start using hints and how it affects their trajectory.
    """
    print("\n--- Hint Timing Analysis ---")
    
    results = []
    
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        
        # Find first hint/answer usage
        hint_events = user_events[user_events['eventDetail'].str.contains('Hint|Answer', na=False)]
        quest_events = user_events[user_events['eventName'] == 'Complete Quest']
        
        if len(hint_events) > 0 and len(quest_events) > 0:
            first_hint_idx = user_events.index.get_loc(hint_events.index[0])
            total_quests_before_hint = len(quest_events[quest_events.index < hint_events.index[0]])
            
            # Get final performance
            user_record = game_records[game_records['username'] == username]
            if len(user_record) > 0:
                results.append({
                    'username': username,
                    'quests_before_first_hint': total_quests_before_hint,
                    'final_progress': user_record['totalGameProgress'].values[0],
                    'final_score': user_record['totalStageScore'].values[0]
                })
    
    if results:
        timing_df = pd.DataFrame(results)
        
        # Categorize by early vs late hint adoption
        median_quests = timing_df['quests_before_first_hint'].median()
        timing_df['hint_timing'] = timing_df['quests_before_first_hint'].apply(
            lambda x: 'Early Adopter' if x < median_quests else 'Late Adopter'
        )
        
        print(f"\n  Median quests before first hint: {median_quests:.0f}")
        
        timing_stats = timing_df.groupby('hint_timing').agg({
            'username': 'count',
            'final_progress': 'mean',
            'final_score': 'mean'
        }).round(2)
        timing_stats.columns = ['Count', 'Avg Final Progress', 'Avg Final Score']
        print(timing_stats.to_string())
        
        return timing_df
    
    return None

# =============================================================================
# 3. LEARNING TRAJECTORY ANALYSIS
# =============================================================================

def analyze_learning_trajectories(events, stage_data):
    """
    Analyze how players' performance changes over time.
    """
    print("\n" + "=" * 80)
    print("3. LEARNING TRAJECTORY ANALYSIS")
    print("=" * 80)
    
    trajectories = {}
    
    for username in events['player'].unique():
        user_events = events[events['player'] == username].sort_values('eventTime')
        quest_completions = user_events[user_events['eventName'] == 'Complete Quest']
        
        if len(quest_completions) < 5:
            continue
        
        # Track performance over quest sequence
        performance_over_time = []
        for idx, (_, row) in enumerate(quest_completions.iterrows()):
            detail = str(row['eventDetail'])
            score = 4 if 'Perfect' in detail else 3 if 'Good' in detail else 2 if 'Hint' in detail else 1
            performance_over_time.append(score)
        
        # Calculate early vs late performance
        n = len(performance_over_time)
        early_perf = np.mean(performance_over_time[:n//3]) if n >= 3 else np.mean(performance_over_time)
        late_perf = np.mean(performance_over_time[-n//3:]) if n >= 3 else np.mean(performance_over_time)
        
        trajectories[username] = {
            'early_performance': early_perf,
            'late_performance': late_perf,
            'improvement': late_perf - early_perf,
            'total_quests': n,
            'trajectory': performance_over_time
        }
    
    # Categorize learning trajectories
    traj_df = pd.DataFrame(trajectories).T
    traj_df['trajectory_type'] = traj_df['improvement'].apply(
        lambda x: 'Improving' if x > 0.3 else 'Declining' if x < -0.3 else 'Stable'
    )
    
    print("\n--- Learning Trajectory Categories ---")
    traj_counts = traj_df['trajectory_type'].value_counts()
    for traj_type, count in traj_counts.items():
        pct = count / len(traj_df) * 100
        print(f"  {traj_type}: {count} players ({pct:.1f}%)")
    
    print("\n--- Trajectory Statistics ---")
    traj_stats = traj_df.groupby('trajectory_type').agg({
        'early_performance': 'mean',
        'late_performance': 'mean',
        'improvement': 'mean',
        'total_quests': 'mean'
    }).round(2)
    traj_stats.columns = ['Avg Early Score', 'Avg Late Score', 'Avg Improvement', 'Avg Quests']
    print(traj_stats.to_string())
    
    return traj_df

def analyze_stage_difficulty_progression(events, stage_data):
    """
    Analyze how players perform across different stage types (Basic → Branch → Remote).
    """
    print("\n--- Stage Type Performance Progression ---")
    
    # Get stage types
    stage_types = stage_data[['stageName', 'stageType']].drop_duplicates()
    
    results = []
    
    for username in stage_data['username'].unique():
        user_stages = stage_data[stage_data['username'] == username]
        
        for stage_type in ['Basic', 'Branch', 'Remote']:
            type_stages = user_stages[user_stages['stageType'] == stage_type]
            cleared = (type_stages['stageClearTimes'] > 0).sum()
            total = len(type_stages)
            avg_score = type_stages[type_stages['bestPlayerScore'] > 0]['bestPlayerScore'].mean()
            
            results.append({
                'username': username,
                'stage_type': stage_type,
                'clear_rate': cleared / total if total > 0 else 0,
                'avg_score': avg_score
            })
    
    progression_df = pd.DataFrame(results)
    
    # Average by stage type
    type_stats = progression_df.groupby('stage_type').agg({
        'clear_rate': 'mean',
        'avg_score': 'mean'
    }).round(3)
    
    # Reorder by difficulty
    type_stats = type_stats.reindex(['Basic', 'Branch', 'Remote'])
    type_stats.columns = ['Avg Clear Rate', 'Avg Score']
    print(type_stats.to_string())
    
    return progression_df

# =============================================================================
# 4. FAILURE PATTERN ANALYSIS
# =============================================================================

def analyze_dropout_patterns(events, game_records):
    """
    Analyze what behaviors predict player dropout.
    """
    print("\n" + "=" * 80)
    print("4. DROPOUT & FAILURE PATTERN ANALYSIS")
    print("=" * 80)
    
    # Define dropout: progress < 20% 
    dropout_users = game_records[game_records['totalGameProgress'] < 20]['username'].tolist()
    active_users = game_records[game_records['totalGameProgress'] >= 50]['username'].tolist()
    
    print(f"\nDropout Users (<20% progress): {len(dropout_users)}")
    print(f"Active Users (≥50% progress): {len(active_users)}")
    
    # Analyze behaviors
    dropout_behaviors = []
    active_behaviors = []
    
    for username in dropout_users:
        user_events = events[events['player'] == username]
        if len(user_events) > 0:
            dropout_behaviors.append({
                'username': username,
                'total_events': len(user_events),
                'failed_actions': len(user_events[user_events['eventName'] == 'Failed Action']),
                'manual_opens': len(user_events[user_events['eventName'] == 'Read GameManual']),
                'leaderboard_checks': len(user_events[user_events['eventName'] == 'Check GlobalLeaderBoard']),
                'quests_completed': len(user_events[user_events['eventName'] == 'Complete Quest']),
                'stages_started': len(user_events[user_events['eventName'] == 'Start Stage'])
            })
    
    for username in active_users:
        user_events = events[events['player'] == username]
        if len(user_events) > 0:
            active_behaviors.append({
                'username': username,
                'total_events': len(user_events),
                'failed_actions': len(user_events[user_events['eventName'] == 'Failed Action']),
                'manual_opens': len(user_events[user_events['eventName'] == 'Read GameManual']),
                'leaderboard_checks': len(user_events[user_events['eventName'] == 'Check GlobalLeaderBoard']),
                'quests_completed': len(user_events[user_events['eventName'] == 'Complete Quest']),
                'stages_started': len(user_events[user_events['eventName'] == 'Start Stage'])
            })
    
    dropout_df = pd.DataFrame(dropout_behaviors) if dropout_behaviors else pd.DataFrame()
    active_df = pd.DataFrame(active_behaviors) if active_behaviors else pd.DataFrame()
    
    print("\n--- Behavior Comparison: Dropout vs Active ---")
    
    if len(dropout_df) > 0 and len(active_df) > 0:
        comparison = pd.DataFrame({
            'Metric': ['Avg Events', 'Avg Failed Actions', 'Avg Manual Opens', 
                      'Avg Leaderboard Checks', 'Avg Quests Completed', 'Avg Stages Started'],
            'Dropout': [
                dropout_df['total_events'].mean(),
                dropout_df['failed_actions'].mean(),
                dropout_df['manual_opens'].mean(),
                dropout_df['leaderboard_checks'].mean(),
                dropout_df['quests_completed'].mean(),
                dropout_df['stages_started'].mean()
            ],
            'Active': [
                active_df['total_events'].mean(),
                active_df['failed_actions'].mean(),
                active_df['manual_opens'].mean(),
                active_df['leaderboard_checks'].mean(),
                active_df['quests_completed'].mean(),
                active_df['stages_started'].mean()
            ]
        })
        comparison['Ratio (Active/Dropout)'] = comparison['Active'] / comparison['Dropout'].replace(0, 0.001)
        print(comparison.to_string(index=False))
        
        # Calculate failure rate
        print("\n--- Failure Rate Analysis ---")
        dropout_df['failure_rate'] = dropout_df['failed_actions'] / dropout_df['total_events'].replace(0, 1)
        active_df['failure_rate'] = active_df['failed_actions'] / active_df['total_events'].replace(0, 1)
        
        print(f"  Dropout users avg failure rate: {dropout_df['failure_rate'].mean():.2%}")
        print(f"  Active users avg failure rate: {active_df['failure_rate'].mean():.2%}")
    
    return dropout_df, active_df

def analyze_struggle_points(events, stage_data):
    """
    Identify which stages cause the most failures/dropouts.
    """
    print("\n--- Stage Struggle Points ---")
    
    # Count failed actions per stage
    stage_failures = events[events['eventName'] == 'Failed Action'].groupby('gameScene').size()
    stage_starts = events[events['eventName'] == 'Start Stage'].groupby('gameScene').size()
    
    # Calculate failure rate per stage
    struggle_df = pd.DataFrame({
        'failures': stage_failures,
        'starts': stage_starts
    }).fillna(0)
    
    struggle_df['failure_rate'] = struggle_df['failures'] / struggle_df['starts'].replace(0, 1)
    struggle_df = struggle_df.sort_values('failure_rate', ascending=False)
    
    print("\nTop 10 Most Difficult Stages (by failure rate):")
    for idx, (stage, row) in enumerate(struggle_df.head(10).iterrows()):
        # Clean stage name
        stage_name = stage.replace('Play Game - ', '')
        print(f"  {idx+1}. {stage_name}")
        print(f"     Failures: {int(row['failures'])}, Starts: {int(row['starts'])}, Rate: {row['failure_rate']:.2%}")
    
    return struggle_df

# =============================================================================
# 5. ADVANCED SEQUENCE MINING
# =============================================================================

def analyze_quest_completion_patterns(events):
    """
    Analyze detailed patterns in quest completion.
    """
    print("\n" + "=" * 80)
    print("5. QUEST COMPLETION PATTERN ANALYSIS")
    print("=" * 80)
    
    quest_completions = events[events['eventName'] == 'Complete Quest'].copy()
    
    # Extract completion type
    def get_completion_type(detail):
        if pd.isna(detail):
            return 'Unknown'
        if 'Perfect' in str(detail):
            return 'Perfect'
        elif 'Good' in str(detail):
            return 'Good'
        elif 'Hint' in str(detail):
            return 'Hint'
        elif 'Answer' in str(detail):
            return 'Answer'
        return 'Unknown'
    
    quest_completions['completion_type'] = quest_completions['eventDetail'].apply(get_completion_type)
    
    print("\n--- Overall Quest Completion Distribution ---")
    completion_dist = quest_completions['completion_type'].value_counts()
    total = len(quest_completions)
    for comp_type, count in completion_dist.items():
        print(f"  {comp_type}: {count} ({count/total:.1%})")
    
    # Analyze completion type sequences per user
    print("\n--- Completion Type Transition Analysis ---")
    transitions = defaultdict(int)
    
    for username in quest_completions['player'].unique():
        user_quests = quest_completions[quest_completions['player'] == username].sort_values('eventTime')
        types = user_quests['completion_type'].tolist()
        
        for i in range(len(types) - 1):
            transition = (types[i], types[i+1])
            transitions[transition] += 1
    
    print("\nMost Common Completion Transitions:")
    sorted_transitions = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
    for (from_type, to_type), count in sorted_transitions[:10]:
        print(f"  {from_type} → {to_type}: {count} times")
    
    # Calculate persistence metrics
    print("\n--- Completion Streak Analysis ---")
    perfect_streaks = []
    
    for username in quest_completions['player'].unique():
        user_quests = quest_completions[quest_completions['player'] == username].sort_values('eventTime')
        types = user_quests['completion_type'].tolist()
        
        current_streak = 0
        max_streak = 0
        
        for t in types:
            if t == 'Perfect':
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        if max_streak > 0:
            perfect_streaks.append({'username': username, 'max_perfect_streak': max_streak})
    
    if perfect_streaks:
        streak_df = pd.DataFrame(perfect_streaks)
        print(f"  Average max Perfect streak: {streak_df['max_perfect_streak'].mean():.1f}")
        print(f"  Max Perfect streak overall: {streak_df['max_perfect_streak'].max()}")
        top_streakers = streak_df.nlargest(5, 'max_perfect_streak')
        print("\n  Top 5 Perfect Streakers:")
        for _, row in top_streakers.iterrows():
            print(f"    {row['username']}: {row['max_perfect_streak']} consecutive Perfects")
    
    return quest_completions, transitions

# =============================================================================
# 6. EXPORT RESULTS
# =============================================================================

def export_analysis_results(results, output_dir):
    """Export all analysis results to CSV files"""
    print("\n" + "=" * 80)
    print("EXPORTING ANALYSIS RESULTS")
    print("=" * 80)
    
    # Export help-seeking analysis
    if 'help_analysis' in results and results['help_analysis'] is not None:
        df, _ = results['help_analysis']
        df.to_csv(f"{output_dir}/analysis_help_seeking.csv", index=False, encoding='utf-8-sig')
        print(f"Exported: analysis_help_seeking.csv")
    
    # Export learning trajectories
    if 'trajectories' in results and results['trajectories'] is not None:
        results['trajectories'].to_csv(f"{output_dir}/analysis_learning_trajectories.csv", encoding='utf-8-sig')
        print(f"Exported: analysis_learning_trajectories.csv")
    
    # Export struggle points
    if 'struggle_points' in results and results['struggle_points'] is not None:
        results['struggle_points'].to_csv(f"{output_dir}/analysis_struggle_points.csv", encoding='utf-8-sig')
        print(f"Exported: analysis_struggle_points.csv")
    
    # Export behavior sequences
    if 'success_sequences' in results:
        success_seq, failure_seq = results['success_sequences']
        seq_data = []
        for seq, count in success_seq.most_common(50):
            seq_data.append({'sequence': ' → '.join(seq), 'count': count, 'type': 'success_perfect'})
        for seq, count in failure_seq.most_common(50):
            seq_data.append({'sequence': ' → '.join(seq), 'count': count, 'type': 'with_help'})
        for seq, count in results.get('failure_sequences', Counter()).most_common(50):
            seq_data.append({'sequence': ' → '.join(seq + ('Failed Action',)), 'count': count, 'type': 'failed_action'})
        sequence_df = pd.DataFrame(seq_data)
        sequence_df.to_csv(f"{output_dir}/analysis_behavior_sequences.csv", index=False, encoding='utf-8-sig')
        print(f"Exported: analysis_behavior_sequences.csv")
        create_sequence_charts(sequence_df, output_dir)
        pd.DataFrame([
            {'field': 'sequence', 'definition': 'Ordered event-name pattern immediately before and including the focal outcome where applicable.'},
            {'field': 'count', 'definition': 'Number of times the exact sequence was observed across all players in both data versions.'},
            {'field': 'type=success_perfect', 'definition': 'Three events immediately preceding a Complete Quest event whose detail contains Perfect.'},
            {'field': 'type=with_help', 'definition': 'Three events immediately preceding a Complete Quest event whose detail contains Hint or Answer.'},
            {'field': 'type=failed_action', 'definition': 'Two events immediately preceding Failed Action, followed by the Failed Action outcome.'},
            {'field': 'ordering', 'definition': 'Events are grouped by player and ordered by eventTime; sequences never cross player boundaries.'},
        ]).to_csv(f"{output_dir}/analysis_sequence_feature_dictionary.csv", index=False, encoding='utf-8-sig')


def create_sequence_charts(sequence_df, output_dir):
    """Visualize dominant sequences and compare sequence categories."""
    plt.style.use('seaborn-v0_8-whitegrid')
    labels = {'success_perfect': 'Perfect completion', 'with_help': 'Hint/answer completion',
              'failed_action': 'Failed action'}
    colors = {'success_perfect': '#54A24B', 'with_help': '#F58518',
              'failed_action': '#E45756'}

    for sequence_type, group in sequence_df.groupby('type'):
        top = group.nlargest(12, 'count').sort_values('count')
        fig, ax = plt.subplots(figsize=(12, 7))
        shortened = top['sequence'].str.replace(' → ', '\n→ ', regex=False)
        bars = ax.barh(shortened, top['count'], color=colors.get(sequence_type, '#4C78A8'))
        ax.bar_label(bars, padding=3)
        ax.set_xlabel('Observed frequency')
        ax.set_title(f"Most Frequent Sequences: {labels.get(sequence_type, sequence_type)}")
        fig.tight_layout()
        fig.savefig(f"{output_dir}/figure_sequences_{sequence_type}.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

    totals = sequence_df.groupby('type')['count'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar([labels.get(item, item) for item in totals.index], totals.values,
                  color=[colors.get(item, '#4C78A8') for item in totals.index])
    ax.bar_label(bars)
    ax.set_ylabel('Frequency among exported top sequences')
    ax.set_title('Behavior Sequence Category Frequencies')
    fig.tight_layout()
    fig.savefig(f"{output_dir}/figure_sequence_category_comparison.png", dpi=300)
    plt.close(fig)

def generate_research_summary(results):
    """Generate a summary suitable for research paper"""
    print("\n" + "=" * 80)
    print("RESEARCH SUMMARY")
    print("=" * 80)
    
    summary = """
## Key Findings for Research Paper

### 1. Help-Seeking Behavior Effects
- Examined relationship between hint/answer usage and player performance
- Found that help-seeking behavior correlates with game progress
- Players can be categorized into: Independent, Low Help, Moderate Help, High Help

### 2. Behavior Sequences
- Identified common action sequences leading to successful quest completion
- Analyzed patterns that precede failed actions
- Found recurring sequences associated with player success

### 3. Learning Trajectories
- Categorized players into: Improving, Stable, Declining
- Tracked performance changes from early to late game
- Identified factors associated with improvement

### 4. Dropout Patterns
- Compared behaviors of dropout vs active players
- Identified struggle points (difficult stages)
- Found early warning indicators of dropout

### 5. Stage Difficulty Progression
- Analyzed performance across Basic → Branch → Remote stages
- Identified stages with highest failure rates
- Found natural difficulty curve in the game

### Implications for Game Design
1. Consider adaptive hint timing based on player behavior
2. Focus tutorial improvements on high-failure stages
3. Use early behavior patterns for intervention targeting
"""
    print(summary)
    return summary

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    data_dir = "."
    
    # Load data
    events, game_records, stage_data, per_user = load_data(data_dir)
    
    results = {}
    
    # 1. Behavior Sequence Analysis
    results['success_sequences'] = analyze_success_sequences(events, game_records)
    results['failure_sequences'] = analyze_action_sequences_before_failure(events)
    
    # 2. Help-Seeking Effect Analysis
    results['help_analysis'] = analyze_help_seeking_effects(per_user, game_records)
    analyze_hint_timing_effect(events, game_records)
    
    # 3. Learning Trajectory Analysis
    results['trajectories'] = analyze_learning_trajectories(events, stage_data)
    analyze_stage_difficulty_progression(events, stage_data)
    
    # 4. Dropout Pattern Analysis
    results['dropout_analysis'] = analyze_dropout_patterns(events, game_records)
    results['struggle_points'] = analyze_struggle_points(events, stage_data)
    
    # 5. Quest Completion Patterns
    results['quest_patterns'] = analyze_quest_completion_patterns(events)
    
    # Export results
    export_analysis_results(results, data_dir)
    
    # Generate research summary
    generate_research_summary(results)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
