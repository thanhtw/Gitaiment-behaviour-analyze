# Behavioral Analysis Methods

See [the feature explanation](BEHAVIORAL_FEATURE_EXPLANATION.md) for the meaning of each indicator and why correct actions can exceed Git commands.

The Python workflow combines Version-1 JSON and Version-2 CSV exports. See [data provenance](DATA_DICTIONARY.md), [column definitions](COLUMN_DICTIONARY.md), and [current results](ANALYSIS_RESULTS_GUIDE.md).

## Run

From the repository root in the analysis Python environment:

```powershell
python Extract-Data-Code/run_analysis.py
```

To rerun clustering and its transition figures using existing extracted data:

```powershell
python -c "import sys; sys.path.insert(0, 'Extract-Data-Code'); import cluster_profile_analysis as c; c.main('Analysis-Log-Results'); import behavior_transition_analysis as b; b.main('Analysis-Log-Results')"
```

Regression checks:

```powershell
python -m unittest discover -s Extract-Data-Code -p test_cluster_profile_analysis.py
```

The analysis environment requires NumPy, pandas, SciPy, scikit-learn, statsmodels (for Welch ANOVA), matplotlib, and networkx.

## Data preparation and noise filtering

Clustering uses the 11 behavioral and derived inputs listed in the column dictionary. Original source data and the combined per-user table are preserved.

1. Exclude profiles with negative/nonfinite feature values, proportions above one, or no observed commands, actions, help use, play duration, or leaderboard interactions.
2. Leave ratios with missing or zero denominators as missing. Remove constant/all-missing features and median-impute the remaining missing values.
3. Apply `log1p` to counts, duration, and learning efficiency, then standardize all features. Accuracy, perfect-quest rate, and help-dependency ratio remain unlogged.
4. Flag local outliers using Local Outlier Factor with up to 20 neighbors and exclude scores greater than 2.0. This threshold is fixed before K selection and does not force an exclusion percentage.
5. Refit imputation and scaling on retained participants for clustering only. Descriptive profiles and statistical tests use observed values in original units, excluding missing values separately for each indicator. Standardized profiles describe the imputed/transformed clustering representation.

Every participant appears in `analysis_cluster_noise_audit.csv`, with the inclusion decision, reason, and outlier score. Statistical outliers are candidate noise, not confirmed data errors.

## Select K using two scores

Only **silhouette** and **Calinski-Harabasz** determine K. Both scores are higher-is-better.

- Fit K-means for K=2 through 10, limited by sample size and distinct feature vectors. Use 50 initializations and random seed 42 for every candidate and the final fit.
- Exclude solutions containing singleton clusters. There is no percentage-based minimum group size.
- Rank eligible solutions separately by descending silhouette and Calinski-Harabasz scores, with tied scores sharing a rank.
- Select the smallest sum of the two ranks. A shared maximum of both scores wins automatically. Tied sums use higher silhouette, then smaller K.
- If the scores have no shared maximum, report the selection as a compromise and flag disagreement. A search-boundary selection is also flagged.
- Repeat the same two-score decision before statistical outlier exclusions to show sensitivity to filtering; invalid/inactive profiles remain excluded.

The rank sum gives each score equal rank weight without adding values measured on different scales. It is an explicit decision rule, not proof of a unique population partition.

Separate figures show each score across K:

- `figure_cluster_silhouette.png`
- `figure_cluster_calinski_harabasz.png`

`analysis_cluster_selection_methods.csv` contains both scores, ranks, eligibility, and the selected K. `analysis_cluster_selection_summary.json` records the rule, sample counts, score recommendations, and any warnings. Obsolete selection figures and tables are moved to `Analysis-Log-Results/previous_cluster_selection/`.

## Profiles, sequences, and transitions

Cluster profiles report observed means, medians, standard deviations, valid counts, missing counts, and total cluster membership. An observed zero is retained; a missing value is never substituted into descriptive means or tests. Denominators can therefore differ between indicators. Standardized feature means still describe the imputed/transformed data used for clustering.

One-way ANOVA, Kruskal-Wallis, and eta-squared use the same observed observations for each indicator. Test exports include total and per-cluster valid counts, missing counts, and an explicit status. Tests are not calculated when any cluster has fewer than two observed values or an indicator is constant overall. The Kruskal-Wallis small-group flag identifies groups with fewer than five observations. Median-centered Levene results flag evidence of unequal variances at p<0.05; this diagnostic does not certify normality, independence, or choose another test automatically. Ordinary ANOVA retains its equal-variance assumption: consult [SciPy's ANOVA documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html). P-values are unadjusted for multiple testing.

Learning efficiency contains total score, so score comparisons are not independent of cluster construction; comparisons of clustering inputs are descriptive rather than independent validation. If confirmatory comparisons are required, first verify participant eligibility and logging coverage, assess the model assumptions, and specify an appropriate inference and multiplicity procedure.

Welch ANOVA is exported as a supplementary unequal-variance mean comparison for every indicator where each group has at least two observed values and positive sample variance. It uses [statsmodels `anova_oneway(use_var='unequal')`](https://www.statsmodels.org/v0.14.3/generated/statsmodels.stats.oneway.anova_oneway.html), independently of the Levene p-value. `welch_status` records why a result is unavailable, including `zero_variance_group`. Welch does not resolve dependence, data-derived grouping, or all distributional concerns. Eta-squared remains the descriptive between-group/total sum-of-squares effect size, not a Welch-specific effect size.

`analysis_cluster_profile_audit.csv` identifies missing observations and records any value imputed for clustering, plus review-only flags for stage clears with zero saved commands. Those flags do not trigger exclusion. Correct-action events can represent tutorial UI actions without Git commands. Stage-clear counts include repetitions and must not be interpreted as distinct stages.

Sequence analysis orders events within each player. It counts three events preceding perfect or help-assisted quest completion, and two events preceding a failed action followed by that failure. The top 50 patterns per outcome are exported. Sequences never cross player boundaries.

Cluster-specific transitions use retained participants and six states: action, exploration, command manipulation, instructional material/help, failure, and reward/progression. Exact event mappings are in `analysis_behavior_state_dictionary.csv`. Transition probability equals a pair's count divided by all transitions leaving its current state. Diagrams show probabilities of at least 0.15 with at least five observations; tables retain all observed transitions.

These results are exploratory and sample-dependent. Event frequencies and transition probabilities describe associations; they do not establish causality. Repeated events within players are dependent.
