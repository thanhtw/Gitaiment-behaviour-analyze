* Change CD to this export folder on your computer.
CD '/home/selab/Desktop/Thomas/Gitaiment-behaviour-analyze/results/spss'.
GET FILE='Table9_F1_F14_Data.sav'.
DATASET NAME Table9Data.
FILTER OFF.
WEIGHT OFF.
SPLIT FILE OFF.
* F1-F14 are dependent variables; Cluster is the factor.
ONEWAY F1 TO F14 BY Cluster
 /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH
 /MISSING ANALYSIS
 /ES OVERALL.
* For SPSS before 27, remove /ES OVERALL. Eta-squared=SS_between/SS_total.
