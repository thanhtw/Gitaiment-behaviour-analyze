# R1-Q7: learning outcomes across the three exploratory gameplay profiles

## Direct answer to the reviewer

**The new username-linked data now permit the missing learning-outcome analysis.** All 104 retained learners match; independent posttest performance differs across profiles after pretest adjustment. The questionnaire portion remains untestable because survey responses are unidentified. No perception–profile link is inferred.

## 1. Source linkage and sample

Primary source: `Data/R1-Q7/Score-Username.xlsx`, sheet `Score-Username`. `104-Pre-Post-Match-Username.xlsx` corroborates the local No/pre/post values, while `104-Username_Cluster.xlsx` corroborates the username/cluster mapping. Authoritative clusters come from `results/clustering/analysis_kmeans_assignments.csv`. Matching trims leading/trailing username whitespace only and preserves case; no row-order or score-based identity matching is performed. No is a local source record number, not the key for joining to gameplay.

| Item | Value |
| --- | --- |
| authoritative_learners | 104 |
| provided_scores | 104 |
| matched_learners | 104 |
| unmatched_gameplay_learners | 0 |
| unmatched_score_learners | 0 |
| cluster_disagreements | 0 |
| duplicate_normalized_usernames | 0 |
| missing_pretest | 0 |
| missing_posttest | 0 |
| normalization | Trim leading/trailing whitespace only; exact case preserved; no row-order or score matching |
| corroborating_score_rows | 104 |
| corroborating_mapping_rows | 104 |
| questionnaire_status | Anonymous/unidentified questionnaire; profile-perception associations cannot be estimated |

All 104 retained learners have observed scores, so no outcome imputation is performed. These are reviewer-requested analyses; no preregistration was supplied. “Primary” denotes analytic priority within this report, not evidence of prospective specification. The 11 learners excluded from the original behavioral cohort are not assigned profiles or silently included in this comparison. The source usernames have been structurally validated, but the original username-to-test identity records remain the authors’ responsibility. The scores are trusted as supplied, not independently psychometrically validated.

## 2. Descriptive learning outcomes

| Cluster | ClusterName | N | Pretest M (SD) | Posttest M (SD) | Gain M (SD) | Posttest=100 (%) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Sustained Engagers | 57 | 83.37 (13.40) | 98.77 (2.55) | 15.40 (14.17) | 78.95 |
| 2 | Low Activity Learners | 32 | 82.25 (13.02) | 95.78 (4.42) | 13.53 (14.44) | 40.62 |
| 3 | Struggling Learners | 15 | 81.27 (9.65) | 77.67 (13.21) | -3.60 (11.79) | 0 |

Gain is PostTest − PreTest in score points. High posttest ceiling proportions (78.95%, 40.63%, 0%) are an important limitation. Pretest differences are not significant by Welch’s test, but absence of significance does not prove equal baselines or remove confounding.

## 3. Primary analysis: posttest adjusted for pretest

Model: PostTest = intercept + categorical Cluster + (PreTest − 82.72115385). The profile factor has three levels; residual df=100. The dependent variable is the independent Git posttest, not in-game TotalScore or the score-per-minute behavioral indicator. Neither pretest nor posttest was used to create these fixed clusters.

Posttest variances differ strongly (median-centered Levene p=2.0306e-11). Therefore HC3 standard errors and residual-df Wald F/t tests are the primary inference. They address heteroskedasticity, not ceiling nonlinearity, cluster-selection uncertainty or unmeasured confounding.

| Test | F | DF1 | DF2 | p |
| --- | --- | --- | --- | --- |
| Primary: cluster adjusted for pretest (HC3) | 22.75 | 2 | 100 | 7.169e-09 |
| Conventional ANCOVA cluster effect | 77.79 | 2 | 100 | 4.196e-21 |
| Cluster x pretest interaction (HC3) | 1.027 | 2 | 98 | 0.362 |

Conventional ANCOVA gives F(2,100)=77.794803, p=4.19605e-21. The corresponding **classical partial eta-squared is 0.608748**, computed as (SSR_pretest-only − SSR_full) / SSR_pretest-only. This is an OLS variance-decomposition effect size, **not** an effect size calculated from the HC3 Wald F. Do not combine a robust F with a classical F-to-eta formula. Full model R²=0.610023, adjusted R²=0.598323.

