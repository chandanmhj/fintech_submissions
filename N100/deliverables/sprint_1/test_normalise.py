from src.etl.normaliser import normalize_year, normalize_ticker

def test_year_numeric(): assert normalize_year(2024)=='2024-03'
def test_year_string(): assert normalize_year('2024')=='2024-03'
def test_year_month(): assert normalize_year('2024-03')=='2024-03'
def test_year_slash(): assert normalize_year('2024/03')=='2024-03'
def test_year_month_name(): assert normalize_year('Mar 2024')=='2024-03'
def test_year_short_month(): assert normalize_year('Mar-24')=='2024-03'
def test_year_dec(): assert normalize_year('Dec 2012')=='2012-12'
def test_year_jan(): assert normalize_year('Jan 2020')=='2020-01'
def test_year_feb(): assert normalize_year('Feb 2020')=='2020-02'
def test_year_apr(): assert normalize_year('Apr 2020')=='2020-04'
def test_year_may(): assert normalize_year('May 2020')=='2020-05'
def test_year_jun(): assert normalize_year('Jun 2020')=='2020-06'
def test_year_jul(): assert normalize_year('Jul 2020')=='2020-07'
def test_year_aug(): assert normalize_year('Aug 2020')=='2020-08'
def test_year_sep(): assert normalize_year('Sep 2020')=='2020-09'
def test_year_oct(): assert normalize_year('Oct 2020')=='2020-10'
def test_year_nov(): assert normalize_year('Nov 2020')=='2020-11'
def test_year_ttm(): assert normalize_year('TTM')=='2025-03'
def test_year_none(): assert normalize_year(None) is None
def test_year_bad(): assert normalize_year('unknown') is None

def test_ticker_upper(): assert normalize_ticker(' abb ')=='ABB'
def test_ticker_lower(): assert normalize_ticker('tcs')=='TCS'
def test_ticker_spaces(): assert normalize_ticker(' BAJAJ-AUTO ')=='BAJAJ-AUTO'
def test_ticker_none(): assert normalize_ticker(None) is None
def test_ticker_numeric(): assert normalize_ticker(123)=='123'
def test_ticker_case(): assert normalize_ticker('hdfcbank')=='HDFCBANK'
def test_ticker_trim_tabs(): assert normalize_ticker('\tINFY\n')=='INFY'
def test_ticker_empty(): assert normalize_ticker('')==''
def test_ticker_preserves_hyphen(): assert normalize_ticker('M&M')=='M&M'
def test_ticker_length_example(): assert 2 <= len(normalize_ticker('RELIANCE')) <= 12

def test_year_int_string(): assert normalize_year('2019')=='2019-03'
def test_year_iso(): assert normalize_year('2020-09')=='2020-09'
def test_year_iso_slash(): assert normalize_year('2020/09')=='2020-09'
def test_ticker_mixed_case(): assert normalize_ticker('iTc')=='ITC'
def test_ticker_unicode_safe(): assert normalize_ticker(' abc ')=='ABC'
