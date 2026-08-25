"""
GiTaiment Game Analytics - Per-User Data Extraction & Analysis
================================================================
This script extracts and combines data BY USER from all data sources,
with clear documentation of where each metric originates.

DATA SOURCES EXPLANATION:
=========================
1. GEG-database.eventdatas.json → extracted_events.csv
   - Contains: Real-time player actions (login, stage start, quest completion, etc.)
   - Granularity: Individual action events with timestamps
   - Use: Behavioral sequence analysis, session tracking
   
2. GEG-database.playersavedatas.json → extracted_player_game_records.csv
   - Contains: Cumulative player statistics saved in the game
   - Granularity: One record per player (aggregated totals)
   - Use: Overall performance metrics
   
3. GEG-database.playersavedatas.json → extracted_player_stage_data.csv
   - Contains: Per-stage progress for each player
   - Granularity: One record per player per stage (34 stages × players)
   - Use: Learning progression analysis
   
4. GEG-database.globalleaderboarddatas.json → extracted_leaderboards.csv
   - Contains: Global rankings by different criteria
   - Granularity: Leaderboard snapshots
   - Use: Competitive performance benchmarking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DATA LOADING WITH SOURCE DOCUMENTATION
# =============================================================================

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

# =============================================================================
# PER-USER DATA EXTRACTION
# =============================================================================

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
    
    record = user_record.iloc[0].to_dict()
    return record

def extract_user_stage_progress(stage_data_df, username):
    """
    Extract stage-by-stage progress for a specific user.
    
    Source: extracted_player_stage_data.csv (from GEG-database.playersavedatas.json)
    """
    user_stages = stage_data_df[stage_data_df['username'] == username].copy()
    
    if len(user_stages) == 0:
        return None, None
    
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

# =============================================================================
# COMBINED USER PROFILE
# =============================================================================

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

# =============================================================================
# EXTRACT ALL USERS
# =============================================================================

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

# =============================================================================
# PRINT USER PROFILE (DETAILED)
# =============================================================================

def print_user_profile(profile):
    """Print a detailed user profile"""
    print("\n" + "=" * 80)
    print(f"USER PROFILE: {profile['username']}")
    print("=" * 80)
    
    print(f"\nData sources used: {len(profile['data_sources_used'])}")
    for source in profile['data_sources_used']:
        print(f"  - {source}")
    
    # Events-based data
    if 'events' in profile:
        print("\n--- BEHAVIORAL DATA (from Event Logs) ---")
        e = profile['events']
        print(f"  Total Events: {e['total_events']}")
        print(f"  First Activity: {e['first_activity']}")
        print(f"  Last Activity: {e['last_activity']}")
        print(f"  Activity Span: {e['activity_span_days']} days")
        print(f"  Total Logins: {e['total_logins']}")
        print(f"  Total Sessions: {e['total_sessions']}")
        print(f"  Stages Started: {e['stages_started']}")
        print(f"  Quests Added: {e['quests_added']}")
        print(f"  Quests Completed: {e['quests_completed']}")
        print(f"    - Perfect: {e['perfect_quests']}")
        print(f"    - Good: {e['good_quests']}")
        print(f"    - With Hint: {e['hint_used_quests']}")
        print(f"    - With Answer: {e['answer_used_quests']}")
        print(f"  Game Manual Opens: {e['game_manual_opens']}")
        print(f"  Correct Actions: {e['correct_actions']}")
        print(f"  Failed Actions: {e['failed_actions']}")
        print(f"  Leaderboard Checks: {e['leaderboard_checks']}")
        print(f"  Window Opens: {e['window_opens']}")
        print(f"  Last Conversations: {e['last_conversations']}")
    
    # Game record data
    if 'game_record' in profile:
        print("\n--- GAME RECORD (from Player Save Data) ---")
        r = profile['game_record']
        print(f"  Total Stars: {r.get('totalStarCount', 'N/A')}")
        print(f"  Total Score: {r.get('totalStageScore', 'N/A')}")
        print(f"  Game Progress: {r.get('totalGameProgress', 'N/A')}%")
        print(f"  Total Play Time: {r.get('totalPlayTime', 0)} seconds ({r.get('totalPlayTime', 0)/3600:.2f} hours)")
        print(f"  Stages Cleared: {r.get('totalTimesStageClear', 'N/A')}")
        print(f"  Commands Executed: {r.get('totalCommandExecuteTimes', 'N/A')}")
        print(f"  Quest Clears - Perfect: {r.get('totalTimesQuestClearPerfect', 'N/A')}")
        print(f"  Quest Clears - Good: {r.get('totalTimesQuestClearGood', 'N/A')}")
        print(f"  Quest Clears - Hint: {r.get('totalTimesQuestClearHint', 'N/A')}")
        print(f"  Quest Clears - Answer: {r.get('totalTimesQuestClearAnswer', 'N/A')}")
    
    # Stage progress
    if 'stage_summary' in profile:
        print("\n--- STAGE PROGRESS (from Player Save Data) ---")
        s = profile['stage_summary']
        print(f"  Stages Unlocked: {s['stages_unlocked']} / {s['total_stages']}")
        print(f"  Stages Cleared: {s['stages_cleared']}")
        print(f"  Tutorial Cleared: {s['tutorial_stages_cleared']}")
        print(f"  Practice Cleared: {s['practice_stages_cleared']}")
        print(f"  By Type:")
        print(f"    - Basic: {s['basic_stages_unlocked']} unlocked")
        print(f"    - Branch: {s['branch_stages_unlocked']} unlocked")
        print(f"    - Remote: {s['remote_stages_unlocked']} unlocked")
    
    # Rankings
    if 'rankings' in profile:
        print("\n--- LEADERBOARD RANKINGS (from Global Leaderboard) ---")
        r = profile['rankings']
        if 'progress_rank' in r:
            print(f"  Progress Rank: #{r['progress_rank']} of {r['progress_total_players']} (Top {r['progress_percentile']:.1f}%)")
        if 'score_rank' in r:
            print(f"  Score Rank: #{r['score_rank']} of {r['score_total_players']} (Top {r['score_percentile']:.1f}%)")

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_per_user_data(combined_df, output_dir):
    """Export combined per-user data"""
    output_path = f"{output_dir}/analysis_per_user_combined.csv"
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nExported: {output_path}")
    return output_path

def export_data_dictionary(output_dir):
    """Export data dictionary explaining all fields and sources"""
    
    data_dict = """
