# Gitainment behavior analysis

One reproducible workflow for gameplay extraction, exploratory clustering, transition
analysis, source verification, and the F1–F14 SPSS table.

**11 indicators → median imputation → log1p of non-rate indicators → standardization → K-means.**

PCA is used **only for visualization**. The retained solution contains 104 learners
in three exploratory clusters (57, 32, and 15). F12–F14 are profiling indicators, not
clustering inputs. Original source datasets and the manuscript are preserved.

## Install and run

Python 3.10 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[reports,spss]'
MPLBACKEND=Agg gitainment-analysis
```

The command rebuilds every retained output under `results/`. Defaults are 500 learner
bootstrap replicates, 200 subsamples, and 100 random seeds per initialization condition.
Options: `--output-dir`, `--bootstrap`, `--subsamples`, `--seeds`.

## Project layout

```text
Data/                         Original gameplay exports and supplied test workbook
ManuScript/                   Original Word manuscript
src/gitainment_analysis/
  data_io.py                  Shared paths and JSON/flattened-CSV loading
  run_analysis.py             Single pipeline and command-line entry point
  extraction/                 Events, player saves, leaderboards, learner aggregation
  analysis/                   Clustering, transitions, stability, efficiency/source audit
  reporting/                  Cluster report, shared formatting, SPSS export and PDF guide
tests/                        Focused regression checks
results/
  extracted/                  Four normalized input tables and one learner feature table
  clustering/                 Memberships, profiles, ANOVA, audits, stability and figures
    report/                   Word/Markdown report and supporting diagnostic tables
  transitions/                Counts, estimates, uncertainty, sensitivity and figures
  spss/                       One SAV dataset, one Excel workbook, syntax and PDF guide
  run_manifest.json           Input/code hashes, settings and package versions
```

Older loose files, duplicate CSV exports, alternative PCA-clustering workflows, unused
survey/learning-outcome scripts, and unrelated generated analyses have been removed.
The raw Version-2 CSVs remain because the pipeline uses them as source data. The supplied
pre/post workbook and manuscript remain research source documents; this clustering
pipeline does not merge unverified participant identifiers or analyze that workbook.

## Which file to use in SPSS

**[results/spss/Table9_F1_F14_Data.sav](results/spss/Table9_F1_F14_Data.sav)**

Use **Cluster** as the factor and **F1–F14** as dependent variables in One-Way ANOVA.
The [PDF guide](results/spss/SPSS_Table9_Step_by_Step_Guide.pdf) gives step-by-step instructions.
The Excel workbook contains the same learner data, feature-code definitions, valid n,
means/SDs and reference ANOVAs. Separate CSV copies of these sheets are not generated.

- Cluster 1: Sustained Engagers, n=57.
- Cluster 2: Low Activity Learners, n=32.
- Cluster 3: Struggling Learners, n=15.

Observed values and missingness are preserved for ANOVA; the clustering imputations
are not inserted into descriptive tests. Use per-indicator missing-value exclusion.
F8 has 94 observed values (57/25/12); the Cluster 2 SD is **2,462.67**, not 246.67.
F9–F11 are already percentages. F14 uses raw game-score points consistently.

## Methods and limitations

The 11 clustering inputs are CommandsExecuted, CorrectActions, FailedActions, HintQuests,
AnswerQuests, PlayDurationMinutes, LeaderboardInteractions, LearningEfficiency,
AccuracyRate, PerfectQuestRate and HelpDependencyRatio. StageClearOccurrences, GameProgress
and TotalScore are used for profiling only. LearningEfficiency is game-score points per
minute, not measured learning gain. StageClearOccurrences is not a completed-quest count.

K-means uses Euclidean distance, k-means++ initialization, 50 starts and reference seed 42.
Candidate k=2–10 solutions are ranked by silhouette and Calinski–Harabasz scores,
excluding singleton solutions. Both criteria select k=3. PCA displays the assignments
in two dimensions; no principal-component scores enter K-means.

Labels remain exploratory. Modest separation, sampling uncertainty and model dependence
limit their interpretation. ANOVAs of clustering inputs are descriptive, not independent
validation of learner types. Update manuscript wording if it still states PCA before
clustering or different indicator roles. The pipeline does not overwrite the manuscript.

## Useful commands

```bash
# Regenerate the report after a full run.
gitainment-cluster-report --results-dir results/clustering

# Regenerate the single SPSS export.
gitainment-export-anova --results-dir results/clustering --export-dir results/spss

# Regression tests.
python -m unittest discover -s tests -v
```

`requirements-reproduced.txt` records direct dependency versions used for the current
run. `results/run_manifest.json` records input/code hashes. Learner-level exports contain
identifiers; inspect them before sharing.

## Username-linked pretest/posttest comparison (R1-Q7)

`Data/R1-Q7/Score-Username.xlsx` now supplies an explicit username-to-test-score link.
Run the independent-outcome analysis after the clustering pipeline:

```bash
MPLBACKEND=Agg gitainment-profile-outcomes
```

This command validates one-to-one username linkage and supplied cluster labels against
`results/clustering/analysis_kmeans_assignments.csv`, corroborates the other two R1-Q7
workbooks, and analyzes observed pre/post scores for the matched learners. It reports
pretest-adjusted posttest comparisons with HC3 inference, Holm-corrected contrasts,
secondary gains, common-support and leave-one-out checks, and learner-bootstrap CIs.
It does not rerun or change clustering. The primary model and conventional ANCOVA
reference statistics are explicitly distinguished.

Outputs are in `results/profile_outcomes/`. To ask ChatGPT to revise the manuscript,
provide the latest manuscript, `R1_Q7_Analysis_Report.docx`, `Evidence_For_ChatGPT.xlsx`,
and `ChatGPT_Revision_Prompt.txt`. The evidence workbook uses anonymous learner IDs.
`Matched_Username_Data_PRIVATE.xlsx` is for the authors' identity audit, not needed
for the ChatGPT revision. The SAV and SPSS syntax allow author-side verification.

The questionnaire has no identifiers, so profile-perception associations cannot be
estimated. Keep anonymous questionnaire analyses separate and do not match respondents
by row order. Profile-outcome associations remain exploratory and observational;
ceiling effects, small cluster size and cluster-assignment uncertainty remain limitations.
