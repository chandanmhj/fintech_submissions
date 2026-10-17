"""Two-page ReportLab company tearsheets. Uses Paragraph wrapping for every table cell."""
from pathlib import Path
import tempfile, math
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from src.common import connect, REPORTS_DIR, OUTPUT_DIR
NAVY=colors.HexColor('#142B4A'); GREEN=colors.HexColor('#1B7A4B'); RED=colors.HexColor('#B42332'); LIGHT=colors.HexColor('#EEF2F7')

def _fmt(x):
    try:
        if x is None or pd.isna(x): return 'N/A'
        return f'{float(x):,.2f}'
    except Exception: return str(x)
def _last_valid(df, col):
    if col not in df or df.empty: return None
    values=df.sort_values('year')[col].dropna()
    return values.iloc[-1] if len(values) else None
def _fmt_pct(x):
    return f'{_fmt(x)}%' if x is not None and pd.notna(x) else 'N/A'
def _chart(company,pl,ratios,bs,cf,tmp):
    charts=[]
    p=pl.sort_values('year').tail(10)
    fig,ax=plt.subplots(figsize=(8.2,2.5)); x=range(len(p)); w=.38
    ax.bar([i-w/2 for i in x],p['sales'].fillna(0),w,label='Revenue')
    ax.bar([i+w/2 for i in x],p['net_profit'].fillna(0),w,label='Net profit')
    ax.set_xticks(list(x)); ax.set_xticklabels(p['year'].astype(str),rotation=45,ha='right',fontsize=7); ax.set_title('Revenue and Net Profit'); ax.legend(fontsize=7,ncol=2); ax.grid(axis='y',alpha=.2); fig.tight_layout()
    f=Path(tmp)/'pl.png'; fig.savefig(f,dpi=155); plt.close(fig); charts.append(f)
    r=ratios.sort_values('year').tail(10)
    fig,ax=plt.subplots(figsize=(8.2,2.2)); ax2=ax.twinx()
    if 'return_on_equity_pct' in r: ax.plot(r['year'].astype(str),r['return_on_equity_pct'],marker='o',label='ROE')
    if 'roce_pct' in r: ax2.plot(r['year'].astype(str),r['roce_pct'],marker='s',label='ROCE')
    ax.set_title('ROE and ROCE'); ax.set_ylabel('ROE (%)'); ax2.set_ylabel('ROCE (%)'); ax.tick_params(axis='x',rotation=45,labelsize=7); ax.grid(alpha=.2); fig.tight_layout()
    f=Path(tmp)/'roe.png'; fig.savefig(f,dpi=155); plt.close(fig); charts.append(f)
    # Balance sheet composition
    b=bs.sort_values('year').tail(10); fig,ax=plt.subplots(figsize=(8.2,2.1)); x=range(len(b))
    eq=pd.to_numeric(b.get('equity_capital',0),errors='coerce').fillna(0)+pd.to_numeric(b.get('reserves',0),errors='coerce').fillna(0)
    br=pd.to_numeric(b.get('borrowings',0),errors='coerce').fillna(0); ol=pd.to_numeric(b.get('other_liabilities',0),errors='coerce').fillna(0)
    ax.bar(x,eq,label='Equity + reserves'); ax.bar(x,br,bottom=eq,label='Borrowings'); ax.bar(x,ol,bottom=eq+br,label='Other liabilities'); ax.set_xticks(list(x)); ax.set_xticklabels(b['year'].astype(str),rotation=45,ha='right',fontsize=7); ax.set_title('Balance Sheet Composition'); ax.legend(fontsize=6,ncol=3); fig.tight_layout()
    f=Path(tmp)/'bs.png'; fig.savefig(f,dpi=150); plt.close(fig); charts.append(f)
    # cashflow waterfall-ish positive/negative bar chart
    c=cf.sort_values('year'); row=c.iloc[-1] if len(c) else {}
    labels=['CFO','CFI','CFF','Net cash flow']; vals=[row.get('operating_activity',0),row.get('investing_activity',0),row.get('financing_activity',0),row.get('net_cash_flow',0)]
    vals=[float(v) if pd.notna(v) else 0 for v in vals]
    fig,ax=plt.subplots(figsize=(8.2,1.8)); ax.bar(labels,vals); ax.axhline(0,color='black',linewidth=.7); ax.set_title(f'Latest Cash Flow ({row.get("year","N/A")})'); ax.grid(axis='y',alpha=.2); fig.tight_layout()
    f=Path(tmp)/'cf.png'; fig.savefig(f,dpi=150); plt.close(fig); charts.append(f)
    return charts

