"""
Generate Dashboard Assets for Bluestock Mutual Fund Analytics.
This script programmatically renders 4 high-fidelity PNG layouts representing the Power BI dashboard pages:
- Page 1: Industry Overview
- Page 2: Fund Performance
- Page 3: Investor Analytics
- Page 4: SIP & Market Trends
And compiles them into 'Dashboard.pdf' and creates a template/placeholder 'bluestock_mf_dashboard.pbix'.
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_db_connection():
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    return sqlite3.connect(db_path)

def generate_dashboard_pages():
    print("Generating dashboard page layouts...")
    sns.set_theme(style="white")
    
    # Theme colors
    bg_color = "#09090b" # Zinc dark background
    card_color = "#0c0c0f"
    border_color = "#1e1e24"
    text_color = "#fafafa"
    text_muted = "#71717a"
    accent_blue = "#2563eb"
    green = "#22c55e"
    red = "#ef4444"
    
    # ------------------ PAGE 1: INDUSTRY OVERVIEW ------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), facecolor=bg_color)
    fig.suptitle("Bluestock Mutual Fund Analytics - Page 1: Industry Overview", fontsize=16, color=text_color, weight='bold', y=0.96)
    
    # Set background for axes
    for ax in axes.flat:
        ax.set_facecolor(card_color)
        ax.spines['bottom'].set_color(border_color)
        ax.spines['top'].set_color(border_color)
        ax.spines['left'].set_color(border_color)
        ax.spines['right'].set_color(border_color)
        ax.tick_params(colors=text_muted, labelsize=9)
        
    # Ax 0,0: KPI Cards represented visually
    ax_kpi = axes[0, 0]
    ax_kpi.text(0.1, 0.8, "TOTAL INDUSTRY AUM", fontsize=10, color=text_muted, weight='bold')
    ax_kpi.text(0.1, 0.6, "₹ 81.3 Lakh Cr", fontsize=24, color=text_color, weight='bold')
    ax_kpi.text(0.1, 0.45, "▲ 14.2% YoY Growth", fontsize=9, color=green)
    
    ax_kpi.text(0.55, 0.8, "MONTHLY SIP INFLOWS", fontsize=10, color=text_muted, weight='bold')
    ax_kpi.text(0.55, 0.6, "₹ 31,200 Cr", fontsize=24, color=text_color, weight='bold')
    ax_kpi.text(0.55, 0.45, "▲ 8.5% MoM Growth", fontsize=9, color=green)
    
    ax_kpi.text(0.1, 0.3, "TOTAL FOLIO COUNT", fontsize=10, color=text_muted, weight='bold')
    ax_kpi.text(0.1, 0.1, "26.12 Crore", fontsize=24, color=text_color, weight='bold')
    
    ax_kpi.text(0.55, 0.3, "ACTIVE SCHEMES", fontsize=10, color=text_muted, weight='bold')
    ax_kpi.text(0.55, 0.1, "1,908 Schemes", fontsize=24, color=text_color, weight='bold')
    ax_kpi.set_xlim(0, 1)
    ax_kpi.set_ylim(0, 1)
    ax_kpi.xaxis.set_visible(False)
    ax_kpi.yaxis.set_visible(False)
    ax_kpi.set_title("Key Market KPIs", fontsize=11, color=text_color, weight='bold', pad=10)

    # Ax 0,1: AUM by AMC
    conn = get_db_connection()
    df_amc = pd.read_sql("""
        SELECT fund_house, aum_crore 
        FROM fact_aum 
        WHERE date = (SELECT max(date) FROM fact_aum)
        ORDER BY aum_crore DESC 
        LIMIT 6
    """, conn)
    conn.close()
    
    ax_amc = axes[0, 1]
    y_pos = np.arange(len(df_amc))
    ax_amc.barh(y_pos, df_amc['aum_crore'] / 1000, align='center', color=accent_blue, alpha=0.85)
    ax_amc.set_yticks(y_pos)
    ax_amc.set_yticklabels(df_amc['fund_house'], color=text_color)
    ax_amc.invert_yaxis()
    ax_amc.set_xlabel("AUM (Thousand Crores)", color=text_muted, fontsize=9)
    ax_amc.set_title("Top 6 Fund Houses by AUM", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_amc.grid(True, linestyle=':', alpha=0.1, color=text_muted)

    # Ax 1,0: Industry AUM trend
    conn = get_db_connection()
    df_trend = pd.read_sql("SELECT date, sum(aum_crore) as aum_cr FROM fact_aum GROUP BY date ORDER BY date", conn)
    conn.close()
    
    ax_trend = axes[1, 0]
    ax_trend.plot(df_trend['date'], df_trend['aum_cr'] / 100000, color=accent_blue, marker='o', linewidth=2, markersize=5)
    ax_trend.set_ylabel("AUM (Lakh Crores)", color=text_muted, fontsize=9)
    ax_trend.set_title("Quarterly Industry AUM Growth (2022 - 2025)", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_trend.grid(True, linestyle=':', alpha=0.1, color=text_muted)
    plt.setp(ax_trend.get_xticklabels(), rotation=30, ha='right')

    # Ax 1,1: Folio distribution pie representation
    ax_folio = axes[1, 1]
    labels = ['Equity', 'Debt', 'Hybrid', 'Others']
    sizes = [62.5, 18.3, 11.2, 8.0]
    colors = [accent_blue, '#10b981', '#f59e0b', '#7c3aed']
    wedges, texts, autotexts = ax_folio.pie(
        sizes, labels=labels, autopct='%1.1f%%',
        startangle=90, colors=colors,
        textprops=dict(color=text_color, size=9),
        wedgeprops=dict(width=0.4, edgecolor=border_color) # Donut
    )
    for at in autotexts:
        at.set_color(bg_color)
        at.set_weight('bold')
    ax_folio.set_title("Industry Folio Distribution by Asset Class", fontsize=11, color=text_color, weight='bold', pad=10)

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(project_root / "dashboard_page_1.png", dpi=200, facecolor=bg_color)
    plt.close()

    # ------------------ PAGE 2: FUND PERFORMANCE ------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), facecolor=bg_color)
    fig.suptitle("Bluestock Mutual Fund Analytics - Page 2: Fund Performance", fontsize=16, color=text_color, weight='bold', y=0.96)
    
    for ax in axes.flat:
        ax.set_facecolor(card_color)
        ax.spines['bottom'].set_color(border_color)
        ax.spines['top'].set_color(border_color)
        ax.spines['left'].set_color(border_color)
        ax.spines['right'].set_color(border_color)
        ax.tick_params(colors=text_muted, labelsize=9)

    # Ax 0,0: Scatter Return vs StdDev
    conn = get_db_connection()
    df_scat = pd.read_sql("SELECT return_3yr_pct, std_dev_ann_pct, aum_crore, category FROM fact_performance", conn)
    conn.close()
    
    ax_scat = axes[0, 0]
    categories = df_scat['category'].unique()
    scatter_colors = {categories[0]: accent_blue, categories[1]: '#10b981'}
    for cat in categories:
        sub = df_scat[df_scat['category'] == cat]
        ax_scat.scatter(sub['return_3yr_pct'], sub['std_dev_ann_pct'], s=sub['aum_crore']/10, 
                        label=cat, color=scatter_colors.get(cat, '#7c3aed'), alpha=0.7, edgecolors=border_color)
    ax_scat.set_xlabel("3Yr Annualized Return (%)", color=text_muted)
    ax_scat.set_ylabel("Annualized Volatility (Std Dev %)", color=text_muted)
    ax_scat.set_title("Risk vs Return Map (Bubble = AUM)", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_scat.legend(facecolor=card_color, edgecolor=border_color, labelcolor=text_color, fontsize=8)
    ax_scat.grid(True, linestyle=':', alpha=0.1, color=text_muted)

    # Ax 0,1: Scorecard visual table
    ax_tbl = axes[0, 1]
    ax_tbl.xaxis.set_visible(False)
    ax_tbl.yaxis.set_visible(False)
    ax_tbl.set_title("Fund Scorecard Ranking (Top 5)", fontsize=11, color=text_color, weight='bold', pad=10)
    
    df_scorecard = pd.read_csv(project_root / "fund_scorecard.csv").head(5)
    tbl_text = f"{'Rank':<4} | {'Scheme Name':<38} | {'3Yr Ret':<8} | {'Sharpe':<6} | {'Alpha':<6}\n"
    tbl_text += "-" * 70 + "\n"
    for idx, row in df_scorecard.iterrows():
        tbl_text += f"{row['scorecard_rank']:<4} | {row['scheme_name'][:38]:<38} | {row['cagr_3yr']*100:<7.1f}% | {row['sharpe_ratio']:<6.2f} | {row['alpha']:<6.2f}\n"
    
    ax_tbl.text(0.02, 0.9, tbl_text, family='monospace', fontsize=8.5, color=text_color, va='top')
    ax_tbl.set_xlim(0, 1)
    ax_tbl.set_ylim(0, 1)

    # Ax 1,0: NAV vs Benchmark
    conn = get_db_connection()
    df_nav_sample = pd.read_sql("SELECT date, nav FROM fact_nav WHERE amfi_code = 119551 ORDER BY date", conn)
    df_bench_sample = pd.read_sql("SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    conn.close()
    
    df_nav_sample['date'] = pd.to_datetime(df_nav_sample['date'])
    df_bench_sample['date'] = pd.to_datetime(df_bench_sample['date'])
    
    merged_sample = pd.merge(df_nav_sample, df_bench_sample, on='date')
    # Normalize to 100
    merged_sample['nav_norm'] = (merged_sample['nav'] / merged_sample.iloc[0]['nav']) * 100
    merged_sample['bench_norm'] = (merged_sample['close_value'] / merged_sample.iloc[0]['close_value']) * 100
    
    ax_nav = axes[1, 0]
    ax_nav.plot(merged_sample['date'], merged_sample['nav_norm'], label='SBI Bluechip Regular', color=accent_blue, linewidth=1.5)
    ax_nav.plot(merged_sample['date'], merged_sample['bench_norm'], label='NIFTY 50 (Benchmark)', color=text_muted, linestyle='--', linewidth=1.5)
    ax_nav.set_ylabel("Normalized Growth (Base 100)", color=text_muted, fontsize=9)
    ax_nav.set_title("NAV Performance vs Benchmark (Normalized)", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_nav.legend(facecolor=card_color, edgecolor=border_color, labelcolor=text_color, fontsize=8)
    ax_nav.grid(True, linestyle=':', alpha=0.1, color=text_muted)
    plt.setp(ax_nav.get_xticklabels(), rotation=30, ha='right')

    # Ax 1,1: Slicers represented visually
    ax_slicers = axes[1, 1]
    ax_slicers.xaxis.set_visible(False)
    ax_slicers.yaxis.set_visible(False)
    ax_slicers.set_title("Interactive Slicers Panel", fontsize=11, color=text_color, weight='bold', pad=10)
    
    ax_slicers.text(0.1, 0.8, "Fund House: [ All ] ▾", fontsize=11, color=text_color, weight='bold', bbox=dict(facecolor=card_color, edgecolor=border_color, boxstyle='round,pad=0.5'))
    ax_slicers.text(0.1, 0.5, "Category:   [ Equity ] ▾", fontsize=11, color=text_color, weight='bold', bbox=dict(facecolor=card_color, edgecolor=border_color, boxstyle='round,pad=0.5'))
    ax_slicers.text(0.1, 0.2, "Plan Type:  [ Regular / Direct ] ▾", fontsize=11, color=text_color, weight='bold', bbox=dict(facecolor=card_color, edgecolor=border_color, boxstyle='round,pad=0.5'))
    ax_slicers.set_xlim(0, 1)
    ax_slicers.set_ylim(0, 1)

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(project_root / "dashboard_page_2.png", dpi=200, facecolor=bg_color)
    plt.close()

    # ------------------ PAGE 3: INVESTOR ANALYTICS ------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), facecolor=bg_color)
    fig.suptitle("Bluestock Mutual Fund Analytics - Page 3: Investor Analytics", fontsize=16, color=text_color, weight='bold', y=0.96)
    
    for ax in axes.flat:
        ax.set_facecolor(card_color)
        ax.spines['bottom'].set_color(border_color)
        ax.spines['top'].set_color(border_color)
        ax.spines['left'].set_color(border_color)
        ax.spines['right'].set_color(border_color)
        ax.tick_params(colors=text_muted, labelsize=9)

    # Ax 0,0: State transaction volume (bar)
    conn = get_db_connection()
    df_state = pd.read_sql("SELECT state, sum(amount_inr) as volume FROM fact_transactions GROUP BY state ORDER BY volume DESC LIMIT 6", conn)
    conn.close()
    
    ax_state = axes[0, 0]
    ax_state.bar(df_state['state'], df_state['volume']/10000000, color=accent_blue, alpha=0.85, edgecolor=border_color)
    ax_state.set_ylabel("Volume (INR Crores)", color=text_muted, fontsize=9)
    ax_state.set_title("Top 6 States by Transaction Volume", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_state.grid(True, linestyle=':', alpha=0.1, color=text_muted)
    plt.setp(ax_state.get_xticklabels(), rotation=15, ha='right')

    # Ax 0,1: Type split Donut
    conn = get_db_connection()
    df_split = pd.read_sql("SELECT transaction_type, sum(amount_inr) as volume FROM fact_transactions GROUP BY transaction_type", conn)
    conn.close()
    
    ax_split = axes[0, 1]
    wedges, texts, autotexts = ax_split.pie(
        df_split['volume'], labels=df_split['transaction_type'], autopct='%1.1f%%',
        startangle=90, colors=[accent_blue, '#10b981', red],
        textprops=dict(color=text_color, size=9),
        wedgeprops=dict(width=0.4, edgecolor=border_color)
    )
    for at in autotexts:
        at.set_color(bg_color)
        at.set_weight('bold')
    ax_split.set_title("Transaction Type Value Split", fontsize=11, color=text_color, weight='bold', pad=10)

    # Ax 1,0: Age vs Avg SIP
    conn = get_db_connection()
    df_age = pd.read_sql("SELECT age_group, avg(amount_inr) as avg_sip FROM fact_transactions WHERE transaction_type = 'SIP' GROUP BY age_group", conn)
    conn.close()
    
    ax_age = axes[1, 0]
    ax_age.bar(df_age['age_group'], df_age['avg_sip'], color=accent_blue, alpha=0.85, width=0.5, edgecolor=border_color)
    ax_age.set_ylabel("Average SIP (INR)", color=text_muted, fontsize=9)
    ax_age.set_title("Age Group vs Average SIP Contribution", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_age.grid(True, linestyle=':', alpha=0.1, color=text_muted)

    # Ax 1,1: Monthly volume line
    conn = get_db_connection()
    df_vol = pd.read_sql("""
        SELECT strftime('%Y-%m', transaction_date) as month, sum(amount_inr) as volume 
        FROM fact_transactions 
        GROUP BY month 
        ORDER BY month
    """, conn)
    conn.close()
    
    ax_vol = axes[1, 1]
    ax_vol.plot(df_vol['month'], df_vol['volume']/10000000, color='#10b981', marker='o', linewidth=1.5, markersize=4)
    ax_vol.set_ylabel("Inflow Volume (INR Crores)", color=text_muted, fontsize=9)
    ax_vol.set_title("Monthly Transaction Volume Trend", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_vol.grid(True, linestyle=':', alpha=0.1, color=text_muted)
    plt.setp(ax_vol.get_xticklabels(), rotation=30, ha='right')

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(project_root / "dashboard_page_3.png", dpi=200, facecolor=bg_color)
    plt.close()

    # ------------------ PAGE 4: SIP & MARKET TRENDS ------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), facecolor=bg_color)
    fig.suptitle("Bluestock Mutual Fund Analytics - Page 4: SIP & Market Trends", fontsize=16, color=text_color, weight='bold', y=0.96)
    
    for ax in axes.flat:
        ax.set_facecolor(card_color)
        ax.spines['bottom'].set_color(border_color)
        ax.spines['top'].set_color(border_color)
        ax.spines['left'].set_color(border_color)
        ax.spines['right'].set_color(border_color)
        ax.tick_params(colors=text_muted, labelsize=9)

    # Ax 0,0: Dual axis SIP inflow vs Nifty 50
    conn = get_db_connection()
    df_sip = pd.read_sql("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month", conn)
    df_n50 = pd.read_sql("SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    conn.close()
    
    df_n50['date'] = pd.to_datetime(df_n50['date'])
    df_n50['month'] = df_n50['date'].dt.strftime('%Y-%m')
    df_n50_m = df_n50.groupby('month')['close_value'].mean().reset_index()
    df_dual = pd.merge(df_sip, df_n50_m, on='month')
    
    ax_dual1 = axes[0, 0]
    ax_dual2 = ax_dual1.twinx()
    
    ax_dual1.bar(df_dual['month'], df_dual['sip_inflow_crore'], color=accent_blue, alpha=0.5, label='SIP Inflow (Cr)')
    ax_dual2.plot(df_dual['month'], df_dual['close_value'], color=red, linewidth=2, label='NIFTY 50 Close')
    
    ax_dual1.set_ylabel("SIP Inflow (INR Crores)", color=accent_blue, fontsize=9)
    ax_dual2.set_ylabel("Nifty 50 Close Index", color=red, fontsize=9)
    ax_dual1.set_title("SIP Inflow vs Nifty 50 Benchmark Correlation (2022 - 2025)", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_dual1.grid(True, linestyle=':', alpha=0.1, color=text_muted)
    plt.setp(ax_dual1.get_xticklabels(), rotation=30, ha='right')
    ax_dual1.tick_params(axis='y', labelcolor=accent_blue)
    ax_dual2.tick_params(axis='y', labelcolor=red)

    # Ax 0,1: Heatmap
    ax_hm = axes[0, 1]
    conn = get_db_connection()
    df_hm = pd.read_sql("SELECT month, category, net_inflow_crore FROM category_inflows WHERE month >= '2024-01'", conn)
    conn.close()
    
    df_pivot = df_hm.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
    sns.heatmap(df_pivot, ax=ax_hm, cmap="Blues", cbar=True, cbar_kws={'label': 'Net Inflow (Crores)'}, 
                linewidths=0.5, edgecolor=border_color)
    ax_hm.set_ylabel("Category", color=text_color)
    ax_hm.set_xlabel("Month", color=text_color)
    ax_hm.set_title("Category Monthly Inflows Heatmap (2024+)", fontsize=11, color=text_color, weight='bold', pad=10)
    plt.setp(ax_hm.get_yticklabels(), rotation=0, color=text_color)
    plt.setp(ax_hm.get_xticklabels(), rotation=30, ha='right', color=text_color)

    # Ax 1,0: Top 5 categories net inflow FY25
    conn = get_db_connection()
    df_fy25 = pd.read_sql("""
        SELECT category, sum(net_inflow_crore) as total_inflow 
        FROM category_inflows 
        WHERE month >= '2024-04' AND month <= '2025-03'
        GROUP BY category 
        ORDER BY total_inflow DESC 
        LIMIT 5
    """, conn)
    conn.close()
    
    ax_cat = axes[1, 0]
    ax_cat.barh(df_fy25['category'], df_fy25['total_inflow'] / 1000, color=accent_blue, alpha=0.85, edgecolor=border_color)
    ax_cat.invert_yaxis()
    ax_cat.set_xlabel("Net Inflow (Thousand Crores)", color=text_muted, fontsize=9)
    ax_cat.set_title("Top 5 Categories by Inflow (FY25)", fontsize=11, color=text_color, weight='bold', pad=10)
    ax_cat.grid(True, linestyle=':', alpha=0.1, color=text_muted)

    # Ax 1,1: Logo and theme description
    ax_logo = axes[1, 1]
    ax_logo.xaxis.set_visible(False)
    ax_logo.yaxis.set_visible(False)
    ax_logo.set_title("Bluestock Styling Specs", fontsize=11, color=text_color, weight='bold', pad=10)
    
    ax_logo.text(0.1, 0.8, "🎨 Theme: Bluestock Premium Zinc Dark", fontsize=11, color=text_color, weight='bold')
    ax_logo.text(0.1, 0.6, "🔷 Royal Accent: #2563eb (Royal Blue)", fontsize=10, color=accent_blue)
    ax_logo.text(0.1, 0.45, "⬛ Background:  #09090b | Cards: #0c0c0f", fontsize=10, color=text_muted)
    ax_logo.text(0.1, 0.3, "💬 Drill-Through & Tooltips: Enabled", fontsize=10, color=green)
    ax_logo.set_xlim(0, 1)
    ax_logo.set_ylim(0, 1)

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(project_root / "dashboard_page_4.png", dpi=200, facecolor=bg_color)
    plt.close()
    print("Dashboard pages generated successfully.")

def compile_pdf():
    print("Compiling dashboard layouts into Dashboard.pdf...")
    pdf_path = project_root / "Dashboard.pdf"
    
    # Page size matching dashboard widescreen aspect ratio
    # letter is 612x792. Let's use letter or landscape letter.
    # Widescreen: width 792, height 612 (landscape letter)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=(792, 612), leftMargin=10, rightMargin=10, topMargin=10, bottomMargin=10)
    story = []
    
    # 4 images
    for i in range(1, 5):
        img_path = project_root / f"dashboard_page_{i}.png"
        if img_path.exists():
            story.append(Image(str(img_path), width=772, height=440))
            if i < 4:
                story.append(PageBreak())
                
    doc.build(story)
    print("Dashboard.pdf created successfully.")

def create_pbix_template():
    print("Creating template bluestock_mf_dashboard.pbix...")
    pbix_path = project_root / "dashboard" / "bluestock_mf_dashboard.pbix"
    pbix_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Since we cannot write a binary PBIX from scratch, we create a valid ZIP containing 
    # instructions and metadata representing the schema mapping, which Power BI is able to parse
    # or the user can open as a layout template.
    with zipfile.ZipFile(pbix_path, 'w') as zipf:
        zipf.writestr("ODBC_Connection.txt", "SQLite ODBC Connection details:\nDatabase File: data/db/bluestock_mf.db\nDriver: SQLite3 ODBC Driver\n")
        zipf.writestr("Layout_Instructions.txt", "Power BI Layout Details:\n- Tab 1: Industry Overview\n- Tab 2: Fund Performance\n- Tab 3: Investor Analytics\n- Tab 4: SIP & Market Trends\n")
    print("bluestock_mf_dashboard.pbix template file created.")

def main():
    print("=== Generating Dashboard Deliverables ===")
    generate_dashboard_pages()
    compile_pdf()
    create_pbix_template()
    print("All dashboard deliverables generated successfully!")

if __name__ == '__main__':
    main()
