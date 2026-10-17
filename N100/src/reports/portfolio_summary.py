"""One-page-per-company alphabetical portfolio summary with latest-year trend arrows."""
from pathlib import Path
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from src.common import connect, REPORTS_DIR
NAVY=colors.HexColor('#142B4A'); GREEN=colors.HexColor('#1B7A4B'); RED=colors.HexColor('#B42332'); GREY=colors.HexColor('#5B6573')
def _last_two(df,col):
    if col not in df or df.empty: return (None,None)
    vals=df.sort_values('year')[col].dropna().tolist()
    return (vals[-1],vals[-2]) if len(vals)>1 else ((vals[-1],None) if vals else (None,None))
def generate_portfolio_summary(db_path=None, output_path=None):
    con=connect(db_path)
    co=pd.read_sql_query('select id as company_id,company_name from companies',con); sec=pd.read_sql_query('select company_id,broad_sector from sectors',con); pl=pd.read_sql_query('select company_id,year,sales,net_profit,eps,opm_percentage from profitandloss',con); r=pd.read_sql_query('select company_id,year,return_on_equity_pct,roce_pct,debt_to_equity,free_cash_flow_cr,composite_quality_score from financial_ratios',con); mc=pd.read_sql_query('select company_id,year,market_cap_crore,pe_ratio from market_cap',con); con.close()
    output_path=Path(output_path or REPORTS_DIR/'portfolio'/'portfolio_summary.pdf'); output_path.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(output_path),pagesize=A4); W,H=A4
    for _,company in co.sort_values('company_id').iterrows():
        cid=company.company_id; p=pl[pl.company_id==cid].sort_values('year'); rr=r[r.company_id==cid].sort_values('year'); m=mc[mc.company_id==cid].sort_values('year'); s=sec[sec.company_id==cid]
        latestp=p.iloc[-1] if len(p) else {}; prevp=p.iloc[-2] if len(p)>1 else {}; latestm=m.iloc[-1] if len(m) else {}
        roe,roe_prev=_last_two(rr,'return_on_equity_pct'); roce,roce_prev=_last_two(rr,'roce_pct'); de,de_prev=_last_two(rr,'debt_to_equity'); fcf,fcf_prev=_last_two(rr,'free_cash_flow_cr')
        c.setFillColor(NAVY); c.rect(0,H-88,W,88,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont('Helvetica-Bold',17); c.drawString(40,H-42,str(company.company_name or cid)[:58]); c.setFont('Helvetica',10); c.drawString(40,H-62,f'{cid}  |  {s.broad_sector.iloc[0] if len(s) else "Unknown"}  |  latest period: {latestp.get("year","N/A")}')
        items=[('Revenue',latestp.get('sales'),prevp.get('sales')),('Net Profit',latestp.get('net_profit'),prevp.get('net_profit')),('ROE %',roe,roe_prev),('ROCE %',roce,roce_prev),('D/E',de,de_prev),('FCF',fcf,fcf_prev)]
        y=H-130; c.setFont('Helvetica-Bold',12); c.setFillColor(NAVY); c.drawString(40,y,'Key KPIs and year-over-year trend'); y-=24
        for i,(label,val,old) in enumerate(items):
            col=i%2; row=i//2; x=40+col*260; yy=y-row*76
            c.setFillColor(colors.HexColor('#EEF2F7')); c.roundRect(x,yy-45,230,58,7,fill=1,stroke=0); c.setFillColor(NAVY); c.setFont('Helvetica-Bold',9); c.drawString(x+12,yy-5,label)
            try: vv=float(val); txt=f'{vv:,.2f}'
            except Exception: vv=None; txt='N/A'
            c.setFont('Helvetica-Bold',15); c.drawString(x+12,yy-27,txt)
            try:
                ov=float(old); pct=((vv-ov)/abs(ov)*100) if abs(ov)>1e-9 else (0 if vv==0 else 100)
                arrow='→' if abs(pct)<=2 else ('↑' if vv>ov else '↓')
                color=GREY if arrow=='→' else (GREEN if arrow=='↑' else RED)
                c.setFillColor(color); c.setFont('Helvetica-Bold',13); c.drawRightString(x+215,yy-25,arrow)
                c.setFont('Helvetica',7); c.drawRightString(x+215,yy-38,f'{pct:+.1f}%')
            except Exception: c.setFillColor(GREY); c.setFont('Helvetica',8); c.drawRightString(x+215,yy-25,'—')
        c.setFillColor(GREY); c.setFont('Helvetica',8); c.drawString(40,40,'Trend arrows compare latest available year with the preceding available year; flat = within ±2%.')
        c.showPage()
    c.save(); return {'pages':len(co),'path':str(output_path)}
