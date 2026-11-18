"""Behavioral invariants of the single direct K-means workflow."""
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

from gitainment_analysis.analysis import clustering
from gitainment_analysis.analysis.transitions import prepare_events,transition_pairs
from gitainment_analysis.reporting.spss_data import prepare_export
from gitainment_analysis.reporting.table9 import FEATURES as TABLE_CODES


class WorkflowTests(unittest.TestCase):
    def observations(self):
        rng=np.random.default_rng(42)
        data=pd.DataFrame(rng.uniform(1,10,(18,14)),columns=clustering.FEATURES+clustering.OUTCOMES)
        for rate in clustering.RATE_FEATURES:data[rate]/=10
        data.insert(0,'ID',[f'p{i:02}' for i in range(len(data))])
        return data

    def test_clustering_uses_eleven_features_without_pca(self):
        data=self.observations()
        with patch.object(clustering,'PCA',side_effect=AssertionError('PCA cannot precede K-means')):
            names,imputed,scaled=clustering.prepare_features(data)
            validity,_=clustering.calculate_cluster_validity(scaled,max_k=3)
        self.assertEqual(names,clustering.FEATURES)
        self.assertEqual(scaled.shape,(18,11))
        changed=data.copy();changed[clustering.OUTCOMES]=1e6
        np.testing.assert_allclose(scaled,clustering.prepare_features(changed)[2])
        self.assertEqual(set(validity.k),{2,3})

    def test_missing_observations_are_not_imputed_into_anova(self):
        data=self.observations();data.loc[0,'LearningEfficiency']=np.nan
        names,imputed,scaled=clustering.prepare_features(data)
        self.assertTrue(np.isfinite(imputed).all())
        profiles,_,comparisons=clustering.profile_clusters(data,names,scaled,np.repeat([1,2,3],6))
        first=profiles.set_index('Cluster').loc[1]
        self.assertEqual(first.LearningEfficiency_count,5)
        self.assertAlmostEqual(first.LearningEfficiency_std,data.loc[1:5,'LearningEfficiency'].std(ddof=1))
        self.assertEqual(comparisons.set_index('feature').loc['LearningEfficiency','n_observed'],17)

    def test_export_retains_observed_missing_values_and_percent_units(self):
        data=self.observations();data.insert(1,'Cluster',np.repeat([1,2,3],6));data.loc[0,'LearningEfficiency']=np.nan
        exported,dictionary=prepare_export(data)
        self.assertTrue(pd.isna(exported.loc[0,'LearningEfficiency']))
        np.testing.assert_allclose(exported.AccuracyRatePct,data.AccuracyRate*100)
        self.assertEqual(len(dictionary),14)
        self.assertEqual([x[0] for x in TABLE_CODES],[f'F{i}' for i in range(1,15)])
        self.assertEqual(TABLE_CODES[7][1],'LearningEfficiency')
        self.assertEqual(TABLE_CODES[13][1],'TotalScore')

    def test_transition_pairs_never_cross_learners(self):
        events=pd.DataFrame({'player':['a','a','b'],'eventName':['Failed Action','Use Hint','Correct Action'],
                             'eventTime':['2024-01-01T00:00:00Z','2024-01-01T00:01:00Z','2024-01-01T00:02:00Z']})
        assignments=pd.DataFrame({'ID':['a','b'],'Cluster':[1,1]})
        pairs=transition_pairs(prepare_events(events,assignments))
        self.assertEqual(len(pairs),1)
        self.assertEqual(pairs.iloc[0].state,'F')
        self.assertEqual(pairs.iloc[0].next_state,'IM')


if __name__=='__main__':unittest.main()
