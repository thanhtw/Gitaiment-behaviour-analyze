"""Source extraction used by the retained analysis pipeline."""
import pandas as pd

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
