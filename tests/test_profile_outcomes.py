"""Verify username linkage, pretest-adjusted effects and HC3 calculations."""
import unittest
import numpy as np
import pandas as pd
from scipy.stats import f

from gitainment_analysis.analysis.profile_outcomes import link_scores,fit_ancova,bootstrap_intervals


class ProfileOutcomesTests(unittest.TestCase):
    def scores(self):
        rng=np.random.default_rng(8)
        cluster=np.repeat([1,2,3],20)
        pre=rng.uniform(40,85,60)+np.where(cluster==1,8,0)
        effects=np.select([cluster==1,cluster==2],[10,5],default=0)
        post=20+.6*pre+effects+rng.normal(0,.5,60)
        return pd.DataFrame({'No':np.arange(1,61),'username':[f'p{i:02}' for i in range(60)],
                             'cluster':cluster,'PreTest':pre,'PostTest':post})

    def linked(self):
        scores=self.scores();assign=scores[['username','cluster']].rename(columns={'username':'ID','cluster':'Cluster'})
        return link_scores(scores,assign)

    def test_username_join_is_independent_of_row_order(self):
        scores=self.scores();assign=scores[['username','cluster']].rename(columns={'username':'ID','cluster':'Cluster'})
        assign=assign.sample(frac=1,random_state=3)
        result=link_scores(scores,assign)
        expected=assign.set_index('ID').Cluster.to_dict()
        self.assertTrue(all(expected[row.Username]==row.Cluster for row in result.itertuples()))
        self.assertEqual(len(result),60)

    def test_ambiguous_duplicate_or_mismatched_linkage_is_rejected(self):
        scores=self.scores();assign=scores[['username','cluster']].rename(columns={'username':'ID','cluster':'Cluster'})
        bad=scores.copy();bad.loc[0,'username']='unknown'
        with self.assertRaises(ValueError):link_scores(bad,assign)
        bad=scores.copy();bad.loc[0,'username']=bad.loc[1,'username']+' '
        with self.assertRaises(ValueError):link_scores(bad,assign)
        bad=scores.copy();bad.loc[0,'cluster']=3
        with self.assertRaises(ValueError):link_scores(bad,assign)

    def test_pretest_adjusted_effects_recover_known_differences(self):
        frame=self.linked();result=fit_ancova(frame)
        pair=result['pairs'].query('ClusterA==1 and ClusterB==3').iloc[0]
        self.assertAlmostEqual(pair.Difference,10,delta=.4)
        self.assertEqual(result['metadata']['primary_df_residual'],56)
        self.assertTrue((result['pairs'].p_Holm>=result['pairs'].p_HC3).all())
        self.assertEqual(result['tests'].iloc[0].DF1,2)

    def test_hc3_omnibus_matches_independent_matrix_calculation(self):
        frame=self.linked();result=fit_ancova(frame)
        X=np.column_stack([np.ones(len(frame)),frame.PreTest-frame.PreTest.mean(),frame.Cluster.eq(2),frame.Cluster.eq(3)])
        y=frame.PostTest.to_numpy();inv=np.linalg.inv(X.T@X)
        beta=inv@X.T@y;residual=y-X@beta
        leverage=np.einsum('ij,jk,ik->i',X,inv,X)
        weighted=X*(residual/(1-leverage))[:,None]
        covariance=inv@weighted.T@weighted@inv
        R=np.eye(4)[[2,3]]
        wald=(R@beta).T@np.linalg.inv(R@covariance@R.T)@(R@beta)/2
        self.assertAlmostEqual(result['tests'].iloc[0].F,wald,places=8)
        self.assertAlmostEqual(result['tests'].iloc[0].p,f.sf(wald,2,len(frame)-4),places=10)

    def test_bootstrap_is_reproducible_and_gain_records_remain_paired(self):
        frame=self.linked()
        first,meta=bootstrap_intervals(frame,n_boot=100,seed=17)
        second,_=bootstrap_intervals(frame,n_boot=100,seed=17)
        pd.testing.assert_frame_equal(first,second)
        self.assertEqual(meta['successful_replicates'],100)
        self.assertTrue((first.CI_High>=first.CI_Low).all())
        np.testing.assert_allclose(frame.Gain,frame.PostTest-frame.PreTest)


if __name__=='__main__':unittest.main()
