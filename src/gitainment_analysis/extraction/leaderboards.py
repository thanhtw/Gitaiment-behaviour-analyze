"""Source extraction used by the retained analysis pipeline."""
import pandas as pd

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


def entries_to_dataframe(entries):
    """Convert entries list to pandas DataFrame"""
    df = pd.DataFrame(entries)
    return df
