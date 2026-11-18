# Focused report: exploratory learner-profile separation and stability

> **Workflow:** K-means uses all 11 transformed, standardized clustering indicators directly. PCA is used only to visualize and describe the two-dimensional projection. Three additional indicators are used only for profiling/ANOVA.

## Overall finding

The three-profile solution is a useful, reproducible exploratory summary of this cohort, but its separation is modest and its membership depends partly on sampling and modeling choices. The evidence supports cautious descriptive use of “Sustained Engagers,” “Low Activity Learners,” and “Struggling Learners.” It does not establish three definitive learner classifications, independent educational validity, or stable traits across settings.

The reviewer is asking about four different properties: geometric separation, computational reproducibility, sample-resampling stability, and sensitivity to modeling choices. A high score on one property cannot compensate for an untested or weak result on another.

## 1. Sample, input variables, preprocessing, and exact settings

The combined feature table contains 115 learner identifiers. Eleven records with no observed activity were excluded, leaving 104 learners in clusters of 57, 32, and 15. The conservative LOF screening rule used 20 neighbors and a threshold greater than 2.0; it removed no additional learners in this run. Identifier-to-human uniqueness is assumed, not verified by these analyses.

The 11 clustering inputs were CommandsExecuted, CorrectActions, FailedActions, HintQuests, AnswerQuests, PlayDurationMinutes, LeaderboardInteractions, LearningEfficiency, AccuracyRate, PerfectQuestRate, and HelpDependencyRatio. Missing values were median-imputed for clustering; non-rate variables were log1p-transformed, and all features were standardized to comparable scales. Profile means remain on their original observed scales. LearningEfficiency means game-score points per minute, not measured learning gain.

| Setting | Value |
|---|---|
| Method and distance | K-means; Euclidean distance in all 11 standardized features |
| Final k | 3 |
| Initialization | k-means++ |
| Starts per fit | 50; lowest-inertia fitted solution retained |
| Reference random seed | 42 |
| Algorithm | Lloyd |
| Maximum iterations / tolerance | 300 / 0.0001 |
| Candidate k | 2 through 10 |
| Eligibility | Smallest fitted group must contain at least two learners |
| Selection rule | Minimum sum of descending silhouette and Calinski–Harabasz ranks; ties use larger silhouette, then smaller k |

Both criteria favor k=3 in the original retained cohort: silhouette = **0.309257**, Calinski–Harabasz = **39.539062**. The next-highest silhouette is k=6 (0.295136), only 0.014120 lower; the next-highest Calinski–Harabasz score is k=2 (35.225719). These criteria assess the candidate solutions within this feature space; their agreement does not prove that three latent populations exist.

| k | silhouette | calinski_harabasz | smallest_group_n | selected |
| --- | --- | --- | --- | --- |
| 2 | 0.2665 | 35.23 | 35 | False |
| 3 | 0.3093 | 39.54 | 15 | True |
| 4 | 0.2452 | 35.13 | 14 | False |
| 5 | 0.2724 | 33.39 | 5 | False |
| 6 | 0.2951 | 32.16 | 5 | False |
| 7 | 0.2703 | 30.5 | 5 | False |
| 8 | 0.286 | 30.05 | 4 | False |
| 9 | 0.2865 | 29.54 | 4 | False |
| 10 | 0.2693 | 28.63 | 3 | False |

## 2. Principal components: clarify the manuscript wording

**No dimensionality reduction was used before the original clustering.** K-means used all 11 transformed, standardized behavioral inputs. Two PCs were retained only for the two-dimensional figure. PC1 explains **33.855967%**, PC2 **28.012009%**, and together they explain **61.867975%** of standardized-feature variance. The remaining **38.132025%** is absent from the plot, so visual overlap or separation in that plot is not a complete representation of the clustering space. This explained variance is not prediction accuracy or a percentage of learners correctly classified.

