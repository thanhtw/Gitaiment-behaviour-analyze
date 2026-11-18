"""Observed indicator preparation and SPSS metadata."""
import numpy as np
import pandas as pd
from ..analysis.clustering import FEATURE_DEFINITIONS, OUTCOME_DEFINITIONS

CLUSTERS = {1: 'Sustained Engagers', 2: 'Low Activity Learners', 3: 'Struggling Learners'}
# Original column, SPSS column, table label, category, scale multiplier.
INDICATORS = [
    ('CommandsExecuted', 'CommandsExecuted', 'Commands Executed', 'Command and Action Execution', 1),
    ('CorrectActions', 'CorrectActions', 'Correct Actions', 'Command and Action Execution', 1),
    ('FailedActions', 'FailedActions', 'Failed Actions', 'Command and Action Execution', 1),
    ('HintQuests', 'HintQuests', 'Hint Quests', 'Help-Seeking Behavior', 1),
    ('AnswerQuests', 'AnswerQuests', 'Answer Quests', 'Help-Seeking Behavior', 1),
    ('PlayDurationMinutes', 'PlayDurationMinutes', 'Play Duration (min)', 'Engagement Indicators', 1),
    ('LeaderboardInteractions', 'LeaderboardInteractions', 'Leaderboard Interactions', 'Engagement Indicators', 1),
    ('StageClearOccurrences', 'StageClearOccurrences', 'Stage Clear Occurrences', 'Learning Progression', 1),
    ('GameProgress', 'GameProgress', 'Game Progress (%)', 'Learning Progression', 1),
    ('TotalScore', 'TotalScore', 'Total Score', 'Learning Progression', 1),
    ('LearningEfficiency', 'LearningEfficiency', 'Learning Efficiency (score/min)', 'Derived Behavioral Variables', 1),
    ('AccuracyRate', 'AccuracyRatePct', 'Accuracy Rate (%)', 'Derived Behavioral Variables', 100),
    ('PerfectQuestRate', 'PerfectQuestRatePct', 'Perfect Quest Rate (%)', 'Derived Behavioral Variables', 100),
    ('HelpDependencyRatio', 'HelpDependencyPct', 'Help Dependency Ratio (%)', 'Derived Behavioral Variables', 100),
]


def prepare_export(assignments, cluster_labels=None):
    cluster_labels = CLUSTERS if cluster_labels is None else cluster_labels
    required = ['ID', 'Cluster'] + [row[0] for row in INDICATORS]
    if not set(required).issubset(assignments.columns):
        raise ValueError('Missing columns: ' + ', '.join(sorted(set(required)-set(assignments.columns))))
    if assignments.ID.isna().any() or assignments.ID.astype(str).str.strip().eq('').any() or assignments.ID.duplicated().any():
        raise ValueError('Learner IDs must be nonempty and unique')
    if set(assignments.Cluster.unique()) != set(cluster_labels):
        raise ValueError('Profile labels assume the current clusters 1, 2 and 3; provide explicit labels after refitting')
    data = assignments[['ID', 'Cluster']].copy()
    # SAV fixed-width strings discard trailing padding; normalize consistently.
    data['ID'] = data.ID.astype(str).str.rstrip()
    if data.ID.duplicated().any():
        raise ValueError('Removing trailing ID whitespace would merge learner identifiers')
    data['ClusterLabel'] = data.Cluster.map(cluster_labels)
    dictionary = []
    definitions = {**FEATURE_DEFINITIONS, **OUTCOME_DEFINITIONS}
    for source, target, label, category, multiplier in INDICATORS:
        values = pd.to_numeric(assignments[source], errors='raise')
        if np.isinf(values).any():
            raise ValueError(f'Infinite value in {source}')
        data[target] = values * multiplier
        dictionary.append(dict(variable=target, label=label, category=category, source_variable=source,
                               multiplier=multiplier, definition=definitions[source],
                               missing_values='Blank in CSV/Excel; system-missing in SAV. Not zero-filled or imputed.'))
    return data, pd.DataFrame(dictionary)


