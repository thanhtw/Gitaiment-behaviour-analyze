"""Regression checks for preprocessing, filtering, and cluster selection."""

import os
os.environ.setdefault('OMP_NUM_THREADS', '1')

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs

import cluster_profile_analysis as analysis


class ClusterAnalysisTests(unittest.TestCase):
    def test_main_limits_loaded_thread_pools(self):
        from threadpoolctl import threadpool_info
        def check_pools(data_dir):
            self.assertEqual(data_dir, 'example')
            self.assertTrue(all(pool['num_threads'] == 1 for pool in threadpool_info()))
        with patch.object(analysis, '_run_analysis', side_effect=check_pools) as run:
            analysis.main('example')
        run.assert_called_once_with('example')

    def test_undefined_ratios_stay_missing(self):
        fields = ['event_quests_added', 'event_quests_completed', 'event_correct_actions',
                  'event_failed_actions', 'record_totalPlayTime', 'record_totalStageScore',
                  'record_totalCommandExecuteTimes', 'event_hint_used_quests',
                  'event_answer_used_quests', 'event_leaderboard_checks', 'event_perfect_quests',
                  'record_totalTimesStageClear', 'record_totalGameProgress']
        raw = pd.DataFrame({name: [0.] for name in fields})
        raw['username'] = ['example']
        with patch.object(analysis.pd, 'read_csv', return_value=raw):
            frame = analysis.build_python_feature_table('unused.csv')
        self.assertTrue(frame[analysis.RATE_FEATURES + ['LearningEfficiency']].isna().all().all())

    def test_filter_records_reasons_and_preserves_input(self):
        rng = np.random.default_rng(42)
        frame = pd.DataFrame(rng.uniform(1, 2, (30, len(analysis.FEATURES))),
                             columns=analysis.FEATURES)
        frame[analysis.RATE_FEATURES] = rng.uniform(.3, .7, (30, 3))
        frame.insert(0, 'ID', [str(i) for i in range(len(frame))])
        frame.loc[0, analysis.FEATURES] = 0
        frame.loc[1, 'CommandsExecuted'] = -1
        frame.loc[2, [name for name in analysis.FEATURES if name not in analysis.RATE_FEATURES]] = 1e20
        original = frame.copy(deep=True)
        cleaned, audit, valid = analysis.filter_noise(frame)
        self.assertEqual(audit.loc[0, 'reason'], 'no_observed_activity')
        self.assertEqual(audit.loc[1, 'reason'], 'invalid_feature_value')
        self.assertEqual(audit.loc[2, 'reason'], 'local_outlier')
        self.assertEqual(len(cleaned) + (~audit.included).sum(), len(frame))
        self.assertIn(2, valid.index)
        pd.testing.assert_frame_equal(frame, original)

    def test_preprocessing_imputes_missing_and_keeps_raw_profiles(self):
        frame = pd.DataFrame({'CommandsExecuted': [0., 10., 100.],
                              'AccuracyRate': [0., np.nan, 1.]})
        names, raw, scaled = analysis.prepare_features(frame)
        self.assertEqual(names, ['CommandsExecuted', 'AccuracyRate'])
        self.assertEqual(raw[1, 1], .5)
        self.assertEqual(raw[2, 0], 100.)
        self.assertTrue(np.isfinite(scaled).all())
        np.testing.assert_allclose(scaled.mean(axis=0), 0, atol=1e-12)

    def test_clear_two_group_data_selects_two(self):
        values, _ = make_blobs(n_samples=40, centers=[[-5, -5], [5, 5]],
                               cluster_std=.2, random_state=42)
        with patch.object(analysis, 'N_INIT', 5):
            validity, recommendations = analysis.calculate_cluster_validity(values, max_k=4)
        self.assertEqual(recommendations['silhouette'], 2)
        self.assertEqual(recommendations['calinski_harabasz'], 2)
        self.assertEqual(set(recommendations), {'silhouette', 'calinski_harabasz'})
        self.assertTrue(validity.loc[validity.k.eq(2), 'eligible'].iloc[0])
        _, selected, agreement = analysis.select_cluster_count(validity)
        self.assertEqual(selected, 2)
        self.assertTrue(agreement)

    def test_disagreement_uses_both_scores(self):
        scores = pd.DataFrame({'k': [2, 3, 4], 'silhouette': [.5, .4, .3],
                               'calinski_harabasz': [10., 30., 20.], 'eligible': [True] * 3})
        ranked, selected, agreement = analysis.select_cluster_count(scores)
        self.assertEqual(selected, 3)
        self.assertFalse(agreement)
        self.assertEqual(ranked.combined_rank.tolist(), [4., 3., 5.])

    def test_ties_and_ineligible_candidates(self):
        scores = pd.DataFrame({'k': [4, 3, 2], 'silhouette': [.9, .5, .5],
                               'calinski_harabasz': [99., 30., 30.],
                               'eligible': [False, True, True]})
        _, selected, agreement = analysis.select_cluster_count(scores)
        self.assertEqual(selected, 2)
        self.assertTrue(agreement)

    def test_rank_tie_prefers_higher_silhouette(self):
        scores = pd.DataFrame({'k': [2, 3], 'silhouette': [.4, .5],
                               'calinski_harabasz': [30., 20.], 'eligible': [True, True]})
        _, selected, agreement = analysis.select_cluster_count(scores)
        self.assertEqual(selected, 3)
        self.assertFalse(agreement)


if __name__ == '__main__':
    unittest.main()
