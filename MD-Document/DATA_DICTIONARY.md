
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
