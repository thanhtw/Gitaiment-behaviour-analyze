"""Source extraction used by the retained analysis pipeline."""
import pandas as pd
from datetime import timedelta

def load_all_data(data_dir):
    """
    Load all data sources with documentation of origin.
    
    Returns dictionary with data and metadata about each source.
    """
    print("=" * 80)
    print("DATA SOURCES AND LOADING")
    print("=" * 80)
    
    data_sources = {}
    
    # Source 1: Event Data (from GEG-database.eventdatas.json)
    print("\n[SOURCE 1] Event Data")
    print("  Origin: GEG-database.eventdatas.json")
    print("  Description: Real-time player action logs")
    events = pd.read_csv(f"{data_dir}/extracted_events.csv")
    events['eventTime'] = pd.to_datetime(events['eventTime'], format='mixed')
    data_sources['events'] = {
        'data': events,
        'origin': 'GEG-database.eventdatas.json',
        'records': len(events),
        'unique_players': events['player'].nunique(),
        'fields': ['player', 'eventName', 'eventDetail', 'gameScene', 'eventTime']
    }
    print(f"  Records: {len(events)}, Unique Players: {events['player'].nunique()}")
    
    # Source 2: Player Game Records (from GEG-database.playersavedatas.json)
    print("\n[SOURCE 2] Player Game Records")
    print("  Origin: GEG-database.playersavedatas.json → gameRecordData")
    print("  Description: Cumulative player statistics")
    game_records = pd.read_csv(f"{data_dir}/extracted_player_game_records.csv")
    data_sources['game_records'] = {
        'data': game_records,
        'origin': 'GEG-database.playersavedatas.json',
        'records': len(game_records),
        'fields': ['totalStarCount', 'totalStageScore', 'totalGameProgress', 
                   'totalPlayTime', 'totalTimesStageClear', 'totalCommandExecuteTimes']
    }
    print(f"  Records: {len(game_records)} players")
    
    # Source 3: Player Stage Data (from GEG-database.playersavedatas.json)
    print("\n[SOURCE 3] Player Stage Data")
    print("  Origin: GEG-database.playersavedatas.json → stageData")
    print("  Description: Per-stage progress for each player")
    stage_data = pd.read_csv(f"{data_dir}/extracted_player_stage_data.csv")
    data_sources['stage_data'] = {
        'data': stage_data,
        'origin': 'GEG-database.playersavedatas.json',
        'records': len(stage_data),
        'fields': ['stageName', 'stageType', 'isStageUnlock', 'stageClearTimes', 
                   'bestPlayerScore', 'bestPlayerClearTime']
    }
    print(f"  Records: {len(stage_data)} (players × stages)")
    
    # Source 4: Global Leaderboards (from GEG-database.globalleaderboarddatas.json)
    print("\n[SOURCE 4] Global Leaderboards")
    print("  Origin: GEG-database.globalleaderboarddatas.json")
    print("  Description: Global rankings by criteria")
    leaderboards = pd.read_csv(f"{data_dir}/extracted_leaderboards.csv")
    data_sources['leaderboards'] = {
        'data': leaderboards,
        'origin': 'GEG-database.globalleaderboarddatas.json',
        'records': len(leaderboards),
        'fields': ['leaderBoardType', 'playerName', 'playTime', 'gameProgress', 'totalScore']
    }
    print(f"  Records: {len(leaderboards)} entries")
    
    return data_sources


