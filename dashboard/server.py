"""
Flask Backend Web Server for Bluestock Mutual Fund Analytics.
This server connects to data/db/bluestock_mf.db and exposes REST API endpoints
for the interactive HTML/JS/CSS dashboard.
"""

import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from flask import Flask, jsonify, render_template, request

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

app = Flask(__name__, 
            template_folder=str(project_root / "dashboard" / "templates"),
            static_folder=str(project_root / "dashboard" / "static"))

def get_db_connection():
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    return sqlite3.connect(db_path)

@app.route('/')
def home():
    """Serves the main dashboard HTML page."""
    return render_template('index.html')

@app.route('/api/kpis')
def get_kpis():
    """Returns top-level KPIs for the Industry Overview tab."""
    # We use high-fidelity industry metrics as requested
    return jsonify({
        "total_aum": "₹81.3L Cr",
        "total_aum_delta": "▲ 14.2% YoY",
        "sip_inflow": "₹31,200 Cr",
        "sip_inflow_delta": "▲ 8.5% MoM",
        "folios": "26.12 Cr",
        "schemes": "1,908"
    })

@app.route('/api/aum_trend')
def get_aum_trend():
    """Returns quarterly industry AUM growth trend."""
    conn = get_db_connection()
    df = pd.read_sql("SELECT date, sum(aum_crore) as aum_cr FROM fact_aum GROUP BY date ORDER BY date", conn)
    conn.close()
    
    # Format and convert to Lakh Crores
    df['aum_lakh_cr'] = df['aum_cr'] / 100000
    
    return jsonify({
        "labels": df['date'].tolist(),
        "values": df['aum_lakh_cr'].tolist()
    })

@app.route('/api/top_amcs')
def get_top_amcs():
    """Returns AUM for top 10 AMCs."""
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT fund_house, aum_crore 
        FROM fact_aum 
        WHERE date = (SELECT max(date) FROM fact_aum)
        ORDER BY aum_crore DESC 
        LIMIT 10
    """, conn)
    conn.close()
    
    return jsonify({
        "labels": df['fund_house'].tolist(),
        "values": (df['aum_crore'] / 1000).tolist() # In thousand crores
    })

@app.route('/api/performance')
def get_performance():
    """Returns performance records for the scatter map and scorecard."""
    conn = get_db_connection()
    query = """
        SELECT 
            f.amfi_code, f.scheme_name, f.fund_house, f.category, f.plan, f.risk_category,
            p.return_3yr_pct, p.std_dev_ann_pct, p.aum_crore, p.sharpe_ratio, p.alpha, p.beta
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Apply clean filters if provided
    amc = request.args.get('amc', 'All')
    category = request.args.get('category', 'All')
    plan = request.args.get('plan', 'All')
    
    if amc != 'All':
        df = df[df['fund_house'] == amc]
    if category != 'All':
        df = df[df['category'] == category]
    if plan != 'All':
        df = df[df['plan'] == plan]
        
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/scorecard')
def get_scorecard():
    """Returns top ranked schemes from fund_scorecard.csv."""
    df = pd.read_csv(project_root / "fund_scorecard.csv")
    
    # Filters
    amc = request.args.get('amc', 'All')
    category = request.args.get('category', 'All')
    
    if amc != 'All':
        df = df[df['fund_house'] == amc]
    if category != 'All':
        df = df[df['category'] == category]
        
    return jsonify(df.head(10).to_dict(orient='records'))

