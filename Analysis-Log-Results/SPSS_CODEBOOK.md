# SPSS Variable Codebook
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
