"""
Generate PDF & PPTX Reports for Bluestock Mutual Fund Analytics.
This script programmatically generates:
1. reports/Final_Report.pdf (approx 15-20 pages, embedded with 6 charts, SQL queries, and data dictionary).
2. reports/Presentation.pptx (12 slides including problem statement, architecture, performance, and findings).
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def generate_pdf():
    print("Generating reports/Final_Report.pdf...")
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    pdf_path = project_root / "reports" / "Final_Report.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#2563eb"), # Royal Blue
        alignment=1, # Center
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#4b5563"),
        alignment=1,
        spaceAfter=40
    )
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        alignment=1,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=4,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1f2937"),
        leftIndent=20,
        firstLineIndent=-10,
        spaceBefore=2,
        spaceAfter=3
    )
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=5,
        spaceAfter=5
    )

    story = []
    
    # ------------------ COVER PAGE (Page 1) ------------------
    story.append(Spacer(1, 100))
    # Add a mock logo using standard reportlab flowable or spacer representation
    story.append(Paragraph("BLUESTOCK MUTUAL FUND ANALYTICS", title_style))
    story.append(Paragraph("A Comprehensive Capstone Project on Ingestion, ETL Pipeline Design, Performance Evaluation, and Advanced Quantitative Portfolio Risk Modeling", subtitle_style))
    story.append(Spacer(1, 120))
    story.append(Paragraph("<b>Prepared For:</b> Bluestock Fintech Academy Review Board", meta_style))
    story.append(Paragraph("<b>Author:</b> Nitheesh Thondapu", meta_style))
    story.append(Paragraph("<b>Date:</b> August 2026", meta_style))
    story.append(Paragraph("<b>Version:</b> 1.0 (Final)", meta_style))
    story.append(PageBreak())
    
    # ------------------ TABLE OF CONTENTS (Page 2) ------------------
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 10))
    
    toc_data = [
        ["1. Executive Summary", "......................................................................................................................................", "Page 3"],
        ["2. Data Sources & Schema Design", "......................................................................................................................................", "Page 4"],
        ["3. Data Quality & ETL Pipeline", "......................................................................................................................................", "Page 6"],
        ["4. Exploratory Data Analysis (EDA) Findings", "......................................................................................................................................", "Page 8"],
        ["5. Mutual Fund Performance Analytics", "......................................................................................................................................", "Page 11"],
        ["6. Advanced Quantitative Risk Analysis", "......................................................................................................................................", "Page 13"],
        ["7. Interactive Dashboard Design", "......................................................................................................................................", "Page 15"],
        ["8. Limitations, Conclusions & Recommendations", "......................................................................................................................................", "Page 16"],
        ["9. Appendix: SQL Queries", "......................................................................................................................................", "Page 18"]
    ]
    t_toc = Table(toc_data, colWidths=[180, 260, 50])
    t_toc.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1f2937")),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_toc)
    story.append(PageBreak())
    
    # ------------------ 1. EXECUTIVE SUMMARY (Page 3) ------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This project delivers an end-to-end investment intelligence system for analyzing Indian Mutual Fund schemes. "
        "The primary purpose is to ingestion historical Net Asset Values (NAV), clean values, store facts in a relational "
        "star schema database, evaluate fund risks and returns, and present interactive analytics to assist portfolio managers. "
        "By applying robust statistical techniques, we evaluated 40 schemes over a 4.4-year history (Jan 2022 to May 2026) representing equity, debt, and liquid asset classes.",
        body_style
    ))
    story.append(Paragraph("Key Findings of the Analytics Capstone:", h2_style))
    story.append(Paragraph("• <b>Performance leaders:</b> SBI Small Cap Fund (23.39% 3-year return) and Kotak Emerging Equity (18.23%) dominate return performance but introduce high volatility.", bullet_style))
    story.append(Paragraph("• <b>Risk-adjusted efficiency:</b> HDFC Top 100 Regular leads Large Cap equity funds with a Sharpe ratio of 1.060. Liquid funds exhibit mathematical anomalies due to near-zero standard deviation.", bullet_style))
    story.append(Paragraph("• <b>Tail Risk Assessment:</b> SBI Small Cap Fund and Quant Mid Cap have the highest daily VaR (95%) of -2.12% and -1.95%, whereas HDFC Liquid Fund exhibits a minimal VaR of -0.01%.", bullet_style))
    story.append(Paragraph("• <b>SIP Mandate Retention Gaps:</b> Over 97.8% of long-term SIP investors show an average gap greater than 35 days between consecutive installments, indicating high friction or mandate failure risks.", bullet_style))
    story.append(Paragraph("• <b>Portfolio Sector Concentration:</b> HDFC Money Market and SBI Small Cap exhibit high concentration (HHI > 2800), while Nippon Large Cap provides excellent diversification (HHI: 1,142) across 15+ sectors.", bullet_style))
    story.append(PageBreak())
    
    # ------------------ 2. DATA SOURCES & SCHEMA DESIGN (Page 4-5) ------------------
    story.append(Paragraph("2. Data Sources & Schema Design", h1_style))
    story.append(Paragraph(
        "The analytics platform blends 10 structured CSV data sources mapping AMC fund details, NAV history, investor profiles, and market index closes. "
        "To support high-performance analytical queries, we engineered an SQLite database using a <b>Star Schema</b> design. "
        "This isolates dimensional properties (funds, dates) from transactional and historical facts.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Database Star Schema Architecture:", h2_style))
    
    schema_desc = [
        ["Table Name", "Table Type", "Primary/Foreign Keys", "Description"],
        ["dim_fund", "Dimension", "amfi_code (PK)", "Stores fund manager, launch dates, risk categories, expense ratios."],
        ["dim_date", "Dimension", "date (PK)", "Calendar dates mapped to year, month, day, quarter, and weekend flags."],
        ["fact_nav", "Fact", "amfi_code, date (Composite PK)", "Tracks historical net asset values of 40 schemes on a daily basis."],
        ["fact_transactions", "Fact", "transaction_id (PK)", "Records purchase and redemption transactions for 32,778 investors."],
        ["fact_performance", "Fact", "amfi_code (PK)", "Holds performance statistics (ratios, CAGR, Std Dev, Alpha, Beta)."],
        ["fact_aum", "Fact", "aum_id (PK)", "Tracks monthly assets under management trend for AMC fund houses."]
    ]
    t_schema = Table(schema_desc, colWidths=[100, 70, 150, 180])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 15))
    story.append(Paragraph("Auxiliary Dimension & Ingest Tables:", h2_style))
    story.append(Paragraph("• <b>portfolio_holdings:</b> Tracks detailed stock symbol, name, sector weight, and market value for equity funds.", bullet_style))
    story.append(Paragraph("• <b>benchmark_indices:</b> Stores daily closing values of benchmark indices (Nifty 50, Nifty 100) for returns comparison.", bullet_style))
    story.append(Paragraph("• <b>monthly_sip_inflows / category_inflows:</b> Monitors monthly inflow trends across asset categories (Equity, Hybrid, Debt).", bullet_style))
    story.append(PageBreak())
    
    # ------------------ 3. DATA QUALITY & ETL PIPELINE (Page 6-7) ------------------
    story.append(Paragraph("3. Data Quality & ETL Pipeline", h1_style))
    story.append(Paragraph(
        "A master ETL orchestrator script (<code>etl_pipeline.py</code>) was designed to automate data ingestion, cleaning, and DB loading. "
        "Specific cleaning rules ensure data quality before insertion:",
        body_style
    ))
    story.append(Paragraph("• <b>NAV History Cleaning:</b> Standardized date formats. Filtered out duplicate rows and rows with non-positive NAV values. Reindexed the daily NAV records and forward-filled (<code>ffill</code>) NAVs for holidays and weekends.", bullet_style))
    story.append(Paragraph("• <b>Transaction Normalization:</b> Fixed transaction dates. Cleaned and standardized the transaction types to 'SIP', 'Lumpsum', or 'Redemption'. Standardized KYC statuses to 'Verified' or 'Pending'.", bullet_style))
    story.append(Paragraph("• <b>Performance Validation:</b> Coerced all returns to numeric types. Flagged anomalies like liquid funds where volatility standard deviation is extremely low, skewing Sharpe and Sortino ratios.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("ETL Data Integrity & Row Count Verification:", h2_style))
    
    # Table of row counts (from etl_pipeline run)
    rows_data = [
        ["Filename", "Table Name", "CSV Rows", "DB Rows", "Integrity Match"],
        ["01_fund_master.csv", "dim_fund", "40", "40", "MATCHED"],
        ["02_nav_history.csv", "fact_nav", "64,320", "64,320", "MATCHED"],
        ["03_aum_by_fund_house.csv", "fact_aum", "90", "90", "MATCHED"],
        ["04_monthly_sip_inflows.csv", "monthly_sip_inflows", "48", "48", "MATCHED"],
        ["05_category_inflows.csv", "category_inflows", "144", "144", "MATCHED"],
        ["06_industry_folio_count.csv", "industry_folio_count", "21", "21", "MATCHED"],
        ["07_scheme_performance.csv", "fact_performance", "40", "40", "MATCHED"],
        ["08_investor_transactions.csv", "fact_transactions", "32,778", "32,778", "MATCHED"],
        ["09_portfolio_holdings.csv", "portfolio_holdings", "322", "322", "MATCHED"],
        ["10_benchmark_indices.csv", "benchmark_indices", "8,050", "8,050", "MATCHED"]
    ]
    t_rows = Table(rows_data, colWidths=[150, 130, 70, 70, 80])
    t_rows.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ALIGN', (2,1), (3,-1), 'RIGHT'),
        ('ALIGN', (4,1), (4,-1), 'CENTER'),
        ('TEXTCOLOR', (4,1), (4,-1), colors.HexColor("#16a34a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rows)
    story.append(PageBreak())
    
    # ------------------ 4. EXPLORATORY DATA ANALYSIS (Page 8-10) ------------------
    story.append(Paragraph("4. Exploratory Data Analysis (EDA) Findings", h1_style))
    story.append(Paragraph(
        "Exploratory data analysis reveals high growth rates across the mutual fund industry. "
        "Total Industry AUM has experienced a significant upward trajectory between 2022 and 2025. "
        "Furthermore, monthly SIP inflows show strong momentum, reflecting growing retail investor confidence.",
        body_style
    ))
    
    # Embed total AUM growth chart
    img_aum_path = project_root / "eda_total_aum_growth.png"
    if img_aum_path.exists():
        story.append(Spacer(1, 10))
        story.append(Image(str(img_aum_path), width=450, height=220))
        story.append(Paragraph("Figure 4.1: Cumulative Industry AUM Growth (2022-2025)", subtitle_style))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph(
        "Demographic analysis indicates that retail participation is heavily skewed towards the young working population. "
        "The 18-25 and 26-35 age groups represent the highest transaction frequency, although their average SIP ticket sizes are smaller than the mature 36-55 age group.",
        body_style
    ))
    
    # Embed age pie chart or state bar chart
    img_state_path = project_root / "eda_geographic_state_bar.png"
    if img_state_path.exists():
        story.append(Image(str(img_state_path), width=450, height=220))
        story.append(Paragraph("Figure 4.2: Total Investment Inflows by State", subtitle_style))
        
    story.append(PageBreak())
    
    # ------------------ 5. MUTUAL FUND PERFORMANCE ANALYTICS (Page 11-12) ------------------
    story.append(Paragraph("5. Mutual Fund Performance Analytics", h1_style))
    story.append(Paragraph(
        "We evaluated performance using the compound annual growth rate (CAGR), standard deviation (annualized volatility), Sharpe ratio (annualized risk-adjusted excess returns), and Sortino ratio (downside deviation risk-adjusted return).",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Top 5 Mutual Funds Ranked by Performance Scorecard:", h2_style))
    
    # Load scorecard data
    try:
        df_scorecard = pd.read_csv(project_root / "fund_scorecard.csv")
        top_5_data = [["AMFI Code", "Scheme Name", "3Yr Return", "Sharpe", "Alpha", "Score (0-100)"]]
        for idx, row in df_scorecard.head(5).iterrows():
            top_5_data.append([
                str(row['amfi_code']),
                row['scheme_name'][:35] + "...",
                f"{row['return_3yr_pct']:.2f}%",
                f"{row['sharpe_ratio']:.3f}",
                f"{row['alpha']:.3f}",
                f"{row['score']:.1f}"
            ])
        t_top5 = Table(top_5_data, colWidths=[70, 180, 60, 50, 50, 70])
        t_top5.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_top5)
    except Exception as e:
        story.append(Paragraph(f"Scorecard data not loaded: {e}", body_style))
        
    story.append(Spacer(1, 15))
    
    # Embed benchmark comparison chart
    img_bench_path = project_root / "benchmark_comparison_chart.png"
    if img_bench_path.exists():
        story.append(Image(str(img_bench_path), width=450, height=220))
        story.append(Paragraph("Figure 5.1: Top 5 Funds Cumulative Returns vs Nifty 50 and Nifty 100 (3 Years)", subtitle_style))
        
    story.append(PageBreak())
    
    # ------------------ 6. ADVANCED QUANTITATIVE RISK ANALYSIS (Page 13-14) ------------------
    story.append(Paragraph("6. Advanced Quantitative Risk Analysis", h1_style))
    story.append(Paragraph(
        "Advanced analysis examines tail risk (Value at Risk and Conditional VaR) to quantify potential losses in a volatile market environment. "
        "Additionally, herfindahl-hirschman index (HHI) was computed to assess sector concentration risk across equity funds.",
        body_style
    ))
    
    # Embed rolling Sharpe plot
    img_sharpe_path = project_root / "rolling_sharpe_chart.png"
    if img_sharpe_path.exists():
        story.append(Spacer(1, 10))
        story.append(Image(str(img_sharpe_path), width=450, height=220))
        story.append(Paragraph("Figure 6.1: Rolling 90-Day Sharpe Ratio Comparison Over Time", subtitle_style))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph(
        "Value at Risk (VaR) at 95% indicates that SBI Small Cap Fund exhibits a -2.12% daily loss threshold, showing high tail risk. "
        "However, this is compensated by its strong alpha generation of 2.45% against Nifty 100. "
        "In contrast, HDFC Money Market Fund shows low risk (VaR: -0.05%) but high sector HHI concentration (3,124).",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ 7. INTERACTIVE DASHBOARD DESIGN (Page 15) ------------------
    story.append(Paragraph("7. Interactive Dashboard Design", h1_style))
    story.append(Paragraph(
        "To replace traditional reporting, we built an interactive Streamlit data application (dashboard/app.py) organized into 4 analytical tabs:",
        body_style
    ))
    story.append(Paragraph("1. <b>Industry Overview:</b> Provides macro-level statistics including industry AUM growth, monthly SIP trends, and AMC market shares.", bullet_style))
    story.append(Paragraph("2. <b>Fund Performance:</b> Shows an interactive Risk-Return scatter plot and a sortable scorecard table. Slicers filter by fund house, category, and plan.", bullet_style))
    story.append(Paragraph("3. <b>Investor Analytics:</b> Details demographic breakdowns (transactions by state, city tier splits, age profiles) using interactive bar and pie charts.", bullet_style))
    story.append(Paragraph("4. <b>SIP & Market Trends:</b> Combines monthly SIP inflows with the Nifty 50 close price to identify sentiment correlations.", bullet_style))
    story.append(Paragraph("• <b>Intelligent Recommender:</b> Integrated a rule-based engine in the dashboard that recommends the top 3 funds by Sharpe ratio within a selected risk appetite.", bullet_style))
    story.append(PageBreak())
    
    # ------------------ 8. LIMITATIONS & RECOMMENDATIONS (Page 16-17) ------------------
    story.append(Paragraph("8. Limitations, Conclusions & Recommendations", h1_style))
    story.append(Paragraph(
        "<b>Limitations identified:</b><br/>"
        "• Historical data covers a period of approximately 4.4 years, which does not encompass multiple macro interest rate cycles.<br/>"
        "• The investor transactions dataset contains a high attrition risk (97.8% showing gaps > 35 days), which may indicate data collection discrepancies or failed bank mandates.<br/>"
        "• The benchmark comparisons are restricted to Nifty 50 and Nifty 100, which are large-cap indices, presenting benchmark mismatch for mid and small cap funds.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Conclusions & Recommendations:</b>", h2_style))
    story.append(Paragraph("1. <b>Enhance SIP Reminders:</b> AMCs must address the 97.8% 'at-risk' investor gaps. Automate payment alerts via SMS, Whatsapp, and email around the SIP date.", bullet_style))
    story.append(Paragraph("2. <b>Diversify High-Concentration Portfolios:</b> Portfolios like HDFC Money Market should reduce financial sector weights (currently HHI > 3000) to protect against systemic sector shocks.", bullet_style))
    story.append(Paragraph("3. <b>Deploy Automated ETL fetches:</b> Maintain the scheduled weekday 8 PM cron job (schedule_etl.py) to fetch live NAVs from mfapi.in, ensuring database tables are always current.", bullet_style))
    story.append(PageBreak())
    
    # ------------------ 9. APPENDIX: SQL QUERIES (Page 18-20) ------------------
    story.append(Paragraph("9. Appendix: SQL Queries", h1_style))
    story.append(Paragraph(
        "Below are samples of the analytical SQL queries defined in <code>sql/queries.sql</code> to inspect AUM, NAV, and transactions.",
        body_style
    ))
    
    query_sample = """
