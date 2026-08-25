# Current Analysis Results Guide

This document describes the Python analysis generated on 2026-08-25. The canonical methods and interpretation guide is [PYTHON_ANALYSIS_RESEARCH_GUIDE.md](PYTHON_ANALYSIS_RESEARCH_GUIDE.md).

## Analytic sample

- Combined events: 31,630 (Version-1: 22,118; Version-2: 9,512)
- Distinct per-user profiles: 105
- Active player records with positive play time: 84
- Player-stage rows: 3,536
- Global leaderboard entries: 930

## Current clustering result

Gap Statistic selected `k=4` using 11 standardized behavioral and derived indicators.

| Cluster | Players |
|---|---:|
| 1 | 21 |
| 2 | 44 |
| 3 | 31 |
| 4 | 9 |

Sensitivity diagnostics recommended `k=5` (Silhouette), `k=2` (Calinski–Harabasz), `k=4` (Davies–Bouldin), and `k=3` (stability ARI). This disagreement must be reported; four clusters are a defensible Gap-based exploratory solution, not a uniquely proven partition.

## Main outputs

| Output | Purpose |
|---|---|
| `analysis_gap_statistic.csv` | Gap values and selected `k` |
| `analysis_cluster_selection_methods.csv` | Alternative internal-validity measures |
| `analysis_kmeans_assignments.csv` | Player membership and variables |
| `analysis_cluster_profiles.csv` | Raw profile summaries |
| `analysis_cluster_profiles_standardized.csv` | Behavioral z-score profiles |
| `analysis_cluster_group_comparisons.csv` | ANOVA, Kruskal–Wallis, and eta-squared |
| `analysis_behavior_sequences.csv` | Frequent success, help, and failure sequences |
| `analysis_behavior_transitions_by_cluster.csv` | Cluster-specific transition probabilities |

All tables and figures are in `Analysis-Log-Results`.

## Interpretation cautions

The analysis is exploratory and observational. Sequence frequency and transition probability do not demonstrate causality. Cluster labels are sample-dependent behavioral patterns. Do not report the smallest cluster membership as the number of clusters.
