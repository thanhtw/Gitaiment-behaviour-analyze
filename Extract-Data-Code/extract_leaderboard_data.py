import json
import pandas as pd
from datetime import datetime

# Load the JSON data
def load_leaderboard_data(filepath):
    """Load leaderboard data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Extract and flatten the data
def extract_leaderboards(data):
    """Extract all leaderboard entries into a flat structure"""
    all_entries = []
    leaderboard_summary = {}
    
    for board in data:
        board_id = board.get('_id', {}).get('$oid', '')
        board_type = board.get('leaderBoardType', 'Unknown')
        # Flattened CSV rows for stages with no scores contain no
        # leaderBoardData columns at all. Treat those as empty boards.
        board_data = board.get('leaderBoardData') or []
        
        # Track summary
        if board_type not in leaderboard_summary:
            leaderboard_summary[board_type] = 0
        leaderboard_summary[board_type] += len(board_data)
        
        # Extract each player entry
        for entry in board_data:
            flat_entry = {
                'boardId': board_id,
                'leaderBoardType': board_type,
                'playerName': entry.get('playerName', ''),
                'playTime': entry.get('playTime', 0),
            }
            
            # Add type-specific fields
            if 'gameProgress' in entry:
                flat_entry['gameProgress'] = entry['gameProgress']
            if 'totalScore' in entry:
                flat_entry['totalScore'] = entry['totalScore']
            if 'stageScore' in entry:
                flat_entry['stageScore'] = entry['stageScore']
            if 'stageName' in entry or 'stageName' in board:
                flat_entry['stageName'] = entry.get('stageName', board.get('stageName', ''))
            
            all_entries.append(flat_entry)
    
    return all_entries, leaderboard_summary

# Convert to DataFrame
def entries_to_dataframe(entries):
    """Convert entries list to pandas DataFrame"""
    df = pd.DataFrame(entries)
    return df

# Extract by leaderboard type
def extract_by_type(data, board_type):
    """Extract data for a specific leaderboard type"""
    entries = []
    for board in data:
        if board['leaderBoardType'] == board_type:
            board_id = board.get('_id', {}).get('$oid', '')
            for entry in board.get('leaderBoardData') or []:
                entry_copy = entry.copy()
                entry_copy['boardId'] = board_id
                entries.append(entry_copy)
    return pd.DataFrame(entries)

# Get unique leaderboard types
def get_leaderboard_types(data):
    """Get all unique leaderboard types"""
    return list(set(board['leaderBoardType'] for board in data))

# Analysis functions
def get_summary_statistics(df, leaderboard_summary):
    """Get summary statistics of the leaderboard data"""
    print("=" * 60)
    print("GLOBAL LEADERBOARD DATA SUMMARY")
    print("=" * 60)
    print(f"\nTotal number of entries: {len(df)}")
    print(f"Unique players: {df['playerName'].nunique()}")
    print(f"Unique leaderboard types: {df['leaderBoardType'].nunique()}")
    
    print("\n" + "-" * 60)
    print("LEADERBOARD TYPES AND ENTRY COUNTS:")
    print("-" * 60)
    for board_type, count in leaderboard_summary.items():
        print(f"  {board_type}: {count} entries")
    
    print("\n" + "-" * 60)
    print("TOP 10 PLAYERS BY PLAY TIME:")
    print("-" * 60)
    if 'playTime' in df.columns:
        top_playtime = df.groupby('playerName')['playTime'].max().sort_values(ascending=False).head(10)
        for player, time in top_playtime.items():
            hours = time // 3600
            minutes = (time % 3600) // 60
            seconds = time % 60
            print(f"  {player}: {time} seconds ({hours}h {minutes}m {seconds}s)")

def analyze_game_progress(df):
    """Analyze game progress leaderboard"""
    progress_df = df[df['leaderBoardType'] == 'GameProgress'].copy()
    if len(progress_df) == 0:
        print("No GameProgress data found")
        return None
    
    print("\n" + "=" * 60)
    print("GAME PROGRESS ANALYSIS")
    print("=" * 60)
    print(f"Total entries: {len(progress_df)}")
    print(f"Unique players: {progress_df['playerName'].nunique()}")
    
    if 'gameProgress' in progress_df.columns:
        print(f"\nProgress Statistics:")
        print(f"  Mean progress: {progress_df['gameProgress'].mean():.2f}%")
        print(f"  Median progress: {progress_df['gameProgress'].median():.2f}%")
        print(f"  Max progress: {progress_df['gameProgress'].max()}%")
        print(f"  Min progress: {progress_df['gameProgress'].min()}%")
        
        print("\nTop 10 Players by Progress:")
        top_progress = progress_df.nlargest(10, 'gameProgress')[['playerName', 'gameProgress', 'playTime']]
        print(top_progress.to_string(index=False))
    
    return progress_df

def analyze_total_score(df):
    """Analyze total score leaderboard"""
    score_df = df[df['leaderBoardType'] == 'TotalScore'].copy()
    if len(score_df) == 0:
        print("No TotalScore data found")
        return None
    
    print("\n" + "=" * 60)
    print("TOTAL SCORE ANALYSIS")
    print("=" * 60)
    print(f"Total entries: {len(score_df)}")
    print(f"Unique players: {score_df['playerName'].nunique()}")
    
    if 'totalScore' in score_df.columns:
        print(f"\nScore Statistics:")
        print(f"  Mean score: {score_df['totalScore'].mean():.2f}")
        print(f"  Median score: {score_df['totalScore'].median():.2f}")
        print(f"  Max score: {score_df['totalScore'].max()}")
        print(f"  Min score: {score_df['totalScore'].min()}")
        
        print("\nTop 10 Players by Score:")
        top_scores = score_df.nlargest(10, 'totalScore')[['playerName', 'totalScore', 'playTime']]
        print(top_scores.to_string(index=False))
    
    return score_df

def export_to_csv(df, output_path):
    """Export DataFrame to CSV"""
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nData exported to {output_path}")

def export_by_type(data, output_dir):
    """Export each leaderboard type to separate CSV files"""
    board_types = get_leaderboard_types(data)
    for board_type in board_types:
        type_df = extract_by_type(data, board_type)
        safe_name = board_type.replace(' ', '_').replace('/', '_')
        output_path = f"{output_dir}/leaderboard_{safe_name}.csv"
        type_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Exported {board_type} to {output_path}")

# Main execution
if __name__ == "__main__":
    # File path
    filepath = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData\GEG-database.globalleaderboarddatas.json"
    
    # Load data
    print("Loading data...")
    data = load_leaderboard_data(filepath)
    print(f"Loaded {len(data)} leaderboard records")
    
    # Get leaderboard types
    board_types = get_leaderboard_types(data)
    print(f"\nLeaderboard types found: {board_types}")
    
    # Extract all entries
    entries, leaderboard_summary = extract_leaderboards(data)
    
    # Convert to DataFrame
    df = entries_to_dataframe(entries)
    
    # Display summary statistics
    get_summary_statistics(df, leaderboard_summary)
    
    # Analyze specific leaderboards
    analyze_game_progress(df)
    analyze_total_score(df)
    
    # Show sample data
    print("\n" + "=" * 60)
    print("SAMPLE DATA (First 10 rows):")
    print("=" * 60)
    print(df.head(10).to_string())
    
    # Export all data to single CSV
    output_csv = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData\extracted_leaderboards.csv"
    export_to_csv(df, output_csv)
    
    # Export by type (optional - uncomment to use)
    # output_dir = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData"
    # export_by_type(data, output_dir)
