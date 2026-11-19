"""Username-linked learning outcomes for the R1-Q7 reviewer request."""
import argparse
from datetime import datetime,timezone
from itertools import combinations
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.oneway import anova_oneway

from ..data_io import PROJECT_ROOT,OUTPUT_DIR

LABELS={1:'Sustained Engagers',2:'Low Activity Learners',3:'Struggling Learners'}
INPUT_DIR=PROJECT_ROOT/'Data/R1-Q7'


def link_scores(scores,assignments):
    """Match by explicit username, never by row number; reject ambiguous identities."""
    required={'No','PreTest','PostTest','username','cluster'}
    if not required.issubset(scores):raise ValueError('Missing linked-score columns: '+str(required-set(scores)))
    scores=scores.copy();assignments=assignments[['ID','Cluster']].copy()
    scores['UsernameKey']=scores.username.astype('string').str.strip()
    assignments['UsernameKey']=assignments.ID.astype('string').str.strip()
    for table in [scores,assignments]:
        if table.UsernameKey.isna().any() or table.UsernameKey.eq('').any() or table.UsernameKey.duplicated().any():
            raise ValueError('Missing or ambiguous usernames after trimming edge whitespace')
    if scores.No.isna().any() or scores.No.duplicated().any():raise ValueError('Score workbook No must be unique and nonmissing')
    for name in ['PreTest','PostTest','cluster']:
        scores[name]=pd.to_numeric(scores[name],errors='raise')
        if not np.isfinite(scores[name]).all():raise ValueError('Missing/nonfinite scores or cluster')
    if not scores[['PreTest','PostTest']].apply(lambda x:x.between(0,100)).all().all():raise ValueError('Expected scores in 0–100')
    merged=scores.merge(assignments,on='UsernameKey',how='outer',validate='one_to_one',indicator=True)
    merged['LinkageStatus']=merged['_merge'].astype(str)
    if not merged['_merge'].eq('both').all():raise ValueError('Username linkage is incomplete; review unmatched rows before analysis')
    if not merged.cluster.eq(merged.Cluster).all():raise ValueError('Supplied clusters disagree with authoritative assignments')
    merged['Username']=merged.ID
    merged['Cluster']=merged.Cluster.astype(int)
    if set(merged.Cluster)!=set(LABELS):raise ValueError('This analysis requires all three retained profiles')
    merged['ClusterName']=merged.Cluster.map(LABELS)
    merged['AnonID']=[f'P{i:03}' for i in range(1,len(merged)+1)]
    merged['Gain']=merged.PostTest-merged.PreTest
    merged['PreCentered']=merged.PreTest-merged.PreTest.mean()
    return merged[['AnonID','Username','UsernameKey','No','Cluster','ClusterName','PreTest','PostTest','Gain','PreCentered','LinkageStatus']]


def design(frame,center,interaction=False):
    X=pd.DataFrame({'Intercept':np.ones(len(frame)),'PreCentered':frame.PreTest.to_numpy()-center,
                    'Cluster2':frame.Cluster.eq(2).astype(float).to_numpy(),
                    'Cluster3':frame.Cluster.eq(3).astype(float).to_numpy()})
    if interaction:
        X['PreByCluster2']=X.PreCentered*X.Cluster2
        X['PreByCluster3']=X.PreCentered*X.Cluster3
    return X


