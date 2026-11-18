"""Create a portable PDF tutorial for the original Table 9 F1–F14 SPSS dataset."""
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
import pyreadstat
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted

from ..data_io import OUTPUT_DIR
from .table9 import FEATURES


def run(folder=None):
    folder=Path(folder) if folder else OUTPUT_DIR/'spss'
    pdf=folder/'SPSS_Table9_Step_by_Step_Guide.pdf'
    data,metadata=pyreadstat.read_sav(folder/'Table9_F1_F14_Data.sav')
    expected=pd.read_excel(folder/'Table9_F1_F14_Data.xlsx',sheet_name='Expected_ANOVA').set_index('FeatureCode')
    desc=pd.read_excel(folder/'Table9_F1_F14_Data.xlsx',sheet_name='Expected_Mean_SD_N')
    assert len(data)==104 and data.groupby('Cluster').size().tolist()==[57,32,15]
    fontdir=Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('Guide',str(fontdir/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('GuideBold',str(fontdir/'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('GuideMono',str(fontdir/'DejaVuSansMono.ttf')))
    pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold',italic='Guide',boldItalic='GuideBold')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyGuide',fontName='Guide',fontSize=9.2,leading=13.5,spaceAfter=7))
    styles.add(ParagraphStyle(name='HeadingGuide',fontName='GuideBold',fontSize=17,leading=22,spaceAfter=13,textColor=colors.HexColor('#163858')))
    styles.add(ParagraphStyle(name='SubGuide',fontName='GuideBold',fontSize=11,leading=15,spaceBefore=8,spaceAfter=6))
    styles.add(ParagraphStyle(name='SmallGuide',fontName='Guide',fontSize=7.7,leading=10.5,spaceAfter=5))
    styles.add(ParagraphStyle(name='CellGuide',fontName='Guide',fontSize=8,leading=11))
    styles.add(ParagraphStyle(name='CodeGuide',fontName='GuideMono',fontSize=8,leading=11,spaceAfter=6))
    story=[]
    def para(text,style='BodyGuide'):story.append(Paragraph(text,styles[style]))
    def heading(number,title):para(f'{number}. {title}','HeadingGuide')
    def step(number,text):para(f'<b>{number}.</b> {text}')
    def sub(text):para(text,'SubGuide')
    def table(rows,widths,small=False):
        cells=[[Paragraph(escape(str(c)),styles['SmallGuide' if small else 'CellGuide']) for c in row] for row in rows]
        t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eff7')),
            ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#9aabb8')),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.append(t);story.append(Spacer(1,9))
    def page():story.append(PageBreak())

    heading(1,'Use this input file')
    para('<b>Table9_F1_F14_Data.sav</b> is the input data file to open in SPSS. It contains individual learner observations, not just the means and SDs displayed in Table 9.')
    table([['File','Purpose'],['Table9_F1_F14_Data.sav','Recommended SPSS input: 104 learner rows, Cluster, ClusterLabel, ID, and F1–F14.'],
        ['Table9_F1_F14_Data.xlsx','Alternative input. Import the All_Learners sheet only.'],
        ['Run_Table9_ANOVA.sps','Ready-made SPSS syntax; not a data file.'],
        ['Expected_Mean_SD_N / Expected_ANOVA workbook sheets','Reference results for checking your output. Do not use these summary rows as learner input.']], [190,315])
    sub('Step 1: extract and open the data')
    step(1,'Copy the files from <b>results/spss</b> into one folder on your computer. Keep the SAV, syntax and this PDF together.')
    step(2,'Start IBM SPSS Statistics. Choose <b>File → Open → Data</b>, browse to that folder, select <b>Table9_F1_F14_Data.sav</b>, and click <b>Open</b>.')
    step(3,'In <b>Data View</b>, check the columns ID, Cluster, ClusterLabel and F1 through F14. There should be <b>104 learner rows</b>.')
    step(4,'In <b>Variable View</b>, Cluster should be numeric/nominal and F1–F14 numeric/scale. The SAV file already defines these settings and the cluster value labels. ID and ClusterLabel are not dependent variables.')
    sub('Step 2: verify the grouping variable')
    para('Choose <b>Analyze → Descriptive Statistics → Frequencies</b>. Move <b>Cluster</b> into the variable box and click <b>OK</b>. Check these counts:')
    table([['Cluster','Table 9 label','Learners'],['1','Sustained Engagers','57'],['2','Low Activity Learners','32'],['3','Struggling Learners','15'],['Total','','104']], [55,365,85])
    para('This file uses the <b>original three-cluster assignments underlying the attached Table 9</b>. The retained workflow applies K-means directly to standardized indicators; PCA is used only for visualization.','SmallGuide')
    page()

    heading(2,'Understand F1–F14')
    para('Use all 14 codes as dependent variables. The codes match the order in your attached table. F1–F11 were inputs to the original clustering; F12–F14 were used only for profiling. This tutorial does <b>not</b> rerun PCA or clustering.')
    table([['Code','Indicator','Exported units']]+[[code,label,unit] for code,_,label,unit in FEATURES],[40,235,230])
    sub('Important units and missing values')
    para('• <b>F9–F11 are already percentages (0–100).</b> Do not multiply them by 100 again.<br/>'
         '• <b>F14 is in raw game-score points.</b> The average for Cluster 1 is about 91,951.75 points, not 91.95 raw points.<br/>'
         '• <b>F8 is game-score points per minute</b>, not pre/post learning gain.<br/>'
         '• F12 uses the saved stage-clear counter; do not interpret it as the number of completed quests.<br/>'
         '• A dot/blank in a numeric field is missing data. Keep it missing. Do not replace missing values with zero or a clustering-imputed median.')
    para('Cluster membership counts (57/32/15) are header totals. A feature can have fewer usable observations. For example, F8 has <b>57/25/12</b> valid observations. The next steps preserve those feature-specific sample sizes.')
    page()

    heading(3,'Run the one-way ANOVA in SPSS')
    sub('Step 3: make sure all learners are available')
    para('If you have changed the dataset or are reusing an SPSS session, check:<br/>'
         '• <b>Data → Select Cases → All cases</b>.<br/>'
         '• <b>Data → Split File → Analyze all cases, do not create groups</b>.<br/>'
         '• <b>Data → Weight Cases → Do not weight cases</b>.<br/>'
         'These settings prevent accidental case filtering, separate analyses, or weighting.')
    sub('Step 4: choose the analysis')
    step(1,'Choose <b>Analyze → Compare Means → One-Way ANOVA</b>. Some versions organize the menu slightly differently; look for the procedure named <b>One-Way ANOVA</b>, not ANCOVA, GLM, or Bayesian ANOVA.')
    step(2,'Select <b>F1, F2, …, F14</b> and move them into <b>Dependent List</b>. SPSS may display the longer indicator labels; they refer to the same feature codes.')
    step(3,'Move <b>Cluster</b> into <b>Factor</b>. Do not use ClusterLabel or ID as the factor. Do not put Cluster into Dependent List.')
    table([['Box in the SPSS dialog','Your selection'],['Dependent List','F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14'],['Factor','Cluster']], [165,340])
    step(4,'Select <b>Estimate effect size for overall tests</b> if available (SPSS 27 and later). This requests the eta-squared output used in Table 9.')
    sub('Step 5: set Options')
    step(1,'Click <b>Options</b>. Request <b>Descriptive</b> statistics, <b>Homogeneity of variance test</b>, and <b>Welch</b> if offered. Keep the confidence level at <b>95%</b>.')
    step(2,'Under missing values, select <b>Exclude cases analysis by analysis</b>. Do <b>not</b> choose “Exclude cases listwise.” Each indicator must use its own valid observations.')
    step(3,'Click <b>Continue</b>, then <b>OK</b>. The SPSS Output Viewer should display results for F1–F14.')
    para('<b>Post Hoc is not required to reproduce Table 9.</b> The table reports omnibus ANOVA tests, not pairwise comparisons. Welch is a supplementary variance-sensitivity check, not the source of the ordinary F values in the table.','SmallGuide')
    page()

    heading(4,'Read the output and build Table 9')
    table([['Your Table 9 column','Where to find it in SPSS'],
        ['M (SD) for each profile','Descriptives table: copy Mean and Std. Deviation for Cluster 1, 2 and 3. Do not copy Std. Error.'],
        ['Valid sample size','Descriptives table: N for that feature and cluster. It can differ from the membership total.'],
        ['F','ANOVA table: F in the Between Groups row for that feature.'],
        ['p','ANOVA table: Sig. in that same row.'],
        ['η²','ANOVA Effect Sizes table: Eta-squared, Point Estimate. Do not substitute omega-squared, epsilon-squared or Cohen’s f.']], [140,365])
    sub('Step 6: report correctly')
    para('Round means, SDs and F to two decimals if following your table style. Report eta-squared to three decimals. SPSS may display <b>.000</b> for very small p-values; write <b>p &lt; .001</b>, not p = .000. Do not multiply eta-squared by 100 unless explicitly reporting a percentage.')
    sub('Worked check: F8, Learning Efficiency')
    f8=desc.loc[desc.FeatureCode.eq('F8')].sort_values('Cluster')
    table([['Cluster','Valid N','Mean','Sample SD']]+[[int(r.Cluster),int(r.ValidN),f'{r.Mean:,.2f}',f'{r.SampleSD:,.2f}'] for r in f8.itertuples()],[70,80,175,180])
    r=expected.loc['F8']
    para(f'The ordinary test should be <b>F(2, {int(r.DFWithin)}) = {r.F:.3f}, p &lt; .001, η² = {r.EtaSquared:.3f}</b>. Total valid N = {int(r.ValidN)}. The Low Activity Learners SD is <b>2,462.67</b>; the attached table’s <b>246.67</b> is a typographical error. Do not alter the data to reproduce that incorrect SD.')
    sub('If your SPSS version does not report effect sizes')
    para('Use the ordinary ANOVA sums of squares for each feature:<br/><b>η² = Between Groups Sum of Squares ÷ Total Sum of Squares.</b><br/>Use the same feature and the same analysis-specific valid cases. With a one-factor ANOVA this also equals partial eta-squared, but an adjusted ANCOVA effect size would describe a different model.')
    para('Levene tests assess equality of variances. Welch results appear under robust tests of equality of means. If a group has zero variance (for example F4 in Cluster 2), a Welch result may be unavailable. This does not mean the entire dataset is invalid. Do not combine a Welch F with ordinary ANOVA degrees of freedom.','SmallGuide')
    page()

    heading(5,'Check your numerical results')
    para('These values are calculated from the supplied learner observations. N1/N2/N3 are valid observations in Clusters 1/2/3. Cluster membership totals remain 57/32/15.')
    rows=[['Code','N1','N2','N3','Ordinary F','p','η²']]
    for code,_,_,_ in FEATURES:
        row=expected.loc[code]
        ns=desc.loc[desc.FeatureCode.eq(code)].sort_values('Cluster').ValidN.astype(int).tolist()
        rows.append([code,*ns,f'{row.F:.2f}','< .001' if row.p<.001 else f'{row.p:.3f}',f'{row.EtaSquared:.3f}'])
    table(rows,[45,40,40,40,115,100,125])
    sub('F14 score units: use consistent means and SDs')
    f14=desc.loc[desc.FeatureCode.eq('F14')].sort_values('Cluster')
    table([['Cluster','Valid N','Mean (raw points)','SD (raw points)']]+[[int(r.Cluster),int(r.ValidN),f'{r.Mean:,.2f}',f'{r.SampleSD:,.2f}'] for r in f14.itertuples()],[70,80,175,180])
    para('If you prefer <b>thousands of points</b>, divide <b>every F14 observation</b> by 1,000 and label the unit. Both means <i>and</i> SDs must then be divided by 1,000. F, p and eta-squared do not change under that linear rescaling. Do not mix a raw-point mean with an SD expressed in thousands.')
    sub('If your output does not match')
    para('First check that you opened <b>Table9_F1_F14_Data.sav</b>, that Cluster has 57/32/15 cases, that filters/weights/split-file are off, and that missing values are excluded <b>analysis by analysis</b>. Check you copied Std. Deviation rather than Std. Error, and used the ordinary ANOVA row. Compare full values with the Expected_Mean_SD_N workbook sheet and the Expected_ANOVA workbook sheet.')
    page()

    heading(6,'Run syntax, save and export results')
    sub('Alternative: run the supplied syntax')
    step(1,'Choose <b>File → Open → Syntax</b> and open <b>Run_Table9_ANOVA.sps</b>.')
    step(2,'Replace the first <b>CD</b> directory with the location of your extracted folder. A Windows example is shown below; replace it with your actual directory.')
    code="""CD 'C:/Research/Table9-F1-F14-SPSS'.
GET FILE='Table9_F1_F14_Data.sav'.
DATASET NAME Table9Data.
FILTER OFF.
WEIGHT OFF.
SPLIT FILE OFF.

ONEWAY F1 TO F14 BY Cluster
 /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH
 /MISSING ANALYSIS
 /ES OVERALL."""
    story.append(Preformatted(code,styles['CodeGuide']))
    step(3,'Choose <b>Run → All</b>. On SPSS before version 27, remove the line <b>/ES OVERALL</b> and place the final period after <b>/MISSING ANALYSIS</b>. Then calculate eta-squared from sums of squares as described on page 4.')
    sub('Step 7: save your SPSS analysis output')
    step(1,'In the <b>Output Viewer</b>, choose <b>File → Save As</b> and save an <b>.spv</b> output file. Saving the data file alone does not save the analysis tables.')
    step(2,'To share results, use <b>File → Export</b> from the Output Viewer and choose PDF, Word or Excel if supported by your version. Export the Descriptives, ANOVA, ANOVA Effect Sizes and relevant variance-check tables.')
    step(3,'Construct your publication table using the three means (SDs), ordinary F, p and eta-squared for each F-code. Add a note that valid n differs by indicator and disclose the corrected F8 SD and consistent F14 score units.')
    sub('Scope of the interpretation')
    para('This workflow reproduces a <b>descriptive one-way ANOVA table</b>. It does not run ANCOVA, adjust for pretest, prove causal effects, or validate learner types independently. F1–F11 helped form the original clusters, so their between-cluster comparisons are descriptive. SPSS itself is not installed in the generation environment; the data and reference arithmetic were verified, and menu/syntax instructions follow IBM documentation.')
    sub('Official IBM references')
    for title,url in [
        ('One-Way ANOVA procedure','https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=features-one-way-anova'),
        ('Options and per-analysis missingness','https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=anova-one-way-options'),
        ('ONEWAY command syntax','https://www.ibm.com/docs/en/spss-statistics/31.0.0?topic=reference-oneway'),
        ('Overall effect sizes','https://www.ibm.com/docs/en/spss-statistics/32.0.0?topic=oneway-es-subcommand-command')]:
        para(f'<link href="{url}" color="#145a96">{escape(title)}</link>','SmallGuide')

    def footer(canvas,document):
        canvas.saveState();canvas.setFont('Guide',8);canvas.setFillColor(colors.HexColor('#52616c'))
        canvas.drawString(45,23,'Table 9 • F1–F14 • original 57/32/15 clusters')
        canvas.drawRightString(A4[0]-45,23,f'Page {document.page}')
        canvas.restoreState()
    document=SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=40,bottomMargin=43,
        title='SPSS step-by-step guide: Table 9 F1–F14',author='Gitainment behavior analysis project')
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF guide written: '+str(pdf))
    return pdf


if __name__=='__main__':run()
