import re
from pathlib import Path

def test_parser_pattern_examples():
    p=re.compile(r'(\d+)\s*Years?:?\s*([\d.]+)%',re.I)
    m=p.search('10 Years: 21%'); assert m and (int(m.group(1)),float(m.group(2)))==(10,21.0)
    m=p.search('5 Years:       24%'); assert m and (int(m.group(1)),float(m.group(2)))==(5,24.0)

def test_expected_modules_exist():
    root=Path(__file__).resolve().parents[1]
    for p in ['src/nlp/parser.py','src/nlp/pros_cons_generator.py','src/analytics/cashflow_kpis.py','src/reports/tearsheet.py','src/reports/sector_report.py','src/reports/portfolio_summary.py']:
        assert (root/p).exists()