def fit_ancova(frame,center=None):
    center=float(frame.PreTest.mean()) if center is None else float(center)
    X=design(frame,center)
    if np.linalg.matrix_rank(X)<X.shape[1]:raise ValueError('Rank-deficient ANCOVA')
    model=sm.OLS(frame.PostTest.to_numpy(),X).fit()
    robust=model.get_robustcov_results(cov_type='HC3',use_t=True)
    R=np.array([[0,0,1,0],[0,0,0,1]],dtype=float)
    omnibus=robust.f_test(R)
    reduced=sm.OLS(frame.PostTest.to_numpy(),X[['Intercept','PreCentered']]).fit()
    classical=model.compare_f_test(reduced)
    partial_eta=(reduced.ssr-model.ssr)/reduced.ssr
    D=np.array([[1,0,0,0],[1,0,1,0],[1,0,0,1]],dtype=float)
    prediction=robust.get_prediction(D).summary_frame(alpha=.05)
    adjusted=pd.DataFrame({'Cluster':[1,2,3],'ClusterName':[LABELS[c] for c in [1,2,3]],
        'ReferencePretest':center,'AdjustedPosttest':prediction['mean'],
        'SE_HC3':prediction.mean_se,'CI_Low_HC3':prediction.mean_ci_lower,'CI_High_HC3':prediction.mean_ci_upper})
    pairs=[]
    for a,b in combinations(range(3),2):
        contrast=robust.t_test(D[a]-D[b]);ci=contrast.conf_int()[0]
        pairs.append(dict(ClusterA=a+1,ClusterB=b+1,Difference=float(contrast.effect.item()),
            SE_HC3=float(contrast.sd.item()),t_HC3=float(contrast.tvalue.item()),DF=model.df_resid,
            p_HC3=float(contrast.pvalue),CI_Low_HC3=float(ci[0]),CI_High_HC3=float(ci[1])))
    pairs=pd.DataFrame(pairs);pairs['p_Holm']=multipletests(pairs.p_HC3,method='holm')[1]
    coefficients=pd.DataFrame({'Term':X.columns,'B':robust.params,'SE_HC3':robust.bse,
        't_HC3':robust.tvalues,'p_HC3':robust.pvalues,'CI_Low_HC3':robust.conf_int()[:,0],'CI_High_HC3':robust.conf_int()[:,1]})
    Xi=design(frame,center,interaction=True)
    interaction=sm.OLS(frame.PostTest.to_numpy(),Xi).fit()
    robust_i=interaction.get_robustcov_results(cov_type='HC3',use_t=True)
    slope_test=robust_i.f_test(np.eye(6)[[4,5]])
    tests=pd.DataFrame([
        dict(Test='Primary: cluster adjusted for pretest (HC3)',F=float(omnibus.fvalue),DF1=float(omnibus.df_num),DF2=float(omnibus.df_denom),p=float(omnibus.pvalue)),
        dict(Test='Conventional ANCOVA cluster effect',F=float(classical[0]),DF1=float(classical[2]),DF2=float(model.df_resid),p=float(classical[1])),
        dict(Test='Cluster x pretest interaction (HC3)',F=float(slope_test.fvalue),DF1=float(slope_test.df_num),DF2=float(slope_test.df_denom),p=float(slope_test.pvalue)),
    ])
    meta=dict(n=len(frame),reference_pretest=center,partial_eta_squared_classical=float(partial_eta),
        r_squared=float(model.rsquared),adjusted_r_squared=float(model.rsquared_adj),
        residual_shapiro_p=float(stats.shapiro(model.resid).pvalue),
        interaction_p_HC3=float(slope_test.pvalue),primary_df_residual=float(model.df_resid))
    icoeff=pd.DataFrame({'Term':Xi.columns,'B':robust_i.params,'SE_HC3':robust_i.bse,'p_HC3':robust_i.pvalues,
                        'CI_Low_HC3':robust_i.conf_int()[:,0],'CI_High_HC3':robust_i.conf_int()[:,1]})
    # Interaction sensitivity at the same reference pretest, not extrapolation at zero.
    Di=np.column_stack([D,np.zeros((3,2))]);ipairs=[]
    for a,b in combinations(range(3),2):
        t=robust_i.t_test(Di[a]-Di[b]);ci=t.conf_int()[0]
        ipairs.append(dict(ClusterA=a+1,ClusterB=b+1,ReferencePretest=center,Difference=float(t.effect.item()),
                           CI_Low_HC3=float(ci[0]),CI_High_HC3=float(ci[1]),p_HC3=float(t.pvalue)))
    ipairs=pd.DataFrame(ipairs);ipairs['p_Holm']=multipletests(ipairs.p_HC3,method='holm')[1]
    return dict(model=model,robust=robust,adjusted=adjusted,pairs=pairs,tests=tests,coefficients=coefficients,
                interaction_coefficients=icoeff,interaction_pairs=ipairs,metadata=meta)


def bootstrap_intervals(frame,n_boot=5000,seed=20261118):
    rng=np.random.default_rng(seed);center=float(frame.PreTest.mean())
    group_indices=[np.flatnonzero(frame.Cluster.eq(c).to_numpy()) for c in [1,2,3]]
    output=[];invalid=0
    for replicate in range(n_boot):
        draw=np.concatenate([rng.choice(indices,size=len(indices),replace=True) for indices in group_indices])
        sample=frame.iloc[draw]
        X=design(sample,center).to_numpy()
        if np.linalg.matrix_rank(X)<4:invalid+=1;continue
        B=np.linalg.lstsq(X,sample.PostTest.to_numpy(),rcond=None)[0]
        adjusted=np.array([B[0],B[0]+B[2],B[0]+B[3]])
        gains=[sample.loc[sample.Cluster.eq(c),'Gain'].mean() for c in [1,2,3]]
        output.append([*adjusted,adjusted[0]-adjusted[1],adjusted[0]-adjusted[2],adjusted[1]-adjusted[2],*gains])
    columns=['Adjusted_1','Adjusted_2','Adjusted_3','Difference_1_2','Difference_1_3','Difference_2_3','Gain_1','Gain_2','Gain_3']
    values=pd.DataFrame(output,columns=columns)
    intervals=pd.DataFrame([dict(Quantity=c,BootstrapMean=values[c].mean(),CI_Low=values[c].quantile(.025),CI_High=values[c].quantile(.975)) for c in columns])
    return intervals,dict(requested_replicates=n_boot,successful_replicates=len(values),rank_deficient_replicates=invalid,seed=seed,
                         method='Percentile; resample complete learner records within fixed clusters; refit common-slope model; original mean pretest held fixed')