Adjusted posttest means evaluated at the original pooled pretest mean:

| ClusterName | AdjustedPosttest | CI_Low_HC3 | CI_High_HC3 |
| --- | --- | --- | --- |
| Sustained Engagers | 98.76 | 98.07 | 99.46 |
| Low Activity Learners | 95.79 | 94.19 | 97.39 |
| Struggling Learners | 77.68 | 70.65 | 84.71 |

Pairwise comparisons are ClusterA − ClusterB. Confidence intervals are pointwise 95% HC3 intervals; p_Holm corrects the three pairwise p-values as a family. They are not simultaneous confidence intervals.

| ClusterA | ClusterB | Difference | CI_Low_HC3 | CI_High_HC3 | p_Holm |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 2.978 | 1.241 | 4.716 | 0.0009673 |
| 1 | 3 | 21.08 | 14.02 | 28.14 | 1.326e-07 |
| 2 | 3 | 18.1 | 10.89 | 25.32 | 5.393e-06 |

## 4. Slope, ceiling and robustness checks

The profile-by-pretest interaction has robust F(2,98)=1.026830, p=0.361961. This does not reject equal slopes using the robust test, but it does not prove equal slopes, especially with only 15 Struggling Learners. The interaction coefficients and contrasts at the same reference pretest are supplied for sensitivity.

| ClusterA | ClusterB | ReferencePretest | Difference | CI_Low_HC3 | CI_High_HC3 | p_HC3 | p_Holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 82.72 | 3.044 | 1.332 | 4.756 | 0.0006372 | 0.0006372 |
| 1 | 3 | 82.72 | 20.13 | 13.63 | 26.62 | 1.672e-08 | 5.017e-08 |
| 2 | 3 | 82.72 | 17.08 | 10.44 | 23.73 | 1.66e-06 | 3.32e-06 |

Pretest support shared by all profiles is [50, 90]. Restricting to that interval retains 87 learners with counts {'1': 44, '2': 28, '3': 15}. The original reference pretest is retained in this model. This avoids range extrapolation, although similar min/max ranges do not guarantee equal score density.

| Test | F | DF1 | DF2 | p |
| --- | --- | --- | --- | --- |
| Primary: cluster adjusted for pretest (HC3) | 21.43 | 2 | 83 | 3.129e-08 |
| Conventional ANCOVA cluster effect | 63.59 | 2 | 83 | 1.792e-17 |
| Cluster x pretest interaction (HC3) | 1.208 | 2 | 81 | 0.3041 |

| ClusterA | ClusterB | Difference | SE_HC3 | t_HC3 | DF | p_HC3 | CI_Low_HC3 | CI_High_HC3 | p_Holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 3.289 | 1.047 | 3.141 | 83 | 0.002333 | 1.206 | 5.372 | 0.002333 |
| 1 | 3 | 21.04 | 3.542 | 5.94 | 83 | 6.428e-08 | 13.99 | 28.08 | 1.928e-07 |
| 2 | 3 | 17.75 | 3.626 | 4.894 | 83 | 4.783e-06 | 10.54 | 24.96 | 9.567e-06 |

The learner bootstrap uses 5000 successful samples out of 5000, with seed 20261118. Complete pre/post records are resampled within fixed profiles, the common-slope model is refitted, and the original reference pretest is held fixed. Percentile 95% CIs are conditional on the sample, model and fixed clustering; they do not include uncertainty in assigning profiles or validate an external population.

| Quantity | BootstrapMean | CI_Low | CI_High |
| --- | --- | --- | --- |
| Adjusted_1 | 98.75 | 98.02 | 99.39 |
| Adjusted_2 | 95.75 | 94.13 | 97.2 |
| Adjusted_3 | 77.77 | 70.94 | 83.7 |
| Difference_1_2 | 2.999 | 1.39 | 4.701 |
| Difference_1_3 | 20.98 | 14.92 | 27.89 |
| Difference_2_3 | 17.98 | 11.78 | 24.86 |
| Gain_1 | 15.46 | 12.12 | 19.44 |
| Gain_2 | 13.55 | 9.219 | 19.09 |
| Gain_3 | -3.549 | -9.867 | 1.6 |

