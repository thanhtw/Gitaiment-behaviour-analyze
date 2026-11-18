"""Cluster-specific behavioral transition analysis and diagrams."""

from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

STATE_LABELS = {
    "A": "Action",
    "E": "Exploration",
    "CM": "Command manipulation",
    "IM": "Instructional material/help",
    "F": "Failure",
    "R": "Reward/progression",
}
STATE_ORDER = list(STATE_LABELS)
POSITIONS = {"A": (0, 2), "E": (2, 2), "CM": (0, 1), "IM": (2, 1), "F": (0, 0), "R": (2, 0)}

EVENT_TO_STATE = {
    "Correct Action": "A",
    "Open Window": "E", "Check GlobalLeaderBoard": "E", "Login": "E",
    "Execute Git Command": "CM",
    "Read GameManual": "IM", "Use Hint": "IM", "Use Answer": "IM",
    "Last Conversation": "IM",
    "Failed Action": "F", "Restart Stage(Not Clear)": "F",
    "Back To Stage Select(Not Clear)": "F",
    "Add New Quest": "R", "Complete Quest": "R", "Complete Stage": "R",
    "Start Stage": "R", "Back To Stage Select(Clear)": "R",
    "Restart Stage(Clear)": "R",
}

STATE_DESCRIPTIONS = {
    "A": "Successful task-level action; currently represented by Correct Action.",
    "E": "Navigation or information exploration: opening windows, checking the global leaderboard, or logging in.",
    "CM": "Direct Git command manipulation; represented by Execute Git Command.",
    "IM": "Use of instructional or conversational support: game manual, hint, answer, or last conversation.",
    "F": "Unsuccessful behavior or unresolved stage exit: failed action, unclear restart, or return without clearing.",
    "R": "Quest/stage progression or reward-related activity: add/complete quest, start/complete stage, or clear-stage return/restart.",
}


def prepare_events(events, assignments):
    """Retain mapped, timestamped events in stable source order for tied times."""
    assignments = assignments[["ID", "Cluster"]].copy()
    assignments["ID"] = assignments["ID"].astype(str)
    if assignments["ID"].duplicated().any():
        raise ValueError("Cluster assignments must contain one row per learner")
    events = events.copy()
    events["player"] = events["player"].astype(str)
    events["source_order"] = np.arange(len(events))
    events = events.merge(assignments, left_on="player", right_on="ID", validate="many_to_one")
    events["eventTime"] = pd.to_datetime(events["eventTime"], format="mixed", errors="coerce", utc=True)
    events["state"] = events["eventName"].map(EVENT_TO_STATE)
    return events.dropna(subset=["state", "eventTime"]).sort_values(
        ["Cluster", "player", "eventTime", "source_order"], kind="stable")


def transition_pairs(events, *, session_minutes=None, collapse_states=False):
    """Baseline follows next mapped event; optional sessions/runs are sensitivity analyses."""
    events = events.copy()
    keys = ["Cluster", "player"]
    gaps = events.groupby(keys)["eventTime"].diff().dt.total_seconds()
    if session_minutes is not None:
        events["session"] = gaps.gt(session_minutes * 60).groupby(
            [events[k] for k in keys]).cumsum()
        keys = keys + ["session"]
    if collapse_states:
        previous = events.groupby(keys)["state"].shift()
        events = events.loc[events["state"].ne(previous)].copy()
    grouped = events.groupby(keys)
    for column in ("state", "eventTime", "eventName", "eventDetail", "gameScene"):
        if column in events:
            events["next_" + column] = grouped[column].shift(-1)
    events["gap_seconds"] = (events["next_eventTime"] - events["eventTime"]).dt.total_seconds()
    return events.dropna(subset=["next_state"])


