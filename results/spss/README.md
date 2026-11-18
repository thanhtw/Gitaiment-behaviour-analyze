# Table 9: F1–F14 data for SPSS

**Open Table9_F1_F14_Data.sav.** It has 104 learner rows and the original Table 9
clusters: 1=Sustained Engagers (57), 2=Low Activity Learners (32), and
3=Struggling Learners (15). These are the assignments underlying the attached
three-column table. K-means uses the standardized indicators directly; PCA is visualization only.

## SPSS

1. File > Open > Data: select Table9_F1_F14_Data.sav.
2. Analyze > Compare Means > One-Way ANOVA.
3. Dependent List: **F1–F14**. Factor: **Cluster**.
4. Request descriptives, homogeneity, Welch and overall effect sizes.
5. Exclude missing observations separately for each dependent variable.

Alternatively open Run_Table9_ANOVA.sps, change its CD path to your folder, and
Run > All. Eta-squared is in the overall ANOVA Effect Sizes output in SPSS 27+;
on older versions remove /ES OVERALL and calculate SS_between/SS_total.

The Excel All_Learners sheet contains the same observations. Use this combined
sheet for between-cluster ANOVA; Cluster_1/2/3 sheets are supplied for inspection.
Feature_Codes maps all 14 codes to the attached table. F1–F11 are the original
clustering inputs and F12–F14 are profile-only indicators, as the table note says.
No clustering is performed by this export; original memberships are retained.

## Verified values and corrections

The export contains observed unrounded values, not the displayed means/SDs,
PCA scores, standardized values, or clustering-imputed medians. Missing values
remain system-missing/blank. Header membership n is not every feature's valid n;
The Expected_Mean_SD_N workbook sheet lists each feature's valid/missing sample sizes.

F8 is Learning Efficiency, in raw score points/minute. Its Low Activity Learners
sample SD is **2462.67**, not **246.67** printed in the image. Valid n for F8 are
57, 25 and 12. The corrected data reproduce F(2,91)=36.253 and eta-squared=.443.

F9–F11 are already percentages on a 0–100 scale. Do not multiply them by 100 again.
F12 is the saved stage-clear counter, not the number of completed quest events.
F14 uses raw game-score points consistently: means (SDs) are
91951.75 (37937.14), 12927.42 (27308.51), and 6850.00 (5597.99).
The image's F14 formatting mixes truncation/separators; use consistent units in
both means and SDs. Scaling BOTH all F14 observations and their descriptives by
1000 is permissible for reporting in thousands of points, but must be labeled.
It does not change F, p or eta-squared.

Source player-save score/time values were checked before export. The data will
reproduce the verified ANOVA statistics, not typographical errors in the image.
These cluster comparisons are descriptive: the same F1–F11 helped define the
groups, so their ANOVAs are not independent validation of learner classes.
SPSS syntax was generated but SPSS itself has not been executed here.