Leave-one-learner-out analysis reports ranges of estimated adjusted differences and the largest Holm-corrected p-value across all 104 deletions. These ranges are sensitivity diagnostics, not confidence intervals.

| ClusterA | ClusterB | LOO_DifferenceMin | LOO_DifferenceMax | Largest_HolmP |
| --- | --- | --- | --- | --- |
| 1 | 2 | 2.627 | 3.146 | 0.002007 |
| 1 | 3 | 19.1 | 21.97 | 1.044e-06 |
| 2 | 3 | 16.12 | 18.99 | 2.911e-05 |

The linear model can theoretically predict scores outside 0–100. Predictions and CIs are not clipped. The ceiling is structural: HC3 and bootstrap do not undo restricted score ranges or recover unobserved achievement above the maximum.

## 5. Secondary analysis: raw learning gains

Welch gain comparison: F(2,39.972025)=14.488931, p=1.85252e-05. Gains are secondary, unadjusted comparisons and share the same pre/post data; they are not an independent replication. No normalized-gain ratio is used.

| ClusterA | ClusterB | GainDifference | SE | DF | t | p | CI_Low | CI_High | p_Holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 1.872 | 3.168 | 63.36 | 0.5909 | 0.5567 | -4.459 | 8.203 | 0.5567 |
| 1 | 3 | 19 | 3.578 | 25.74 | 5.312 | 1.525e-05 | 11.65 | 26.36 | 4.576e-05 |
| 2 | 3 | 17.13 | 3.973 | 33.18 | 4.311 | 0.0001367 | 9.049 | 25.21 | 0.0002734 |

Within-profile negative average gain is not itself a test of decline. For Struggling Learners the mean is −3.60 points, with bootstrap CI [-9.867, 1.600]. Interpret the smaller gain relative to other profiles separately from evidence of absolute loss.

## 6. What can be said about perceptions

**No profile–perception test is possible from unidentified questionnaire responses.** Do not match survey rows to the usernames, profiles or test scores by ordering or by similar response patterns. Anonymous survey constructs can be analyzed within their own respondent dataset, but those results must remain separate from gameplay-profile associations. Remove or qualify any sentence implying that perceptions are individually related to the three profiles. This is a limitation of linkage, not a finding that perceptions have no relationship.

## 7. Proposed manuscript revisions

**Methods:**

Pretest and posttest scores were linked to gameplay profiles using participant usernames rather than row order. All 104 retained gameplay learners had complete linked scores. Posttest scores were modeled as a function of categorical profile and mean-centered pretest score using ordinary least-squares ANCOVA, with HC3 covariance and residual-df F/t inference for the primary tests and pointwise 95% confidence intervals. Pairwise profile contrasts were corrected using Holm’s method within the three-comparison family. A profile-by-pretest interaction model assessed sensitivity to unequal slopes. Secondary outcomes were raw gains (posttest minus pretest), compared using Welch’s ANOVA and Holm-corrected pairwise Welch tests. Additional sensitivity analyses used 5000 within-profile learner bootstrap samples, a shared-pretest-support subset, and leave-one-learner-out refits. Anonymous questionnaire responses were not linked to behavioral profiles.

**Results:**

Pretest means were 83.37, 82.25 and 81.27 for Sustained Engagers, Low Activity Learners and Struggling Learners, respectively (Welch p=0.785; this does not establish equivalence). Their posttest means were 98.77, 95.78 and 77.67. The pretest-adjusted profile effect was significant using HC3 inference (F(2,100)=22.755, p<.001). Adjusted means at pretest=82.72 were 98.76, 95.79 and 77.68. All three adjusted pairwise comparisons remained significant after Holm correction. Mean raw gains were 15.40, 13.53 and −3.60 points; secondary Welch ANOVA was significant (F(2,39.97)=14.489, p<.001). The negative mean in Struggling Learners is descriptive: its bootstrap gain CI [-9.87, 1.60] includes zero and does not independently establish a within-group decline. Pairwise gain comparisons distinguish Struggling Learners from both other profiles (Holm p=4.57609e-05 and 0.000273399), but Sustained Engagers and Low Activity Learners do not differ significantly in gains (Holm p=0.557).

