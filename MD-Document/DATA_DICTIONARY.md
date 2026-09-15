# Current Data Dictionary

The pipeline combines both folders under `Data` before analysis.

| Collection | Version-1 | Version-2 | Combined rows |
|---|---:|---:|---:|
| Events | 22,118 | 9,794 | 31,912 |
| Player saves | 50 | 64 | 114 |
| Player-stage records | 1,700 | 2,176 | 3,876 |
| Stage leaderboard entries | 741 | 267 | 1,008 |
| Global leaderboard entries | 637 | 326 | 963 |

Every combined extracted table contains `dataVersion`. Event histories are concatenated. Cumulative save/stage snapshots for the one overlapping username are resolved to Version-2 in the per-user profile to prevent double-counting.

The combined per-user table contains 115 distinct usernames. Clustering retains 104 after excluding 11 profiles with no observed activity. Cluster-specific transitions use the retained participants; sequence analysis uses timestamp-ordered events within username from the full event dataset. Analyses requiring positive play duration use 94 active player records.

See [column definitions](COLUMN_DICTIONARY.md), [analysis methods](PYTHON_ANALYSIS_RESEARCH_GUIDE.md), and [current results](ANALYSIS_RESULTS_GUIDE.md).
