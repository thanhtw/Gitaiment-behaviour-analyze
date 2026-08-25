# Current Data Dictionary

The pipeline combines both folders under `Data` before analysis.

| Collection | Version-1 | Version-2 | Combined rows |
|---|---:|---:|---:|
| Events | 22,118 | 9,512 | 31,630 |
| Player saves | 50 | 54 | 104 |
| Player-stage records | 1,700 | 1,836 | 3,536 |
| Stage leaderboard entries | 741 | 254 | 995 |
| Global leaderboard entries | 637 | 293 | 930 |

Every combined extracted table contains `dataVersion`. Event histories are concatenated. Cumulative save/stage snapshots for the one overlapping username are resolved to Version-2 in the per-user profile to prevent double-counting.

The clustering unit is one row per distinct username (`n=105`). Sequence analysis uses timestamp-ordered events within username (`n=31,630` events). Analyses requiring positive play duration use 84 active player records.