**Discussion / limitation:**

The profile comparison adds educational relevance to the behavioral findings: learners assigned to the Struggling profile showed substantially lower posttest achievement after accounting for baseline performance. However, Low Activity Learners also achieved high posttest scores and positive gains, so limited logged activity should not be equated with low achievement. These are exploratory associations, not causal effects or stable learner classifications. High posttest ceilings can compress differences and obscure the relationship with baseline scores. The small Struggling profile limits precision. The anonymous questionnaire cannot support individual-level links between profile membership and perceived experience; survey findings must be discussed separately.

These are proposed replacements. No manuscript file has been edited and no page/line references are invented. The authors should insert the text where the reviewer’s claimed association is currently stated.

## 8. Draft response to the reviewer

Thank you for identifying the need to connect behavioral profiles with independent learning outcomes. We have now analyzed username-linked pretest and posttest scores for all 104 learners in the retained gameplay cohort. All usernames matched the authoritative cluster assignments, with no missing scores or cluster discrepancies (57 Sustained Engagers, 32 Low Activity Learners, and 15 Struggling Learners).

We compared posttest performance across the three profiles while accounting for pretest performance. Because posttest variances were strongly unequal and ceiling scores were common, primary inference used HC3 heteroskedasticity-robust standard errors. The pretest-adjusted cluster effect was F(2,100)=22.755, p=7.17e-09. At the overall mean pretest of 82.72, adjusted posttest means were 98.76, 95.79, and 77.68, respectively. The adjusted Sustained Engagers and Low Activity Learners advantages over Struggling Learners were 21.08 points (95% HC3 CI 14.02–28.14) and 18.10 points (95% HC3 CI 10.89–25.32); both remained significant after Holm correction.

As a secondary analysis, mean unadjusted gains were 15.40, 13.53, and -3.60 points; Welch’s test yielded F(2,39.97)=14.489, p=1.85e-05. These results indicate that the identified profiles are associated with independently measured achievement, rather than only differences in game interaction. They do not show that profile membership or help use causes learning outcomes. Ceiling effects, the n=15 profile, fixed estimated cluster membership and the single-cohort observational design remain limitations.

The questionnaire was anonymous and cannot be linked to gameplay usernames. Therefore a profile–perception association cannot be tested. The proposed revision separates the questionnaire findings from gameplay-profile findings and removes any unsupported claim that perceptions differ across or are individually associated with these profiles.

## 9. What to give ChatGPT for the manuscript revision

Upload the latest manuscript Word file, **this report** (`R1_Q7_Analysis_Report.docx`), **Evidence_For_ChatGPT.xlsx**, the exact reviewer comment, and **ChatGPT_Revision_Prompt.txt**. The workbook contains all evidence tables and anonymized learner rows. Raw usernames are unnecessary for writing the revision. Do not upload the PRIVATE linkage workbook or the username-containing SAV unless there is a specific authorized need. The report and evidence workbook are sufficient to write an evidence-based response.

`Matched_Username_Data_PRIVATE.xlsx` and `Profile_Learning_Outcomes.sav` are for the authors’ identity audit and SPSS use. `Run_Profile_ANCOVA.sps` includes HC3 custom hypothesis tests; ordinary SPSS ANOVA F and EMMEANS CIs must not be mistaken for the primary robust tests. SPSS itself is not installed here; syntax is based on IBM documentation and has not been executed in SPSS.

## Methods references

- [IBM: covariate-slope checks](https://www.ibm.com/docs/en/spss-statistics/31.0.0?topic=covariance-checking-homogeneity-covariate-coefficients)
- [IBM: HC3 and robust custom tests](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=unianova-robust-subcommand-command)
- [IBM: LMATRIX contrasts](https://www.ibm.com/docs/en/spss-statistics/32.0.0?topic=unianova-lmatrix-subcommand-command)
- [statsmodels: heteroskedasticity-robust ANOVA](https://www.statsmodels.org/stable/_modules/statsmodels/stats/anova.html)