def extract_user_events_profile(events_df, username):
    """
    Extract behavioral profile from event data for a specific user.
    
    Source: extracted_events.csv (from GEG-database.eventdatas.json)
    """
    user_events = events_df[events_df['player'] == username].copy()
    
    if len(user_events) == 0:
        return None
    
    user_events = user_events.sort_values('eventTime')
    
    profile = {
        # Basic info
        'username': username,
        'total_events': len(user_events),
        'first_activity': user_events['eventTime'].min(),
        'last_activity': user_events['eventTime'].max(),
        
        # Session analysis
        'total_logins': len(user_events[user_events['eventName'] == 'Login']),
        'total_sessions': calculate_sessions(user_events),
        
        # Stage interactions
        'stages_started': len(user_events[user_events['eventName'] == 'Start Stage']),
        # Note: Stage clear/fail events are tracked via 'Complete Quest' with last quest completion
        'last_conversations': len(user_events[user_events['eventName'] == 'Last Conversation']),  # Stage completion indicator
        
        # Quest interactions
        'quests_added': len(user_events[user_events['eventName'] == 'Add New Quest']),
        'quests_completed': len(user_events[user_events['eventName'] == 'Complete Quest']),
        'perfect_quests': len(user_events[user_events['eventDetail'].str.contains('Perfect', na=False)]),
        'good_quests': len(user_events[user_events['eventDetail'].str.contains('Good', na=False)]),
        'hint_used_quests': len(user_events[user_events['eventDetail'].str.contains('Hint', na=False)]),
        'answer_used_quests': len(user_events[user_events['eventDetail'].str.contains('Answer', na=False)]),
        
        # Help-seeking behavior
        'window_opens': len(user_events[user_events['eventName'] == 'Open Window']),
        'game_manual_opens': len(user_events[user_events['eventDetail'] == 'GameManual']),
        'manual_pages_read': len(user_events[user_events['eventName'] == 'Read GameManual']),
        'player_records_viewed': len(user_events[user_events['eventDetail'] == 'PlayerGameRecords']),
        
        # Actions in game
        'correct_actions': len(user_events[user_events['eventName'] == 'Correct Action']),
        'failed_actions': len(user_events[user_events['eventName'] == 'Failed Action']),
        
        # Leaderboard checks
        'leaderboard_checks': len(user_events[user_events['eventName'] == 'Check GlobalLeaderBoard']),
        'leaderboard_score_checks': len(user_events[user_events['eventDetail'] == 'TotalScore']),
        'leaderboard_progress_checks': len(user_events[user_events['eventDetail'] == 'GameProgress']),
        
        # Unique stages attempted
        'unique_stages_attempted': user_events[user_events['eventName'] == 'Start Stage']['eventDetail'].nunique(),
    }
    
    # Calculate activity duration
    if profile['first_activity'] and profile['last_activity']:
        profile['activity_span_days'] = (profile['last_activity'] - profile['first_activity']).days
    else:
        profile['activity_span_days'] = 0
    
    return profile


def calculate_sessions(user_events, session_gap_minutes=30):
    """Calculate number of sessions based on time gaps"""
    if len(user_events) < 2:
        return 1
    
    times = user_events['eventTime'].sort_values()
    gaps = times.diff()
    session_breaks = gaps > timedelta(minutes=session_gap_minutes)
    return session_breaks.sum() + 1


def extract_user_game_record(game_records_df, username):
    """
    Extract game record data for a specific user.
    
    Source: extracted_player_game_records.csv (from GEG-database.playersavedatas.json)
    """
    user_record = game_records_df[game_records_df['username'] == username]
    
    if len(user_record) == 0:
        return None
    
    # Player-save values are cumulative. If a player occurs in both exports,
    # use the latest Version-2 snapshot instead of summing or taking Version-1.
    if 'dataVersion' in user_record.columns and (user_record['dataVersion'] == 'Version-2').any():
        user_record = user_record[user_record['dataVersion'] == 'Version-2']
    record = user_record.iloc[-1].to_dict()
    return record


def extract_user_stage_progress(stage_data_df, username):
    """
    Extract stage-by-stage progress for a specific user.
    
    Source: extracted_player_stage_data.csv (from GEG-database.playersavedatas.json)
    """
    user_stages = stage_data_df[stage_data_df['username'] == username].copy()
    
    if len(user_stages) == 0:
        return None, None

    # Stage rows are also cumulative snapshots; retain the latest version for
    # overlapping users so the same stages are not counted twice.
    if 'dataVersion' in user_stages.columns and (user_stages['dataVersion'] == 'Version-2').any():
        user_stages = user_stages[user_stages['dataVersion'] == 'Version-2'].copy()
    
    # Summary statistics
    summary = {
        'total_stages': len(user_stages),
        'stages_unlocked': user_stages['isStageUnlock'].sum(),
        'stages_cleared': (user_stages['stageClearTimes'] > 0).sum(),
        'total_clear_times': user_stages['stageClearTimes'].sum(),
        'avg_best_score': user_stages[user_stages['bestPlayerScore'] > 0]['bestPlayerScore'].mean(),
        'avg_clear_time': user_stages[user_stages['bestPlayerClearTime'] > 0]['bestPlayerClearTime'].mean(),
        
        # By stage type
        'basic_stages_unlocked': user_stages[user_stages['stageType'] == 'Basic']['isStageUnlock'].sum(),
        'branch_stages_unlocked': user_stages[user_stages['stageType'] == 'Branch']['isStageUnlock'].sum(),
        'remote_stages_unlocked': user_stages[user_stages['stageType'] == 'Remote']['isStageUnlock'].sum(),
        
        # Tutorial vs Practice
        'tutorial_stages_cleared': len(user_stages[(user_stages['stageName'].str.contains('Tutorial')) & (user_stages['stageClearTimes'] > 0)]),
        'practice_stages_cleared': len(user_stages[(user_stages['stageName'].str.contains('Practice')) & (user_stages['stageClearTimes'] > 0)]),
    }
    
    # Detailed stage list
    stage_details = user_stages[['stageName', 'stageType', 'isStageUnlock', 
                                  'stageClearTimes', 'bestPlayerScore', 'bestPlayerClearTime']].to_dict('records')
    
    return summary, stage_details