def summarize_transitions(pairs, assignments, *, n_boot=5000, seed=42):
    """Report pooled and equal-learner estimates with learner-resampled percentile CIs.

    Resampling whole learner count vectors preserves within-learner dependence.
    Intervals condition on fitted clusters and state eligibility; they do not include
    clustering uncertainty. Degenerate empirical samples are flagged explicitly.
    """
    rng = np.random.default_rng(seed)
    records, participant_tables = [], []
    for cluster, members in assignments.groupby("Cluster"):
        cluster_pairs = pairs.loc[pairs.Cluster.eq(cluster)]
        for state in STATE_ORDER:
            origin = cluster_pairs.loc[cluster_pairs.state.eq(state)]
            matrix = pd.crosstab(origin.player, origin.next_state).reindex(columns=STATE_ORDER, fill_value=0)
            counts = matrix.to_numpy(dtype=float)
            totals = counts.sum(axis=1)
            n = len(matrix)
            probabilities = counts / totals[:, None] if n else counts
            for i, player in enumerate(matrix.index):
                for j, destination in enumerate(STATE_ORDER):
                    participant_tables.append(dict(Cluster=cluster, player=player, state=state,
                        next_state=destination, count=int(counts[i, j]), outgoing_total=int(totals[i]),
                        probability=probabilities[i, j]))
            pooled = counts.sum(axis=0) / totals.sum() if n else np.full(6, np.nan)
            mean = probabilities.mean(axis=0) if n else np.full(6, np.nan)
            low = high = mean_low = mean_high = np.full(6, np.nan)
            if n >= 2:
                draws = rng.integers(n, size=(n_boot, n))
                boot_counts = counts[draws].sum(axis=1)
                boot_pooled = boot_counts / totals[draws].sum(axis=1)[:, None]
                low, high = np.quantile(boot_pooled, [.025, .975], axis=0)
                mean_low, mean_high = np.quantile(probabilities[draws].mean(axis=1), [.025, .975], axis=0)
            for j, destination in enumerate(STATE_ORDER):
                records.append(dict(Cluster=cluster, state=state, next_state=destination,
                    cluster_n=len(members), participants_with_outgoing=n,
                    participants_with_transition=int((counts[:, j] > 0).sum()) if n else 0,
                    count=int(counts[:, j].sum()) if n else 0, outgoing_total=int(totals.sum()),
                    probability=pooled[j], pooled_ci_low=low[j], pooled_ci_high=high[j],
                    mean_participant_probability=mean[j], mean_ci_low=mean_low[j], mean_ci_high=mean_high[j],
                    max_participant_outgoing_share=float(totals.max()/totals.sum()) if n else np.nan,
                    ci_status="unavailable" if n < 2 else
                        ("degenerate_empirical_sample" if np.ptp(probabilities[:, j]) == 0 else "estimated")))
    return pd.DataFrame(records), pd.DataFrame(participant_tables)


def calculate_transitions(events, assignments):
    prepared = prepare_events(events, assignments)
    counts, _ = summarize_transitions(transition_pairs(prepared), assignments)
    state_counts = prepared.groupby(["Cluster", "state"]).size().rename("state_count").reset_index()
    state_counts["state_share"] = state_counts["state_count"] / state_counts.groupby("Cluster")["state_count"].transform("sum")
    return counts, state_counts