| component | explained_variance_percent | cumulative_percent |
| --- | --- | --- |
| 1 | 33.86 | 33.86 |
| 2 | 28.01 | 61.87 |
| 3 | 9.251 | 71.12 |
| 4 | 7.587 | 78.71 |
| 5 | 6.781 | 85.49 |
| 6 | 5.547 | 91.03 |
| 7 | 4.717 | 95.75 |
| 8 | 1.811 | 97.56 |
| 9 | 1.306 | 98.87 |
| 10 | 0.7817 | 99.65 |
| 11 | 0.3497 | 100 |

If the manuscript says clustering was performed “on retained principal components,” that description is inconsistent with the implemented analysis and should be corrected. Do not retrospectively present the two plotting components as the original clustering inputs.

## 3. What silhouette 0.309 means, including learner-level overlap

For learner i, s(i) = [b(i) − a(i)] / max[a(i), b(i)], where a(i) is the mean distance to learners in the assigned cluster and b(i) is the smallest mean distance to another cluster. Values near zero indicate overlap; negative values indicate closer average proximity to another cluster under this metric. A negative value is a diagnostic of geometric ambiguity, not proof that a learner has a known “true” label elsewhere.

The global silhouette is a learner-weighted mean, not classification accuracy or a p-value. There is no universal cutoff that validates learner types. Calling 0.309 “modest separation” is appropriate; calling it strong evidence for discrete populations would overstate the result.

| Cluster | exploratory_label | n | mean_silhouette | median_silhouette | minimum_silhouette | maximum_silhouette | negative_n | negative_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sustained Engagers | 57 | 0.3038 | 0.3119 | 0.08763 | 0.4693 | 0 | 0 |
| 2 | Low Activity Learners | 32 | 0.3778 | 0.3969 | 0.1402 | 0.5422 | 0 | 0 |
| 3 | Struggling Learners | 15 | 0.1838 | 0.2072 | -0.06592 | 0.3831 | 2 | 0.1333 |

In total, **2/104 learners (1.9%)** have negative silhouettes. Cluster-specific summaries reveal ambiguity hidden by the overall average. In particular, the mean silhouette is 0.303791 for Sustained Engagers, 0.377790 for Low Activity Learners, and only 0.183820 for Struggling Learners. Both negative silhouettes occur in the smallest profile (2/15, 13.3%), whereas neither larger profile has a negative value. Thus the smallest profile has the weakest geometric separation. The accompanying silhouette figure displays all learner values without reducing the analysis to two PCs.

## 4. Sensitivity to random initializations

The earlier analysis fit the same retained data with 100 seeds (0–99), once using one start per fit and once using 50 starts. ARI compares partitions while ignoring arbitrary numeric label names; ARI=1 means identical grouping, and values near zero indicate chance-level agreement under the ARI adjustment. Agreement is with the reference solution, not ground truth.

| n_init | runs | median_ARI | min_ARI | max_ARI | exact_reference_n |
| --- | --- | --- | --- | --- | --- |
| 1 | 100 | 0.9725 | 0.2276 | 1 | 33 |
| 50 | 100 | 1 | 1 | 1 | 100 |

With 50 starts, **100/100 runs** reproduced the reference partition (ARI=1.000 throughout). With one start, only **33/100** reproduced it; median ARI=0.972526 and the minimum was 0.227573. Multiple starts therefore materially reduce local-optimum sensitivity. The 50-start result establishes computational reproducibility on this dataset, not perfect separation, a guaranteed global optimum, or stability in a new population.

## 5. Bootstrap stability: partition and profile membership

The existing fixed-k analysis used 500 learner bootstrap replicates (sampling learners with replacement, seed 42). Each replicate refit median imputation, transformation, standardization, and 50-start K-means at k=3, then assigned the original retained cohort to the fitted centers. ARI was calculated for the full cohort and its out-of-bag (OOB) learners. The original active-cohort selection and k=3 were held fixed; LOF and k selection were not rerun inside these bootstrap replicates.

