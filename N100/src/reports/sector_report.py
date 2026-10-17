"""Batch sector PDFs with sector medians and wrapped company metrics."""
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from src.common import connect, REPORTS_DIR
NAVY=colors.HexColor('#142B4A'); LIGHT=colors.HexColor('#EEF2F7')
def generate_sector_reports(db_path=None, output_dir=None):
    out=Path(output_dir or REPORTS_DIR/'sector'); out.mkdir(parents=True,exist_ok=True)
    con=connect(db_path)
    co=pd.read_sql_query('select id as company_id,company_name from companies',con); sec=pd.read_sql_query('select company_id,broad_sector,sub_sector from sectors',con)
    pl=pd.read_sql_query('select company_id,year,sales,net_profit,opm_percentage from profitandloss',con); r=pd.read_sql_query('select company_id,year,return_on_equity_pct,roce_pct,debt_to_equity,interest_coverage,free_cash_flow_cr,capital_allocation_pattern from financial_ratios',con); mc=pd.read_sql_query('select company_id,year,market_cap_crore,pe_ratio,dividend_yield_pct from market_cap',con); con.close()
    latest=lambda df: df.sort_values('year').groupby('company_id').tail(1)
    d=co.merge(sec,on='company_id',how='left').merge(latest(pl),on='company_id',how='left',suffixes=('','_pl')).merge(latest(r),on=['company_id','year'],how='left',suffixes=('','_r')).merge(latest(mc),on=['company_id','year'],how='left',suffixes=('','_mc'))
    d['broad_sector']=d['broad_sector'].fillna('Unknown')
    styles=getSampleStyleSheet(); title=ParagraphStyle('title',parent=styles['Title'],fontSize=17,textColor=NAVY); small=ParagraphStyle('small',parent=styles['BodyText'],fontSize=7,leading=8); cell=ParagraphStyle('cell',parent=small,wordWrap='CJK')
    sectors=sorted(d.broad_sector.unique().tolist())
    # Source snapshot contains 10 real broad sectors; add All Sectors benchmark as requested 11th PDF.
    tasks=[(s,d[d.broad_sector==s].copy(),False) for s in sectors]+[('All Sectors',d.copy(),True)]
    for sector,g,overall in tasks:
        safe='all_sectors' if overall else ''.join(ch.lower() if ch.isalnum() else '_' for ch in sector).strip('_')
        path=out/f'{safe}_report.pdf'; story=[Paragraph(f'{sector} — Sector Report',title),Paragraph(f'Companies covered: {g.company_id.nunique()} | Report includes latest available company metrics.',small),Spacer(1,4*mm)]
        metrics=['sales','net_profit','opm_percentage','return_on_equity_pct','roce_pct','debt_to_equity','interest_coverage','free_cash_flow_cr','market_cap_crore','pe_ratio']
        labels={'sales':'Revenue','net_profit':'Net Profit','opm_percentage':'OPM %','return_on_equity_pct':'ROE %','roce_pct':'ROCE %','debt_to_equity':'D/E','interest_coverage':'ICR','free_cash_flow_cr':'FCF','market_cap_crore':'Market Cap','pe_ratio':'P/E'}
        med=[]
        for m in metrics:
            if m in g: med.append([labels[m],f'{pd.to_numeric(g[m],errors="coerce").median():,.2f}' if pd.to_numeric(g[m],errors='coerce').notna().any() else 'N/A'])
        story += [Paragraph('Sector median KPIs',styles['Heading2'])]
        mt=Table([[Paragraph('<b>Metric</b>',cell),Paragraph('<b>Median</b>',cell)]]+[[Paragraph(str(a),cell),Paragraph(str(b),cell)] for a,b in med],colWidths=[55*mm,40*mm]); mt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT])])); story += [mt,Spacer(1,4*mm),Paragraph('Companies and latest metrics',styles['Heading2'])]
        headers=['Ticker','Company','Revenue','Net Profit','ROE %','ROCE %','D/E','ICR','FCF','Pattern']
        data=[[Paragraph(f'<b>{h}</b>',cell) for h in headers]]
        for _,x in g.sort_values('company_id').iterrows():
            data.append([Paragraph(str(x.get('company_id','')),cell),Paragraph(str(x.get('company_name',''))[:100],cell)]+[Paragraph((f'{float(x.get(m)):,.1f}' if pd.notna(x.get(m)) else 'N/A'),cell) for m in ['sales','net_profit','return_on_equity_pct','roce_pct','debt_to_equity','interest_coverage','free_cash_flow_cr']]+[Paragraph(str(x.get('capital_allocation_pattern') or 'N/A'),cell)])
        widths=[19*mm,42*mm,18*mm,18*mm,14*mm,14*mm,12*mm,12*mm,15*mm,25*mm]
        tab=Table(data,colWidths=widths,repeatRows=1); tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.25,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)])); story.append(tab)
        doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),rightMargin=9*mm,leftMargin=9*mm,topMargin=9*mm,bottomMargin=9*mm,title=f'{sector} report'); doc.build(story)
    return {'reports':len(tasks),'sectors':sectors,'output_dir':str(out)}
