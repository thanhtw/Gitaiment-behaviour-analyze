"""Reports, SPSS data, and a ChatGPT revision packet for linked profile outcomes."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pyreadstat

from .formatting import markdown_table,export_docx
from ..analysis.profile_outcomes import LABELS


def export_results(folder,data,tables,model_meta,linkage,boot_meta,sensitivity_meta):
    folder=Path(folder)
    public=data[['AnonID','Cluster','ClusterName','PreTest','PostTest','Gain','PreCentered']].copy()
    data.to_excel(folder/'Matched_Username_Data_PRIVATE.xlsx',sheet_name='Verified_Linkage',index=False)
    with pd.ExcelWriter(folder/'Evidence_For_ChatGPT.xlsx',engine='openpyxl') as writer:
        public.to_excel(writer,sheet_name='Anonymous_Learner_Data',index=False)
        for name,table in tables.items():table.to_excel(writer,sheet_name=name[:31],index=False)
        pd.DataFrame([{'Item':k,'Value':json.dumps(v) if isinstance(v,dict) else str(v)} for k,v in linkage.items()]).to_excel(writer,sheet_name='Linkage_Audit',index=False)
        for sheet in writer.sheets.values():sheet.freeze_panes='A2'
    spss=data[['AnonID','Username','Cluster','PreTest','PostTest','Gain','PreCentered']].copy()
    pyreadstat.write_sav(spss,folder/'Profile_Learning_Outcomes.sav',variable_value_labels={'Cluster':LABELS},
        variable_measure={name:'nominal' if name in ['AnonID','Username','Cluster'] else 'scale' for name in spss},
        column_labels={'PreTest':'Username-linked pretest score (0–100)','PostTest':'Independent Git posttest score (0–100)',
            'Gain':'PostTest minus PreTest','PreCentered':'PreTest minus full-cohort pretest mean'},
        note=['104 verified username matches; fixed behavioral clusters; no questionnaire link.',
              'Primary comparisons adjust for pretest; cluster membership is observational.'])
    back,_=pyreadstat.read_sav(folder/'Profile_Learning_Outcomes.sav')
    np.testing.assert_allclose(back[['Cluster','PreTest','PostTest','Gain','PreCentered']],spss[['Cluster','PreTest','PostTest','Gain','PreCentered']])
    if back.Username.tolist()!=spss.Username.str.rstrip().tolist():raise ValueError('SPSS username round-trip failed')
    export_syntax(folder)
    report,response=build_report(data,tables,model_meta,linkage,boot_meta,sensitivity_meta)
    (folder/'R1_Q7_Analysis_Report.md').write_text(report,encoding='utf-8')
    export_docx(report,folder/'R1_Q7_Analysis_Report.docx')
    (folder/'Reviewer_Response_Draft.txt').write_text(response+'\n',encoding='utf-8')
    prompt=build_prompt(tables)
    (folder/'ChatGPT_Revision_Prompt.txt').write_text(prompt,encoding='utf-8')
    create_figure(folder,tables)


def build_report(data,tables,model,linkage,bootstrap,sensitivity):
    d=tables['Descriptives'];tests=tables['Primary_ANCOVA'];means=tables['Adjusted_Posttest'];pairs=tables['Adjusted_Contrasts']
    primary=tests.iloc[0];ordinary=tests.iloc[1];interaction=tests.iloc[2]
    gain_test=tables['Secondary_Tests'].set_index('Outcome').loc['Gain']
    pre_test=tables['Secondary_Tests'].set_index('Outcome').loc['PreTest']
    post_test=tables['Secondary_Tests'].set_index('Outcome').loc['PostTest']
    readable=d[['Cluster','ClusterName','N']].copy()
    for outcome,mean,sd in [('Pretest','PreMean','PreSD'),('Posttest','PostMean','PostSD'),('Gain','GainMean','GainSD')]:
        readable[outcome+' M (SD)']=[f'{r[mean]:.2f} ({r[sd]:.2f})' for _,r in d.iterrows()]
    readable['Posttest=100 (%)']=100*d.PostCeilingFraction
    adjusted=means[['ClusterName','AdjustedPosttest','CI_Low_HC3','CI_High_HC3']]
    contrast=pairs[['ClusterA','ClusterB','Difference','CI_Low_HC3','CI_High_HC3','p_Holm']]
    boot=tables['Bootstrap_CI']
    gain_ci=boot.loc[boot.Quantity.eq('Gain_3')].iloc[0]
    response=(
        'Thank you for identifying the need to connect behavioral profiles with independent learning '
        'outcomes. We have now analyzed username-linked pretest and posttest scores for all 104 '
        'learners in the retained gameplay cohort. All usernames matched the authoritative cluster '
        'assignments, with no missing scores or cluster discrepancies (57 Sustained Engagers, '
        '32 Low Activity Learners, and 15 Struggling Learners).\n\n'
        'We compared posttest performance across the three profiles while accounting for pretest '
        'performance. Because posttest variances were strongly unequal and ceiling scores were '
        'common, primary inference used HC3 heteroskedasticity-robust standard errors. The '
        f'pretest-adjusted cluster effect was F({primary.DF1:.0f},{primary.DF2:.0f})='
        f'{primary.F:.3f}, p={primary.p:.3g}. At the overall mean pretest of '
        f'{model["reference_pretest"]:.2f}, adjusted posttest means were '
        f'{means.iloc[0].AdjustedPosttest:.2f}, {means.iloc[1].AdjustedPosttest:.2f}, and '
        f'{means.iloc[2].AdjustedPosttest:.2f}, respectively. The adjusted Sustained Engagers '
        f'and Low Activity Learners advantages over Struggling Learners were '
        f'{pairs.iloc[1].Difference:.2f} points (95% HC3 CI {pairs.iloc[1].CI_Low_HC3:.2f}–'
        f'{pairs.iloc[1].CI_High_HC3:.2f}) and {pairs.iloc[2].Difference:.2f} points '
        f'(95% HC3 CI {pairs.iloc[2].CI_Low_HC3:.2f}–{pairs.iloc[2].CI_High_HC3:.2f}); '
        'both remained significant after Holm correction.\n\n'
        f'As a secondary analysis, mean unadjusted gains were {d.iloc[0].GainMean:.2f}, '
        f'{d.iloc[1].GainMean:.2f}, and {d.iloc[2].GainMean:.2f} points; Welch’s test yielded '
        f'F({gain_test.WelchDF1:.0f},{gain_test.WelchDF2:.2f})={gain_test.WelchF:.3f}, '
        f'p={gain_test.WelchP:.3g}. These results indicate that the identified profiles are '
        'associated with independently measured achievement, rather than only differences in '
        'game interaction. They do not show that profile membership or help use causes learning '
        'outcomes. Ceiling effects, the n=15 profile, fixed estimated cluster membership and '
        'the single-cohort observational design remain limitations.\n\n'
        'The questionnaire was anonymous and cannot be linked to gameplay usernames. Therefore '
        'a profile–perception association cannot be tested. The proposed revision separates '
        'the questionnaire findings from gameplay-profile findings and removes any unsupported '
        'claim that perceptions differ across or are individually associated with these profiles.'
    )
    methods=(
        'Pretest and posttest scores were linked to gameplay profiles using participant usernames '
        'rather than row order. All 104 retained gameplay learners had complete linked scores. '
        'Posttest scores were modeled as a function of categorical profile and mean-centered '
        'pretest score using ordinary least-squares ANCOVA, with HC3 covariance and residual-df '
        'F/t inference for the primary tests and pointwise 95% confidence intervals. Pairwise '
        'profile contrasts were corrected using Holm’s method within the three-comparison '
        'family. A profile-by-pretest interaction model assessed sensitivity to unequal slopes. '
        'Secondary outcomes were raw gains (posttest minus pretest), compared using Welch’s '
        'ANOVA and Holm-corrected pairwise Welch tests. Additional sensitivity analyses used '
        f'{bootstrap["successful_replicates"]} within-profile learner bootstrap samples, a '
        'shared-pretest-support subset, and leave-one-learner-out refits. Anonymous questionnaire '
        'responses were not linked to behavioral profiles.'
    )
    results=(
        f'Pretest means were 83.37, 82.25 and 81.27 for Sustained Engagers, Low Activity Learners '
        f'and Struggling Learners, respectively (Welch p={pre_test.WelchP:.3f}; this does not '
        f'establish equivalence). Their posttest means were 98.77, 95.78 and 77.67. The '
        f'pretest-adjusted profile effect was significant using HC3 inference '
        f'(F({primary.DF1:.0f},{primary.DF2:.0f})={primary.F:.3f}, p<.001). Adjusted means at '
        f'pretest={model["reference_pretest"]:.2f} were {means.iloc[0].AdjustedPosttest:.2f}, '
        f'{means.iloc[1].AdjustedPosttest:.2f} and {means.iloc[2].AdjustedPosttest:.2f}. '
        f'All three adjusted pairwise comparisons remained significant after Holm correction. '
        f'Mean raw gains were 15.40, 13.53 and −3.60 points; secondary Welch ANOVA was '
        f'significant (F(2,{gain_test.WelchDF2:.2f})={gain_test.WelchF:.3f}, p<.001). '
        f'The negative mean in Struggling Learners is descriptive: its bootstrap gain CI '
        f'[{gain_ci.CI_Low:.2f}, {gain_ci.CI_High:.2f}] includes zero and does not independently '
        f'establish a within-group decline.'
    )
    gain_pairs=tables['Gain_Contrasts']
    results += (f' Pairwise gain comparisons distinguish Struggling Learners from both other profiles '
        f'(Holm p={gain_pairs.iloc[1].p_Holm:.6g} and {gain_pairs.iloc[2].p_Holm:.6g}), '
        f'but Sustained Engagers and Low Activity Learners do not differ significantly in gains '
        f'(Holm p={gain_pairs.iloc[0].p_Holm:.3f}).')
    discussion=(
        'The profile comparison adds educational relevance to the behavioral findings: learners '
        'assigned to the Struggling profile showed substantially lower posttest achievement after '
        'accounting for baseline performance. However, Low Activity Learners also achieved high '
        'posttest scores and positive gains, so limited logged activity should not be equated '
        'with low achievement. These are exploratory associations, not causal effects or stable '
        'learner classifications. High posttest ceilings can compress differences and obscure '
        'the relationship with baseline scores. The small Struggling profile limits precision. '
        'The anonymous questionnaire cannot support individual-level links between profile '
        'membership and perceived experience; survey findings must be discussed separately.'
    )
    report='\n'.join([
        '# R1-Q7: learning outcomes across the three exploratory gameplay profiles','',
        '## Direct answer to the reviewer','',
        '**The new username-linked data now permit the missing learning-outcome analysis.** '
        'All 104 retained learners match; independent posttest performance differs across '
        'profiles after pretest adjustment. The questionnaire portion remains untestable '
        'because survey responses are unidentified. No perception–profile link is inferred.','',
        '## 1. Source linkage and sample','',
        'Primary source: `Data/R1-Q7/Score-Username.xlsx`, sheet `Score-Username`. '
        '`104-Pre-Post-Match-Username.xlsx` corroborates the local No/pre/post values, while '
        '`104-Username_Cluster.xlsx` corroborates the username/cluster mapping. '
        'Authoritative clusters come from `results/clustering/analysis_kmeans_assignments.csv`. '
        'Matching trims leading/trailing username whitespace only and preserves case; '
        'no row-order or score-based identity matching is performed. No is a local source '
        'record number, not the key for joining to gameplay.','',
        markdown_table(pd.DataFrame([{'Item':k,'Value':v} for k,v in linkage.items()])),'',
        'All 104 retained learners have observed scores, so no outcome imputation is performed. '
        'These are reviewer-requested analyses; no preregistration was supplied. “Primary” '
        'denotes analytic priority within this report, not evidence of prospective specification. '
        'The 11 learners excluded from the original behavioral cohort are not assigned profiles '
        'or silently included in this comparison. The source usernames have been structurally '
        'validated, but the original username-to-test identity records remain the authors’ '
        'responsibility. The scores are trusted as supplied, not independently psychometrically validated.','',
        '## 2. Descriptive learning outcomes','',markdown_table(readable),'',
        'Gain is PostTest − PreTest in score points. High posttest ceiling proportions '
        '(78.95%, 40.63%, 0%) are an important limitation. Pretest differences are not '
        'significant by Welch’s test, but absence of significance does not prove equal '
        'baselines or remove confounding.','',
        '## 3. Primary analysis: posttest adjusted for pretest','',
        f'Model: PostTest = intercept + categorical Cluster + (PreTest − '
        f'{model["reference_pretest"]:.8f}). The profile factor has three levels; residual '
        'df=100. The dependent variable is the independent Git posttest, not in-game TotalScore '
        'or the score-per-minute behavioral indicator. Neither pretest nor posttest was used '
        'to create these fixed clusters.','',
        'Posttest variances differ strongly (median-centered Levene '
        f'p={post_test.LeveneMedianP:.6g}). Therefore HC3 standard errors and residual-df '
        'Wald F/t tests are the primary inference. They address heteroskedasticity, not '
        'ceiling nonlinearity, cluster-selection uncertainty or unmeasured confounding.','',
        markdown_table(tests),'',
        f'Conventional ANCOVA gives F(2,100)={ordinary.F:.6f}, p={ordinary.p:.6g}. '
        f'The corresponding **classical partial eta-squared is {model["partial_eta_squared_classical"]:.6f}**, '
        'computed as (SSR_pretest-only − SSR_full) / SSR_pretest-only. This is an OLS '
        'variance-decomposition effect size, **not** an effect size calculated from the '
        'HC3 Wald F. Do not combine a robust F with a classical F-to-eta formula. '
        f'Full model R²={model["r_squared"]:.6f}, adjusted R²={model["adjusted_r_squared"]:.6f}.','',
        'Adjusted posttest means evaluated at the original pooled pretest mean:','',
        markdown_table(adjusted),'',
        'Pairwise comparisons are ClusterA − ClusterB. Confidence intervals are pointwise '
        '95% HC3 intervals; p_Holm corrects the three pairwise p-values as a family. '
        'They are not simultaneous confidence intervals.','',markdown_table(contrast),'',
        '## 4. Slope, ceiling and robustness checks','',
        f'The profile-by-pretest interaction has robust F({interaction.DF1:.0f},'
        f'{interaction.DF2:.0f})={interaction.F:.6f}, p={interaction.p:.6g}. '
        'This does not reject equal slopes using the robust test, but it does not prove '
        'equal slopes, especially with only 15 Struggling Learners. The interaction '
        'coefficients and contrasts at the same reference pretest are supplied for sensitivity.','',
        markdown_table(tables['Interaction_Contrasts']),'',
        f'Pretest support shared by all profiles is [{sensitivity["common_pretest_min"]:.0f}, '
        f'{sensitivity["common_pretest_max"]:.0f}]. Restricting to that interval retains '
        f'{sensitivity["common_n"]} learners with counts {sensitivity["common_cluster_counts"]}. '
        'The original reference pretest is retained in this model. This avoids range '
        'extrapolation, although similar min/max ranges do not guarantee equal score density.','',
        markdown_table(tables['Common_Support_Tests']), '',markdown_table(tables['Common_Support_Contrasts']),'',
        f'The learner bootstrap uses {bootstrap["successful_replicates"]} successful samples '
        f'out of {bootstrap["requested_replicates"]}, with seed {bootstrap["seed"]}. Complete '
        'pre/post records are resampled within fixed profiles, the common-slope model is '
        'refitted, and the original reference pretest is held fixed. Percentile 95% CIs '
        'are conditional on the sample, model and fixed clustering; they do not include '
        'uncertainty in assigning profiles or validate an external population.','',
        markdown_table(tables['Bootstrap_CI']),'',
        'Leave-one-learner-out analysis reports ranges of estimated adjusted differences '
        'and the largest Holm-corrected p-value across all 104 deletions. These ranges '
        'are sensitivity diagnostics, not confidence intervals.','',
        markdown_table(tables['Leave_One_Out']),'',
        'The linear model can theoretically predict scores outside 0–100. Predictions '
        'and CIs are not clipped. The ceiling is structural: HC3 and bootstrap do not '
        'undo restricted score ranges or recover unobserved achievement above the maximum.','',
        '## 5. Secondary analysis: raw learning gains','',
        f'Welch gain comparison: F({gain_test.WelchDF1:.0f},{gain_test.WelchDF2:.6f})='
        f'{gain_test.WelchF:.6f}, p={gain_test.WelchP:.6g}. Gains are secondary, unadjusted '
        'comparisons and share the same pre/post data; they are not an independent '
        'replication. No normalized-gain ratio is used.','',
        markdown_table(tables['Gain_Contrasts']),'',
        'Within-profile negative average gain is not itself a test of decline. For '
        f'Struggling Learners the mean is −3.60 points, with bootstrap CI '
        f'[{gain_ci.CI_Low:.3f}, {gain_ci.CI_High:.3f}]. Interpret the smaller gain '
        'relative to other profiles separately from evidence of absolute loss.','',
        '## 6. What can be said about perceptions','',
        '**No profile–perception test is possible from unidentified questionnaire responses.** '
        'Do not match survey rows to the usernames, profiles or test scores by ordering '
        'or by similar response patterns. Anonymous survey constructs can be analyzed '
        'within their own respondent dataset, but those results must remain separate '
        'from gameplay-profile associations. Remove or qualify any sentence implying '
        'that perceptions are individually related to the three profiles. This is a '
        'limitation of linkage, not a finding that perceptions have no relationship.','',
        '## 7. Proposed manuscript revisions','',
        '**Methods:**','',methods,'', '**Results:**','',results,'',
        '**Discussion / limitation:**','',discussion,'',
        'These are proposed replacements. No manuscript file has been edited and no '
        'page/line references are invented. The authors should insert the text where '
        'the reviewer’s claimed association is currently stated.','',
        '## 8. Draft response to the reviewer','',response,'',
        '## 9. What to give ChatGPT for the manuscript revision','',
        'Upload the latest manuscript Word file, **this report** (`R1_Q7_Analysis_Report.docx`), '
        '**Evidence_For_ChatGPT.xlsx**, the exact reviewer comment, and **ChatGPT_Revision_Prompt.txt**. '
        'The workbook contains all evidence tables and anonymized learner rows. Raw '
        'usernames are unnecessary for writing the revision. Do not upload the PRIVATE '
        'linkage workbook or the username-containing SAV unless there is a specific '
        'authorized need. The report and evidence workbook are sufficient to write '
        'an evidence-based response.','',
        '`Matched_Username_Data_PRIVATE.xlsx` and `Profile_Learning_Outcomes.sav` are '
        'for the authors’ identity audit and SPSS use. `Run_Profile_ANCOVA.sps` includes '
        'HC3 custom hypothesis tests; ordinary SPSS ANOVA F and EMMEANS CIs must not '
        'be mistaken for the primary robust tests. SPSS itself is not installed here; '
        'syntax is based on IBM documentation and has not been executed in SPSS.','',
        '## Methods references','',
        '- [IBM: covariate-slope checks](https://www.ibm.com/docs/en/spss-statistics/31.0.0?topic=covariance-checking-homogeneity-covariate-coefficients)',
        '- [IBM: HC3 and robust custom tests](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=unianova-robust-subcommand-command)',
        '- [IBM: LMATRIX contrasts](https://www.ibm.com/docs/en/spss-statistics/32.0.0?topic=unianova-lmatrix-subcommand-command)',
        '- [statsmodels: heteroskedasticity-robust ANOVA](https://www.statsmodels.org/stable/_modules/statsmodels/stats/anova.html)',''])
    return report,response


def build_prompt(tables):
    primary=tables['Primary_ANCOVA'].iloc[0]
    return f'''Revise ONLY the manuscript content needed to address this reviewer comment:

"The manuscript states that gameplay profiles are related to player perceptions and post-test performance. However, the presented results primarily describe behavioural indicators and transition patterns. A particularly important missing analysis is whether the three behavioural clusters differ in post-test performance or learning gains. The authors are encouraged to compare learning outcomes across the identified profiles, preferably accounting for pretest performance. This would help establish whether the observed behavioural differences have meaningful educational implications rather than representing only differences in game interaction."

I attach:
1. The current manuscript Word file.
2. R1_Q7_Analysis_Report.docx.
3. Evidence_For_ChatGPT.xlsx (analysis tables and anonymized learner records).

Author-confirmed facts:
- All 104 username-linked learners matched the retained clusters (57/32/15). No scores are missing.
- PreTest/PostTest are the independent test outcomes provided in Data/R1-Q7. Gain=PostTest-PreTest.
- Primary model: PostTest ~ Cluster + centered PreTest; HC3 covariance and residual-df Wald inference.
- Primary cluster test: F({primary.DF1:.0f},{primary.DF2:.0f})={primary.F:.6f}, p={primary.p:.8g}.
- Questionnaire responses are unidentified. No profile-perception association can be estimated. Never match questionnaire rows by ordering or similar answers.

Tasks:
A. Locate the exact manuscript sentences making profile-performance or profile-perception claims.
B. Write precise replacement Methods, Results, Discussion and Limitations text, using only the supplied evidence.
C. Propose a compact table of n, pre/post/gain M(SD), adjusted posttest means with 95% HC3 CIs, and the adjusted contrasts/effect-size notes.
D. Draft a respectful, point-by-point reviewer response explaining the completed username linkage, adjusted outcome comparison, secondary gains, robustness checks, and questionnaire limitation.
E. Identify anything that remains unsupported and should be removed or qualified.

Requirements:
- Preserve the fixed three-cluster assignments; do not rerun clustering or introduce PCA-before-clustering.
- Keep primary HC3 F/t tests separate from conventional ANCOVA. Classical partial eta-squared comes from OLS residual sums of squares, not the HC3 F.
- Use Holm-adjusted p-values for pairwise contrasts. Confidence intervals are pointwise, not simultaneous.
- Do not treat gains as an independent replication of the same pre/post data.
- Do not claim pretest equivalence solely from a nonsignificant test, equal slopes from nonsignificance, or proven learning loss from a negative mean gain.
- Explain the small n=15 profile, high posttest ceilings, model dependence, and observational rather than causal profile associations.
- State that Low Activity Learners can still have high achievement; do not equate limited logs with poor learning.
- Remove any unsupported individual profile-perception claim while allowing the anonymous questionnaire analysis to remain a separate study component.
- Do not invent data, analyses, SPSS execution, manuscript edits, page numbers or line numbers.
- If producing proposed text rather than editing the document, state that clearly. Use actual section names/paragraphs from the supplied manuscript.
'''


def export_syntax(folder):
    directory=str(folder.resolve()).replace("'","''")
    text=f"CD '{directory}'.\nGET FILE='Profile_Learning_Outcomes.sav'.\nFILTER OFF.\nWEIGHT OFF.\nSPLIT FILE OFF.\n"
    text+='''
* Primary common-slope ANCOVA. ROBUST adds HC3 parameter/custom-hypothesis output.
* The standard Tests of Between-Subjects Effects remain conventional: do not mix them with HC3.
UNIANOVA PostTest BY Cluster WITH PreCentered
 /METHOD=SSTYPE(3)
 /ROBUST=HC3
 /PRINT=DESCRIPTIVE HOMOGENEITY PARAMETER ETASQ
 /LMATRIX='Overall cluster HC3' Cluster 1 -1 0; Cluster 1 0 -1
 /LMATRIX='Profile 1 minus 2 HC3' Cluster 1 -1 0
 /LMATRIX='Profile 1 minus 3 HC3' Cluster 1 0 -1
 /LMATRIX='Profile 2 minus 3 HC3' Cluster 0 1 -1
 /LMATRIX='Profile 1 adjusted mean HC3' INTERCEPT 1 Cluster 1 0 0
 /LMATRIX='Profile 2 adjusted mean HC3' INTERCEPT 1 Cluster 0 1 0
 /LMATRIX='Profile 3 adjusted mean HC3' INTERCEPT 1 Cluster 0 0 1
 /EMMEANS=TABLES(Cluster) WITH(PreCentered=0)
 /DESIGN=PreCentered Cluster.

* EMMEANS points agree, but EMMEANS CIs are conventional, not the HC3 custom-test CIs.
* LMATRIX pairwise p-values are unadjusted. Use Holm p-values from the evidence workbook.
* Or sort the three raw p-values and apply step-down multipliers 3,2,1 with cumulative maximum, capped at 1.

* Sensitivity to unequal pretest slopes. Use the robust two-df interaction hypothesis.
UNIANOVA PostTest BY Cluster WITH PreCentered
 /METHOD=SSTYPE(3)
 /ROBUST=HC3
 /PRINT=PARAMETER
 /LMATRIX='Slope interaction HC3' PreCentered*Cluster 1 -1 0; PreCentered*Cluster 1 0 -1
 /DESIGN=PreCentered Cluster PreCentered*Cluster.

* Raw learning gains are secondary; retain the Welch row, not only ordinary ANOVA.
ONEWAY Gain BY Cluster
 /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH
 /MISSING ANALYSIS.

* SPSS syntax has not been executed in the analysis environment.
* If an older version does not support ROBUST, ordinary output will not reproduce HC3 inference.
'''
    (folder/'Run_Profile_ANCOVA.sps').write_text(text,encoding='utf-8')


def create_figure(folder,tables):
    import matplotlib.pyplot as plt
    means=tables['Adjusted_Posttest'];d=tables['Descriptives'];boot=tables['Bootstrap_CI'].set_index('Quantity')
    labels=['Sustained\nEngagers','Low Activity\nLearners','Struggling\nLearners']
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    axes[0].errorbar(range(3),means.AdjustedPosttest,yerr=np.stack([means.AdjustedPosttest-means.CI_Low_HC3,means.CI_High_HC3-means.AdjustedPosttest]),fmt='o',capsize=5)
    axes[0].set(xticks=range(3),xticklabels=labels,ylabel='Adjusted posttest score',ylim=(0,105),title='Pretest-adjusted posttest (95% HC3 CI)')
    low=np.array([boot.loc[f'Gain_{c}','CI_Low'] for c in [1,2,3]])
    high=np.array([boot.loc[f'Gain_{c}','CI_High'] for c in [1,2,3]])
    axes[1].errorbar(range(3),d.GainMean,yerr=np.stack([d.GainMean-low,high-d.GainMean]),fmt='o',capsize=5,color='#C35A26')
    axes[1].axhline(0,color='gray',linewidth=1)
    axes[1].set(xticks=range(3),xticklabels=labels,ylabel='Posttest − pretest (points)',title='Raw gains (95% learner-bootstrap CI)')
    fig.tight_layout();fig.savefig(Path(folder)/'Profile_Learning_Outcomes.png',dpi=300);plt.close(fig)