# GiTaiment Data Dictionary
# =========================
# This document explains all data fields and their sources.

## DATA SOURCES
---------------

### 1. GEG-database.eventdatas.json
- **Description**: Real-time event logs capturing every player action
- **Granularity**: One record per action
- **Key Fields**: player, eventName, eventDetail, gameScene, eventTime

### 2. GEG-database.playersavedatas.json  
- **Description**: Player save data containing cumulative statistics
- **Granularity**: One record per player (for game records) + one per stage per player (for stage data)
- **Key Fields**: 
  - gameRecordData: totalStarCount, totalStageScore, totalGameProgress, etc.
  - stageData: stageName, isStageUnlock, stageClearTimes, etc.

### 3. GEG-database.globalleaderboarddatas.json
- **Description**: Global leaderboard rankings
- **Granularity**: Leaderboard snapshots by type
- **Key Fields**: leaderBoardType, playerName, gameProgress, totalScore, playTime


## FIELD DEFINITIONS
--------------------

### Event-Based Fields (from eventdatas.json)
| Field | Description | How Calculated |
|-------|-------------|----------------|
| event_total_events | Total number of action events | Count of all events for user |
| event_total_logins | Number of login events | Count where eventName='Login' |
| event_total_sessions | Number of play sessions | Login gaps > 30 minutes |
| event_stages_started | Stages attempted | Count where eventName='Start Stage' |
| event_quests_added | New quests started | Count where eventName='Add New Quest' |
| event_quests_completed | Total quests completed | Count where eventName='Complete Quest' |
| event_perfect_quests | Quests with perfect score | Count where eventDetail contains 'Perfect' |
| event_good_quests | Quests with good score | Count where eventDetail contains 'Good' |
| event_hint_used_quests | Quests using hints | Count where eventDetail contains 'Hint' |
| event_answer_used_quests | Quests using answer | Count where eventDetail contains 'Answer' |
| event_game_manual_opens | Times manual was opened | Count where eventName='Read GameManual' |
| event_correct_actions | Correct in-game actions | Count where eventName='Correct Action' |
| event_failed_actions | Failed in-game actions | Count where eventName='Failed Action' |
| event_leaderboard_checks | Times leaderboard viewed | Count where eventName='Check GlobalLeaderBoard' |
| event_window_opens | Window open events | Count where eventName='Open Window' |
| event_last_conversations | Last conversation events | Count where eventName='Last Conversation' |