def summarize(frame):
    descriptive=frame.groupby(['Cluster','ClusterName']).agg(
        N=('AnonID','size'),PreMean=('PreTest','mean'),PreSD=('PreTest','std'),
        PostMean=('PostTest','mean'),PostSD=('PostTest','std'),GainMean=('Gain','mean'),GainSD=('Gain','std'),
        PostMedian=('PostTest','median'),PostCeilingN=('PostTest',lambda x:int(x.eq(100).sum())),
        PostCeilingFraction=('PostTest',lambda x:x.eq(100).mean()),PreMin=('PreTest','min'),PreMax=('PreTest','max')).reset_index()
    tests=[]
    for variable in ['PreTest','PostTest','Gain']:
        groups=[g[variable].to_numpy() for _,g in frame.groupby('Cluster')]
        welch=anova_oneway(groups,use_var='unequal',welch_correction=True)
        ordinary=stats.f_oneway(*groups)
        kw=stats.kruskal(*groups)
        tests.append(dict(Outcome=variable,WelchF=welch.statistic,WelchDF1=welch.df[0],WelchDF2=welch.df[1],
            WelchP=welch.pvalue,OrdinaryF=ordinary.statistic,OrdinaryP=ordinary.pvalue,
            KruskalH=kw.statistic,KruskalP=kw.pvalue,LeveneMedianP=stats.levene(*groups,center='median').pvalue))
    gain_pairs=[]
    for a,b in combinations([1,2,3],2):
        x=frame.loc[frame.Cluster.eq(a),'Gain'];y=frame.loc[frame.Cluster.eq(b),'Gain']
        t=stats.ttest_ind(x,y,equal_var=False)
        varx=x.var(ddof=1)/len(x);vary=y.var(ddof=1)/len(y);se=np.sqrt(varx+vary)
        df=(varx+vary)**2/(varx**2/(len(x)-1)+vary**2/(len(y)-1));delta=x.mean()-y.mean()
        low,high=delta+np.array([-1,1])*stats.t.ppf(.975,df)*se
        gain_pairs.append(dict(ClusterA=a,ClusterB=b,GainDifference=delta,SE=se,DF=df,t=t.statistic,p=t.pvalue,CI_Low=low,CI_High=high))
    gain_pairs=pd.DataFrame(gain_pairs);gain_pairs['p_Holm']=multipletests(gain_pairs.p,method='holm')[1]
    return descriptive,pd.DataFrame(tests),gain_pairs


def sensitivity_analyses(frame,primary):
    # Compare in the shared observed baseline range; keep the original reference score.
    ranges=frame.groupby('Cluster').PreTest.agg(['min','max'])
    lower,upper=float(ranges['min'].max()),float(ranges['max'].min())
    common=frame.loc[frame.PreTest.between(lower,upper)].copy()
    common_fit=fit_ancova(common,center=primary['metadata']['reference_pretest'])
    loo=[]
    for index,row in frame.iterrows():
        fit=fit_ancova(frame.drop(index),center=primary['metadata']['reference_pretest'])
        item=dict(RemovedAnonID=row.AnonID,RemovedCluster=int(row.Cluster),PrimaryP=fit['tests'].iloc[0].p)
        for pair in fit['pairs'].itertuples():
            item[f'Difference_{pair.ClusterA}_{pair.ClusterB}']=pair.Difference
            item[f'HolmP_{pair.ClusterA}_{pair.ClusterB}']=pair.p_Holm
        loo.append(item)
    loo=pd.DataFrame(loo)
    ranges=[]
    for a,b in combinations([1,2,3],2):
        ranges.append(dict(ClusterA=a,ClusterB=b,LOO_DifferenceMin=loo[f'Difference_{a}_{b}'].min(),
            LOO_DifferenceMax=loo[f'Difference_{a}_{b}'].max(),Largest_HolmP=loo[f'HolmP_{a}_{b}'].max()))
    metadata=dict(common_pretest_min=lower,common_pretest_max=upper,common_n=len(common),
                  common_cluster_counts={str(k):int(v) for k,v in common.groupby('Cluster').size().items()})
    return common_fit,pd.DataFrame(ranges),metadata


