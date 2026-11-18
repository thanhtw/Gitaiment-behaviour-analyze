"""Verify source score/time values before exporting behavioral observations."""
import numpy as np
import pandas as pd
from ..data_io import VERSIONS,load_records,source_file
from ..reporting.spss_data import prepare_export

def source_snapshots():
    records=[]
    for version in VERSIONS:
        for player in load_records(source_file(version,'GEG-database.playersavedatas')):
            saved=player.get('saveData',{}).get('gameRecordData',{})
            records.append(dict(ID=str(player['username']),SourceVersion=version,
                VerifiedTotalScore=saved.get('totalStageScore',np.nan),
                SourcePlayTimeSeconds=saved.get('totalPlayTime',np.nan)))
    source=pd.DataFrame(records).drop_duplicates('ID',keep='last')
    for column in ['VerifiedTotalScore','SourcePlayTimeSeconds']:
        source[column]=pd.to_numeric(source[column],errors='coerce')
    source['VerifiedPlayMinutes']=source.SourcePlayTimeSeconds/60
    source['VerifiedEfficiency']=source.VerifiedTotalScore.div(source.VerifiedPlayMinutes).where(source.VerifiedPlayMinutes.gt(0))
    return source


def verified_dataset(assignments,source,labels):
    # Join raw identifiers before the consistent SAV trailing-space normalization.
    audit=assignments[['ID','TotalScore','PlayDurationMinutes','LearningEfficiency']].merge(
        source,on='ID',how='left',validate='one_to_one',indicator=True)
    audit['SourceRecordPresent']=audit['_merge'].eq('both').astype(int)
    audit['ScoreMatchesSource']=np.isclose(audit.TotalScore,audit.VerifiedTotalScore,equal_nan=True,rtol=1e-10).astype(int)
    audit['EfficiencyMatchesSource']=np.isclose(audit.LearningEfficiency,audit.VerifiedEfficiency,equal_nan=True,rtol=1e-10).astype(int)
    if not audit.ScoreMatchesSource.eq(1).all() or not audit.EfficiencyMatchesSource.eq(1).all():
        raise ValueError('Source recalculation differs from saved features; resolve before exporting')
    corrected=assignments.copy()
    corrected['TotalScore']=audit.VerifiedTotalScore.to_numpy()
    corrected['PlayDurationMinutes']=audit.VerifiedPlayMinutes.to_numpy()
    corrected['LearningEfficiency']=audit.VerifiedEfficiency.to_numpy()
    data,dictionary=prepare_export(corrected,labels)
    audit.ID=audit.ID.str.rstrip()
    audit=audit.drop(columns=['_merge','TotalScore','PlayDurationMinutes','LearningEfficiency'])
    data=data.merge(audit,on='ID',how='left',validate='one_to_one')
    data['EfficiencyUndefined']=data.LearningEfficiency.isna().astype(int)
    return data,dictionary