| metric | mean | median | q025 | q975 |
| --- | --- | --- | --- | --- |
| ari | 0.9192 | 0.9543 | 0.6183 | 1 |
| oob_ari | 0.9103 | 0.9321 | 0.6129 | 1 |
| cluster_1_jaccard | 0.9562 | 0.9825 | 0.7128 | 1 |
| cluster_2_jaccard | 0.9643 | 0.9697 | 0.8889 | 1 |
| cluster_3_jaccard | 0.8159 | 0.875 | 0.4237 | 1 |

Mean full-cohort ARI was **0.919228**, with empirical 2.5th–97.5th percentiles **0.618261–1.000000**. Mean OOB ARI was **0.910300**, range **0.612852–1.000000**. Full-cohort comparison includes sampled learners, so OOB results are a useful additional check. These percentiles are resampling stability ranges, **not confidence intervals for a population parameter**. They show generally reproducible partitions with occasional substantially different fits.

Jaccard overlap is intersection divided by union of a reference cluster and its matched resampled cluster, using one-to-one matching that maximizes total Jaccard overlap. Mean overlaps were **0.956223**, **0.964315**, and **0.815867** for clusters 1, 2, and 3. The third profile has the lowest average overlap and widest lower-tail instability (2.5th percentile **0.423733**). Its small n=15 makes its boundaries especially sensitive to changes in the sampled learners. Overall ARI can obscure this weaker small-profile stability.

## 6. New analysis: OOB membership reproduction for each learner

This extension reran 500 bootstrap replicates using the same sampling design and recorded how frequently each learner returned to the reference profile when omitted from the fitting sample. Numeric labels were aligned by maximum overlap using only unique in-bag learners; the OOB learners were not used for label alignment. This alignment differs from the Jaccard matching above because its purpose is individual label reproduction.

| Cluster | n | mean_oob_reproduction | median_oob_reproduction | minimum_oob_reproduction | maximum_oob_reproduction | learners_below_80pct |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 57 | 0.9712 | 0.9949 | 0.6579 | 1 | 1 |
| 2 | 32 | 0.9929 | 1 | 0.9081 | 1 | 0 |
| 3 | 15 | 0.8579 | 0.9568 | 0.5307 | 1 | 5 |

Mean learner-level OOB reproduction was 97.12%, 99.29%, and 85.79% for clusters 1, 2, and 3. Five of the 15 Struggling Learners had reproduction rates below 80%, compared with one of 57 Sustained Engagers and none of 32 Low Activity Learners. This reinforces the interpretation that the third profile is useful descriptively but has less certain boundaries. These are equal-learner averages; pooled OOB assignment shares in the confusion file weight learners by how often they were left out and differ slightly.

An OOB reproduction rate is an empirical frequency conditional on the original solution, feature definitions, and k=3. It is **not the probability of belonging to a true learner type**. The “below 80%” count is a transparent descriptive screening threshold, not a validated classification cutoff. OOB learners still come from the original cohort used to define the reference solution; this is not independent external validation. Detailed learner-level files and an OOB transition/confusion table accompany this report.

## 7. New analysis: does k=3 remain preferred when learners change?

The previous bootstrap held k fixed. To address that limitation, this extension drew **200 independent 80% subsamples without replacement (83 of 104 learners)**, using seed 20261117. Each subsample refit preprocessing and evaluated k=2–10 with the original 50-start K-means settings and the same two-score selection rule. Sampling without replacement avoids artificial duplicate observations that can distort within-sample silhouette scores in an ordinary bootstrap. Active-cohort selection and feature definitions remain fixed, and subsamples overlap; they are not independent study replications.

| k | selected_n | selected_fraction |
| --- | --- | --- |
| 2 | 0 | 0 |
| 3 | 190 | 0.95 |
| 4 | 0 | 0 |
| 5 | 0 | 0 |
| 6 | 6 | 0.03 |
| 7 | 0 | 0 |
| 8 | 3 | 0.015 |
| 9 | 0 | 0 |
| 10 | 1 | 0.005 |

