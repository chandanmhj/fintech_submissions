SELECT COUNT(*) AS schemes FROM dim_fund;
SELECT COUNT(*) AS nav_rows FROM fact_nav;
SELECT COUNT(*) AS transactions FROM fact_investor_transactions;
SELECT COUNT(DISTINCT investor_id) AS investors FROM fact_investor_transactions;
SELECT transaction_type,COUNT(*) transactions,SUM(amount_inr) total_amount_inr FROM fact_investor_transactions GROUP BY transaction_type;