### Game Record Fields (from playersavedatas.json → gameRecordData)
| Field | Description | Direct from JSON |
|-------|-------------|------------------|
| record_totalStarCount | Total stars earned | Yes |
| record_totalStageScore | Cumulative score | Yes |
| record_totalGameProgress | Overall progress (%) | Yes |
| record_totalPlayTime | Total time played (seconds) | Yes |
| record_totalTimesStageClear | Number of stages cleared | Yes |
| record_totalTimesUsedGameManual | Manual usage count | Yes |
| record_totalCommandExecuteTimes | Git commands executed | Yes |
| record_totalTimesQuestClearPerfect | Perfect quest completions | Yes |
| record_totalTimesQuestClearGood | Good quest completions | Yes |
| record_totalTimesQuestClearHint | Quest completions with hints | Yes |
| record_totalTimesQuestClearAnswer | Quest completions with answers | Yes |

### Stage Progress Fields (from playersavedatas.json → stageData)
| Field | Description | How Calculated |
|-------|-------------|----------------|
| stage_total_stages | Total stages in game | Count of stage records |
| stage_stages_unlocked | Stages unlocked by user | Sum where isStageUnlock=True |
| stage_stages_cleared | Stages completed at least once | Count where stageClearTimes > 0 |
| stage_basic_stages_unlocked | Basic type stages unlocked | Filter by stageType='Basic' |
| stage_branch_stages_unlocked | Branch type stages unlocked | Filter by stageType='Branch' |
| stage_remote_stages_unlocked | Remote type stages unlocked | Filter by stageType='Remote' |

### Ranking Fields (from globalleaderboarddatas.json)
| Field | Description | How Calculated |
|-------|-------------|----------------|
| rank_progress_rank | Rank by game progress | Rank in GameProgress leaderboard |
| rank_progress_percentile | Percentile ranking | (1 - rank/total) × 100 |
| rank_score_rank | Rank by total score | Rank in TotalScore leaderboard |
| rank_score_percentile | Percentile ranking | (1 - rank/total) × 100 |


## DATA LINEAGE DIAGRAM
-----------------------

```
GEG-database.eventdatas.json
    │
    └──► extracted_events.csv
            │
            └──► event_* fields (behavioral data)

GEG-database.playersavedatas.json
    │
    ├──► extracted_player_game_records.csv
    │       │
    │       └──► record_* fields (cumulative stats)
    │
    └──► extracted_player_stage_data.csv
            │
            └──► stage_* fields (progression data)

GEG-database.globalleaderboarddatas.json
    │
    └──► extracted_leaderboards.csv
            │
            └──► rank_* fields (competitive rankings)
```


## RESEARCH PAPER CITATION
--------------------------

When using this data in your research paper, cite as:

"Player behavior data was collected from the GiTaiment game database, 
consisting of: (1) event logs capturing 22,120 individual player actions 
from 47 active users, (2) player save data containing cumulative game 
statistics and per-stage progress across 34 stages, and (3) global 
leaderboard rankings for competitive benchmarking."
"""
    
    output_path = f"{output_dir}/DATA_DICTIONARY.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data_dict)
    print(f"Exported: {output_path}")
    return output_path

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Data directory
    data_dir = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData"
    
    # Load all data sources with documentation
    data_sources = load_all_data(data_dir)
    
    # Extract combined per-user data
    combined_df = extract_all_users_combined(data_sources)
    
    # Export combined data
    export_per_user_data(combined_df, data_dir)
    
    # Export data dictionary
    export_data_dictionary(data_dir)
    
    # Show sample user profiles
    print("\n" + "=" * 80)
    print("SAMPLE USER PROFILES")
    print("=" * 80)
    
    # Get list of users with most data
    sample_users = ['D1018508', 'Loe', 'ccc']
    
    for username in sample_users:
        if username in data_sources['game_records']['data']['username'].values:
            profile = create_complete_user_profile(data_sources, username)
            print_user_profile(profile)
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("COMBINED DATA SUMMARY")
    print("=" * 80)
    print(f"\nTotal columns in combined dataset: {len(combined_df.columns)}")
    print(f"Total users: {len(combined_df)}")
    print("\nColumn categories:")
    print(f"  - Event-based (event_*): {len([c for c in combined_df.columns if c.startswith('event_')])}")
    print(f"  - Game record (record_*): {len([c for c in combined_df.columns if c.startswith('record_')])}")
    print(f"  - Stage progress (stage_*): {len([c for c in combined_df.columns if c.startswith('stage_')])}")
    print(f"  - Rankings (rank_*): {len([c for c in combined_df.columns if c.startswith('rank_')])}")
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE!")
    print("=" * 80)