def export_sensitivity_and_audit(events, assignments, output_dir):
    prepared = prepare_events(events, assignments)
    summaries = []
    for name, options in {
        "baseline": {}, "within_30min_sessions": {"session_minutes": 30},
        "collapsed_state_runs": {"collapse_states": True},
        "within_30min_collapsed_runs": {"session_minutes": 30, "collapse_states": True},
    }.items():
        pairs = transition_pairs(prepared, **options)
        summary, participants = summarize_transitions(pairs, assignments)
        summary.insert(0, "sequence_definition", name)
        summaries.append(summary)
        if name == "baseline":
            participants.to_csv(output_dir / "analysis_transition_participant_counts.csv", index=False)
            audit = []
            for (cluster, state, destination), group in pairs.groupby(["Cluster", "state", "next_state"]):
                same_event = group.eventName.eq(group.next_eventName)
                same_payload = same_event.copy()
                for field in ("eventDetail", "gameScene"):
                    same_payload &= group[field].fillna("").eq(group["next_" + field].fillna(""))
                audit.append(dict(Cluster=cluster, state=state, next_state=destination,
                    count=len(group), same_event_name=int(same_event.sum()),
                    same_event_payload=int(same_payload.sum()),
                    same_payload_within_1s=int((same_payload & group.gap_seconds.le(1)).sum()),
                    tied_timestamp=int(group.gap_seconds.eq(0).sum()),
                    gap_over_30min=int(group.gap_seconds.gt(1800).sum()),
                    median_gap_seconds=group.gap_seconds.median()))
            pd.DataFrame(audit).to_csv(output_dir / "analysis_transition_logging_audit.csv", index=False)
    combined = pd.concat(summaries, ignore_index=True)
    combined.to_csv(output_dir / "analysis_transition_sensitivity.csv", index=False)
    # Quantify potential export duplication without silently deleting real repeats.
    audit = {"input_events": len(events), "mapped_valid_cluster_events": len(prepared),
             "unmapped_input_events": int(events.eventName.map(EVENT_TO_STATE).isna().sum()),
             "invalid_input_timestamps": int(pd.to_datetime(events.eventTime, format="mixed", errors="coerce", utc=True).isna().sum()),
             "duplicate_nonempty_event_ids": int(events.loc[events.id.notna() & events.id.ne("")].id.duplicated().sum()),
             "bootstrap_resamples": 5000, "bootstrap_seed": 42,
             "bootstrap_unit": "learner with outgoing transitions from originating state",
             "ci": "95% percentile; fixed clusters; degenerate samples flagged; n<2 unavailable"}
    import json
    (output_dir / "analysis_transition_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    return combined.loc[combined.sequence_definition.eq("baseline")].drop(columns="sequence_definition")


def draw_transition_diagram(cluster, transitions, state_counts, output_dir):
    graph = nx.DiGraph()
    graph.add_nodes_from(STATE_ORDER)
    # A 15% probability and five-observation threshold keeps the paper figure readable;
    # the accompanying CSV retains every observed transition.
    shown = transitions[(transitions["probability"] >= .15) & (transitions["count"] >= 5)]
    for row in shown.itertuples():
        graph.add_edge(row.state, row.next_state, probability=row.probability, count=row.count)

    fig, ax = plt.subplots(figsize=(9, 8))
    node_sizes = []
    count_lookup = state_counts.set_index("state")["state_count"].to_dict()
    maximum = max(count_lookup.values(), default=1)
    for state in STATE_ORDER:
        node_sizes.append(1800 + 2200 * count_lookup.get(state, 0) / maximum)
    nx.draw_networkx_nodes(graph, POSITIONS, node_size=node_sizes, node_color="#D0D0D0",
                           node_shape="s", edgecolors="#555555", linewidths=1.5, ax=ax)
    nx.draw_networkx_labels(graph, POSITIONS, font_size=12, font_weight="bold", ax=ax)

    edges = list(graph.edges(data=True))
    widths = [1 + 7 * data["probability"] for _, _, data in edges]
    nx.draw_networkx_edges(graph, POSITIONS, width=widths, edge_color="#333333",
                           arrows=True, arrowsize=20, node_size=node_sizes,
                           connectionstyle="arc3,rad=0.12", ax=ax)
    legend = "   ".join(f"{code} = {label}" for code, label in STATE_LABELS.items())
    ax.set_title(f"Behavioral Transition Diagram — Cluster {cluster}\n"
                 "Dominant edges: probability ≥ .15 and count ≥ 5", fontsize=14)
    ax.text(.5, -.06, legend, transform=ax.transAxes, ha="center", va="top", fontsize=8, wrap=True)
    ax.set_xlim(-.65, 2.65); ax.set_ylim(-.55, 2.55); ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_dir / f"figure_behavior_transitions_cluster_{cluster}.png",
                dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_transition_heatmaps(all_transitions, output_dir):
    clusters = sorted(all_transitions["Cluster"].unique())
    fig, axes = plt.subplots(1, len(clusters), figsize=(7 * len(clusters), 6), squeeze=False)
    for ax, cluster in zip(axes.flat, clusters):
        subset = all_transitions[all_transitions["Cluster"] == cluster]
        matrix = subset.pivot(index="state", columns="next_state", values="probability").reindex(
            index=STATE_ORDER, columns=STATE_ORDER
        )
        image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(.5, all_transitions["probability"].max()))
        ax.set_xticks(range(6), STATE_ORDER); ax.set_yticks(range(6), STATE_ORDER)
        ax.set(xlabel="Next behavior", ylabel="Current behavior", title=f"Cluster {cluster}")
        for row in range(6):
            for col in range(6):
                ax.text(col, row, ("NA" if pd.isna(matrix.iloc[row, col]) else f"{matrix.iloc[row, col]:.2f}"), ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=axes.ravel().tolist(), label="Transition probability", shrink=.8)
    fig.suptitle("Behavioral Transition Probability Matrices")
    fig.savefig(output_dir / "figure_behavior_transition_heatmaps.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main(data_dir=".", events_path=None, assignments_path=None):
    data_dir = Path(data_dir)
    events = pd.read_csv(events_path or data_dir / "extracted_events.csv")
    assignments = pd.read_csv(assignments_path or data_dir / "analysis_kmeans_assignments.csv")
    prepared = prepare_events(events, assignments)
    state_counts = prepared.groupby(["Cluster", "state"]).size().rename("state_count").reset_index()
    state_counts["state_share"] = state_counts["state_count"] / state_counts.groupby("Cluster")["state_count"].transform("sum")
    transitions = export_sensitivity_and_audit(events, assignments, data_dir)
    # Preserve obsolete generated figures outside the current result set.
    current_names = {f"figure_behavior_transitions_cluster_{k}.png"
                     for k in transitions['Cluster'].unique()}
    for old_figure in data_dir.glob('figure_behavior_transitions_cluster_*.png'):
        if old_figure.name not in current_names:
            archive = data_dir / 'previous_cluster_figures' / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            archive.mkdir(parents=True, exist_ok=True)
            old_figure.replace(archive / old_figure.name)
    transitions.to_csv(data_dir / "analysis_behavior_transitions_by_cluster.csv", index=False, encoding="utf-8-sig")
    state_counts.to_csv(data_dir / "analysis_behavior_state_profiles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([
        {"state": state, "label": STATE_LABELS[state], "definition": STATE_DESCRIPTIONS[state],
         "included_events": "; ".join(event for event, mapped in EVENT_TO_STATE.items() if mapped == state)}
        for state in STATE_ORDER
    ]).to_csv(data_dir / "analysis_behavior_state_dictionary.csv", index=False, encoding="utf-8-sig")
    for cluster in sorted(transitions["Cluster"].unique()):
        draw_transition_diagram(cluster, transitions[transitions["Cluster"] == cluster],
                                state_counts[state_counts["Cluster"] == cluster], data_dir)
    draw_transition_heatmaps(transitions, data_dir)
    print(f"Behavior transition diagrams created for {len(transitions['Cluster'].unique())} clusters")


if __name__ == "__main__":
    main()
