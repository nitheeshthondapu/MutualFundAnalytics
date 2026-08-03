-- 10 Analytical SQL Queries for Bluestock Mutual Fund Analytics

-- Query 1: Top 5 funds by AUM (Asset Under Management)
-- Gets the top 5 funds from fact_performance based on their current AUM (in Crores).
SELECT 
    amfi_code, 
    scheme_name, 
    aum_crore
FROM fact_performance 
ORDER BY aum_crore DESC 
LIMIT 5;


-- Query 2: Average NAV per month for each scheme
-- Calculates the average NAV for each mutual fund scheme for each calendar month.
SELECT 
    amfi_code, 
    strftime('%Y-%m', date) AS month, 
    ROUND(AVG(nav), 4) AS avg_nav 
FROM fact_nav 
GROUP BY amfi_code, month 
ORDER BY amfi_code, month;


-- Query 3: SIP Year-over-Year (YoY) Inflow Growth
-- Dynamically calculates the YoY growth of SIP transaction volumes per month from transaction facts.
WITH monthly_sip AS (
    SELECT 
        strftime('%Y-%m', transaction_date) AS month,
        strftime('%Y', transaction_date) AS yr,
        strftime('%m', transaction_date) AS mth,
        SUM(amount_inr) AS total_sip_amount
    FROM fact_transactions
    WHERE transaction_type = 'SIP'
    GROUP BY month
)
SELECT 
    t1.month AS current_month, 
    t1.total_sip_amount AS current_amount, 
    t2.month AS prior_year_month, 
    t2.total_sip_amount AS prior_year_amount,
    ROUND(((t1.total_sip_amount - t2.total_sip_amount) * 100.0 / t2.total_sip_amount), 2) AS yoy_growth_pct
FROM monthly_sip t1
JOIN monthly_sip t2 
  ON CAST(t1.yr AS INTEGER) = CAST(t2.yr AS INTEGER) + 1 
 AND t1.mth = t2.mth
ORDER BY t1.month;


-- Query 4: Total Transactions and Volume by State
-- Summarizes mutual fund transaction count and total transaction amount by investor state.
SELECT 
    state, 
    COUNT(*) AS transaction_count, 
    SUM(amount_inr) AS total_transaction_volume,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount
FROM fact_transactions 
GROUP BY state 
ORDER BY total_transaction_volume DESC;


-- Query 5: Funds with expense_ratio < 1%
-- Retrieves schemes from dim_fund that have an expense ratio below 1%, sorted by cost efficiency.
SELECT 
    amfi_code, 
    scheme_name, 
    fund_house, 
    expense_ratio_pct 
FROM dim_fund 
WHERE expense_ratio_pct < 1.0 
ORDER BY expense_ratio_pct;


-- Query 6: Average transaction amount and count by age group and gender
-- Analyzes investor demographic behavior (age groups and gender) against transaction stats.
SELECT 
    age_group, 
    gender, 
    COUNT(*) AS tx_count, 
    ROUND(AVG(amount_inr), 2) AS avg_amount,
    SUM(amount_inr) AS total_amount
FROM fact_transactions 
GROUP BY age_group, gender 
ORDER BY age_group, gender;


-- Query 7: Monthly AUM growth trend per fund house
-- Tracks total AUM and number of active schemes managed by each fund house month by month.
SELECT 
    date, 
    fund_house, 
    aum_crore, 
    num_schemes 
FROM fact_aum 
ORDER BY fund_house, date;


-- Query 8: Top 5 sectors by total market value in portfolio holdings
-- Identifies the top 5 sectors where mutual funds have the largest aggregate stock investments.
SELECT 
    sector, 
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr,
    COUNT(DISTINCT stock_symbol) AS distinct_stocks_held
FROM portfolio_holdings 
GROUP BY sector 
ORDER BY total_market_value_cr DESC 
LIMIT 5;


-- Query 9: Scheme performance returns vs benchmark index performance returns
-- Compares scheme returns over 3 years against their benchmark returns and retrieves their alpha value.
SELECT 
    p.amfi_code, 
    f.scheme_name, 
    p.return_3yr_pct AS scheme_return_3yr, 
    p.benchmark_3yr_pct AS benchmark_return_3yr, 
    p.alpha AS alpha_generation
FROM fact_performance p 
JOIN dim_fund f ON p.amfi_code = f.amfi_code 
ORDER BY p.alpha DESC;


-- Query 10: High-weight stocks in mutual fund portfolios (weight > 10%)
-- Finds individual stock holdings that comprise more than 10% weight of any mutual fund scheme.
SELECT 
    f.scheme_name, 
    h.stock_name, 
    h.sector, 
    h.weight_pct 
FROM portfolio_holdings h 
JOIN dim_fund f ON h.amfi_code = f.amfi_code 
WHERE h.weight_pct > 10.0 
ORDER BY h.weight_pct DESC;