def extract_user_leaderboard_rank(leaderboards_df, username):
    """
    Extract leaderboard rankings for a specific user.
    
    Source: extracted_leaderboards.csv (from GEG-database.globalleaderboarddatas.json)
    """
    # GameProgress leaderboard
    progress_lb = leaderboards_df[leaderboards_df['leaderBoardType'] == 'GameProgress'].copy()
    progress_lb['rank'] = progress_lb['gameProgress'].rank(ascending=False, method='min')
    
    # TotalScore leaderboard
    score_lb = leaderboards_df[leaderboards_df['leaderBoardType'] == 'TotalScore'].copy()
    score_lb['rank'] = score_lb['totalScore'].rank(ascending=False, method='min')
    
    rankings = {}
    
    # Get user's progress rank
    user_progress = progress_lb[progress_lb['playerName'] == username]
    if len(user_progress) > 0:
        rankings['progress_rank'] = int(user_progress['rank'].iloc[0])
        rankings['progress_value'] = user_progress['gameProgress'].iloc[0]
        rankings['progress_total_players'] = len(progress_lb)
        rankings['progress_percentile'] = (1 - rankings['progress_rank'] / rankings['progress_total_players']) * 100
    
    # Get user's score rank
    user_score = score_lb[score_lb['playerName'] == username]
    if len(user_score) > 0:
        rankings['score_rank'] = int(user_score['rank'].iloc[0])
        rankings['score_value'] = user_score['totalScore'].iloc[0]
        rankings['score_total_players'] = len(score_lb)
        rankings['score_percentile'] = (1 - rankings['score_rank'] / rankings['score_total_players']) * 100
    
    return rankings if rankings else None


def create_complete_user_profile(data_sources, username):
    """
    Create a complete profile for a user by combining all data sources.
    """
    profile = {
        'username': username,
        'data_sources_used': []
    }
    
    # 1. Event-based profile
    events_profile = extract_user_events_profile(data_sources['events']['data'], username)
    if events_profile:
        profile['events'] = events_profile
        profile['data_sources_used'].append('events (GEG-database.eventdatas.json)')
    
    # 2. Game record
    game_record = extract_user_game_record(data_sources['game_records']['data'], username)
    if game_record:
        profile['game_record'] = game_record
        profile['data_sources_used'].append('game_records (GEG-database.playersavedatas.json)')
    
    # 3. Stage progress
    stage_summary, stage_details = extract_user_stage_progress(data_sources['stage_data']['data'], username)
    if stage_summary:
        profile['stage_summary'] = stage_summary
        profile['stage_details'] = stage_details
        profile['data_sources_used'].append('stage_data (GEG-database.playersavedatas.json)')
    
    # 4. Leaderboard rankings
    rankings = extract_user_leaderboard_rank(data_sources['leaderboards']['data'], username)
    if rankings:
        profile['rankings'] = rankings
        profile['data_sources_used'].append('leaderboards (GEG-database.globalleaderboarddatas.json)')
    
    return profile


def extract_all_users_combined(data_sources):
    """
    Extract combined profiles for ALL users.
    Returns a DataFrame with one row per user.
    """
    print("\n" + "=" * 80)
    print("EXTRACTING PER-USER COMBINED DATA")
    print("=" * 80)
    
    # Get all unique usernames from all sources
    all_usernames = set()
    all_usernames.update(data_sources['events']['data']['player'].unique())
    all_usernames.update(data_sources['game_records']['data']['username'].unique())
    
    print(f"\nTotal unique users found: {len(all_usernames)}")
    
    all_profiles = []
    
    for username in sorted(all_usernames):
        profile = create_complete_user_profile(data_sources, username)
        
        # Flatten profile for DataFrame
        flat_profile = {'username': username}
        
        # From events
        if 'events' in profile:
            for key, value in profile['events'].items():
                if key != 'username':
                    flat_profile[f'event_{key}'] = value
        
        # From game records
        if 'game_record' in profile:
            for key, value in profile['game_record'].items():
                if key not in ['playerId', 'username']:
                    flat_profile[f'record_{key}'] = value
        
        # From stage summary
        if 'stage_summary' in profile:
            for key, value in profile['stage_summary'].items():
                flat_profile[f'stage_{key}'] = value
        
        # From rankings
        if 'rankings' in profile:
            for key, value in profile['rankings'].items():
                flat_profile[f'rank_{key}'] = value
        
        all_profiles.append(flat_profile)
    
    df = pd.DataFrame(all_profiles)
    print(f"Created combined profile for {len(df)} users")
    
    return df


def export_per_user_data(combined_df, output_dir):
    """Export combined per-user data"""
    output_path = f"{output_dir}/analysis_per_user_combined.csv"
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nExported: {output_path}")
    return output_path