def generate_one(ticker, db_path=None, output_path=None, pros_cons_path=None):
    con=connect(db_path)
    co=con.execute('select * from companies where id=?',(ticker,)).fetchone()
    if not co: con.close(); raise ValueError(f'Unknown ticker: {ticker}')
    name=co['company_name'] or ticker
    def df(q,args=(ticker,)): return pd.read_sql_query(q,con,params=args)
    pl=df('select * from profitandloss where company_id=?'); ratios=df('select * from financial_ratios where company_id=?'); bs=df('select * from balancesheet where company_id=?'); cf=df('select * from cashflow where company_id=?')
    sec=con.execute('select broad_sector,sub_sector from sectors where company_id=?',(ticker,)).fetchone()
    mc=con.execute('select * from market_cap where company_id=? order by year desc limit 1',(ticker,)).fetchone(); con.close()
    if len(pl)<3: raise ValueError(f'{ticker} has fewer than 3 years of P&L data')
    if output_path is None: output_path=REPORTS_DIR/'tearsheets'/f'{ticker}_tearsheet.pdf'
    output_path=Path(output_path); output_path.parent.mkdir(parents=True,exist_ok=True)
    # Load generated pros/cons, falling back to database text only when output is not yet generated.
    pc=pd.DataFrame()
    pp=Path(pros_cons_path) if pros_cons_path else OUTPUT_DIR/'pros_cons_generated.csv'
    if pp.exists():
        allpc=pd.read_csv(pp); pc=allpc[allpc.company_id==ticker]
    styles=getSampleStyleSheet(); body=ParagraphStyle('body',parent=styles['BodyText'],fontSize=7.5,leading=9,spaceAfter=2); small=ParagraphStyle('small',parent=body,fontSize=6.5,leading=8); title=ParagraphStyle('title',parent=styles['Title'],fontSize=16,leading=19,textColor=colors.white,alignment=TA_LEFT); h=ParagraphStyle('h',parent=styles['Heading2'],fontSize=10,leading=12,textColor=NAVY,spaceBefore=3,spaceAfter=4)
    story=[]
    header=Table([[Paragraph(f'{name}  |  {ticker}',title)]],colWidths=[180*mm],rowHeights=[15*mm]); header.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)])); story.extend([header,Spacer(1,4*mm)])
    latestpl=pl.sort_values('year').iloc[-1]
    roe=_last_valid(ratios,'return_on_equity_pct'); roce=_last_valid(ratios,'roce_pct'); de=_last_valid(ratios,'debt_to_equity'); fcf=_last_valid(ratios,'free_cash_flow_cr')
    tilevals=[('Revenue',_fmt(latestpl.get('sales'))),('Net Profit',_fmt(latestpl.get('net_profit'))),('ROE',_fmt_pct(roe)),('ROCE',_fmt_pct(roce)),('D/E',_fmt(de)),('FCF',_fmt(fcf))]
    tiles=[]
    for i in range(0,6,3):
        row=[]
        for label,value in tilevals[i:i+3]: row.append(Paragraph(f'<b>{label}</b><br/><font size="12">{value}</font>',body))
        tiles.append(row)
    t=Table(tiles,colWidths=[60*mm]*3,rowHeights=[15*mm]*2); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.5,colors.white),('INNERGRID',(0,0),(-1,-1),2,colors.white),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)])); story.extend([t,Spacer(1,2*mm)])
    with tempfile.TemporaryDirectory() as td:
        charts=_chart(ticker,pl,ratios,bs,cf,td)
        story += [Paragraph('Financial Performance',h),Image(str(charts[0]),width=174*mm,height=53*mm),Image(str(charts[1]),width=174*mm,height=43*mm),PageBreak()]
        story += [Paragraph(f'{name} — Financial Position & Cash Flow',h),Image(str(charts[2]),width=174*mm,height=42*mm),Image(str(charts[3]),width=174*mm,height=34*mm)]
        patterns=ratios.sort_values('year')['capital_allocation_pattern'].dropna() if 'capital_allocation_pattern' in ratios else []
        pat=patterns.iloc[-1] if len(patterns) else 'N/A'
        if not isinstance(pat,str) or not pat: pat='N/A'
        badge=Table([[Paragraph(f'<b>Capital Allocation: {pat}</b>',body)]],colWidths=[174*mm]); badge.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.5,NAVY),('LEFTPADDING',(0,0),(-1,-1),6)])); story += [badge,Spacer(1,2*mm)]
        pro=pc[pc.type=='pro'] if len(pc) and 'type' in pc else pd.DataFrame(); condata=pc[pc.type=='con'] if len(pc) and 'type' in pc else pd.DataFrame()
        story.append(Paragraph('Pros',h))
        if len(pro):
            for _,r in pro.head(5).iterrows(): story.append(Paragraph(f'<font color="#1B7A4B">&#8226;</font> {str(r["text"])} <font size="6">({int(r["confidence_pct"])}%)</font>',body))
        else: story.append(Paragraph('• No high-confidence pro rule triggered; review full financial history.',body))
        story.append(Paragraph('Cons / Risks',h))
        if len(condata):
            for _,r in condata.head(5).iterrows(): story.append(Paragraph(f'<font color="#B42332">&#8226;</font> {str(r["text"])} <font size="6">({int(r["confidence_pct"])}%)</font>',body))
        else: story.append(Paragraph('• No high-confidence con rule triggered; continue monitoring.',body))
        story.append(Spacer(1,1*mm))
        story.append(Paragraph(f'Sector: {sec[0] if sec else "Unknown"}  |  Sub-sector: {sec[1] if sec else "Unknown"}  |  Report generated from local N100 database.',small))
        doc=SimpleDocTemplate(str(output_path),pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=10*mm,bottomMargin=10*mm,title=f'{ticker} company tearsheet')
        doc.build(story)
    return output_path