def run(input_dir=INPUT_DIR,output_dir=None,n_boot=5000):
    from ..reporting.profile_outcomes import export_results
    input_dir=Path(input_dir);output_dir=Path(output_dir) if output_dir else OUTPUT_DIR/'profile_outcomes'
    output_dir.mkdir(parents=True,exist_ok=True)
    score_path=input_dir/'Score-Username.xlsx'
    scores=pd.read_excel(score_path,sheet_name='Score-Username',dtype={'username':str})
    assignments_path=OUTPUT_DIR/'clustering/analysis_kmeans_assignments.csv'
    assignments=pd.read_csv(assignments_path,dtype={'ID':str})
    data=link_scores(scores,assignments)
    # Redundant source sheets corroborate scores and labels; they do not determine matching.
    score_check_path=input_dir/'104-Pre-Post-Match-Username.xlsx'
    score_check=pd.read_excel(score_check_path,sheet_name='PrePostTestByGroup')
    if score_check.No.duplicated().any():raise ValueError('Duplicate local No in corroborating score file')
    check=scores[['No','PreTest','PostTest']].merge(score_check,on='No',validate='one_to_one',suffixes=('_linked','_check'))
    if len(check)!=len(scores) or not check.PreTest_linked.eq(check.PreTest_check).all() or not check.PostTest_linked.eq(check.PostTest_check).all():
        raise ValueError('Score source files disagree')
    label_path=input_dir/'104-Username_Cluster.xlsx'
    label_check=pd.read_excel(label_path,sheet_name='Username_Cluster',dtype={'Username':str})
    label_check['UsernameKey']=label_check.Username.str.strip()
    check2=data.merge(label_check[['UsernameKey','Cluster']],on='UsernameKey',validate='one_to_one',suffixes=('_linked','_check'))
    if len(check2)!=len(data) or not check2.Cluster_linked.eq(check2.Cluster_check).all():raise ValueError('Supplied username mapping disagrees')
    print(f'Username linkage complete: {len(data)} learners; clusters {data.groupby("Cluster").size().to_dict()}',flush=True)
    primary=fit_ancova(data)
    descriptive,secondary,gain_pairs=summarize(data)
    boot,boot_meta=bootstrap_intervals(data,n_boot=n_boot)
    common,loo,sensitivity_meta=sensitivity_analyses(data,primary)
    linkage=dict(authoritative_learners=len(assignments),provided_scores=len(scores),matched_learners=len(data),
        unmatched_gameplay_learners=0,unmatched_score_learners=0,cluster_disagreements=0,
        duplicate_normalized_usernames=0,missing_pretest=0,missing_posttest=0,
        normalization='Trim leading/trailing whitespace only; exact case preserved; no row-order or score matching',
        corroborating_score_rows=len(check),corroborating_mapping_rows=len(check2),
        questionnaire_status='Anonymous/unidentified questionnaire; profile-perception associations cannot be estimated')
    tables={'Descriptives':descriptive,'Primary_ANCOVA':primary['tests'],'Adjusted_Posttest':primary['adjusted'],
        'Adjusted_Contrasts':primary['pairs'],'Coefficients_HC3':primary['coefficients'],
        'Interaction_Coefficients':primary['interaction_coefficients'],'Interaction_Contrasts':primary['interaction_pairs'],
        'Secondary_Tests':secondary,'Gain_Contrasts':gain_pairs,'Bootstrap_CI':boot,
        'Common_Support_Tests':common['tests'],'Common_Support_Contrasts':common['pairs'],'Leave_One_Out':loo}
    export_results(output_dir,data,tables,primary['metadata'],linkage,boot_meta,sensitivity_meta)
    sources=[score_path,score_check_path,label_path,assignments_path,Path(__file__),Path(__file__).parents[1]/'reporting/profile_outcomes.py']
    manifest=dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),
        inputs_sha256={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        packages={p:version(p) for p in ['pandas','numpy','scipy','statsmodels','pyreadstat','python-docx','openpyxl']},
        bootstrap=boot_meta,linkage=linkage,model=primary['metadata'],sensitivity=sensitivity_meta,
        primary_inference='HC3 Wald F/t tests with residual degrees of freedom; fixed observed cluster assignments')
    (output_dir/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Profile learning-outcome analysis complete: '+str(output_dir),flush=True)
    return output_dir


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=INPUT_DIR)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--bootstrap',type=int,default=5000)
    args=parser.parse_args()
    if args.bootstrap<100:parser.error('Use at least 100 bootstrap replicates')
    run(args.input_dir,args.output_dir,args.bootstrap)


if __name__=='__main__':main()
