"""Run the single retained direct K-means workflow and its reports/exports."""
import argparse
from datetime import datetime,timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

from .data_io import PROJECT_ROOT,OUTPUT_DIR,VERSIONS,source_file,load_records,combine_frames
from .extraction.events import extract_events,events_to_dataframe
from .extraction.players import extract_game_records,extract_stage_data
from .extraction.leaderboards import extract_leaderboards,entries_to_dataframe
from .extraction.learners import load_all_data,extract_all_users_combined,export_per_user_data


def build_extracted_data(output_dir):
    """Produce the four tables consumed by learner aggregation; retain provenance."""
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    frames={name:[] for name in ['extracted_events.csv','extracted_player_game_records.csv',
                                'extracted_player_stage_data.csv','extracted_leaderboards.csv']}
    for data_version in VERSIONS:
        events=load_records(source_file(data_version,'GEG-database.eventdatas'))
        players=load_records(source_file(data_version,'GEG-database.playersavedatas'))
        boards=load_records(source_file(data_version,'GEG-database.globalleaderboarddatas'))
        entries,_=extract_leaderboards(boards)
        for name,frame in [('extracted_events.csv',events_to_dataframe(extract_events(events))),
                           ('extracted_player_game_records.csv',extract_game_records(players)),
                           ('extracted_player_stage_data.csv',extract_stage_data(players)),
                           ('extracted_leaderboards.csv',entries_to_dataframe(entries))]:
            frames[name].append((data_version,frame))
    for name,versioned in frames.items():
        combined=combine_frames(versioned)
        combined.to_csv(output_dir/name,index=False,encoding='utf-8-sig')
        print(f'Extracted {name}: {len(combined)} rows',flush=True)


def run(output_dir=OUTPUT_DIR,n_boot=500,n_subsamples=200,n_seeds=100):
    """Keep intermediate data, clustering, transitions and SPSS outputs separate."""
    from .analysis import clustering,transitions,stability,efficiency
    from .reporting import cluster_report,table9,spss_guide
    output_dir=Path(output_dir).resolve()
    extracted=output_dir/'extracted';clusters=output_dir/'clustering';transition_dir=output_dir/'transitions';spss=output_dir/'spss'
    for folder in [extracted,clusters,transition_dir,spss]:folder.mkdir(parents=True,exist_ok=True)
    build_extracted_data(extracted)
    sources=load_all_data(str(extracted))
    export_per_user_data(extract_all_users_combined(sources),str(extracted))
    clustering.main(clusters,feature_source=extracted/'analysis_per_user_combined.csv')
    transitions.main(transition_dir,events_path=extracted/'extracted_events.csv',
                     assignments_path=clusters/'analysis_kmeans_assignments.csv')
    efficiency.run(clusters)
    stability.run(clusters,n_boot=n_boot,n_seeds=n_seeds)
    cluster_report.run(clusters,folder=clusters/'report',n_boot=n_boot,n_subsamples=n_subsamples)
    table9.run(clusters,spss)
    spss_guide.run(spss)
    inputs=[source_file(v,stem) for v in VERSIONS for stem in ['GEG-database.eventdatas','GEG-database.playersavedatas','GEG-database.globalleaderboarddatas']]
    manifest=dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        workflow='11 indicators -> median imputation -> log1p non-rate indicators -> standardization -> K-means; PCA visualization only',
        sources_sha256={str(p.relative_to(PROJECT_ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        code_sha256={str(p.relative_to(PROJECT_ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.rglob('*.py')},
        packages={p:version(p) for p in ['pandas','numpy','scipy','scikit-learn','matplotlib','statsmodels','networkx','python-docx','pyreadstat','reportlab']})
    (output_dir/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Completed: {output_dir}',flush=True)
    return output_dir


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=OUTPUT_DIR)
    parser.add_argument('--bootstrap',type=int,default=500)
    parser.add_argument('--subsamples',type=int,default=200)
    parser.add_argument('--seeds',type=int,default=100)
    args=parser.parse_args()
    if min(args.bootstrap,args.subsamples,args.seeds)<2:parser.error('replicate counts must be at least 2')
    run(args.output_dir,args.bootstrap,args.subsamples,args.seeds)


if __name__=='__main__':main()
