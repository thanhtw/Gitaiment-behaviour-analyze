"""Export F1–F14 learner observations for the attached original three-cluster Table 9."""
import hashlib
import json
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import pyreadstat
from scipy.stats import f_oneway

from ..data_io import OUTPUT_DIR
from .spss_data import CLUSTERS
from ..analysis.source_audit import source_snapshots,verified_dataset

# Code, source export variable, label, units. This order matches the attached table.
FEATURES = [
 ('F1','CommandsExecuted','Commands Executed','count'),
 ('F2','CorrectActions','Correct Actions','count'),
 ('F3','FailedActions','Failed Actions','count'),
 ('F4','HintQuests','Hint Quests','count'),
 ('F5','AnswerQuests','Answer Quests','count'),
 ('F6','PlayDurationMinutes','Play Duration','minutes'),
 ('F7','LeaderboardInteractions','Leaderboard Interactions','count'),
 ('F8','LearningEfficiency','Learning Efficiency','game-score points per minute'),
 ('F9','AccuracyRatePct','Accuracy Rate','percent, 0–100'),
 ('F10','PerfectQuestRatePct','Perfect Quest Rate','percent, 0–100'),
 ('F11','HelpDependencyPct','Help Dependency Ratio','percent, 0–100'),
 ('F12','StageClearOccurrences','Stage Clear Occurrences','count; not completed quests'),
 ('F13','GameProgress','Game Progress','percent, 0–100'),
 ('F14','TotalScore','Total Score','raw game-score points'),
]


def run(results_dir=None, export_dir=None):
    results_dir=Path(results_dir) if results_dir else OUTPUT_DIR/'clustering'
    folder=Path(export_dir) if export_dir else OUTPUT_DIR/'spss'
    folder.mkdir(parents=True,exist_ok=True)
    source=results_dir/'analysis_kmeans_assignments.csv'
    assignments=pd.read_csv(source,dtype={'ID':str})
    observed,_=verified_dataset(assignments,source_snapshots(),CLUSTERS)
    data=observed[['ID','Cluster','ClusterLabel']].copy()
    dictionary=[];descriptives=[];tests=[]
    for index,(code,variable,label,unit) in enumerate(FEATURES,1):
        data[code]=observed[variable]
        dictionary.append(dict(FeatureCode=code,Indicator=label,Units=unit,SourceVariable=variable,
            ClusteringInputForOriginalTable='Yes' if index<=11 else 'No; profiling only'))
        groups=[]
        for cluster,cluster_label in CLUSTERS.items():
            values=data.loc[data.Cluster.eq(cluster),code]
            valid=values.dropna();groups.append(valid.to_numpy())
            descriptives.append(dict(FeatureCode=code,Indicator=label,Cluster=cluster,ClusterLabel=cluster_label,
                MembershipN=len(values),ValidN=len(valid),MissingN=int(values.isna().sum()),
                Mean=valid.mean(),SampleSD=valid.std(ddof=1)))
        f,p=f_oneway(*groups)
        combined=np.concatenate(groups);grand=combined.mean()
        between=sum(len(g)*(g.mean()-grand)**2 for g in groups)
        total=((combined-grand)**2).sum()
        tests.append(dict(FeatureCode=code,Indicator=label,ValidN=len(combined),DFBetween=2,
            DFWithin=len(combined)-3,F=f,p=p,EtaSquared=between/total))
    dictionary=pd.DataFrame(dictionary);desc=pd.DataFrame(descriptives);tests=pd.DataFrame(tests)
    pyreadstat.write_sav(data,folder/'Table9_F1_F14_Data.sav',
        column_labels={**{code:f'{code}: {label} ({unit})' for code,_,label,unit in FEATURES},
                       'ID':'Learner identifier','Cluster':'Original Table 9 cluster','ClusterLabel':'Original Table 9 cluster label'},
        variable_value_labels={'Cluster':CLUSTERS},
        variable_measure={c:'nominal' if c in ['ID','Cluster','ClusterLabel'] else 'scale' for c in data},
        variable_format={**{code:'F16.4' for code,_,_,_ in FEATURES},'Cluster':'F1.0'},
        note=['Original three-cluster assignments: 57, 32 and 15 learners.',
              'Observed F1-F14 data; no inferential imputation. F14 uses raw score points.'])
    with pd.ExcelWriter(folder/'Table9_F1_F14_Data.xlsx',engine='openpyxl') as writer:
        sheets=[('All_Learners',data),('Cluster_1',data.loc[data.Cluster.eq(1)]),
            ('Cluster_2',data.loc[data.Cluster.eq(2)]),('Cluster_3',data.loc[data.Cluster.eq(3)]),
            ('Feature_Codes',dictionary),('Expected_Mean_SD_N',desc),('Expected_ANOVA',tests)]
        for name,frame in sheets:
            frame.to_excel(writer,sheet_name=name,index=False)
            writer.sheets[name].freeze_panes='A2'
    directory=str(folder.resolve()).replace("'","''")
    (folder/'Run_Table9_ANOVA.sps').write_text(
        f"* Change CD to this export folder on your computer.\nCD '{directory}'.\n"
        "GET FILE='Table9_F1_F14_Data.sav'.\nDATASET NAME Table9Data.\n"
        'FILTER OFF.\nWEIGHT OFF.\nSPLIT FILE OFF.\n'
        '* F1-F14 are dependent variables; Cluster is the factor.\n'
        'ONEWAY F1 TO F14 BY Cluster\n'
        ' /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH\n /MISSING ANALYSIS\n /ES OVERALL.\n'
        '* For SPSS before 27, remove /ES OVERALL. Eta-squared=SS_between/SS_total.\n',encoding='utf-8')
    (folder/'README.md').write_text('''# Table 9: F1–F14 data for SPSS

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
''',encoding='utf-8')
    saved,meta=pyreadstat.read_sav(folder/'Table9_F1_F14_Data.sav')
    assert saved.ID.tolist()==data.ID.tolist()
    np.testing.assert_allclose(saved.select_dtypes('number'),data.select_dtypes('number'),equal_nan=True)
    assert data.groupby('Cluster').size().tolist()==[57,32,15]
    assert data.F8.notna().sum()==94
    (folder/'export_manifest.json').write_text(json.dumps(dict(input=str(source.resolve()),
        input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),rows=104,indicators=14,
        cluster_counts={'1':57,'2':32,'3':15},validation='SAV read-back values/IDs/missingness agree; original Table 9 memberships preserved'),indent=2)+'\n')
    print('F1–F14 export complete: '+str(folder))
    return folder


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir',type=Path,default=OUTPUT_DIR/'clustering')
    parser.add_argument('--export-dir',type=Path,default=OUTPUT_DIR/'spss')
    args=parser.parse_args()
    run(args.results_dir,args.export_dir)


if __name__=='__main__':main()
