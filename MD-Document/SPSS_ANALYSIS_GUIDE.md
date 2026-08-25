# SPSS Analysis Guide for GiTaiment Data
# =======================================
# Step-by-Step Instructions for Statistical Analysis

---

## Table of Contents

1. [Importing Data into SPSS](#1-importing-data-into-spss)
2. [Setting Up Variable Properties](#2-setting-up-variable-properties)
3. [Descriptive Statistics](#3-descriptive-statistics)
4. [Research Question 1: Help-Seeking Effects](#4-rq1-help-seeking-effects)
5. [Research Question 2: Dropout Prediction](#5-rq2-dropout-prediction)
6. [Research Question 3: Learning Trajectories](#6-rq3-learning-trajectories)
7. [Research Question 4: Stage Difficulty](#7-rq4-stage-difficulty)
8. [Advanced Analyses](#8-advanced-analyses)
9. [Creating Tables for Publication](#9-creating-tables-for-publication)
10. [Creating Figures](#10-creating-figures)

---

## 1. Importing Data into SPSS

### Step 1.1: Open SPSS
1. Launch IBM SPSS Statistics
2. Select "Open another file" or go to **File > Open > Data**

### Step 1.2: Import CSV File
1. Navigate to your data folder
2. Change file type to **"CSV (*.csv)"**
3. Select **`analysis_spss_ready.csv`**
4. Click **Open**

### Step 1.3: Text Import Wizard
1. **Step 1 of 6**: Select "Yes" for variable names in first row
2. **Step 2 of 6**: Keep default delimiter (comma)
3. **Step 3 of 6**: Keep "First case begins on line 2"
4. **Step 4 of 6**: Keep defaults for delimiters
5. **Step 5 of 6**: Review variables, click **Next**
6. **Step 6 of 6**: Click **Finish**

### Step 1.4: Save as SPSS File
1. **File > Save As**
2. Save as **`GiTaiment_Analysis.sav`**

---

## 2. Setting Up Variable Properties

### Step 2.1: Open Variable View
Click the **Variable View** tab at the bottom of the Data Editor

### Step 2.2: Define Measurement Levels

Set the **Measure** column for each variable:

| Variable | Measure | Type |
|----------|---------|------|
| ID | Nominal | String |
| HelpCategory | Ordinal | Numeric |
| HintTimingCategory | Nominal | Numeric |
| ProgressCategory | Ordinal | Numeric |
| IsDropout | Nominal | Numeric |
| TrajectoryType | Nominal | Numeric |
| All other numeric variables | Scale | Numeric |

### Step 2.3: Add Value Labels

#### For HelpCategory:
1. Click the **Values** cell for HelpCategory
2. Click the **...** button
3. Add labels:
   - 1 = "Independent"
   - 2 = "Low Help"
   - 3 = "Moderate Help"
   - 4 = "High Help"
4. Click **OK**

#### For HintTimingCategory:
- 0 = "Never Used"
- 1 = "Early Adopter"
- 2 = "Late Adopter"

#### For ProgressCategory:
- 1 = "Dropout"
- 2 = "Low Progress"
- 3 = "Medium Progress"
- 4 = "High Progress"
- 5 = "Complete"

#### For IsDropout:
- 0 = "Active"
- 1 = "Dropout"

#### For TrajectoryType:
- 1 = "Improving"
- 2 = "Stable"
- 3 = "Declining"

### Step 2.4: Set Missing Values
For **QuestsBeforeFirstHint**:
1. Click **Missing** cell
2. Select "Discrete missing values"
3. Enter: -1
4. Click **OK**

---

## 3. Descriptive Statistics

### Step 3.1: Overall Sample Description

**Menu Path**: Analyze > Descriptive Statistics > Descriptives

**Variables to include**:
- TotalEvents
- TotalSessions
- PlayTimeMinutes
- QuestsCompleted
- GameProgress
- TotalScore
- StagesCleared

**Options**: Check Mean, Std. Deviation, Minimum, Maximum

**Syntax**:
```spss
DESCRIPTIVES VARIABLES=TotalEvents TotalSessions PlayTimeMinutes 
  QuestsCompleted GameProgress TotalScore StagesCleared
  /STATISTICS=MEAN STDDEV MIN MAX.
```

### Step 3.2: Frequency Tables for Categorical Variables

**Menu Path**: Analyze > Descriptive Statistics > Frequencies

**Variables**:
- HelpCategory
- ProgressCategory
- TrajectoryType
- IsDropout

**Syntax**:
```spss
FREQUENCIES VARIABLES=HelpCategory ProgressCategory TrajectoryType IsDropout
  /ORDER=ANALYSIS.
```

### Step 3.3: Crosstabulation

**Menu Path**: Analyze > Descriptive Statistics > Crosstabs

**Row**: HelpCategory
**Column**: ProgressCategory

**Statistics**: Chi-square, Phi and Cramer's V

**Syntax**:
```spss
CROSSTABS
  /TABLES=HelpCategory BY ProgressCategory
  /FORMAT=AVALUE TABLES
  /STATISTICS=CHISQ PHI
  /CELLS=COUNT ROW COLUMN TOTAL.
```

---

## 4. RQ1: Help-Seeking Effects on Performance

### Research Question
**"How does help-seeking behavior affect learning outcomes?"**

### Analysis 4.1: Correlation Analysis

**Menu Path**: Analyze > Correlate > Bivariate

**Variables**:
- HelpRatio
- HintRatio
- AnswerRatio
- GameProgress
- TotalScore
- StagesCleared
- PerfectRatio

**Options**: Pearson, Two-tailed, Flag significant

**Syntax**:
```spss
CORRELATIONS
  /VARIABLES=HelpRatio HintRatio AnswerRatio GameProgress TotalScore 
    StagesCleared PerfectRatio
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.
```

**How to Report**:
> "Pearson correlation analysis revealed a significant negative relationship between help-seeking ratio and game progress (r = -.XX, p < .05)."

### Analysis 4.2: Compare Groups by Help Category

**Menu Path**: Analyze > Compare Means > One-Way ANOVA

**Dependent Variables**: GameProgress, TotalScore, PerfectRatio
**Factor**: HelpCategory

**Post Hoc**: Tukey HSD (if significant)
**Options**: Descriptive, Homogeneity of variance test

**Syntax**:
```spss
ONEWAY GameProgress TotalScore PerfectRatio BY HelpCategory
  /STATISTICS DESCRIPTIVES HOMOGENEITY
  /MISSING ANALYSIS
  /POSTHOC=TUKEY ALPHA(0.05).
```

**How to Report**:
> "One-way ANOVA indicated significant differences in game progress across help-seeking categories, F(3, 47) = X.XX, p < .05, η² = .XX."

### Analysis 4.3: Independent Samples T-Test (Early vs Late Hint Users)

**Menu Path**: Analyze > Compare Means > Independent-Samples T Test

**Test Variable**: GameProgress, TotalScore
**Grouping Variable**: HintTimingCategory
**Define Groups**: 1 and 2 (excluding 0=Never)

**First, filter out "Never Used"**:
```spss
USE ALL.
SELECT IF (HintTimingCategory > 0).
EXECUTE.

T-TEST GROUPS=HintTimingCategory(1 2)
  /MISSING=ANALYSIS
  /VARIABLES=GameProgress TotalScore
  /CRITERIA=CI(.95).
```

**How to Report**:
> "Early hint adopters (M = XX.X, SD = XX.X) showed significantly lower game progress than late adopters (M = XX.X, SD = XX.X), t(XX) = X.XX, p < .05, d = X.XX."

### Analysis 4.4: Multiple Regression

**Menu Path**: Analyze > Regression > Linear

**Dependent**: GameProgress
**Independent (Method: Enter)**:
- PlayTimeMinutes
- HelpRatio
- FailureRate
- ManualOpens
- LeaderboardChecks

**Statistics**: Estimates, Model fit, R squared change, Collinearity diagnostics

**Syntax**:
```spss
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL CHANGE
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT GameProgress
  /METHOD=ENTER PlayTimeMinutes HelpRatio FailureRate ManualOpens LeaderboardChecks.
```

**How to Report**:
> "Multiple regression analysis revealed that the model significantly predicted game progress, F(5, 45) = X.XX, p < .001, R² = .XX. Help ratio (β = -.XX, p < .05) and failure rate (β = -.XX, p < .01) were significant negative predictors."

---

## 5. RQ2: Dropout Prediction

### Research Question
**"What behavioral indicators predict player dropout?"**

### Analysis 5.1: Compare Dropout vs Active Groups

**Menu Path**: Analyze > Compare Means > Independent-Samples T Test

**Test Variables**: 
- TotalEvents
- FailureRate
- ManualOpens
- LeaderboardChecks
- QuestsCompleted

**Grouping Variable**: IsDropout (0, 1)

**Syntax**:
```spss
T-TEST GROUPS=IsDropout(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=TotalEvents FailureRate ManualOpens LeaderboardChecks QuestsCompleted
  /CRITERIA=CI(.95).
```

### Analysis 5.2: Logistic Regression (Predicting Dropout)

**Menu Path**: Analyze > Regression > Binary Logistic

**Dependent**: IsDropout
**Covariates** (Method: Enter):
- FailureRate
- ManualOpens
- LeaderboardChecks
- EventsPerSession

**Options**: Classification plots, Hosmer-Lemeshow goodness-of-fit

**Syntax**:
```spss
LOGISTIC REGRESSION VARIABLES IsDropout
  /METHOD=ENTER FailureRate ManualOpens LeaderboardChecks EventsPerSession
  /CLASSPLOT
  /PRINT=GOODFIT CI(95)
  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5).
```

**How to Report**:
> "Logistic regression was conducted to predict dropout status. The model was statistically significant, χ²(4) = XX.XX, p < .001, explaining XX.X% (Nagelkerke R²) of the variance. Failure rate (OR = X.XX, 95% CI [X.XX, X.XX]) was a significant predictor of dropout."

### Analysis 5.3: ROC Curve for Prediction Accuracy

**Menu Path**: Analyze > Regression > Binary Logistic
(Use "Save" button to save predicted probabilities)

Then: Analyze > ROC Curve

**Syntax**:
```spss
* First save predicted probabilities from logistic regression.
* Then create ROC curve.
ROC PRE_1 BY IsDropout (1)
  /PLOT=CURVE(REFERENCE)
  /PRINT=SE COORDINATES
  /CRITERIA=CUTOFF(INCLUDE) TESTPOS(LARGE) DISTRIBUTION(FREE) CI(95).
```

---

## 6. RQ3: Learning Trajectories

### Research Question
**"How do player performance levels change over gameplay?"**

### Analysis 6.1: Frequency of Trajectory Types

**Syntax**:
```spss
FREQUENCIES VARIABLES=TrajectoryType
  /ORDER=ANALYSIS.
```

### Analysis 6.2: Paired Samples T-Test (Early vs Late Performance)

**Menu Path**: Analyze > Compare Means > Paired-Samples T Test

**Pair 1**: EarlyScore - LateScore

**Syntax**:
```spss
T-TEST PAIRS=EarlyScore WITH LateScore (PAIRED)
  /CRITERIA=CI(.9500)
  /MISSING=ANALYSIS.
```

**How to Report**:
> "A paired-samples t-test revealed no significant difference between early-game performance (M = X.XX, SD = X.XX) and late-game performance (M = X.XX, SD = X.XX), t(XX) = X.XX, p = .XX."

### Analysis 6.3: Compare Trajectory Groups

**Menu Path**: Analyze > Compare Means > One-Way ANOVA

**Dependent**: GameProgress, TotalScore, QuestsCompleted
**Factor**: TrajectoryType

**Syntax**:
```spss
ONEWAY GameProgress TotalScore QuestsCompleted BY TrajectoryType
  /STATISTICS DESCRIPTIVES HOMOGENEITY
  /MISSING ANALYSIS
  /POSTHOC=TUKEY ALPHA(0.05).
```

### Analysis 6.4: Chi-Square Test (Trajectory × Dropout)

**Menu Path**: Analyze > Descriptive Statistics > Crosstabs

**Syntax**:
```spss
CROSSTABS
  /TABLES=TrajectoryType BY IsDropout
  /FORMAT=AVALUE TABLES
  /STATISTICS=CHISQ PHI
  /CELLS=COUNT ROW COLUMN TOTAL.
```

---

## 7. RQ4: Stage Difficulty Analysis

### Research Question
**"Which stages present the greatest learning challenges?"**

### Analysis 7.1: Repeated Measures ANOVA (Stage Type Clear Rates)

**Note**: Need to restructure data for this. Use descriptives instead:

**Syntax**:
```spss
DESCRIPTIVES VARIABLES=BasicClearRate BranchClearRate RemoteClearRate
  /STATISTICS=MEAN STDDEV MIN MAX.
```

### Analysis 7.2: Paired Comparisons

**Menu Path**: Analyze > Compare Means > Paired-Samples T Test

**Pairs**:
- BasicClearRate - BranchClearRate
- BranchClearRate - RemoteClearRate
- BasicClearRate - RemoteClearRate

**Syntax**:
```spss
T-TEST PAIRS=BasicClearRate WITH BranchClearRate (PAIRED)
  BasicClearRate WITH RemoteClearRate (PAIRED)
  BranchClearRate WITH RemoteClearRate (PAIRED)
  /CRITERIA=CI(.9500)
  /MISSING=ANALYSIS.
```

**How to Report**:
> "Paired-samples t-tests revealed significant decreases in clear rates from Basic (M = .XX) to Branch (M = .XX), t(XX) = X.XX, p < .05, and from Branch to Remote (M = .XX), t(XX) = X.XX, p < .05, confirming the intended difficulty progression."

---

## 8. Advanced Analyses

### Analysis 8.1: Hierarchical Multiple Regression

**Purpose**: Test if help-seeking adds predictive power beyond engagement

**Step 1 Variables**: PlayTimeMinutes, TotalSessions
**Step 2 Variables**: HelpRatio, FailureRate

**Syntax**:
```spss
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA CHANGE
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN 
  /DEPENDENT GameProgress
  /METHOD=ENTER PlayTimeMinutes TotalSessions
  /METHOD=ENTER HelpRatio FailureRate.
```

### Analysis 8.2: Mediation Analysis

**Purpose**: Test if FailureRate mediates Help-Seeking → Performance

**Use PROCESS macro by Andrew Hayes** (download separately)

Or use Baron & Kenny steps:

**Step 1**: HelpRatio → GameProgress
**Step 2**: HelpRatio → FailureRate
**Step 3**: HelpRatio + FailureRate → GameProgress

**Syntax**:
```spss
* Step 1: Direct effect.
REGRESSION
  /DEPENDENT GameProgress
  /METHOD=ENTER HelpRatio.

* Step 2: Path a.
REGRESSION
  /DEPENDENT FailureRate
  /METHOD=ENTER HelpRatio.

* Step 3: Mediation test.
REGRESSION
  /DEPENDENT GameProgress
  /METHOD=ENTER HelpRatio FailureRate.
```

### Analysis 8.3: Cluster Analysis (Player Segmentation)

**Menu Path**: Analyze > Classify > K-Means Cluster

**Variables**: 
- GameProgress_Z
- HelpRatio_Z
- PlayTimeMinutes_Z

**Number of Clusters**: 3 or 4

**Syntax**:
```spss
QUICK CLUSTER GameProgress_Z HelpRatio_Z PlayTimeMinutes_Z
  /MISSING=LISTWISE
  /CRITERIA=CLUSTER(3) MXITER(10) CONVERGE(0)
  /METHOD=KMEANS(NOUPDATE)
  /SAVE CLUSTER
  /PRINT INITIAL ANOVA CLUSTER DISTAN.
```

---

## 9. Creating Tables for Publication

### Table 1: Sample Descriptive Statistics

**Syntax**:
```spss
DESCRIPTIVES VARIABLES=TotalEvents TotalSessions PlayTimeMinutes 
  QuestsCompleted GameProgress TotalScore StagesCleared HelpRatio FailureRate
  /STATISTICS=MEAN STDDEV MIN MAX.
```

**Format for Paper**:

| Variable | M | SD | Min | Max |
|----------|---|----|----|-----|
| Total Events | XXX.XX | XXX.XX | XX | XXXX |
| Play Time (min) | XXX.XX | XXX.XX | XX | XXXX |
| Game Progress (%) | XX.XX | XX.XX | 0 | 100 |
| Help Ratio | .XX | .XX | 0 | 1 |

### Table 2: Correlation Matrix

**Syntax**:
```spss
CORRELATIONS
  /VARIABLES=HelpRatio FailureRate ManualOpens GameProgress TotalScore
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.
```

### Table 3: Regression Results

Copy from SPSS output and format:

| Predictor | B | SE | β | t | p |
|-----------|---|----|----|---|---|
| (Constant) | XX.XX | XX.XX | | X.XX | .XXX |
| Help Ratio | -XX.XX | XX.XX | -.XX | -X.XX | .XXX |
| Failure Rate | -XX.XX | XX.XX | -.XX | -X.XX | .XXX |

---

## 10. Creating Figures

### Figure 1: Bar Chart - Help Category Performance

**Menu Path**: Graphs > Legacy Dialogs > Bar > Simple

**Syntax**:
```spss
GRAPH
  /BAR(SIMPLE)=MEAN(GameProgress) BY HelpCategory.
```

### Figure 2: Scatter Plot - Help Ratio vs Progress

**Menu Path**: Graphs > Legacy Dialogs > Scatter/Dot > Simple Scatter

**Syntax**:
```spss
GRAPH
  /SCATTERPLOT(BIVAR)=HelpRatio WITH GameProgress
  /MISSING=LISTWISE.
```

Add trend line: Double-click chart, Elements > Fit Line at Total

### Figure 3: Boxplot - Dropout vs Active

**Syntax**:
```spss
GRAPH
  /BOXPLOT(SIMPLE)=FailureRate BY IsDropout.
```

### Figure 4: Line Chart - Stage Difficulty Progression

**Syntax**:
```spss
* Create summary data first.
GRAPH
  /BAR(SIMPLE)=MEAN(BasicClearRate) MEAN(BranchClearRate) MEAN(RemoteClearRate).
```

### Figure 5: Pie Chart - Trajectory Distribution

**Syntax**:
```spss
GRAPH
  /PIE=COUNT BY TrajectoryType.
```

---

## Quick Reference: Key Analyses Summary

| Research Question | Analysis | SPSS Menu |
|-------------------|----------|-----------|
| Help-seeking effect | Correlation | Analyze > Correlate > Bivariate |
| Help-seeking effect | ANOVA | Analyze > Compare Means > One-Way ANOVA |
| Help-seeking effect | Regression | Analyze > Regression > Linear |
| Dropout prediction | T-Test | Analyze > Compare Means > Independent T-Test |
| Dropout prediction | Logistic Regression | Analyze > Regression > Binary Logistic |
| Learning trajectory | Paired T-Test | Analyze > Compare Means > Paired T-Test |
| Stage difficulty | Paired T-Test | Analyze > Compare Means > Paired T-Test |
| Player segmentation | Cluster Analysis | Analyze > Classify > K-Means |

---

## Reporting Guidelines

### Effect Size Guidelines
| Test | Effect Size | Small | Medium | Large |
|------|-------------|-------|--------|-------|
| Correlation | r | .10 | .30 | .50 |
| T-Test | d | .20 | .50 | .80 |
| ANOVA | η² | .01 | .06 | .14 |
| Regression | R² | .02 | .13 | .26 |

### APA Format Examples

**Correlation**:
> There was a significant negative correlation between help ratio and game progress, r(49) = -.34, p = .014.

**T-Test**:
> Active players (M = 672.11, SD = 400.23) showed significantly more events than dropout players (M = 69.67, SD = 50.12), t(27) = 4.56, p < .001, d = 2.10.

**ANOVA**:
> There was a significant effect of help category on game progress, F(3, 47) = 4.23, p = .010, η² = .21.

**Regression**:
> The regression model significantly predicted game progress, F(5, 45) = 12.34, p < .001, R² = .58. Help ratio was a significant negative predictor (β = -.28, p = .023).

**Logistic Regression**:
> Failure rate significantly predicted dropout (B = 15.23, SE = 4.56, Wald = 11.15, p < .001, OR = 4.12, 95% CI [2.34, 7.25]).

---

## Troubleshooting

### Common Issues

1. **"Missing values"**: Use Analyze > Missing Value Analysis to check patterns

2. **"Non-normal distribution"**: 
   - Check with Shapiro-Wilk test
   - Use non-parametric alternatives if needed

3. **"Homogeneity of variance violated"**:
   - Use Welch's t-test instead
   - Report Games-Howell post-hoc for ANOVA

4. **"Multicollinearity in regression"**:
   - Check VIF values (should be < 5)
   - Remove highly correlated predictors

---

## Files Reference

| File | Description |
|------|-------------|
| `analysis_spss_ready.csv` | Main data file (73 variables, 51 cases) |
| `SPSS_CODEBOOK.md` | Variable definitions and codes |
| `SPSS_ANALYSIS_GUIDE.md` | This guide |

---

*Guide created for GiTaiment research paper preparation*
*Last updated: December 2024*