-- Query: Top 5 funds by AUM
SELECT amfi_code, scheme_name, aum_crore
FROM fact_performance 
ORDER BY aum_crore DESC 
LIMIT 5;

-- Query: Average NAV per month for each scheme
SELECT amfi_code, strftime('%Y-%m', date) AS month, ROUND(AVG(nav), 4) AS avg_nav 
FROM fact_nav 
GROUP BY amfi_code, month 
LIMIT 3;
    """
    story.append(Paragraph(query_sample.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("End of Report. Bluestock Mutual Fund Analytics Capstone © 2026.", subtitle_style))
    
    # Build Document
    doc.build(story)
    print("reports/Final_Report.pdf generated successfully!")

def generate_pptx():
    print("Generating reports/Presentation.pptx...")
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    
    prs = Presentation()
    
    # Layout styles
    title_slide_layout = prs.slide_layouts[0]
    bullet_slide_layout = prs.slide_layouts[1]
    blank_slide_layout = prs.slide_layouts[6]
    
    # Color constants
    royal_blue = RGBColor(37, 99, 235)
    dark_gray = RGBColor(31, 41, 55)
    light_gray = RGBColor(107, 114, 128)
    
    def set_font(run, font_name='Arial', size=Pt(14), bold=False, color=dark_gray):
        run.font.name = font_name
        run.font.size = size
        run.font.bold = bold
        run.font.color.rgb = color

    # Slide 1: Title
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Bluestock Mutual Fund Analytics"
    subtitle.text = "Capstone Project Presentation: Ingestion, ETL, Performance & Quantitative Risk\nAuthor: Nitheesh Thondapu | Date: August 2026"
    
    set_font(title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(36), bold=True, color=royal_blue)
    set_font(subtitle.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(14), bold=False, color=light_gray)
    
    # Slide 2: Problem & Objective
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    title_shape.text = "Problem Statement & Project Objectives"
    set_font(title_shape.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    body_shape = shapes.placeholders[1]
    tf = body_shape.text_frame
    
    p = tf.add_paragraph()
    p.text = "Problem Statement:"
    p.level = 0
    set_font(p.runs[0], size=Pt(18), bold=True, color=royal_blue)
    
    p2 = tf.add_paragraph()
    p2.text = "Mutual fund data is stored across disparate formats, presenting gaps, weekends, and holidays in NAV values, as well as unstandardized transaction types and KYC statuses. Portfolio managers require structured risk models and interactive dashboards to evaluate performance."
    p2.level = 1
    
    p3 = tf.add_paragraph()
    p3.text = "Project Objectives:"
    p3.level = 0
    set_font(p3.runs[0], size=Pt(18), bold=True, color=royal_blue)
    
    p4 = tf.add_paragraph()
    p4.text = "1. Clean, reindex, and forward-fill NAV records; standardize transaction details.\n2. Design SQLite Star Schema to store facts and dimensions.\n3. Evaluate CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR/CVaR, and Sector HHI concentration.\n4. Deploy Streamlit interactive web application and schedule weekday ETL fetches."
    p4.level = 1

    # Slide 3: Data Sources
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "Structured Data Sources"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    tf.text = "Blending 10 CSV datasets and live API feeds:"
    
    datasets = [
        "01_fund_master: Scheme info, expense ratios, exit loads.",
        "02_nav_history: 64,320 rows of daily NAV records.",
        "03_aum_by_fund_house: Total AMC assets and scheme counts.",
        "04_monthly_sip_inflows / 05_category_inflows: Systematic inflow records.",
        "06_industry_folio_count: Total, equity, debt, and hybrid accounts.",
        "07_scheme_performance: Metrics including ratings and risk grades.",
        "08_investor_transactions: 32,778 rows of investor transaction records.",
        "09_portfolio_holdings: Weighted stock symbols and sectors.",
        "10_benchmark_indices: Nifty 50 and Nifty 100 historical closes.",
        "mfapi.in API: Live NAV history fetch for key schemes."
    ]
    for ds in datasets:
        p = tf.add_paragraph()
        p.text = ds
        p.level = 1
        set_font(p.runs[0], size=Pt(12))

    # Slide 4: Database Architecture & ETL
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "ETL Design & Relational Star Schema"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    tf.text = "Relational SQLite Star Schema (bluestock_mf.db) loaded via SQLAlchemy:"
    
    bullets = [
        "Dimension Tables: dim_fund (scheme manager/metadata) and dim_date (time-series indicators).",
        "Fact Tables: fact_nav (daily net asset values), fact_transactions (investor actions), fact_performance (risk ratios), fact_aum (AMC total assets).",
        "Orchestrator: scripts/etl_pipeline.py cleans datasets, establishes foreign key constraints, populates tables, and prints row count match reports.",
        "B1 Scheduler: scripts/schedule_etl.py creates Windows Task Scheduler / Cron job to fetch live NAVs weekdays at 8 PM."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = b
        p.level = 1
        set_font(p.runs[0], size=Pt(14))

    # Slide 5: EDA - AUM Growth
    slide = prs.slides.add_slide(blank_slide_layout)
    # Add title manually
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    tf = txBox.text_frame
    tf.text = "EDA Highlight: Industry AUM Growth"
    set_font(tf.paragraphs[0].runs[0], font_name='Arial', size=Pt(24), bold=True, color=royal_blue)
    
    img_path = project_root / "eda_total_aum_growth.png"
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.2), width=Inches(8), height=Inches(4.5))

    # Slide 6: EDA - Demographics
    slide = prs.slides.add_slide(blank_slide_layout)
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    tf = txBox.text_frame
    tf.text = "EDA Highlight: Investor Inflow by State"
    set_font(tf.paragraphs[0].runs[0], font_name='Arial', size=Pt(24), bold=True, color=royal_blue)
    
    img_path = project_root / "eda_geographic_state_bar.png"
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.2), width=Inches(8), height=Inches(4.5))

    # Slide 7: Performance Metrics
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "Mutual Fund Performance Analytics"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    tf.text = "Comprehensive performance ranking across 40 schemes:"
    
    perf_pts = [
        "CAGR: Annualized returns calculated for 1yr, 3yr, and 5yr using 252 trading days.",
        "Sharpe Ratio: Annualized risk-adjusted excess return using Rf = 6.5% (RBI repo rate proxy).",
        "Sortino Ratio: Downside deviation risk-adjusted return (excluding positive return days).",
        "Alpha & Beta: Calculated via OLS regression against Nifty 100 benchmark index.",
        "Maximum Drawdown: Tracks worst peak-to-trough drop and historical recovery duration.",
        "Scorecard (0-100): Composite metric: 30% Return + 25% Sharpe + 20% Alpha + 15% Expense (inverse) + 10% Max Drawdown (inverse)."
    ]
    for pt in perf_pts:
        p = tf.add_paragraph()
        p.text = pt
        p.level = 1
        set_font(p.runs[0], size=Pt(13))

    # Slide 8: Performance - Benchmark comparison
    slide = prs.slides.add_slide(blank_slide_layout)
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    tf = txBox.text_frame
    tf.text = "Performance: Top Funds vs Benchmark (3 Years)"
    set_font(tf.paragraphs[0].runs[0], font_name='Arial', size=Pt(24), bold=True, color=royal_blue)
    
    img_path = project_root / "benchmark_comparison_chart.png"
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.2), width=Inches(8), height=Inches(4.5))

    # Slide 9: Advanced - Value at Risk (VaR)
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "Advanced Risk Modeling: VaR & CVaR"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    tf.text = "Assessing extreme tail risk via Historical Value at Risk (95%):"
    
    var_pts = [
        "VaR (95%) represents the 5th percentile of daily returns for each mutual fund.",
        "CVaR (Conditional VaR) is the average loss on days exceeding the VaR threshold.",
        "SBI Small Cap Fund (VaR: -2.12%) and Quant Mid Cap Fund (VaR: -1.95%) have the highest daily tail risk.",
        "HDFC Liquid Fund (VaR: -0.01%) represents minimal daily risk.",
        "Sector HHI: herfindahl-hirschman index highlights high concentration in HDFC Money Market Fund (HHI: 3,124) vs. Nippon Large Cap (HHI: 1,142)."
    ]
    for pt in var_pts:
        p = tf.add_paragraph()
        p.text = pt
        p.level = 1
        set_font(p.runs[0], size=Pt(14))

    # Slide 10: Advanced - Rolling Sharpe Comparison
    slide = prs.slides.add_slide(blank_slide_layout)
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    tf = txBox.text_frame
    tf.text = "Advanced: Rolling 90-Day Sharpe Ratio"
    set_font(tf.paragraphs[0].runs[0], font_name='Arial', size=Pt(24), bold=True, color=royal_blue)
    
    img_path = project_root / "rolling_sharpe_chart.png"
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.2), width=Inches(8), height=Inches(4.5))

    # Slide 11: Interactive Dashboard (Streamlit Web App)
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "Premium Interactive Streamlit Web App"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    tf.text = "A full web app (dashboard/app.py) engineered to replace static slides:"
    
    dash_pts = [
        "Industry Overview: KPI cards for total industry assets and line trends.",
        "Fund Performance: Live Risk-Return scatter plot and sortable tables.",
        "Investor Analytics: Split of transactions by state, age, and payment modes.",
        "SIP & Market Trends: Dual-axis monthly SIP inflow vs. Nifty 50 close.",
        "Intelligent Fund Recommender: Embedded engine recommending top 3 funds by Sharpe ratio matching risk appetites (Low / Moderate / High)."
    ]
    for pt in dash_pts:
        p = tf.add_paragraph()
        p.text = pt
        p.level = 1
        set_font(p.runs[0], size=Pt(14))

    # Slide 12: Findings & Thank You
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    shapes.title.text = "Key Takeaways & Recommendations"
    set_font(shapes.title.text_frame.paragraphs[0].runs[0], font_name='Arial', size=Pt(28), bold=True, color=royal_blue)
    
    tf = shapes.placeholders[1].text_frame
    
    p = tf.add_paragraph()
    p.text = "Key Recommendations:"
    set_font(p.runs[0], size=Pt(18), bold=True, color=royal_blue)
    
    recs = [
        "1. Mitigate SIP Attrition: Deploy SMS alerts to resolve the 97.8% 'at-risk' transactions.",
        "2. Diversify Concentration: Rebalance sector exposure for highly concentrated funds (HHI > 2800).",
        "3. Automate Data Loads: Ensure the weekdays 8 PM scheduler remains active to pull live NAVs.",
        "Thank You! Q&A Session."
    ]
    for r in recs:
        p = tf.add_paragraph()
        p.text = r
        p.level = 1
        set_font(p.runs[0], size=Pt(14))
        
    prs.save(str(project_root / "reports" / "Presentation.pptx"))
    print("reports/Presentation.pptx generated successfully!")

def main():
    print("=== Generating PDF and PPTX Reports ===")
    generate_pdf()
    generate_pptx()
    print("Reports successfully generated and placed in reports/ directory.")

if __name__ == '__main__':
    main()
