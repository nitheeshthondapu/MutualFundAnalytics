"""
Streamlit Dashboard for Bluestock Mutual Fund Analytics.
This dashboard acts as an interactive alternative to Power BI (B2 Bonus).
It contains 4 pages (tabs):
1. Industry Overview: Key market indicators and AMC distributions.
2. Fund Performance: Returns, risk metrics, and NAV trends.
3. Investor Analytics: Demographic patterns and transaction summaries.
4. SIP & Market Trends: SIP inflows mapped against market indices.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# 1. Page Configuration
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Theme State Management
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# 3. CSS Variables Setup based on active theme
if IS_DARK:
    bg_color = "#09090b"
    bg_subtle = "#0c0c0f"
    card_color = "#0c0c0f"
    card_hover = "#131316"
    border_color = "#1e1e24"
    border_subtle = "#16161a"
    text_color = "#fafafa"
    text_muted = "#71717a"
    text_dim = "#52525b"
    grid_color = "rgba(255,255,255,0.04)"
    plotly_template = "plotly_dark"
else:
    bg_color = "#ffffff"
    bg_subtle = "#f9fafb"
    card_color = "#ffffff"
    card_hover = "#f4f4f5"
    border_color = "#e4e4e7"
    border_subtle = "#f0f0f2"
    text_color = "#09090b"
    text_muted = "#71717a"
    text_dim = "#a1a1aa"
    grid_color = "rgba(0,0,0,0.04)"
    plotly_template = "plotly"

accent_color = "#2563eb" # Royal Blue
green_color = "#22c55e" if IS_DARK else "#16a34a"
red_color = "#ef4444" if IS_DARK else "#dc2626"

# Inject CSS Design System
st.markdown(f"""
<style>
    /* Hide default streamlit elements */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    /* Core Layout */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 1.5rem 2.5rem 3rem !important;
        max-width: 1400px !important;
    }}
    
    /* Brand Header */
    .brand-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {border_color};
    }}
    .brand-logo {{
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: {accent_color};
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .brand-logo span {{
        color: {text_color};
    }}
    
    /* Tabs styling (pill-style) */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: {text_muted} !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: {text_color} !important;
        background: {card_hover} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {text_color} !important;
        background: {card_color} !important;
        border-color: {border_color} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: {bg_subtle} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 4px;
        margin-bottom: 1.5rem;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: {card_color};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .metric-label {{
        font-size: 0.76rem;
        color: {text_muted};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}
    .metric-value {{
        font-size: 1.7rem;
        font-weight: 700;
        color: {text_color};
        letter-spacing: -0.03em;
    }}
    .metric-delta {{
        font-size: 0.74rem;
        font-weight: 600;
        margin-top: 0.35rem;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        width: fit-content;
        gap: 3px;
    }}
    .delta-up {{ color: {green_color}; background: rgba(34,197,94,0.1); }}
    .delta-down {{ color: {red_color}; background: rgba(239,68,68,0.1); }}
    
    /* Chart wrappers */
    .chart-wrap {{
        background: {card_color};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.88rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 0.2rem;
    }}
    .chart-subtitle {{
        font-size: 0.74rem;
        color: {text_muted};
        margin-bottom: 1rem;
    }}
    
    /* Data tables */
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.8rem;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.6rem 0.8rem;
        color: {text_muted};
        font-weight: 500;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid {border_color};
    }}
    .data-table td {{
        padding: 0.65rem 0.8rem;
        color: {text_color};
        border-bottom: 1px solid {border_subtle};
    }}
    .data-table tr:last-child td {{
        border-bottom: none;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }}
    .badge-green {{ color: {green_color}; background: rgba(34,197,94,0.1); }}
    .badge-red {{ color: {red_color}; background: rgba(239,68,68,0.1); }}
    .badge-blue {{ color: {accent_color}; background: rgba(37,99,235,0.1); }}
    
    /* Standard streamlit gap adjustment */
    [data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}
</style>
""", unsafe_allow_html=True)

# Helper function to connect to SQLite
def get_db_connection():
    db_path = Path("data/db/bluestock_mf.db")
    if not db_path.exists():
        # fallback to root path if running differently
        db_path = Path("bluestock_mf.db")
    return sqlite3.connect(db_path)

# Helper to plot themed plotly figures
def apply_plotly_theme(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=text_muted, size=11),
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            linecolor=border_color,
            tickfont=dict(size=10, color=text_muted),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            linecolor=border_color,
            tickfont=dict(size=10, color=text_muted),
        ),
    )
    return fig

# Metric card component
def metric_card(label, value, delta=None, delta_type="up"):
    delta_html = ""
    if delta:
        cls = "delta-up" if delta_type == "up" else "delta-down"
        arrow = "↑" if delta_type == "up" else "↓"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'
        
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Header Section
st.markdown(f"""
<div class="brand-container">
    <div class="brand-logo">
        📈 Bluestock <span>Mutual Fund Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Theme selection layout
th_col1, th_col2 = st.columns([12, 1.2])
with th_col2:
    theme_text = "☀️ Light Mode" if IS_DARK else "🌙 Dark Mode"
    st.button(theme_text, on_click=toggle_theme, use_container_width=True)

# Navigation via Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Industry Overview", 
    "Fund Performance", 
    "Investor Analytics", 
    "SIP & Market Trends"
])

