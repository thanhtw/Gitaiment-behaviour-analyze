CD '/home/selab/Desktop/Thomas/Gitaiment-behaviour-analyze/results/profile_outcomes'.
GET FILE='Profile_Learning_Outcomes.sav'.
FILTER OFF.
WEIGHT OFF.
SPLIT FILE OFF.

* Primary common-slope ANCOVA. ROBUST adds HC3 parameter/custom-hypothesis output.
* The standard Tests of Between-Subjects Effects remain conventional: do not mix them with HC3.
UNIANOVA PostTest BY Cluster WITH PreCentered
 /METHOD=SSTYPE(3)
 /ROBUST=HC3
 /PRINT=DESCRIPTIVE HOMOGENEITY PARAMETER ETASQ
 /LMATRIX='Overall cluster HC3' Cluster 1 -1 0; Cluster 1 0 -1
 /LMATRIX='Profile 1 minus 2 HC3' Cluster 1 -1 0
 /LMATRIX='Profile 1 minus 3 HC3' Cluster 1 0 -1
 /LMATRIX='Profile 2 minus 3 HC3' Cluster 0 1 -1
 /LMATRIX='Profile 1 adjusted mean HC3' INTERCEPT 1 Cluster 1 0 0
 /LMATRIX='Profile 2 adjusted mean HC3' INTERCEPT 1 Cluster 0 1 0
 /LMATRIX='Profile 3 adjusted mean HC3' INTERCEPT 1 Cluster 0 0 1
 /EMMEANS=TABLES(Cluster) WITH(PreCentered=0)
 /DESIGN=PreCentered Cluster.

* EMMEANS points agree, but EMMEANS CIs are conventional, not the HC3 custom-test CIs.
* LMATRIX pairwise p-values are unadjusted. Use Holm p-values from the evidence workbook.
* Or sort the three raw p-values and apply step-down multipliers 3,2,1 with cumulative maximum, capped at 1.

* Sensitivity to unequal pretest slopes. Use the robust two-df interaction hypothesis.
UNIANOVA PostTest BY Cluster WITH PreCentered
 /METHOD=SSTYPE(3)
 /ROBUST=HC3
 /PRINT=PARAMETER
 /LMATRIX='Slope interaction HC3' PreCentered*Cluster 1 -1 0; PreCentered*Cluster 1 0 -1
 /DESIGN=PreCentered Cluster PreCentered*Cluster.

* Raw learning gains are secondary; retain the Welch row, not only ordinary ANOVA.
ONEWAY Gain BY Cluster
 /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH
 /MISSING ANALYSIS.

* SPSS syntax has not been executed in the analysis environment.
* If an older version does not support ROBUST, ordinary output will not reproduce HC3 inference.
