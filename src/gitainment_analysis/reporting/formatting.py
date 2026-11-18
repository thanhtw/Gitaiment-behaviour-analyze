"""Shared Markdown table and Word export helpers."""
import pandas as pd

def markdown_table(frame, digits=4):
    def cell(value):
        if pd.isna(value):
            return 'NA'
        return f'{value:.{digits}g}' if isinstance(value, float) else str(value)
    lines = ['| ' + ' | '.join(map(str, frame.columns)) + ' |',
             '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |']
    lines += ['| ' + ' | '.join(cell(value) for value in row) + ' |' for row in frame.itertuples(index=False, name=None)]
    return '\n'.join(lines)



def export_docx(report,path):
    from docx import Document
    from docx.shared import Pt
    document=Document()
    document.styles['Normal'].font.size=Pt(10)
    lines=report.splitlines()
    i=0
    while i<len(lines):
        line=lines[i]
        if line.startswith('|'):
            table_lines=[]
            while i<len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i]);i+=1
            rows=[[x.strip().replace('**','') for x in text.strip('|').split('|')] for text in table_lines]
            rows=[row for row in rows if not all(set(x)<=set('-: ') for x in row)]
            table=document.add_table(rows=0,cols=len(rows[0]));table.style='Table Grid'
            for row in rows:
                cells=table.add_row().cells
                for cell,value in zip(cells,row):cell.text=value
            continue
        if line.startswith('# '):document.add_heading(line[2:],0)
        elif line.startswith('## '):document.add_heading(line[3:],1)
        elif line.startswith('> '):document.add_paragraph(line[2:].replace('**',''),style='Quote')
        elif line.strip():document.add_paragraph(line.replace('**','').replace('`',''))
        i+=1
    document.save(path)