# ==============================================================================
# TAB 1: INDUSTRY OVERVIEW
# ==============================================================================
with tab1:
    # KPI Row
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        metric_card("Total Industry AUM", "₹81.3L Cr", "14.2% YoY", "up")
    with kpi_cols[1]:
        metric_card("Monthly SIP Inflows", "₹31.2K Cr", "8.5% MoM", "up")
    with kpi_cols[2]:
        metric_card("Total Folio Count", "26.12 Cr", "2.1M new", "up")
    with kpi_cols[3]:
        metric_card("Total Active Schemes", "1,908", "12 new", "up")
        
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Graphs Row
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Industry AUM Growth Trend</div>
            <div class="chart-subtitle">Quarterly AUM in Lakh Crores (2022 - 2025)</div>
        """, unsafe_allow_html=True)
        
        # Load from fact_aum
        conn = get_db_connection()
        df_aum = pd.read_sql("SELECT date, sum(aum_crore) as aum_cr, count(distinct fund_house) as amcs FROM fact_aum GROUP BY date ORDER BY date", conn)
        conn.close()
        
        # Convert AUM to Lakh Crores
        df_aum['aum_lakh_cr'] = df_aum['aum_cr'] / 100000
        
        fig_aum = px.line(
            df_aum, x='date', y='aum_lakh_cr',
            labels={'aum_lakh_cr': 'AUM (Lakh Crore)', 'date': 'Quarter'},
            color_discrete_sequence=[accent_color]
        )
        apply_plotly_theme(fig_aum)
        st.plotly_chart(fig_aum, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Top 10 Fund Houses by Share</div>
            <div class="chart-subtitle">Asset Under Management in Crores (Latest)</div>
        """, unsafe_allow_html=True)
        
        # Load latest AUM by fund house
        conn = get_db_connection()
        df_aum_amc = pd.read_sql("""
            SELECT fund_house, aum_crore 
            FROM fact_aum 
            WHERE date = (SELECT max(date) FROM fact_aum)
            ORDER BY aum_crore DESC 
            LIMIT 10
        """, conn)
        conn.close()
        
        fig_amc = px.bar(
            df_aum_amc, x='aum_crore', y='fund_house',
            orientation='h',
            labels={'aum_crore': 'AUM (INR Crore)', 'fund_house': 'AMC'},
            color_discrete_sequence=[accent_color]
        )
        fig_amc.update_layout(yaxis={'categoryorder':'total ascending'})
        apply_plotly_theme(fig_amc)
        st.plotly_chart(fig_amc, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 2: FUND PERFORMANCE
# ==============================================================================
with tab2:
    # Sidebar-like filters in top row
    conn = get_db_connection()
    df_meta = pd.read_sql("SELECT DISTINCT fund_house, category, plan FROM dim_fund", conn)
    conn.close()
    
    f_cols = st.columns(3)
    with f_cols[0]:
        selected_amc = st.selectbox("Fund House", ["All"] + sorted(list(df_meta['fund_house'].unique())))
    with f_cols[1]:
        selected_cat = st.selectbox("Category", ["All"] + sorted(list(df_meta['category'].unique())))
    with f_cols[2]:
        selected_plan = st.selectbox("Plan", ["All"] + sorted(list(df_meta['plan'].unique())))
        
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Scatter & Scorecard Row
    c1, c2 = st.columns([1.2, 1])
    
    conn = get_db_connection()
    query_perf = """
        SELECT 
            f.amfi_code, f.scheme_name, f.fund_house, f.category, f.plan, f.risk_category,
            p.return_3yr_pct, p.std_dev_ann_pct, p.aum_crore, p.sharpe_ratio
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """
    df_perf = pd.read_sql(query_perf, conn)
    conn.close()
    
    # Filter
    df_filtered = df_perf.copy()
    if selected_amc != "All":
        df_filtered = df_filtered[df_filtered['fund_house'] == selected_amc]
    if selected_cat != "All":
        df_filtered = df_filtered[df_filtered['category'] == selected_cat]
    if selected_plan != "All":
        df_filtered = df_filtered[df_filtered['plan'] == selected_plan]
        
    with c1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Risk vs Return Mapping</div>
            <div class="chart-subtitle">Annualized Returns (3Yr) vs Standard Deviation (Bubble size = AUM)</div>
        """, unsafe_allow_html=True)
        
        # Clean null values
        df_scatter = df_filtered.dropna(subset=['return_3yr_pct', 'std_dev_ann_pct', 'aum_crore'])
        
        fig_scatter = px.scatter(
            df_scatter, x='return_3yr_pct', y='std_dev_ann_pct',
            size='aum_crore', color='risk_category',
            hover_name='scheme_name',
            labels={'return_3yr_pct': '3Yr Return (%)', 'std_dev_ann_pct': 'Volatility (Std Dev %)', 'risk_category': 'Risk Grade'}
        )
        apply_plotly_theme(fig_scatter)
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Fund Performance Scorecard</div>
            <div class="chart-subtitle">Top Schemes Sorted by Sharpe Ratio</div>
        """, unsafe_allow_html=True)
        
        # Render HTML table of top 6
        top_schemes = df_filtered.sort_values('sharpe_ratio', ascending=False).head(6)
        
        rows_html = ""
        for idx, row in top_schemes.iterrows():
            rows_html += f"""
            <tr>
                <td>{row['scheme_name'][:30]}...</td>
                <td>{row['category']}</td>
                <td><span class="badge badge-blue">{row['sharpe_ratio']:.2f}</span></td>
                <td><b>{row['return_3yr_pct']:.2f}%</b></td>
            </tr>
            """
            
        st.markdown(f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Scheme Name</th>
                    <th>Category</th>
                    <th>Sharpe</th>
                    <th>3Yr Return</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 3: INVESTOR ANALYTICS
# ==============================================================================
with tab3:
    conn = get_db_connection()
    df_tx_meta = pd.read_sql("SELECT DISTINCT state, age_group, city_tier FROM fact_transactions", conn)
    conn.close()
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        selected_state = st.selectbox("Investor State", ["All"] + sorted(list(df_tx_meta['state'].unique())))
    with col_t2:
        selected_age = st.selectbox("Investor Age Group", ["All"] + sorted(list(df_tx_meta['age_group'].unique())))
    with col_t3:
        selected_tier = st.selectbox("City Tier", ["All"] + sorted(list(df_tx_meta['city_tier'].unique())))
        
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Load transactions
    conn = get_db_connection()
    query_tx = "SELECT transaction_type, amount_inr, state, age_group, city_tier, transaction_date FROM fact_transactions"
    df_tx = pd.read_sql(query_tx, conn)
    conn.close()
    
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    df_tx['month'] = df_tx['transaction_date'].dt.strftime('%Y-%m')
    
    # Filter
    df_tx_filt = df_tx.copy()
    if selected_state != "All":
        df_tx_filt = df_tx_filt[df_tx_filt['state'] == selected_state]
    if selected_age != "All":
        df_tx_filt = df_tx_filt[df_tx_filt['age_group'] == selected_age]
    if selected_tier != "All":
        df_tx_filt = df_tx_filt[df_tx_filt['city_tier'] == selected_tier]
        
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Transaction Split (SIP vs Lumpsum vs Redemption)</div>
            <div class="chart-subtitle">Volume contribution by value (INR)</div>
        """, unsafe_allow_html=True)
        
        type_split = df_tx_filt.groupby('transaction_type')['amount_inr'].sum().reset_index()
        fig_donut = px.pie(
            type_split, values='amount_inr', names='transaction_type',
            hole=0.45,
            color_discrete_sequence=['#2563eb', '#10b981', '#ef4444']
        )
        apply_plotly_theme(fig_donut)
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Age Group vs Average Transaction Amount</div>
            <div class="chart-subtitle">Average contribution per age cohort in INR</div>
        """, unsafe_allow_html=True)
        
        age_avg = df_tx_filt.groupby('age_group')['amount_inr'].mean().reset_index()
        fig_age = px.bar(
            age_avg, x='age_group', y='amount_inr',
            labels={'amount_inr': 'Avg Amount (INR)', 'age_group': 'Age Group'},
            color_discrete_sequence=[accent_color]
        )
        apply_plotly_theme(fig_age)
        st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Geographic bar chart
    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">Total Transaction Volume by State</div>
        <div class="chart-subtitle">Top 15 states by volume of investment</div>
    """, unsafe_allow_html=True)
    state_vol = df_tx_filt.groupby('state')['amount_inr'].sum().reset_index()
    state_vol = state_vol.sort_values('amount_inr', ascending=False).head(15)
    fig_state = px.bar(
        state_vol, x='state', y='amount_inr',
        labels={'amount_inr': 'Total Invested (INR)', 'state': 'State'},
        color_discrete_sequence=[accent_color]
    )
    apply_plotly_theme(fig_state)
    st.plotly_chart(fig_state, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 4: SIP & MARKET TRENDS
# ==============================================================================
with tab4:
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Monthly SIP Inflow vs Nifty 50 Close</div>
            <div class="chart-subtitle">Comparing systematic investment inflows with Nifty 50 performance (2022-2025)</div>
        """, unsafe_allow_html=True)
        
        # Load monthly inflows and benchmark close
        conn = get_db_connection()
        df_sip = pd.read_sql("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month", conn)
        df_bench = pd.read_sql("SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY 50' ORDER BY date", conn)
        conn.close()
        
        df_bench['date'] = pd.to_datetime(df_bench['date'])
        df_bench['month'] = df_bench['date'].dt.strftime('%Y-%m')
        df_bench_monthly = df_bench.groupby('month')['close_value'].mean().reset_index()
        
        # Merge
        df_trend = pd.merge(df_sip, df_bench_monthly, on='month')
        
        # Dual axis plot using Plotly Graph Objects
        fig_dual = go.Figure()
        
        fig_dual.add_trace(go.Bar(
            x=df_trend['month'], y=df_trend['sip_inflow_crore'],
            name='SIP Inflow (Cr)',
            marker_color='rgba(37,99,235,0.7)',
            yaxis='y1'
        ))
        
        fig_dual.add_trace(go.Scatter(
            x=df_trend['month'], y=df_trend['close_value'],
            name='Nifty 50 Close',
            line=dict(color=red_color, width=2.5),
            yaxis='y2'
        ))
        
        fig_dual.update_layout(
            yaxis=dict(title='SIP Inflow (Cr)', side='left'),
            yaxis2=dict(title='Nifty 50 Index', side='right', overlaying='y', showgrid=False),
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)')
        )
        
        apply_plotly_theme(fig_dual)
        st.plotly_chart(fig_dual, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Top Categories by Inflow (FY25)</div>
            <div class="chart-subtitle">Sum of net inflows in INR Crores for Financial Year 2024-25</div>
        """, unsafe_allow_html=True)
        
        conn = get_db_connection()
        # FY25 spans Apr 2024 to Mar 2025
        df_inflows = pd.read_sql("""
            SELECT category, sum(net_inflow_crore) as total_inflow
            FROM category_inflows
            WHERE month >= '2024-04' AND month <= '2025-03'
            GROUP BY category
            ORDER BY total_inflow DESC
            LIMIT 5
        """, conn)
        conn.close()
        
        fig_cat_inflow = px.bar(
            df_inflows, x='total_inflow', y='category',
            orientation='h',
            labels={'total_inflow': 'Net Inflow (Crores)', 'category': 'Asset Category'},
            color_discrete_sequence=[accent_color]
        )
        fig_cat_inflow.update_layout(yaxis={'categoryorder':'total ascending'})
        apply_plotly_theme(fig_cat_inflow)
        st.plotly_chart(fig_cat_inflow, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Interactive simple fund recommender inside dashboard
    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">⚡ Intelligent Fund Recommender</div>
        <div class="chart-subtitle">Find top 3 mutual funds by Sharpe ratio matching your risk appetite</div>
    """, unsafe_allow_html=True)
    
    rec_risk = st.radio("Select your Risk Appetite", ['Low', 'Moderate', 'High'], horizontal=True)
    
    from scripts.recommender import recommend_funds
    df_recs = recommend_funds(rec_risk)
    
    if df_recs is not None and len(df_recs) > 0:
        rows_rec = ""
        for idx, row in df_recs.iterrows():
            rows_rec += f"""
            <tr>
                <td><b>{row['amfi_code']}</b></td>
                <td>{row['scheme_name']}</td>
                <td>{row['category']}</td>
                <td>{row['risk_category']}</td>
                <td><span class="badge badge-green">{row['sharpe_ratio']:.3f}</span></td>
                <td>{row['return_3yr_pct']:.2f}%</td>
            </tr>
            """
        st.markdown(f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>AMFI Code</th>
                    <th>Scheme Name</th>
                    <th>Category</th>
                    <th>Risk Category</th>
                    <th>Sharpe Ratio</th>
                    <th>3Yr Return</th>
                </tr>
            </thead>
            <tbody>
                {rows_rec}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.write("No matching funds found.")
        
    st.markdown("</div>", unsafe_allow_html=True)