@app.route('/api/nav_trend/<int:amfi_code>')
def get_nav_trend(amfi_code):
    """Returns NAV history for selected fund vs Nifty 50 benchmark."""
    conn = get_db_connection()
    df_nav = pd.read_sql("SELECT date, nav FROM fact_nav WHERE amfi_code = ? ORDER BY date", conn, params=[amfi_code])
    df_bench = pd.read_sql("SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    conn.close()
    
    if len(df_nav) == 0:
        return jsonify({"error": "Scheme not found"}), 404
        
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_bench['date'] = pd.to_datetime(df_bench['date'])
    
    merged = pd.merge(df_nav, df_bench, on='date').sort_values('date')
    
    # Normalize values to base 100 for comparison
    merged['nav_norm'] = (merged['nav'] / merged.iloc[0]['nav']) * 100
    merged['bench_norm'] = (merged['close_value'] / merged.iloc[0]['close_value']) * 100
    merged['date_str'] = merged['date'].dt.strftime('%Y-%m-%d')
    
    return jsonify({
        "dates": merged['date_str'].tolist(),
        "nav_norm": merged['nav_norm'].tolist(),
        "bench_norm": merged['bench_norm'].tolist(),
        "nav_raw": merged['nav'].tolist()
    })

@app.route('/api/investor_analytics')
def get_investor_analytics():
    """Returns investor demographic distributions."""
    conn = get_db_connection()
    
    # 1. Transaction Type Split
    df_split = pd.read_sql("SELECT transaction_type, sum(amount_inr) as volume FROM fact_transactions GROUP BY transaction_type", conn)
    
    # 2. State-wise Volumes
    df_state = pd.read_sql("""
        SELECT state, sum(amount_inr) as volume 
        FROM fact_transactions 
        GROUP BY state 
        ORDER BY volume DESC 
        LIMIT 8
    """, conn)
    
    # 3. Age vs Avg SIP
    df_age = pd.read_sql("""
        SELECT age_group, avg(amount_inr) as avg_sip 
        FROM fact_transactions 
        WHERE transaction_type = 'SIP' 
        GROUP BY age_group
    """, conn)
    
    # 4. Monthly Inflow Trends
    df_monthly = pd.read_sql("""
        SELECT strftime('%Y-%m', transaction_date) as month, sum(amount_inr) as volume 
        FROM fact_transactions 
        GROUP BY month 
        ORDER BY month
    """, conn)
    
    conn.close()
    
    return jsonify({
        "type_split": {
            "labels": df_split['transaction_type'].tolist(),
            "values": df_split['volume'].tolist()
        },
        "state_volumes": {
            "labels": df_state['state'].tolist(),
            "values": (df_state['volume'] / 10000000).tolist() # Crores
        },
        "age_sip": {
            "labels": df_age['age_group'].tolist(),
            "values": df_age['avg_sip'].tolist()
        },
        "monthly_trend": {
            "labels": df_monthly['month'].tolist(),
            "values": (df_monthly['volume'] / 10000000).tolist() # Crores
        }
    })

@app.route('/api/sip_market_trends')
def get_sip_market_trends():
    """Returns SIP inflows and Nifty 50 close price correlation."""
    conn = get_db_connection()
    
    # Monthly SIP Inflows
    df_sip = pd.read_sql("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month", conn)
    
    # Nifty 50 Close
    df_n50 = pd.read_sql("SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    df_n50['date'] = pd.to_datetime(df_n50['date'])
    df_n50['month'] = df_n50['date'].dt.strftime('%Y-%m')
    df_n50_m = df_n50.groupby('month')['close_value'].mean().reset_index()
    
    df_dual = pd.merge(df_sip, df_n50_m, on='month')
    
    # Top Inflows by Category for FY25
    df_cat = pd.read_sql("""
        SELECT category, sum(net_inflow_crore) as total_inflow 
        FROM category_inflows 
        WHERE month >= '2024-04' AND month <= '2025-03'
        GROUP BY category 
        ORDER BY total_inflow DESC
    """, conn)
    
    # Category monthly inflow matrix (for heatmap)
    df_hm = pd.read_sql("SELECT month, category, net_inflow_crore FROM category_inflows WHERE month >= '2024-01'", conn)
    
    conn.close()
    
    df_pivot = df_hm.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
    
    return jsonify({
        "dual_trend": {
            "months": df_dual['month'].tolist(),
            "sip_inflow": df_dual['sip_inflow_crore'].tolist(),
            "nifty_close": df_dual['close_value'].tolist()
        },
        "top_categories": {
            "labels": df_cat['category'].tolist(),
            "values": (df_cat['total_inflow'] / 1000).tolist() # Thousand crores
        },
        "heatmap": {
            "categories": df_pivot.index.tolist(),
            "months": df_pivot.columns.tolist(),
            "matrix": df_pivot.values.tolist()
        }
    })

@app.route('/api/recommend')
def get_recommendations():
    """Returns top 3 recommendations for a given risk appetite."""
    risk = request.args.get('risk', 'Moderate')
    
    from scripts.recommender import recommend_funds
    df = recommend_funds(risk)
    
    if df is not None and len(df) > 0:
        return jsonify(df.to_dict(orient='records'))
    else:
        return jsonify([])

@app.route('/api/meta_lists')
def get_meta_lists():
    """Returns distinct lists of Fund Houses, Categories, and Plans."""
    conn = get_db_connection()
    df = pd.read_sql("SELECT DISTINCT fund_house, category, plan FROM dim_fund", conn)
    conn.close()
    
    return jsonify({
        "amcs": sorted(df['fund_house'].dropna().unique().tolist()),
        "categories": sorted(df['category'].dropna().unique().tolist()),
        "plans": sorted(df['plan'].dropna().unique().tolist())
    })

if __name__ == '__main__':
    # Run server locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
