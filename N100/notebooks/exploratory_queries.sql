-- 01 table row counts
SELECT 'companies' table_name, COUNT(*) rows FROM companies UNION ALL SELECT 'profitandloss',COUNT(*) FROM profitandloss UNION ALL SELECT 'balancesheet',COUNT(*) FROM balancesheet UNION ALL SELECT 'cashflow',COUNT(*) FROM cashflow;
-- 02 company coverage
SELECT company_id, COUNT(*) years FROM profitandloss GROUP BY company_id ORDER BY years;
-- 03 companies below five years
SELECT company_id, COUNT(*) years FROM profitandloss GROUP BY company_id HAVING COUNT(*)<5;
-- 04 P&L null profile
SELECT COUNT(*) total_rows, SUM(sales IS NULL) null_sales, SUM(net_profit IS NULL) null_profit FROM profitandloss;
-- 05 balance checks
SELECT company_id, year, total_assets, total_liabilities, ABS(total_assets-total_liabilities)/NULLIF(ABS(total_assets),0) diff_pct FROM balancesheet ORDER BY diff_pct DESC LIMIT 20;
-- 06 OPM cross-check
SELECT company_id,year,opm_percentage,(operating_profit/sales)*100 computed_opm FROM profitandloss WHERE sales>0 ORDER BY ABS(opm_percentage-(operating_profit/sales)*100) DESC LIMIT 20;
-- 07 latest P&L
SELECT * FROM profitandloss WHERE year=(SELECT MAX(year) FROM profitandloss) ORDER BY net_profit DESC LIMIT 20;
-- 08 sector distribution
SELECT broad_sector,COUNT(*) companies FROM sectors GROUP BY broad_sector ORDER BY companies DESC;
-- 09 stock price coverage
SELECT company_id,MIN(date) first_date,MAX(date) last_date,COUNT(*) observations FROM stock_prices GROUP BY company_id ORDER BY company_id;
-- 10 market cap snapshot
SELECT company_id,year,market_cap_crore,pe_ratio,pb_ratio FROM market_cap WHERE year=(SELECT MAX(year) FROM market_cap) ORDER BY market_cap_crore DESC LIMIT 20;