k=3 was selected in **190/200 subsamples (95.0%)**. This quantifies how often the current selection procedure returns three clusters after removing 20% of learners. It is not a posterior probability that three groups exist. Selection of other k values is evidence that the number of descriptive profiles is sample-dependent. Interpret this result alongside the original two-score agreement rather than presenting only the original optimum.

## 8. Alternative algorithms and feature dependence

| method | dimensions | ari | silhouette | smallest_cluster_n |
| --- | --- | --- | --- | --- |
| ward_agglomerative | 11 | 0.9822 | 0.3087 | 16 |
| gaussian_mixture_full | 11 | 0.2644 | 0.1972 | 21 |
| kmeans_without_LearningEfficiency | 10 | 0.9654 | 0.3261 | 13 |
| kmeans_without_CommandsExecuted | 10 | 0.8866 | 0.2495 | 18 |
| kmeans_without_CorrectActions | 10 | 0.873 | 0.3065 | 14 |
| kmeans_without_FailedActions | 10 | 0.9086 | 0.3165 | 10 |
| kmeans_without_HintQuests | 10 | 1 | 0.3399 | 15 |
| kmeans_without_AnswerQuests | 10 | 1 | 0.3309 | 15 |
| kmeans_without_PlayDurationMinutes | 10 | 0.9725 | 0.276 | 16 |
| kmeans_without_LeaderboardInteractions | 10 | 0.9388 | 0.3257 | 16 |
| kmeans_without_AccuracyRate | 10 | 0.939 | 0.3324 | 12 |
| kmeans_without_PerfectQuestRate | 10 | 0.9334 | 0.2969 | 19 |
| kmeans_without_HelpDependencyRatio | 10 | 0.9543 | 0.3112 | 17 |

At fixed k=3, Ward agglomerative clustering closely agreed with K-means (ARI=**0.982231**, silhouette=**0.308665**), but a full-covariance Gaussian mixture (20 initializations, seed 42) did not (ARI=**0.264401**, silhouette=**0.197178**). Ward and K-means both favor compact Euclidean groups, so their agreement is useful but not strong evidence of independence from all clustering assumptions. The mixture permits elliptical covariance structures; disagreement illustrates model dependence. Its greater parameter flexibility with n=104 also limits interpretation, and this comparison alone does not establish that either method is correct.

Leaving out one input at a time yielded ARIs ranging from **0.873038 to 1.000000**. Removing LearningEfficiency gave ARI=**0.965364**, indicating that the entire solution is not solely a consequence of that score-rate variable. Nevertheless, the weakest agreement after removing CorrectActions and the changes in small-cluster size demonstrate feature dependence. These are sensitivity checks, not external validation.

## 9. Why the three labels should remain exploratory

| Cluster | cluster_n | CommandsExecuted_mean | FailedActions_mean | PlayDurationMinutes_mean | Accuracy_percent | Help_dependency_percent |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 57 | 136.8 | 11.3 | 73.15 | 70.91 | 3.527 |
| 2 | 32 | 0.129 | 0.9032 | 17.28 | 79.37 | 0.5364 |
| 3 | 15 | 2.933 | 21.4 | 13.71 | 31.51 | 19.74 |

These observed summaries motivate the labels: the first profile has higher command use and longer gameplay; the second has little logged/saved activity; the third has more failed actions, lower accuracy, and greater help dependence. Rates in this table are percentages. Means are based on observed values, and their valid n can differ from total membership. Low activity may reflect limited exposure, logging coverage, or disengagement; the logs do not establish motivation. “Struggling” describes this interaction pattern and must not be treated as a diagnosis or a stable ability judgment.

Use “exploratory behavioral profiles in this cohort,” “learners assigned to the profile,” and “patterns consistent with sustained engagement / limited activity / interaction difficulty.” Avoid “three learner types were validated,” “learners are definitively classified,” or claims that the labels generalize across courses or time. The analysis does not prove educational benefit, pre/post differences, or perception differences. Those claims require linked independent outcomes and preferably external replication.

## 10. Suggested manuscript methods paragraph

