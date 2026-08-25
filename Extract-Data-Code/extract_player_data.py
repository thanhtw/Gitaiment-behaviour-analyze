import json
import pandas as pd
from datetime import datetime

# Load the JSON data
def load_player_data(filepath):
    """Load player save data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Extract player game records (summary data)
def extract_game_records(data):
    """Extract game record summary for each player"""
    records = []
    for player in data:
        player_id = player['_id']['$oid']
        username = player['username']
        
        # Get game record data
        save_data = player.get('saveData', {})
        game_record = save_data.get('gameRecordData', {})
        
        record = {
            'playerId': player_id,
            'username': username,
            'totalStarCount': game_record.get('totalStarCount', 0),
            'totalStageScore': game_record.get('totalStageScore', 0),
            'totalGameProgress': game_record.get('totalGameProgress', 0),
            'totalPlayTime': game_record.get('totalPlayTime', 0),
            'totalTimesStageClear': game_record.get('totalTimesStageClear', 0),
            'totalTimesUsedGameManual': game_record.get('totalTimesUsedGameManual', 0),
            'totalCommandExecuteTimes': game_record.get('totalCommandExecuteTimes', 0),
            'totalTimesQuestClearPerfect': game_record.get('totalTimesQuestClearPerfect', 0),
            'totalTimesQuestClearGood': game_record.get('totalTimesQuestClearGood', 0),
            'totalTimesQuestClearHint': game_record.get('totalTimesQuestClearHint', 0),
            'totalTimesQuestClearAnswer': game_record.get('totalTimesQuestClearAnswer', 0)
        }
        records.append(record)
    
    return pd.DataFrame(records)

# Extract stage data for each player
def extract_stage_data(data):
    """Extract detailed stage progress for each player"""
    stages = []
    for player in data:
        player_id = player['_id']['$oid']
        username = player['username']
        
        save_data = player.get('saveData', {})
        stage_data = save_data.get('stageData', [])
        
        for stage in stage_data:
            stage_entry = {
                'playerId': player_id,
                'username': username,
                'stageName': stage.get('stageName', ''),
                'stageType': stage.get('stageType', ''),
                'isStageUnlock': stage.get('isStageUnlock', False),
                'stageClearTimes': stage.get('stageClearTimes', 0),
            }
            
            # Extract best leaderboard entry for this stage
            leaderboard = stage.get('stageLeaderboardData', [])
            if leaderboard:
                # Find the best score entry (non-empty player)
                best_entry = None
                for entry in leaderboard:
                    if entry.get('playerName') and entry.get('playerScore', 0) > 0:
                        if best_entry is None or entry.get('playerScore', 0) > best_entry.get('playerScore', 0):
                            best_entry = entry
                
                if best_entry:
                    stage_entry['bestPlayerStar'] = best_entry.get('playerStar', 0)
                    stage_entry['bestPlayerScore'] = best_entry.get('playerScore', 0)
                    stage_entry['bestPlayerClearTime'] = best_entry.get('playerClearTime', 0)
                else:
                    stage_entry['bestPlayerStar'] = 0
                    stage_entry['bestPlayerScore'] = 0
                    stage_entry['bestPlayerClearTime'] = 0
            
            stages.append(stage_entry)
    
    return pd.DataFrame(stages)

# Extract stage leaderboard data
def extract_stage_leaderboards(data):
    """Extract all stage leaderboard entries"""
    leaderboards = []
    for player in data:
        player_id = player['_id']['$oid']
        username = player['username']
        
        save_data = player.get('saveData', {})
        stage_data = save_data.get('stageData', [])
        
        for stage in stage_data:
            stage_name = stage.get('stageName', '')
            stage_type = stage.get('stageType', '')
            leaderboard = stage.get('stageLeaderboardData', [])
            
            for rank, entry in enumerate(leaderboard, 1):
                if entry.get('playerName'):  # Only include non-empty entries
                    lb_entry = {
                        'ownerPlayerId': player_id,
                        'ownerUsername': username,
                        'stageName': stage_name,
                        'stageType': stage_type,
                        'rank': rank,
                        'playerName': entry.get('playerName', ''),
                        'playerStar': entry.get('playerStar', 0),
                        'playerScore': entry.get('playerScore', 0),
                        'playerClearTime': entry.get('playerClearTime', 0)
                    }
                    leaderboards.append(lb_entry)
    
    return pd.DataFrame(leaderboards)

# Get unique stage names
def get_stage_names(data):
    """Get all unique stage names"""
    stages = set()
    for player in data:
        save_data = player.get('saveData', {})
        stage_data = save_data.get('stageData', [])
        for stage in stage_data:
            stages.add(stage.get('stageName', ''))
    return sorted(list(stages))

# Get stage types
def get_stage_types(data):
    """Get all unique stage types"""
    types = set()
    for player in data:
        save_data = player.get('saveData', {})
        stage_data = save_data.get('stageData', [])
        for stage in stage_data:
            types.add(stage.get('stageType', ''))
    return sorted(list(types))

# Analysis functions
def get_summary_statistics(game_records_df, stage_df):
    """Get summary statistics of the player data"""
    print("=" * 70)
    print("PLAYER SAVE DATA SUMMARY")
    print("=" * 70)
    print(f"\nTotal number of players: {len(game_records_df)}")
    
    print("\n" + "-" * 70)
    print("GAME RECORD STATISTICS:")
    print("-" * 70)
    
    stats_columns = ['totalStarCount', 'totalStageScore', 'totalGameProgress', 
                     'totalPlayTime', 'totalTimesStageClear']
    
    for col in stats_columns:
        if col in game_records_df.columns:
            print(f"\n{col}:")
            print(f"  Mean: {game_records_df[col].mean():.2f}")
            print(f"  Median: {game_records_df[col].median():.2f}")
            print(f"  Max: {game_records_df[col].max()}")
            print(f"  Min: {game_records_df[col].min()}")
    
    print("\n" + "-" * 70)
    print("TOP 10 PLAYERS BY TOTAL SCORE:")
    print("-" * 70)
    top_scores = game_records_df.nlargest(10, 'totalStageScore')[
        ['username', 'totalStageScore', 'totalGameProgress', 'totalPlayTime']
    ]
    print(top_scores.to_string(index=False))
    
    print("\n" + "-" * 70)
    print("TOP 10 PLAYERS BY GAME PROGRESS:")
    print("-" * 70)
    top_progress = game_records_df.nlargest(10, 'totalGameProgress')[
        ['username', 'totalGameProgress', 'totalStageScore', 'totalPlayTime']
    ]
    print(top_progress.to_string(index=False))
    
    print("\n" + "-" * 70)
    print("QUEST COMPLETION STATISTICS:")
    print("-" * 70)
    quest_cols = ['totalTimesQuestClearPerfect', 'totalTimesQuestClearGood', 
                  'totalTimesQuestClearHint', 'totalTimesQuestClearAnswer']
    quest_totals = game_records_df[quest_cols].sum()
    for col in quest_cols:
        print(f"  {col}: {int(quest_totals[col])}")

def analyze_stage_progress(stage_df):
    """Analyze stage completion rates"""
    print("\n" + "=" * 70)
    print("STAGE PROGRESS ANALYSIS")
    print("=" * 70)
    
    # Group by stage name
    stage_stats = stage_df.groupby('stageName').agg({
        'isStageUnlock': 'sum',
        'stageClearTimes': 'sum',
        'bestPlayerScore': 'mean'
    }).reset_index()
    
    stage_stats.columns = ['stageName', 'timesUnlocked', 'totalClears', 'avgBestScore']
    stage_stats = stage_stats.sort_values('timesUnlocked', ascending=False)
    
    print("\nStage Unlock and Clear Statistics:")
    print(stage_stats.head(20).to_string(index=False))
    
    # Stage type analysis
    print("\n" + "-" * 70)
    print("STAGE TYPE DISTRIBUTION:")
    print("-" * 70)
    type_stats = stage_df.groupby('stageType').agg({
        'isStageUnlock': 'sum',
        'stageClearTimes': 'sum'
    }).reset_index()
    type_stats.columns = ['stageType', 'timesUnlocked', 'totalClears']
    print(type_stats.to_string(index=False))
    
    return stage_stats

def export_to_csv(df, output_path, description=""):
    """Export DataFrame to CSV"""
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"{description} exported to {output_path}")

# Main execution
if __name__ == "__main__":
    # File path
    filepath = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData\GEG-database.playersavedatas.json"
    output_dir = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData"
    
    # Load data
    print("Loading data...")
    data = load_player_data(filepath)
    print(f"Loaded {len(data)} player records")
    
    # Get stage info
    stage_names = get_stage_names(data)
    stage_types = get_stage_types(data)
    print(f"\nUnique stages: {len(stage_names)}")
    print(f"Stage types: {stage_types}")
    
    # Extract game records
    print("\nExtracting game records...")
    game_records_df = extract_game_records(data)
    
    # Extract stage data
    print("Extracting stage data...")
    stage_df = extract_stage_data(data)
    
    # Extract stage leaderboards
    print("Extracting stage leaderboards...")
    leaderboard_df = extract_stage_leaderboards(data)
    
    # Display summary statistics
    get_summary_statistics(game_records_df, stage_df)
    analyze_stage_progress(stage_df)
    
    # Show sample data
    print("\n" + "=" * 70)
    print("SAMPLE GAME RECORDS (First 10 rows):")
    print("=" * 70)
    print(game_records_df.head(10).to_string())
    
    # Export to CSV files
    print("\n" + "=" * 70)
    print("EXPORTING DATA...")
    print("=" * 70)
    
    export_to_csv(game_records_df, 
                  f"{output_dir}/extracted_player_game_records.csv",
                  "Player game records")
    
    export_to_csv(stage_df,
                  f"{output_dir}/extracted_player_stage_data.csv",
                  "Player stage data")
    
    export_to_csv(leaderboard_df,
                  f"{output_dir}/extracted_stage_leaderboards.csv",
                  "Stage leaderboards")
    
    print("\nExtraction complete!")
