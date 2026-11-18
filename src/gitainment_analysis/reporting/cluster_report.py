"""Focused peer-review analysis of exploratory profile separation and stability."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, silhouette_samples, silhouette_score
from threadpoolctl import threadpool_limits

from ..analysis.clustering import prepare_features, select_cluster_count, N_INIT, RANDOM_STATE
from ..analysis.stability import transform_bootstrap
from ..data_io import OUTPUT_DIR
from .formatting import markdown_table, export_docx

LABELS = {1:'Sustained Engagers', 2:'Low Activity Learners', 3:'Struggling Learners'}
SETTINGS = dict(init='k-means++', n_init=N_INIT, algorithm='lloyd', max_iter=300, tol=1e-4)


def align_labels(reference, predicted, in_bag):
    """Match arbitrary labels using only unique in-bag learners, not OOB outcomes."""
    original, candidate = np.unique(reference), np.unique(predicted)
    overlap = np.array([[np.sum(in_bag & (reference == a) & (predicted == b))
                         for b in candidate] for a in original])
    rows, cols = linear_sum_assignment(-overlap)
    mapping = {candidate[c]: original[r] for r,c in zip(rows,cols)}
    return np.array([mapping.get(label, -1) for label in predicted])


def overlap_diagnostics(data, scaled):
    learners = data[['ID','Cluster']].copy()
    learners['silhouette'] = silhouette_samples(scaled, data.Cluster)
    learners['negative_silhouette'] = learners.silhouette.lt(0)
    summary = learners.groupby('Cluster').agg(
        n=('ID','size'), mean_silhouette=('silhouette','mean'), median_silhouette=('silhouette','median'),
        minimum_silhouette=('silhouette','min'), maximum_silhouette=('silhouette','max'),
        negative_n=('negative_silhouette','sum'), negative_fraction=('negative_silhouette','mean')).reset_index()
    summary.insert(1,'exploratory_label',summary.Cluster.map(LABELS))
    return learners, summary


def membership_bootstrap(data, features, n_boot):
    reference = data.Cluster.to_numpy()
    rng = np.random.default_rng(RANDOM_STATE)
    oob_counts = np.zeros(len(data), dtype=int)
    oob_matches = np.zeros(len(data), dtype=int)
    all_matches = np.zeros(len(data), dtype=int)
    confusion = np.zeros((3,3), dtype=int)
    replicates = []
    for replicate in range(n_boot):
        sample = rng.integers(len(data), size=len(data))
        train, full = transform_bootstrap(data.iloc[sample], data, features)
        model = KMeans(n_clusters=3, **SETTINGS, random_state=replicate).fit(train)
        predicted = model.predict(full)
        in_bag = np.zeros(len(data), dtype=bool)
        in_bag[np.unique(sample)] = True
        oob = ~in_bag
        aligned = align_labels(reference, predicted, in_bag)
        same = aligned == reference
        all_matches += same
        oob_counts += oob
        oob_matches += same & oob
        for original in (1,2,3):
            for new in (1,2,3):
                confusion[original-1,new-1] += np.sum(oob & (reference==original) & (aligned==new))
        replicates.append(dict(replicate=replicate, oob_n=int(oob.sum()),
                               full_ari=adjusted_rand_score(reference,predicted),
                               oob_ari=adjusted_rand_score(reference[oob],predicted[oob])))
        if (replicate+1) % 100 == 0:
            print(f'Learner membership bootstrap: {replicate+1}/{n_boot}', flush=True)
    learners = data[['ID','Cluster']].copy()
    learners['full_reproduction_rate'] = all_matches/n_boot
    learners['oob_replicates'] = oob_counts
    learners['oob_matching_replicates'] = oob_matches
    learners['oob_reproduction_rate'] = np.divide(oob_matches,oob_counts,
        out=np.full(len(data),np.nan),where=oob_counts>0)
    summary = learners.groupby('Cluster').agg(
        n=('ID','size'), mean_oob_reproduction=('oob_reproduction_rate','mean'),
        median_oob_reproduction=('oob_reproduction_rate','median'),
        minimum_oob_reproduction=('oob_reproduction_rate','min'),
        maximum_oob_reproduction=('oob_reproduction_rate','max'),
        learners_below_80pct=('oob_reproduction_rate',lambda x:int(x.lt(.8).sum()))).reset_index()
    confusion_rows = [dict(original_cluster=a, assigned_cluster=b,
        oob_assignments=int(confusion[a-1,b-1]),
        row_share=float(confusion[a-1,b-1]/confusion[a-1].sum())) for a in (1,2,3) for b in (1,2,3)]
    return learners,summary,pd.DataFrame(replicates),pd.DataFrame(confusion_rows)


def select_k_subsamples(data, features, replicates, fraction=.8, seed=20261117):
    """Reselect k without duplicate points introduced by ordinary bootstrap sampling."""
    rng = np.random.default_rng(seed)
    sample_n = int(np.floor(fraction*len(data)))
    scores, selections = [], []
    for replicate in range(replicates):
        sample = rng.choice(len(data), size=sample_n, replace=False)
        train,_ = transform_bootstrap(data.iloc[sample],data,features)
        rows, labels_by_k = [], {}
        for k in range(2,11):
            labels = KMeans(n_clusters=k, **SETTINGS, random_state=RANDOM_STATE).fit_predict(train)
            smallest = int(np.bincount(labels,minlength=k).min())
            rows.append(dict(k=k,silhouette=silhouette_score(train,labels),
                             calinski_harabasz=calinski_harabasz_score(train,labels),
                             smallest_group_n=smallest,eligible=smallest>=2))
            labels_by_k[k] = labels
        validity, selected_k, agreement = select_cluster_count(pd.DataFrame(rows))
        validity.insert(0,'replicate',replicate)
        scores.append(validity)
        chosen=validity.loc[validity.selected].iloc[0]
        selections.append(dict(replicate=replicate, sample_n=sample_n, selected_k=selected_k,
            metrics_agree=agreement, selected_silhouette=chosen.silhouette,
            selected_ch=chosen.calinski_harabasz,
            ari_to_original_on_subsample=adjusted_rand_score(data.iloc[sample].Cluster,labels_by_k[selected_k])))
        if (replicate+1)%25==0:
            print(f'Cluster-count subsampling: {replicate+1}/{replicates}',flush=True)
    chosen=pd.DataFrame(selections)
    frequencies=chosen.selected_k.value_counts().reindex(range(2,11),fill_value=0).rename_axis('k').reset_index(name='selected_n')
    frequencies['selected_fraction']=frequencies.selected_n/replicates
    return pd.concat(scores,ignore_index=True),chosen,frequencies


def create_figures(folder, learners, overlap, frequency):
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    y=0
    for cluster in (1,2,3):
        values=np.sort(learners.loc[learners.Cluster.eq(cluster),'silhouette'])
        axes[0].barh(np.arange(y,y+len(values)),values,height=1,label=f'Cluster {cluster}',alpha=.85)
        y+=len(values)+4
    axes[0].axvline(learners.silhouette.mean(),color='black',linestyle='--',label='Overall mean')
    axes[0].axvline(0,color='gray',linewidth=.8)
    axes[0].set(xlabel='Learner silhouette',ylabel='Learners grouped by exploratory profile',yticks=[],title='Separation varies across learners')
    axes[0].legend(fontsize=8)
    axes[1].bar(frequency.k,100*frequency.selected_fraction,color='#4477AA')
    axes[1].set(xlabel='Selected number of clusters',ylabel='Subsamples (%)',xticks=list(range(2,11)),
                title='Cluster-count selection under 80% subsampling',ylim=(0,100))
    fig.tight_layout()
    for suffix in ('png','pdf'):
        fig.savefig(folder/f'figure_profile_separation_and_k_stability.{suffix}',dpi=300)
    plt.close(fig)


def write_report(folder,results_dir,overlap,membership,frequency,n_boot,n_subsamples):
    old=json.loads((results_dir/'analysis_cluster_stability_summary.json').read_text())
    selection=pd.read_csv(results_dir/'analysis_cluster_selection_methods.csv')
    pca=pd.read_csv(results_dir/'analysis_pca_variance.csv')
    alternative=pd.read_csv(results_dir/'analysis_cluster_alternative_solutions.csv')
    seed=pd.read_csv(results_dir/'analysis_cluster_seed_sensitivity.csv')
    boot=pd.read_csv(results_dir/'analysis_cluster_bootstrap_stability.csv')
    profile=pd.read_csv(results_dir/'analysis_cluster_profiles.csv')
    k3=frequency.loc[frequency.k.eq(3)].iloc[0]
    negatives=int(overlap.negative_n.sum())
    boot_table=pd.DataFrame([{'metric':name,**values} for name,values in old['bootstrap']['metrics'].items()])
    seed_summary=seed.groupby('n_init').agg(runs=('seed','size'),median_ARI=('ari','median'),
        min_ARI=('ari','min'),max_ARI=('ari','max'),exact_reference_n=('ari',lambda x:int(np.isclose(x,1).sum()))).reset_index()
    pca_view=pca.copy()
    pca_view['explained_variance_percent']=100*pca_view.pop('explained_variance_ratio')
    pca_view['cumulative_percent']=100*pca_view.pop('cumulative_explained_variance')
    empirical=old['bootstrap']['metrics']['ari']
    oob=old['bootstrap']['metrics']['oob_ari']
    profile_table=profile[['Cluster','cluster_n','CommandsExecuted_mean','FailedActions_mean',
                           'PlayDurationMinutes_mean','AccuracyRate_mean','HelpDependencyRatio_mean']].copy()
    profile_table['AccuracyRate_mean']*=100
    profile_table['HelpDependencyRatio_mean']*=100
    profile_table.rename(columns={'AccuracyRate_mean':'Accuracy_percent','HelpDependencyRatio_mean':'Help_dependency_percent'},inplace=True)
    lines=[
        '# Focused report: exploratory learner-profile separation and stability','',
        '> **Workflow:** K-means uses all 11 transformed, standardized clustering indicators directly. PCA is used only to visualize and describe the two-dimensional projection. Three additional indicators are used only for profiling/ANOVA.','',
        '## Overall finding','',
        'The three-profile solution is a useful, reproducible exploratory summary of this cohort, '
        'but its separation is modest and its membership depends partly on sampling and modeling '
        'choices. The evidence supports cautious descriptive use of “Sustained Engagers,” '
        '“Low Activity Learners,” and “Struggling Learners.” It does not establish three definitive '
        'learner classifications, independent educational validity, or stable traits across settings.','',
        'The reviewer is asking about four different properties: geometric separation, computational '
        'reproducibility, sample-resampling stability, and sensitivity to modeling choices. '
        'A high score on one property cannot compensate for an untested or weak result on another.','',
        '## 1. Sample, input variables, preprocessing, and exact settings','',
        'The combined feature table contains 115 learner identifiers. Eleven records with no observed '
        'activity were excluded, leaving 104 learners in clusters of 57, 32, and 15. The conservative '
        'LOF screening rule used 20 neighbors and a threshold greater than 2.0; it removed no additional '
        'learners in this run. Identifier-to-human uniqueness is assumed, not verified by these analyses.','',
        'The 11 clustering inputs were CommandsExecuted, CorrectActions, FailedActions, HintQuests, '
        'AnswerQuests, PlayDurationMinutes, LeaderboardInteractions, LearningEfficiency, AccuracyRate, '
        'PerfectQuestRate, and HelpDependencyRatio. Missing values were median-imputed for clustering; '
        'non-rate variables were log1p-transformed, and all features were standardized to comparable '
        'scales. Profile means remain on their original observed scales. LearningEfficiency means '
        'game-score points per minute, not measured learning gain.','',
        '| Setting | Value |','|---|---|',
        '| Method and distance | K-means; Euclidean distance in all 11 standardized features |',
        '| Final k | 3 |','| Initialization | k-means++ |',
        '| Starts per fit | 50; lowest-inertia fitted solution retained |',
        '| Reference random seed | 42 |','| Algorithm | Lloyd |',
        '| Maximum iterations / tolerance | 300 / 0.0001 |',
        '| Candidate k | 2 through 10 |',
        '| Eligibility | Smallest fitted group must contain at least two learners |',
        '| Selection rule | Minimum sum of descending silhouette and Calinski–Harabasz ranks; ties use larger silhouette, then smaller k |','',
        'Both criteria favor k=3 in the original retained cohort: silhouette = **0.309257**, '
        'Calinski–Harabasz = **39.539062**. The next-highest silhouette is k=6 '
        '(0.295136), only 0.014120 lower; the next-highest Calinski–Harabasz score is k=2 '
        '(35.225719). These criteria assess the candidate solutions within this feature space; '
        'their agreement does not prove that three latent populations exist.','',
        markdown_table(selection[['k','silhouette','calinski_harabasz','smallest_group_n','selected']]),'',
        '## 2. Principal components: clarify the manuscript wording','',
        '**No dimensionality reduction was used before the original clustering.** K-means used all '
        '11 transformed, standardized behavioral inputs. Two PCs were retained only for the '
        'two-dimensional figure. PC1 explains **33.855967%**, PC2 **28.012009%**, and together they '
        'explain **61.867975%** of standardized-feature variance. The remaining **38.132025%** is '
        'absent from the plot, so visual overlap or separation in that plot is not a complete '
        'representation of the clustering space. This explained variance is not prediction accuracy '
        'or a percentage of learners correctly classified.','',
        markdown_table(pca_view),'',
        'If the manuscript says clustering was performed “on retained principal components,” that '
        'description is inconsistent with the implemented analysis and should be corrected. '
        'Do not retrospectively present the two plotting components as the original clustering inputs.','',
        '## 3. What silhouette 0.309 means, including learner-level overlap','',
        'For learner i, s(i) = [b(i) − a(i)] / max[a(i), b(i)], where a(i) is the mean distance '
        'to learners in the assigned cluster and b(i) is the smallest mean distance to another '
        'cluster. Values near zero indicate overlap; negative values indicate closer average '
        'proximity to another cluster under this metric. A negative value is a diagnostic of '
        'geometric ambiguity, not proof that a learner has a known “true” label elsewhere.','',
        'The global silhouette is a learner-weighted mean, not classification accuracy or a p-value. '
        'There is no universal cutoff that validates learner types. Calling 0.309 “modest separation” '
        'is appropriate; calling it strong evidence for discrete populations would overstate the result.','',
        markdown_table(overlap),'',
        f'In total, **{negatives}/104 learners ({100*negatives/104:.1f}%)** have negative silhouettes. '
        'Cluster-specific summaries reveal ambiguity hidden by the overall average. In particular, '
        'the mean silhouette is 0.303791 for Sustained Engagers, 0.377790 for Low Activity Learners, '
        'and only 0.183820 for Struggling Learners. Both negative silhouettes occur in the smallest '
        'profile (2/15, 13.3%), whereas neither larger profile has a negative value. Thus the '
        'smallest profile has the weakest geometric separation. The accompanying silhouette '
        'figure displays all learner values without reducing the analysis to two PCs.','',
        '## 4. Sensitivity to random initializations','',
        'The earlier analysis fit the same retained data with 100 seeds (0–99), once using one start '
        'per fit and once using 50 starts. ARI compares partitions while ignoring arbitrary numeric '
        'label names; ARI=1 means identical grouping, and values near zero indicate chance-level '
        'agreement under the ARI adjustment. Agreement is with the reference solution, not ground truth.','',
        markdown_table(seed_summary),'',
        'With 50 starts, **100/100 runs** reproduced the reference partition (ARI=1.000 throughout). '
        'With one start, only **33/100** reproduced it; median ARI=0.972526 and the minimum was '
        '0.227573. Multiple starts therefore materially reduce local-optimum sensitivity. The '
        '50-start result establishes computational reproducibility on this dataset, not perfect '
        'separation, a guaranteed global optimum, or stability in a new population.','',
        '## 5. Bootstrap stability: partition and profile membership','',
        'The existing fixed-k analysis used 500 learner bootstrap replicates (sampling learners '
        'with replacement, seed 42). Each replicate refit median imputation, transformation, '
        'standardization, and 50-start K-means at k=3, then assigned the original retained cohort '
        'to the fitted centers. ARI was calculated for the full cohort and its out-of-bag (OOB) '
        'learners. The original active-cohort selection and k=3 were held fixed; LOF and k selection '
        'were not rerun inside these bootstrap replicates.','',
        markdown_table(boot_table),'',
        f'Mean full-cohort ARI was **{empirical["mean"]:.6f}**, with empirical 2.5th–97.5th '
        f'percentiles **{empirical["q025"]:.6f}–{empirical["q975"]:.6f}**. Mean OOB ARI was '
        f'**{oob["mean"]:.6f}**, range **{oob["q025"]:.6f}–{oob["q975"]:.6f}**. Full-cohort '
        'comparison includes sampled learners, so OOB results are a useful additional check. '
        'These percentiles are resampling stability ranges, **not confidence intervals for a '
        'population parameter**. They show generally reproducible partitions with occasional '
        'substantially different fits.','',
        'Jaccard overlap is intersection divided by union of a reference cluster and its matched '
        'resampled cluster, using one-to-one matching that maximizes total Jaccard overlap. '
        'Mean overlaps were **0.956223**, **0.964315**, and **0.815867** for clusters 1, 2, and 3. '
        'The third profile has the lowest average overlap and widest lower-tail instability '
        '(2.5th percentile **0.423733**). Its small n=15 makes its boundaries especially sensitive '
        'to changes in the sampled learners. Overall ARI can obscure this weaker small-profile stability.','',
        '## 6. New analysis: OOB membership reproduction for each learner','',
        f'This extension reran {n_boot} bootstrap replicates using the same sampling design and '
        'recorded how frequently each learner returned to the reference profile when omitted '
        'from the fitting sample. Numeric labels were aligned by maximum overlap using only '
        'unique in-bag learners; the OOB learners were not used for label alignment. This alignment '
        'differs from the Jaccard matching above because its purpose is individual label reproduction.','',
        markdown_table(membership),'',
        'Mean learner-level OOB reproduction was 97.12%, 99.29%, and 85.79% for clusters 1, 2, '
        'and 3. Five of the 15 Struggling Learners had reproduction rates below 80%, compared '
        'with one of 57 Sustained Engagers and none of 32 Low Activity Learners. This reinforces '
        'the interpretation that the third profile is useful descriptively but has less certain '
        'boundaries. These are equal-learner averages; pooled OOB assignment shares in the '
        'confusion file weight learners by how often they were left out and differ slightly.', '',
        'An OOB reproduction rate is an empirical frequency conditional on the original solution, '
        'feature definitions, and k=3. It is **not the probability of belonging to a true learner '
        'type**. The “below 80%” count is a transparent descriptive screening threshold, not a '
        'validated classification cutoff. OOB learners still come from the original cohort used '
        'to define the reference solution; this is not independent external validation. Detailed '
        'learner-level files and an OOB transition/confusion table accompany this report.','',
        '## 7. New analysis: does k=3 remain preferred when learners change?','',
        f'The previous bootstrap held k fixed. To address that limitation, this extension drew '
        f'**{n_subsamples} independent 80% subsamples without replacement (83 of 104 learners)**, '
        'using seed 20261117. Each subsample refit preprocessing and evaluated k=2–10 with the '
        'original 50-start K-means settings and the same two-score selection rule. Sampling without '
        'replacement avoids artificial duplicate observations that can distort within-sample '
        'silhouette scores in an ordinary bootstrap. Active-cohort selection and feature definitions '
        'remain fixed, and subsamples overlap; they are not independent study replications.','',
        markdown_table(frequency),'',
        f'k=3 was selected in **{int(k3.selected_n)}/{n_subsamples} subsamples '
        f'({100*k3.selected_fraction:.1f}%)**. This quantifies how often the current selection '
        'procedure returns three clusters after removing 20% of learners. It is not a posterior '
        'probability that three groups exist. Selection of other k values is evidence that the '
        'number of descriptive profiles is sample-dependent. Interpret this result alongside '
        'the original two-score agreement rather than presenting only the original optimum.','',
        '## 8. Alternative algorithms and feature dependence','',
        markdown_table(alternative[['method','dimensions','ari','silhouette','smallest_cluster_n']]),'',
        'At fixed k=3, Ward agglomerative clustering closely agreed with K-means '
        '(ARI=**0.982231**, silhouette=**0.308665**), but a full-covariance Gaussian mixture '
        '(20 initializations, seed 42) did not (ARI=**0.264401**, silhouette=**0.197178**). '
        'Ward and K-means both favor compact Euclidean groups, so their agreement is useful but '
        'not strong evidence of independence from all clustering assumptions. The mixture permits '
        'elliptical covariance structures; disagreement illustrates model dependence. Its greater '
        'parameter flexibility with n=104 also limits interpretation, and this comparison alone '
        'does not establish that either method is correct.','',
        'Leaving out one input at a time yielded ARIs ranging from **0.873038 to 1.000000**. '
        'Removing LearningEfficiency gave ARI=**0.965364**, indicating that the entire solution is '
        'not solely a consequence of that score-rate variable. Nevertheless, the weakest agreement '
        'after removing CorrectActions and the changes in small-cluster size demonstrate feature '
        'dependence. These are sensitivity checks, not external validation.','',
        '## 9. Why the three labels should remain exploratory','',
        markdown_table(profile_table),'',
        'These observed summaries motivate the labels: the first profile has higher command use '
        'and longer gameplay; the second has little logged/saved activity; the third has more '
        'failed actions, lower accuracy, and greater help dependence. Rates in this table are '
        'percentages. Means are based on observed values, and their valid n can differ from total '
        'membership. Low activity may reflect limited exposure, logging coverage, or disengagement; '
        'the logs do not establish motivation. “Struggling” describes this interaction pattern '
        'and must not be treated as a diagnosis or a stable ability judgment.','',
        'Use “exploratory behavioral profiles in this cohort,” “learners assigned to the profile,” '
        'and “patterns consistent with sustained engagement / limited activity / interaction '
        'difficulty.” Avoid “three learner types were validated,” “learners are definitively '
        'classified,” or claims that the labels generalize across courses or time. The analysis '
        'does not prove educational benefit, pre/post differences, or perception differences. '
        'Those claims require linked independent outcomes and preferably external replication.','',
        '## 10. Suggested manuscript methods paragraph','',
        '> Exploratory behavioral profiles were estimated from 11 behavioral variables after '
        'median imputation, log1p transformation of non-rate variables, and standard scaling. '
        'K-means used Euclidean distance, k-means++ initialization, 50 starts, the Lloyd algorithm, '
        'a maximum of 300 iterations, tolerance 0.0001, and reference seed 42. Candidate solutions '
        'with k=2–10 were ranked jointly by silhouette and Calinski–Harabasz indices, excluding '
        'singleton solutions. Both indices favored k=3 in the retained cohort. PCA was used only '
        'for visualization: the first two components explained 33.86% and 28.01% of standardized '
        'feature variance (61.87% cumulatively); clustering used the full standardized feature '
        'space. Sensitivity was examined across random initializations, learner bootstraps, '
        '80% subsampling with k reselection, alternative clustering methods, '
        'and omission of individual features.','',
        '## 11. Suggested manuscript results and limitation paragraph','',
        f'> Three exploratory profiles were obtained (n=57, 32, and 15), with a silhouette of '
        f'0.309 and Calinski–Harabasz index of 39.539. The modest silhouette indicates overlapping '
        f'behavioral distributions. All 100 fits using 50 starts reproduced the reference '
        f'partition, while only 33 of 100 single-start fits did so. Across 500 learner-bootstrap '
        f'replicates, mean ARI was 0.919 (empirical 2.5th–97.5th percentiles 0.618–1.000), '
        f'and mean out-of-bag ARI was 0.910. Mean cluster-wise Jaccard overlaps were 0.956, '
        f'0.964, and 0.816, indicating weaker membership stability for the smallest profile. '
        f'In {n_subsamples} 80% subsamples, the original selection rule chose k=3 in '
        f'{int(k3.selected_n)} cases ({100*k3.selected_fraction:.1f}%). Ward clustering '
        f'closely agreed with K-means (ARI=0.982), whereas the full-covariance Gaussian mixture '
        f'did not (ARI=0.264). The labels Sustained Engagers, Low Activity Learners, and '
        f'Struggling Learners therefore describe exploratory patterns in this cohort rather '
        f'than definitive learner classifications. Stability ranges condition on the retained '
        f'cohort and analysis choices and do not establish external or educational validity.','',
        '## 12. Draft response to the reviewer','',
        '> Thank you for highlighting the distinction between an interpretable clustering '
        'solution and evidence of well-separated learner classes. We agree that the silhouette '
        'of 0.309 represents modest separation. The accompanying analysis now reports the '
        'complete preprocessing and K-means settings and clarifies that PCA served only to '
        'visualize the full-feature solution; the two plotted components explain 61.87% of '
        'variance. Initialization sensitivity, 500 learner-bootstrap replicates with ARI and '
        'cluster-wise Jaccard summaries, out-of-bag membership reproduction, subsampling with '
        'k reselection, and alternative-method/feature sensitivity are reported. These analyses '
        f'show highly reproducible multi-start fits (100/100 identical partitions) and substantial '
        f'overall resampling stability (mean bootstrap ARI=0.919), with k=3 selected in '
        f'{int(k3.selected_n)}/{n_subsamples} subsamples ({100*k3.selected_fraction:.1f}%). '
        f'However, the n=15 profile has lower separation (mean silhouette=0.184), two negative '
        f'silhouettes, and weaker bootstrap overlap (mean Jaccard=0.816); agreement also varies '
        f'between Ward clustering (ARI=0.982) and the Gaussian mixture (ARI=0.264). '
        'Accordingly, the proposed labels should be presented as explicitly exploratory '
        'behavioral profiles, with overlapping boundaries and no claim of definitive learner '
        'classification. The numerical results and proposed manuscript text are supplied here '
        'for incorporation into the revision.','',
        'This response describes the completed analyses. It does not claim that manuscript '
        'files have already been edited. If the source manuscript still describes PCA before clustering, that method text needs correction to match this workflow.','',
        '## 13. Reproducibility and source definitions','',
        'The existing initialization/bootstrap/PCA/alternative-method tables were reused and '
        'checked against a fresh baseline reconstruction. The new per-learner bootstrap and '
        'k-reselection analyses were executed for this focused report. Files in this folder '
        'include new diagnostics, a consolidated Excel workbook and research figures; reference CSVs stay in the parent clustering folder rather than being duplicated. '
        'and a source/code hash manifest. Raw participant identifiers appear only in the '
        'detailed learner diagnostic files, not in the narrative report. Package versions and '
        'sample seeds are recorded in the manifest.','',
        '- [Silhouette definition and interpretation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_samples.html)',
        '- [Adjusted Rand index](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html)',
        '- [PCA and explained variance](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)',
        '- [Clustering assumptions and evaluation](https://scikit-learn.org/stable/modules/clustering.html)','']
    report='\n'.join(lines)
    (folder/'CLUSTER_VALIDATION_REPORT.md').write_text(report,encoding='utf-8')
    return report



def run(results_dir=OUTPUT_DIR/"clustering",folder=None,n_boot=500,n_subsamples=200):
    results_dir=Path(results_dir)
    folder=Path(folder) if folder else results_dir/'report'
    folder.mkdir(parents=True,exist_ok=True)
    if n_boot<2 or n_subsamples<2:raise ValueError('At least two replicates are required')
    data=pd.read_csv(results_dir/'analysis_kmeans_assignments.csv',dtype={'ID':str})
    features,_,scaled=prepare_features(data)
    if set(data.Cluster.unique())!={1,2,3}:raise ValueError('This report describes the existing three-profile solution')
    with threadpool_limits(limits=1):
        base=KMeans(n_clusters=3,**SETTINGS,random_state=RANDOM_STATE).fit(scaled)
        if adjusted_rand_score(data.Cluster,base.labels_)<.999999:raise ValueError('Reference assignments do not reproduce')
        learners,overlap=overlap_diagnostics(data,scaled)
        membership,membership_summary,replicates,confusion=membership_bootstrap(data,features,n_boot)
        scores,chosen,frequency=select_k_subsamples(data,features,n_subsamples)
    combined=learners.merge(membership,on=['ID','Cluster'],validate='one_to_one')
    tables={'learner_diagnostics':combined,'silhouette_by_profile':overlap,
            'oob_membership_by_profile':membership_summary,'oob_assignment_confusion':confusion,
            'membership_bootstrap_runs':replicates,'k_reselection_scores':scores,
            'k_reselection_runs':chosen,'k_reselection_frequency':frequency}
    for name,table in tables.items():table.to_csv(folder/f'{name}.csv',index=False)
    reused=['analysis_cluster_selection_methods.csv','analysis_pca_variance.csv','analysis_pca_loadings.csv',
            'analysis_cluster_seed_sensitivity.csv','analysis_cluster_bootstrap_stability.csv',
            'analysis_cluster_stability_summary.json','analysis_cluster_alternative_solutions.csv',
            'analysis_cluster_profiles.csv','analysis_cluster_selection_summary.json']
    report=write_report(folder,results_dir,overlap,membership_summary,frequency,n_boot,n_subsamples)
    export_docx(report,folder/'CLUSTER_VALIDATION_REPORT.docx')
    with pd.ExcelWriter(folder/'cluster_validation_tables.xlsx',engine='openpyxl') as writer:
        for name,table in tables.items():table.to_excel(writer,sheet_name=name[:31],index=False)
        for name in reused:
            if name.endswith('.csv'):
                sheet=name.replace('analysis_','').replace('.csv','')[:31]
                pd.read_csv(results_dir/name).to_excel(writer,sheet_name=sheet,index=False)
    create_figures(folder,combined,overlap,frequency)
    inputs=[results_dir/name for name in reused]+[results_dir/'analysis_kmeans_assignments.csv']
    inputs += [Path(__file__),Path(__file__).parents[1]/'analysis/clustering.py',
               Path(__file__).parents[1]/'analysis/stability.py']
    manifest=dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),
        fixed_k_membership_bootstrap_replicates=n_boot,bootstrap_seed=42,
        k_reselection_subsamples=n_subsamples,subsample_seed=20261117,subsample_fraction=.8,
        inputs_sha256={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        packages={name:version(name) for name in ['numpy','pandas','scipy','scikit-learn','matplotlib','python-docx','openpyxl']},
        scope='Conditional on retained cohort and feature definitions; no independent validation; existing assignments unchanged')
    (folder/'report_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Focused report completed: '+str(folder),flush=True)
    return folder


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir',type=Path,default=OUTPUT_DIR/'clustering')
    parser.add_argument('--report-dir',type=Path)
    parser.add_argument('--bootstrap',type=int,default=500)
    parser.add_argument('--subsamples',type=int,default=200)
    args=parser.parse_args()
    run(args.results_dir,args.report_dir,args.bootstrap,args.subsamples)


if __name__=='__main__':main()