> Exploratory behavioral profiles were estimated from 11 behavioral variables after median imputation, log1p transformation of non-rate variables, and standard scaling. K-means used Euclidean distance, k-means++ initialization, 50 starts, the Lloyd algorithm, a maximum of 300 iterations, tolerance 0.0001, and reference seed 42. Candidate solutions with k=2–10 were ranked jointly by silhouette and Calinski–Harabasz indices, excluding singleton solutions. Both indices favored k=3 in the retained cohort. PCA was used only for visualization: the first two components explained 33.86% and 28.01% of standardized feature variance (61.87% cumulatively); clustering used the full standardized feature space. Sensitivity was examined across random initializations, learner bootstraps, 80% subsampling with k reselection, alternative clustering methods, and omission of individual features.

## 11. Suggested manuscript results and limitation paragraph

> Three exploratory profiles were obtained (n=57, 32, and 15), with a silhouette of 0.309 and Calinski–Harabasz index of 39.539. The modest silhouette indicates overlapping behavioral distributions. All 100 fits using 50 starts reproduced the reference partition, while only 33 of 100 single-start fits did so. Across 500 learner-bootstrap replicates, mean ARI was 0.919 (empirical 2.5th–97.5th percentiles 0.618–1.000), and mean out-of-bag ARI was 0.910. Mean cluster-wise Jaccard overlaps were 0.956, 0.964, and 0.816, indicating weaker membership stability for the smallest profile. In 200 80% subsamples, the original selection rule chose k=3 in 190 cases (95.0%). Ward clustering closely agreed with K-means (ARI=0.982), whereas the full-covariance Gaussian mixture did not (ARI=0.264). The labels Sustained Engagers, Low Activity Learners, and Struggling Learners therefore describe exploratory patterns in this cohort rather than definitive learner classifications. Stability ranges condition on the retained cohort and analysis choices and do not establish external or educational validity.

## 12. Draft response to the reviewer

> Thank you for highlighting the distinction between an interpretable clustering solution and evidence of well-separated learner classes. We agree that the silhouette of 0.309 represents modest separation. The accompanying analysis now reports the complete preprocessing and K-means settings and clarifies that PCA served only to visualize the full-feature solution; the two plotted components explain 61.87% of variance. Initialization sensitivity, 500 learner-bootstrap replicates with ARI and cluster-wise Jaccard summaries, out-of-bag membership reproduction, subsampling with k reselection, and alternative-method/feature sensitivity are reported. These analyses show highly reproducible multi-start fits (100/100 identical partitions) and substantial overall resampling stability (mean bootstrap ARI=0.919), with k=3 selected in 190/200 subsamples (95.0%). However, the n=15 profile has lower separation (mean silhouette=0.184), two negative silhouettes, and weaker bootstrap overlap (mean Jaccard=0.816); agreement also varies between Ward clustering (ARI=0.982) and the Gaussian mixture (ARI=0.264). Accordingly, the proposed labels should be presented as explicitly exploratory behavioral profiles, with overlapping boundaries and no claim of definitive learner classification. The numerical results and proposed manuscript text are supplied here for incorporation into the revision.

This response describes the completed analyses. It does not claim that manuscript files have already been edited. If the source manuscript still describes PCA before clustering, that method text needs correction to match this workflow.

## 13. Reproducibility and source definitions

The existing initialization/bootstrap/PCA/alternative-method tables were reused and checked against a fresh baseline reconstruction. The new per-learner bootstrap and k-reselection analyses were executed for this focused report. Files in this folder include new diagnostics, a consolidated Excel workbook and research figures; reference CSVs stay in the parent clustering folder rather than being duplicated. and a source/code hash manifest. Raw participant identifiers appear only in the detailed learner diagnostic files, not in the narrative report. Package versions and sample seeds are recorded in the manifest.

- [Silhouette definition and interpretation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_samples.html)
- [Adjusted Rand index](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html)
- [PCA and explained variance](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [Clustering assumptions and evaluation](https://scikit-learn.org/stable/modules/clustering.html)
