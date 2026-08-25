"""Extract and analyze Data/Version-1 and Data/Version-2 together.

Run from any directory with: python Extract-Data-Code/run_analysis.py
"""

import os
import runpy

from data_io import OUTPUT_DIR, VERSIONS, combine_frames, load_records, source_file
from extract_event_data import events_to_dataframe, extract_events
from extract_leaderboard_data import entries_to_dataframe, extract_leaderboards
from extract_player_data import (
    extract_game_records,
    extract_stage_data,
    extract_stage_leaderboards,
)


def build_extracted_data():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    event_frames = []
    game_frames = []
    stage_frames = []
    stage_board_frames = []
    global_board_frames = []

    for version in VERSIONS:
        print(f"Loading {version} from {source_file(version, 'GEG-database.eventdatas').parent}")
        events = load_records(source_file(version, "GEG-database.eventdatas"))
        players = load_records(source_file(version, "GEG-database.playersavedatas"))
        boards = load_records(source_file(version, "GEG-database.globalleaderboarddatas"))
        board_entries, _ = extract_leaderboards(boards)

        event_frames.append((version, events_to_dataframe(extract_events(events))))
        game_frames.append((version, extract_game_records(players)))
        stage_frames.append((version, extract_stage_data(players)))
        stage_board_frames.append((version, extract_stage_leaderboards(players)))
        global_board_frames.append((version, entries_to_dataframe(board_entries)))

    outputs = {
        "extracted_events.csv": combine_frames(event_frames),
        "extracted_player_game_records.csv": combine_frames(game_frames),
        "extracted_player_stage_data.csv": combine_frames(stage_frames),
        "extracted_stage_leaderboards.csv": combine_frames(stage_board_frames),
        "extracted_leaderboards.csv": combine_frames(global_board_frames),
    }
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / name, index=False, encoding="utf-8-sig")
        counts = frame["dataVersion"].value_counts().to_dict()
        print(f"Wrote {name}: {len(frame)} rows {counts}")


def run_downstream_analysis():
    """Run scripts whose public entry points consume the extracted CSV files."""
    previous = os.getcwd()
    os.chdir(OUTPUT_DIR)
    try:
        import analyze_user_behavior as analysis

        data_dir = str(OUTPUT_DIR)
        game, stages, boards, stage_boards = analysis.load_all_data(data_dir)
        game, stages, boards, stage_boards = analysis.preprocess_data(
            game, stages, boards, stage_boards
        )
        game = analysis.segment_players(game)
        unlock_rates, _ = analysis.analyze_stage_progression(stages, game)
        correlations = analysis.analyze_performance(game, stages)
        game = analysis.analyze_learning_behavior(game)
        game = analysis.analyze_time_patterns(game, stages)
        game = analysis.analyze_retention(game, stages)
        analysis.generate_combined_insights(game, stages, boards, stage_boards)
        analysis.export_analysis_results(game, unlock_rates, correlations, data_dir)

        # These scripts use the current directory by design.
        for script in ("deep_behavior_analysis.py", "cluster_profile_analysis.py",
                       "behavior_transition_analysis.py"):
            runpy.run_path(str(OUTPUT_DIR.parent / "Extract-Data-Code" / script), run_name="__main__")
    finally:
        os.chdir(previous)


if __name__ == "__main__":
    build_extracted_data()
    # Per-user aggregation is required by both downstream analyses.
    from extract_per_user_data import extract_all_users_combined, export_per_user_data, load_all_data
    sources = load_all_data(str(OUTPUT_DIR))
    export_per_user_data(extract_all_users_combined(sources), str(OUTPUT_DIR))
    run_downstream_analysis()
