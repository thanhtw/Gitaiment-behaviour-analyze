"""Cluster-specific behavioral transition analysis and diagrams."""

from pathlib import Path

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


def calculate_transitions(events, assignments):
    events = events.copy()
    events["player"] = events["player"].astype(str)
    assignments = assignments[["ID", "Cluster"]].copy()
    assignments["ID"] = assignments["ID"].astype(str)
    events = events.merge(assignments, left_on="player", right_on="ID", how="inner")
    events["eventTime"] = pd.to_datetime(events["eventTime"], format="mixed", errors="coerce")
    events["state"] = events["eventName"].map(EVENT_TO_STATE)
    events = events.dropna(subset=["state", "eventTime"]).sort_values(["Cluster", "player", "eventTime"])
    events["next_state"] = events.groupby(["Cluster", "player"])["state"].shift(-1)
    transitions = events.dropna(subset=["next_state"])

    counts = transitions.groupby(["Cluster", "state", "next_state"]).size().rename("count").reset_index()
    counts["outgoing_total"] = counts.groupby(["Cluster", "state"])["count"].transform("sum")
    counts["probability"] = counts["count"] / counts["outgoing_total"]
    state_counts = events.groupby(["Cluster", "state"]).size().rename("state_count").reset_index()
    state_counts["state_share"] = state_counts["state_count"] / state_counts.groupby("Cluster")["state_count"].transform("sum")
    return counts, state_counts


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
            index=STATE_ORDER, columns=STATE_ORDER, fill_value=0
        ).fillna(0)
        image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(.5, all_transitions["probability"].max()))
        ax.set_xticks(range(6), STATE_ORDER); ax.set_yticks(range(6), STATE_ORDER)
        ax.set(xlabel="Next behavior", ylabel="Current behavior", title=f"Cluster {cluster}")
        for row in range(6):
            for col in range(6):
                ax.text(col, row, f"{matrix.iloc[row, col]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=axes.ravel().tolist(), label="Transition probability", shrink=.8)
    fig.suptitle("Behavioral Transition Probability Matrices")
    fig.savefig(output_dir / "figure_behavior_transition_heatmaps.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main(data_dir="."):
    data_dir = Path(data_dir)
    events = pd.read_csv(data_dir / "extracted_events.csv")
    assignments = pd.read_csv(data_dir / "analysis_kmeans_assignments.csv")
    transitions, state_counts = calculate_transitions(events, assignments)
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
