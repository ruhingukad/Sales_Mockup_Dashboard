"""
MTN Benin - Sales & Distribution Dashboard
Power BI-style layout with filters on left, tabs on top
Official MTN Colors: Yellow (#FFCB05), Black (#000000), White (#FFFFFF)
Modified Overview page with requested changes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import json
import os
from PIL import Image
import geopandas as gpd

# Page configuration - Remove sidebar
st.set_page_config(
    page_title="MTN Benin - Sales & Distribution",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# MTN Official Color Palette
MTN_YELLOW = "#FFCB05"
MTN_BLACK = "#000000"
MTN_DARK_GRAY = "#1A1A1A"
MTN_GRAY = "#4A4A4A"
MTN_LIGHT_GRAY = "#F5F5F5"
MTN_WHITE = "#FFFFFF"

# Custom CSS - Power BI Layout
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Hide Streamlit default header and menu */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide the Streamlit toolbar */
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main app background */
    .stApp {
        background-color: #F5F5F5;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Ensure header columns don't have overflow issues */
    [data-testid="column"] {
        overflow: visible !important;
    }
    
    /* Fix any potential white overlay on header */
    .element-container {
        z-index: 1;
    }
    
    /* Header styling */
    [data-testid="column"] > div > div > div > div {
        padding: 0 !important;
    }
    
    /* Date input container in header */
    div[data-testid="column"]:has(.stDateInput) {
        background: #F8F8F8;
        position: relative;
        z-index: 10;
    }
    
    /* Date input styling in header */
    .stDateInput > div > div > input {
        font-size: 13px;
        padding: 8px 12px;
        border: 1px solid #D0D0D0;
        border-radius: 2px;
        background: white;
        color: #1A1A1A;
        font-weight: 400;
        cursor: pointer;
        position: relative;
        z-index: 100;
    }
    
    /* Date picker calendar */
    .stDateInput > div > div > div[data-baseweb="calendar"] {
        z-index: 9999 !important;
    }
    
    .stDateInput > label {
        display: none;
    }
    
    .stDateInput {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        margin-top: -60px;
        position: relative;
        z-index: 100;
    }
    
    .stDateInput > div {
        padding-bottom: 0 !important;
    }
    
    /* Ensure date input is clickable */
    .stDateInput input {
        pointer-events: auto !important;
    }
    
    /* Left Filter Panel - Power BI Style - FIXED POSITION */
    .filter-panel {
        background: #FFFFFF;
        border-right: 1px solid #E0E0E0;
        padding: 16px;
        min-height: calc(100vh - 80px);
        position: sticky;
        top: 0;
        overflow-y: auto;
    }
    
    .filter-title {
        font-size: 14px;
        font-weight: 700;
        color: #000000;
        margin: 0 0 12px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 3px solid #FFCB05;
        padding-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .filter-section {
        margin-bottom: 24px;
    }
    
    .filter-label {
        font-size: 12px;
        font-weight: 600;
        color: #4A4A4A;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Tab Navigation - Power BI Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #FFFFFF;
        border-bottom: 2px solid #E0E0E0;
        padding: 0;
        margin: 20px 0 16px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 13px;
        color: #4A4A4A;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #FFF9E6;
        color: #000000;
        border-bottom: 3px solid #FFE082;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFCB05;
        color: #000000;
        border-bottom: 3px solid #000000;
        font-weight: 700;
    }
    
    /* KPI Cards - Compact Power BI Style */
    .kpi-card {
        background: #FFFFFF;
        padding: 12px 16px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 3px solid #FFCB05;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .kpi-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    
    .kpi-label {
        font-size: 9px;
        font-weight: 600;
        color: #4A4A4A;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #000000;
        margin: 4px 0;
        line-height: 1;
        white-space: nowrap;
    }
    
    .kpi-delta {
        font-size: 10px;
        font-weight: 600;
        margin-top: 4px;
    }
    
    .delta-positive {
        color: #107C10;
    }
    
    .delta-negative {
        color: #D13438;
    }
    
    .kpi-compact-grid {
        display: flex;
        gap: 6px;
        margin-top: 8px;
        font-size: 8px;
        color: #4A4A4A;
        flex-wrap: wrap;
    }
    
    .kpi-compact-item {
        padding: 3px 6px;
        background: #F9F9F9;
        border-radius: 3px;
        white-space: nowrap;
    }
    
    .kpi-compact-value {
        font-weight: 600;
        color: #000000;
        margin-left: 2px;
    }
    
    /* Chart Container */
    .chart-container {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    
    .chart-title {
        font-size: 13px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #FFCB05;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #FFCB05;
        color: #000000;
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 11px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #E6B800;
        box-shadow: 0 2px 6px rgba(255,203,5,0.3);
    }
    
    /* Select boxes */
    .stSelectbox label {
        font-size: 11px;
        font-weight: 600;
        color: #4A4A4A;
    }
    
    /* DataFrames */
    .dataframe {
        font-size: 11px;
        border: none !important;
    }
    
    .dataframe thead tr th {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 600;
        padding: 10px 8px;
        font-size: 11px;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #F9F9F9;
    }
    
    .dataframe tbody tr:hover {
        background-color: #FFF9E6;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 20px;
        font-weight: 700;
        color: #000000;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F5F5F5;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FFCB05;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #E6B800;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA GENERATION ====================
@st.cache_data
def generate_sample_data():
    """Generate sample data for MTN Benin dashboard"""
    
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    kpi_data = {
        'market_share': 46.10,
        'budget_market_share': 45.80,
        'total_gross_adds': 16240,
        'budget_gross_adds': 17000,
        'net_adds': -6100,
        'budget_net_adds': -5000,
        'returners': 11460,
        'budget_returners': 12000,
        'airtime_sales': 156.5,
        'budget_airtime_sales': 145.0,
        'float_distributed': 245.8,
        'budget_float_distributed': 230.0,
        'total_agents': 4500,
        'active_agents': 3850,
        'momo_conversions': 3120,
        'data_conversions': 4020,
        'churners': 22340
    }
    
    daily_data = pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=7, freq='D'),
        'market_share': np.random.uniform(45.8, 46.3, 7),
        'gross_adds': np.random.randint(2200, 2500, 7),
        'net_adds': np.random.randint(-220000, -180000, 7),
        'returners': np.random.randint(1500, 1700, 7),
        'airtime_sales': np.random.uniform(5.0, 6.5, 7),
        'float': np.random.uniform(7.5, 9.0, 7),
        'dod': np.random.uniform(-5, 10, 7),
        'mom': np.random.uniform(-8, 12, 7)
    })
    
    trend_data = pd.DataFrame({
        'date': dates,
        'airtime_sales': np.random.normal(5.5, 0.5, 90) + np.linspace(0, 1, 90),
        'float': np.random.normal(8.0, 0.8, 90) + np.linspace(0, 1.5, 90),
        'gross_adds': np.random.normal(2300, 150, 90),
        'net_adds': np.random.normal(-6500, 500, 90),
        'returners': np.random.normal(1600, 100, 90),
        'churners': np.random.normal(8900, 300, 90),
        'momo_conv': np.random.normal(100, 15, 90) + np.linspace(0, 20, 90),
        'data_conv': np.random.normal(130, 20, 90) + np.linspace(0, 25, 90)
    })
    
    channel_data = pd.DataFrame({
        'channel': ['YC (Yellow Centers)', 'DTC (MTN Shops)', 'DTR (Dealers)', 'Digital'],
        'ga_count': [7795, 5686, 2113, 646],
        'airtime_sales': [52.1, 54.8, 23.5, 26.1],
        'share_pct': [48, 35, 13, 4]
    })
    
    regional_data = pd.DataFrame({
        'region': ['Littoral', 'Atlantique', 'Borgou', 'Ouémé', 'Mono', 'Zou', 
                   'Collines', 'Couffo', 'Plateau', 'Donga', 'Atacora', 'Alibori'],
        'gross_adds': [8980, 6500, 3200, 1200, 1640, 2800, 900, 680, 590, 750, 480, 520],
        'airtime_sales': [95.8, 68.2, 32.1, 12.2, 18.6, 28.4, 9.5, 6.9, 6.1, 7.8, 5.0, 5.4],
        'agents': [1565, 1200, 650, 320, 420, 580, 250, 150, 130, 180, 95, 110],
        'float': [131.5, 98.5, 52.3, 19.7, 32.1, 45.8, 15.4, 11.2, 9.9, 12.8, 8.1, 8.7]
    })
    
    agent_tiers = pd.DataFrame({
        'tier': ['Gold (Top 10%)', 'Silver (Next 20%)', 'Bronze (Next 30%)', 'Inactive (40%)'],
        'count': [450, 900, 1350, 1800],
        'avg_revenue': [198.2, 89.6, 45.4, 8.3],
        'productivity_score': [95, 78, 62, 25]
    })
    
    hourly_pattern = pd.DataFrame({
        'hour': list(range(24)),
        'airtime_sales': [2.1, 1.8, 1.5, 1.2, 1.1, 1.8, 3.5, 5.2, 6.8, 7.5,
                          8.2, 8.9, 9.2, 8.5, 7.8, 8.1, 8.9, 9.5, 9.8, 8.2, 6.5, 5.1, 3.8, 2.8],
        'transactions': [850, 720, 610, 490, 450, 740, 1420, 2100, 2750, 3050,
                         3340, 3620, 3740, 3450, 3160, 3290, 3610, 3860, 3980, 3330, 2640, 2070, 1540, 1140]
    })
    
    return {
        'kpi_data': kpi_data,
        'daily_data': daily_data,
        'trend_data': trend_data,
        'channel_data': channel_data,
        'regional_data': regional_data,
        'agent_tiers': agent_tiers,
        'hourly_pattern': hourly_pattern
    }

# ==================== KPI CARD COMPONENT - UPDATED ====================
def create_mtn_kpi_card(label, value, unit, vs_budget_pct, comparisons):
    """Create compact MTN-style KPI card with vs Budget instead of vs previous day"""
    
    is_positive = vs_budget_pct >= 0
    delta_class = "delta-positive" if is_positive else "delta-negative"
    arrow = "↑" if is_positive else "↓"
    
    if isinstance(value, (int, float)):
        if abs(value) >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif abs(value) >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        else:
            formatted_value = f"{value:.1f}" if isinstance(value, float) else f"{value:,}"
    else:
        formatted_value = str(value)
    
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{formatted_value}<span style="font-size: 11px; color: #4A4A4A; margin-left: 2px;">{unit}</span></div>
        <div class="kpi-delta {delta_class}">vs Budget: {arrow} {abs(vs_budget_pct):.1f}%</div>
        <div class="kpi-compact-grid">
            <div class="kpi-compact-item">
                <span>YTD:</span>
                <span class="kpi-compact-value">{comparisons.get('ytd', 'N/A')}</span>
            </div>
            <div class="kpi-compact-item">
                <span>WoW:</span>
                <span class="kpi-compact-value">{comparisons.get('wow', 'N/A')}</span>
            </div>
            <div class="kpi-compact-item">
                <span>MoM:</span>
                <span class="kpi-compact-value">{comparisons.get('mom', 'N/A')}</span>
            </div>
        </div>
    </div>
    """
    return html

# ==================== PLOTLY THEME ====================
def get_mtn_plotly_theme():
    """MTN color scheme for Plotly charts"""
    return {
        'layout': {
            'font': {'family': 'Segoe UI', 'size': 11, 'color': MTN_BLACK},
            'plot_bgcolor': MTN_WHITE,
            'paper_bgcolor': MTN_WHITE,
            'colorway': [MTN_YELLOW, MTN_BLACK, MTN_DARK_GRAY, MTN_GRAY],
            'hovermode': 'x unified'
        }
    }

# ==================== PAGE CONTENT FUNCTIONS ====================
def render_overview_content(data):
    """Render Overview page content with requested modifications"""
    
    # KPI Cards - 6 columns with vs Budget comparison
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        vs_budget = ((data['kpi_data']['market_share'] - data['kpi_data']['budget_market_share']) / 
                    data['kpi_data']['budget_market_share']) * 100
        st.markdown(create_mtn_kpi_card(
            "Market Share",
            46.10,
            "%",
            vs_budget,
            {'ytd': '+2.3%', 'wow': '-0.2%', 'mom': '+0.5%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    with col2:
        vs_budget = ((data['kpi_data']['total_gross_adds'] - data['kpi_data']['budget_gross_adds']) / 
                    data['kpi_data']['budget_gross_adds']) * 100
        st.markdown(create_mtn_kpi_card(
            "Gross Adds",
            data['kpi_data']['total_gross_adds'],
            "",
            vs_budget,
            {'ytd': '-3.8%', 'wow': '-0.4%', 'mom': '-2.8%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    with col3:
        vs_budget = ((data['kpi_data']['net_adds'] - data['kpi_data']['budget_net_adds']) / 
                    abs(data['kpi_data']['budget_net_adds'])) * 100
        st.markdown(create_mtn_kpi_card(
            "Net Adds",
            data['kpi_data']['net_adds'],
            "",
            vs_budget,
            {'ytd': '-12.5%', 'wow': '-8.4%', 'mom': '-22.5%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    with col4:
        vs_budget = ((data['kpi_data']['returners'] - data['kpi_data']['budget_returners']) / 
                    data['kpi_data']['budget_returners']) * 100
        st.markdown(create_mtn_kpi_card(
            "Returners",
            data['kpi_data']['returners'],
            "",
            vs_budget,
            {'ytd': '-5.2%', 'wow': '-9.6%', 'mom': '-22.8%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    with col5:
        vs_budget = ((data['kpi_data']['airtime_sales'] - data['kpi_data']['budget_airtime_sales']) / 
                    data['kpi_data']['budget_airtime_sales']) * 100
        st.markdown(create_mtn_kpi_card(
            "Airtime Sales",
            data['kpi_data']['airtime_sales'],
            "M XOF",
            vs_budget,
            {'ytd': '+8.2%', 'wow': '+7.9%', 'mom': '+7.8%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    with col6:
        vs_budget = ((data['kpi_data']['float_distributed'] - data['kpi_data']['budget_float_distributed']) / 
                    data['kpi_data']['budget_float_distributed']) * 100
        st.markdown(create_mtn_kpi_card(
            "Float Distributed",
            data['kpi_data']['float_distributed'],
            "M XOF",
            vs_budget,
            {'ytd': '+6.9%', 'wow': '+7.5%', 'mom': '+6.2%'}  # Changed to percentages
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Charts Row - Modified Left chart with dual KPI selector
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="chart-title">💰 Airtime Sales & Float Distribution Trends</div>', unsafe_allow_html=True)
        
        fig_sales_float = go.Figure()
        
        # Add YoY and MoM annotations
        current_sales = data['trend_data']['airtime_sales'].iloc[-1]
        prev_year_sales = data['trend_data']['airtime_sales'].iloc[0]
        prev_month_sales = data['trend_data']['airtime_sales'].iloc[-30]
        
        yoy_change = ((current_sales - prev_year_sales) / prev_year_sales) * 100
        mom_change = ((current_sales - prev_month_sales) / prev_month_sales) * 100
        
        fig_sales_float.add_trace(go.Scatter(
            x=data['trend_data']['date'],
            y=data['trend_data']['airtime_sales'],
            name='Airtime Sales (M XOF)',
            mode='lines',
            line=dict(color=MTN_YELLOW, width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 203, 5, 0.2)'
        ))
        
        fig_sales_float.add_trace(go.Scatter(
            x=data['trend_data']['date'],
            y=data['trend_data']['float'],
            name='Float Distributed (M XOF)',
            mode='lines',
            line=dict(color=MTN_BLACK, width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 0, 0, 0.1)'
        ))
        
        # Add YoY and MoM annotations
        fig_sales_float.add_annotation(
            text=f"YoY: {yoy_change:+.1f}%<br>MoM: {mom_change:+.1f}%",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#FFCB05",
            borderwidth=2,
            font=dict(size=10, color="#000000")
        )
        
        fig_sales_float.update_layout(
            height=380,
            **get_mtn_plotly_theme()['layout'],
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Value (M XOF)')
        )
        
        st.plotly_chart(fig_sales_float, use_container_width=True, config={'displayModeBar': False})
    
    with col_right:
        st.markdown('<div class="chart-title">📈 Acquisition KPIs</div>', unsafe_allow_html=True)
        
        # KPI Selector for dual view
        kpi_pair = st.selectbox(
            "Select KPI Pair to View",
            ["GA & Returners", "Net Adds & Churners"],
            key="kpi_pair_selector"
        )
        
        fig_acquisition = go.Figure()
        
        if kpi_pair == "GA & Returners":
            # Calculate YoY and MoM for GA
            current_ga = data['trend_data']['gross_adds'].iloc[-1]
            prev_year_ga = data['trend_data']['gross_adds'].iloc[0]
            prev_month_ga = data['trend_data']['gross_adds'].iloc[-30]
            ga_yoy = ((current_ga - prev_year_ga) / prev_year_ga) * 100
            ga_mom = ((current_ga - prev_month_ga) / prev_month_ga) * 100
            
            # Calculate YoY and MoM for Returners
            current_ret = data['trend_data']['returners'].iloc[-1]
            prev_year_ret = data['trend_data']['returners'].iloc[0]
            prev_month_ret = data['trend_data']['returners'].iloc[-30]
            ret_yoy = ((current_ret - prev_year_ret) / prev_year_ret) * 100
            ret_mom = ((current_ret - prev_month_ret) / prev_month_ret) * 100
            
            fig_acquisition.add_trace(go.Scatter(
                x=data['trend_data']['date'],
                y=data['trend_data']['gross_adds'],
                name='Gross Adds',
                mode='lines+markers',
                line=dict(color=MTN_YELLOW, width=3),
                marker=dict(size=4)
            ))
            
            fig_acquisition.add_trace(go.Scatter(
                x=data['trend_data']['date'],
                y=data['trend_data']['returners'],
                name='Returners',
                mode='lines+markers',
                line=dict(color=MTN_BLACK, width=3),
                marker=dict(size=4)
            ))
            
            # Add variations annotation
            fig_acquisition.add_annotation(
                text=f"<b>GA</b><br>YoY: {ga_yoy:+.1f}%<br>MoM: {ga_mom:+.1f}%<br><br><b>Returners</b><br>YoY: {ret_yoy:+.1f}%<br>MoM: {ret_mom:+.1f}%",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#FFCB05",
                borderwidth=2,
                font=dict(size=9, color="#000000"),
                align="left"
            )
            
            y_title = 'Count'
        else:  # Net Adds & Churners
            # Calculate YoY and MoM for Net Adds
            current_na = data['trend_data']['net_adds'].iloc[-1]
            prev_year_na = data['trend_data']['net_adds'].iloc[0]
            prev_month_na = data['trend_data']['net_adds'].iloc[-30]
            na_yoy = ((current_na - prev_year_na) / abs(prev_year_na)) * 100
            na_mom = ((current_na - prev_month_na) / abs(prev_month_na)) * 100
            
            # Calculate YoY and MoM for Churners
            current_ch = data['trend_data']['churners'].iloc[-1]
            prev_year_ch = data['trend_data']['churners'].iloc[0]
            prev_month_ch = data['trend_data']['churners'].iloc[-30]
            ch_yoy = ((current_ch - prev_year_ch) / prev_year_ch) * 100
            ch_mom = ((current_ch - prev_month_ch) / prev_month_ch) * 100
            
            fig_acquisition.add_trace(go.Scatter(
                x=data['trend_data']['date'],
                y=data['trend_data']['net_adds'],
                name='Net Adds',
                mode='lines+markers',
                line=dict(color='#D32F2F', width=3),
                marker=dict(size=4)
            ))
            
            fig_acquisition.add_trace(go.Scatter(
                x=data['trend_data']['date'],
                y=data['trend_data']['churners'],
                name='Churners',
                mode='lines+markers',
                line=dict(color=MTN_GRAY, width=3),
                marker=dict(size=4)
            ))
            
            # Add variations annotation
            fig_acquisition.add_annotation(
                text=f"<b>Net Adds</b><br>YoY: {na_yoy:+.1f}%<br>MoM: {na_mom:+.1f}%<br><br><b>Churners</b><br>YoY: {ch_yoy:+.1f}%<br>MoM: {ch_mom:+.1f}%",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#FFCB05",
                borderwidth=2,
                font=dict(size=9, color="#000000"),
                align="left"
            )
            
            y_title = 'Count'
        
        fig_acquisition.update_layout(
            height=380,
            **get_mtn_plotly_theme()['layout'],
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title=y_title)
        )
        
        st.plotly_chart(fig_acquisition, use_container_width=True, config={'displayModeBar': False})
    
    # Daily Performance Table - Modified to show one KPI at a time with selector
    st.markdown('<div class="chart-title">📋 Daily Performance - Select KPI (Last 7 Days)</div>', unsafe_allow_html=True)
    
    # KPI Selector
    col_kpi_selector, col_empty = st.columns([2, 3])
    with col_kpi_selector:
        selected_kpi = st.selectbox(
            "Select KPI to Display",
            ["Market Share (%)", "Gross Adds", "Net Adds", "Returners", "Airtime Sales (M XOF)", "Float Distributed (M XOF)"],
            index=0,
            key="daily_kpi_selector"
        )
    
    # Map KPI selection to column names and formatting
    kpi_column_map = {
        "Market Share (%)": ('market_share', '{:.2f}', '%'),
        "Gross Adds": ('gross_adds', '{:,.0f}', ''),
        "Net Adds": ('net_adds', '{:,.0f}', ''),
        "Returners": ('returners', '{:,.0f}', ''),
        "Airtime Sales (M XOF)": ('airtime_sales', '{:.2f}', 'M'),
        "Float Distributed (M XOF)": ('float', '{:.2f}', 'M')
    }
    
    selected_col, value_format, suffix = kpi_column_map[selected_kpi]
    
    # Prepare daily data for the selected KPI
    daily_display = data['daily_data'][['date', selected_col, 'dod', 'mom']].copy()
    daily_display['date'] = daily_display['date'].dt.strftime('%d %b')
    
    # Format the selected KPI column
    if suffix:
        if suffix == '%':
            daily_display[selected_col] = daily_display[selected_col].apply(lambda x: f"{x:.2f}")
        else:
            daily_display[selected_col] = daily_display[selected_col].apply(lambda x: f"{x:.2f}{suffix}")
    else:
        daily_display[selected_col] = daily_display[selected_col].apply(lambda x: f"{x:,.0f}")
    
    # Rename columns for display
    daily_display.columns = ['Date', selected_kpi, 'DoD %', 'MoM %']
    
    # Function to color percentage cells based on value
    def color_percentages(val):
        if isinstance(val, (int, float)):
            if val > 5:
                return 'background-color: #90EE90; color: white; font-weight: bold'  # Light green
            elif val > 0:
                return 'background-color: #FFEB3B; color: black; font-weight: bold'  # Yellow
            else:
                return 'background-color: #FFCDD2; color: white; font-weight: bold'  # Light red
        return ''
    
    # Style the dataframe
    styled_df = daily_display.style.format({
        'DoD %': '{:+.1f}',
        'MoM %': '{:+.1f}'
    }).applymap(color_percentages, subset=['DoD %', 'MoM %']).set_properties(**{
        'text-align': 'center',
        'font-size': '11px',
        'border': '1px solid #E0E0E0'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#000000'),
            ('color', '#FFCB05'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('font-size', '11px'),
            ('padding', '8px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '6px')
        ]}
    ])
    
    st.dataframe(styled_df, use_container_width=True, height=350)
    
    # Bottom row - Benin Map with KPIs
    st.markdown('<br><div class="chart-title">🌍 Performance by Region - Interactive Benin Map</div>', unsafe_allow_html=True)
    
    # KPI selector for the map
    col_selector, col_empty = st.columns([2, 3])
    with col_selector:
        kpi_map = st.selectbox(
            "Select KPI to Display on Map",
            ["Gross Adds", "Airtime Sales (M XOF)", "Number of Agents", "Float Distribution (M XOF)"],
            key="map_kpi_selector"
        )
    
    # Map display name to column
    kpi_col_map = {
        "Gross Adds": 'gross_adds',
        "Airtime Sales (M XOF)": 'airtime_sales',
        "Number of Agents": 'agents',
        "Float Distribution (M XOF)": 'float'
    }
    kpi_col = kpi_col_map[kpi_map]
    
    # Try to load and display map, fallback to bar chart if not available
    geojson_path = 'gadm41_BEN_1.json'
    
    try:
        # Check if we can use geopandas for better map handling
        use_geopandas = False
        try:
            import geopandas as gpd
            use_geopandas = True
        except ImportError:
            pass
        
        if os.path.exists(geojson_path):
            if use_geopandas:
                # Use geopandas for better handling
                benin_gdf = gpd.read_file(geojson_path)
                
                # Find the department name column
                name_column = None
                for col in ['NAME_1', 'ADM1_NAME', 'name', 'Name', 'ADM1_EN']:
                    if col in benin_gdf.columns:
                        name_column = col
                        break
                
                if name_column:
                    # Map KPIs to departments
                    kpi_dict = {}
                    for _, row in data['regional_data'].iterrows():
                        kpi_dict[row['region']] = row[kpi_col]
                    
                    benin_gdf['kpi_value'] = benin_gdf[name_column].map(kpi_dict)
                    benin_gdf['department'] = benin_gdf[name_column]
                    
                    # Create choropleth using the geometry
                    fig_map = px.choropleth(
                        benin_gdf,
                        geojson=benin_gdf.geometry,
                        locations=benin_gdf.index,
                        color='kpi_value',
                        hover_name='department',
                        hover_data={'kpi_value': ':,.0f'},
                        color_continuous_scale='YlOrRd',
                        labels={'kpi_value': kpi_map}
                    )
            else:
                # Use regular JSON loading
                with open(geojson_path) as f:
                    benin_geo = json.load(f)
                
                # Prepare DataFrame
                map_df = data['regional_data'][['region', kpi_col]].copy()
                map_df = map_df.rename(columns={'region': 'department', kpi_col: 'kpi_value'})
                
                # Create choropleth
                fig_map = px.choropleth(
                    map_df,
                    geojson=benin_geo,
                    locations='department',
                    featureidkey='properties.NAME_1',
                    color='kpi_value',
                    hover_name='department',
                    hover_data={'kpi_value': ':,.0f'},
                    color_continuous_scale='YlOrRd',
                    labels={'kpi_value': kpi_map}
                )
            
            # Update layout for better visualization
            fig_map.update_geos(
                fitbounds='locations',
                visible=False,
                projection_type='mercator'
            )
            
            fig_map.update_layout(
                height=550,
                margin={'l': 10, 'r': 10, 't': 10, 'b': 50},
                coloraxis_colorbar=dict(
                    title=kpi_map,
                    orientation='h',
                    y=-0.12,
                    x=0.5,
                    xanchor='center',
                    thickness=15,
                    len=0.6,
                    tickfont=dict(size=10)
                ),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family='Segoe UI', size=11)
            )
            
            st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
            
            # Add KPI statistics below map
            st.markdown("<br>", unsafe_allow_html=True)
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                top_region = data['regional_data'].nlargest(1, kpi_col)['region'].values[0]
                top_value = data['regional_data'].nlargest(1, kpi_col)[kpi_col].values[0]
                st.metric("🏆 Top Region", top_region, f"{top_value:,.0f} {kpi_map.split('(')[0]}")
            
            with col_stat2:
                avg_value = data['regional_data'][kpi_col].mean()
                st.metric("📊 Average", f"{avg_value:,.0f}", f"Across 12 regions")
            
            with col_stat3:
                total_value = data['regional_data'][kpi_col].sum()
                st.metric("📈 Total", f"{total_value:,.0f}", "National total")
            
            with col_stat4:
                bottom_region = data['regional_data'].nsmallest(1, kpi_col)['region'].values[0]
                bottom_value = data['regional_data'].nsmallest(1, kpi_col)[kpi_col].values[0]
                st.metric("📉 Lowest Region", bottom_region, f"{bottom_value:,.0f}")
        
        else:
            raise FileNotFoundError("GeoJSON file not found")
            
    except Exception as e:
        # Fallback: Display horizontal bar chart
        st.info("📍 Map visualization requires 'gadm41_BEN_1.json' file. Displaying bar chart instead.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart as fallback
            fig_regional = px.bar(
                data['regional_data'].sort_values(kpi_col, ascending=True),
                y='region',
                x=kpi_col,
                orientation='h',
                color=kpi_col,
                color_continuous_scale='YlOrRd',
                text=kpi_col,
                title=f'{kpi_map} by Region'
            )
            
            fig_regional.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside'
            )
            
            fig_regional.update_layout(
                height=400,
                **get_mtn_plotly_theme()['layout'],
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=100, r=40, t=40, b=40),
                xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title=kpi_map),
                yaxis=dict(showgrid=False, title='')
            )
            
            st.plotly_chart(fig_regional, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # Channel Mix pie chart
            st.markdown('<div class="chart-title">📊 Channel Mix (GA Share)</div>', unsafe_allow_html=True)
            
            fig_channel = go.Figure(data=[go.Pie(
                labels=data['channel_data']['channel'],
                values=data['channel_data']['share_pct'],
                hole=0.5,
                marker=dict(colors=[MTN_YELLOW, MTN_BLACK, MTN_DARK_GRAY, MTN_GRAY]),
                textfont=dict(size=10, color=MTN_WHITE),
                textinfo='label+percent'
            )])
            
            fig_channel.update_layout(
                height=320,
                **get_mtn_plotly_theme()['layout'],
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig_channel, use_container_width=True, config={'displayModeBar': False})

def render_airtime_sales_content(data):
    """Render Airtime Sales page content - Enhanced with channel breakdown"""
    
    # Top KPI Cards Row - All Channels
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.markdown(create_mtn_kpi_card(
            "Total Sales",
            156.5,
            "M XOF",
            8.5,
            {'ytd': '5.12B', 'wow': '+12.3M', 'mom': '+7.8%'}
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_mtn_kpi_card(
            "Total Volume",
            78540,
            "",
            5.2,
            {'ytd': '2.45M', 'wow': '+2.45K', 'mom': '+4.8%'}
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_mtn_kpi_card(
            "MoMo",
            45.2,
            "M XOF",
            9.1,
            {'ytd': '1.48B', 'wow': '+4.1M', 'mom': '+8.5%'}
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_mtn_kpi_card(
            "EVD",
            38.6,
            "M XOF",
            7.8,
            {'ytd': '1.26B', 'wow': '+3.0M', 'mom': '+7.2%'}
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(create_mtn_kpi_card(
            "DTC",
            32.4,
            "M XOF",
            6.5,
            {'ytd': '1.06B', 'wow': '+2.1M', 'mom': '+6.0%'}
        ), unsafe_allow_html=True)
    
    with col6:
        st.markdown(create_mtn_kpi_card(
            "DTR",
            28.1,
            "M XOF",
            10.2,
            {'ytd': '918M', 'wow': '+2.6M', 'mom': '+9.5%'}
        ), unsafe_allow_html=True)
    
    with col7:
        st.markdown(create_mtn_kpi_card(
            "Xtratime",
            12.2,
            "M XOF",
            12.5,
            {'ytd': '398M', 'wow': '+1.4M', 'mom': '+11.8%'}
        ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Chart Section - Time Series (60%) and Channel Distribution (40%)
    col_chart_left, col_chart_right = st.columns([3, 2])
    
    with col_chart_left:
        st.markdown('<div class="chart-title">📊 Airtime Sales & Transactions Trend</div>', unsafe_allow_html=True)
        
        # Channel selector
        selected_channel = st.selectbox(
            "Select Channel to View",
            ["Total (All Channels)", "MoMo", "EVD", "DTC", "DTR", "Xtratime"],
            key="airtime_channel_selector"
        )
        
        # Generate trend data for all channels
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        
        channel_data_map = {
            "Total (All Channels)": {
                'sales': np.random.uniform(5.0, 6.5, 90) + np.linspace(0, 1, 90),
                'transactions': np.random.randint(2500, 3200, 90),
                'color': MTN_YELLOW
            },
            "MoMo": {
                'sales': np.random.uniform(1.3, 1.8, 90) + np.linspace(0, 0.3, 90),
                'transactions': np.random.randint(800, 1100, 90),
                'color': '#9C27B0'
            },
            "EVD": {
                'sales': np.random.uniform(1.1, 1.5, 90) + np.linspace(0, 0.25, 90),
                'transactions': np.random.randint(700, 950, 90),
                'color': '#2196F3'
            },
            "DTC": {
                'sales': np.random.uniform(0.9, 1.3, 90) + np.linspace(0, 0.2, 90),
                'transactions': np.random.randint(600, 850, 90),
                'color': '#4CAF50'
            },
            "DTR": {
                'sales': np.random.uniform(0.8, 1.1, 90) + np.linspace(0, 0.15, 90),
                'transactions': np.random.randint(500, 750, 90),
                'color': '#FF9800'
            },
            "Xtratime": {
                'sales': np.random.uniform(0.3, 0.5, 90) + np.linspace(0, 0.1, 90),
                'transactions': np.random.randint(200, 400, 90),
                'color': '#E91E63'
            }
        }
        
        channel_config = channel_data_map[selected_channel]
        
        # Create dual-axis chart
        fig_airtime = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Sales line with area fill
        fig_airtime.add_trace(
            go.Scatter(
                x=dates,
                y=channel_config['sales'],
                name="Sales (M XOF)",
                mode='lines+markers',
                line=dict(color=channel_config['color'], width=3),
                marker=dict(size=4),
                fill='tozeroy',
                fillcolor=f'rgba({int(channel_config["color"][1:3], 16)}, {int(channel_config["color"][3:5], 16)}, {int(channel_config["color"][5:7], 16)}, 0.2)'
            ),
            secondary_y=False
        )
        
        # Transactions line
        fig_airtime.add_trace(
            go.Scatter(
                x=dates,
                y=channel_config['transactions'],
                name="Transactions",
                mode='lines+markers',
                line=dict(color=MTN_BLACK, width=2, dash='dot'),
                marker=dict(size=3)
            ),
            secondary_y=True
        )
        
        fig_airtime.update_layout(
            height=450,
            plot_bgcolor=MTN_WHITE,
            paper_bgcolor=MTN_WHITE,
            font=dict(family='Segoe UI', size=11, color=MTN_BLACK),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='x unified'
        )
        
        fig_airtime.update_xaxes(showgrid=True, gridcolor='#F0F0F0', title='Date')
        fig_airtime.update_yaxes(showgrid=True, gridcolor='#F0F0F0', title='Sales (M XOF)', secondary_y=False)
        fig_airtime.update_yaxes(showgrid=False, title='Transactions', secondary_y=True)
        
        st.plotly_chart(fig_airtime, use_container_width=True, config={'displayModeBar': False})
    
    with col_chart_right:
        st.markdown('<div class="chart-title">🗺️ Airtime Sales by Region</div>', unsafe_allow_html=True)
        
        # KPI selector for the map
        airtime_map_kpi = st.selectbox(
            "Select Airtime KPI",
            ["Total Sales", "MoMo Sales", "EVD Sales", "DTC Sales", "DTR Sales", "Xtratime Sales"],
            index=0,
            key="airtime_map_kpi_selector",
            label_visibility="visible"
        )
        
        # Generate regional airtime data
        regions = ['Alibori', 'Atacora', 'Atlantique', 'Borgou', 'Collines', 'Couffo', 
                   'Donga', 'Littoral', 'Mono', 'Oueme', 'Plateau', 'Zou']
        
        regional_airtime = pd.DataFrame({
            'region': regions,
            'Total Sales': np.random.uniform(3.5, 8.5, 12),
            'MoMo Sales': np.random.uniform(1.2, 3.0, 12),
            'EVD Sales': np.random.uniform(1.0, 2.5, 12),
            'DTC Sales': np.random.uniform(0.8, 2.0, 12),
            'DTR Sales': np.random.uniform(0.6, 1.5, 12),
            'Xtratime Sales': np.random.uniform(0.2, 0.8, 12)
        })
        
        # Map selection to data column
        kpi_column_map = {
            "Total Sales": 'Total Sales',
            "MoMo Sales": 'MoMo Sales',
            "EVD Sales": 'EVD Sales',
            "DTC Sales": 'DTC Sales',
            "DTR Sales": 'DTR Sales',
            "Xtratime Sales": 'Xtratime Sales'
        }
        
        selected_col = kpi_column_map[airtime_map_kpi]
        
        # Try to load and display map
        geojson_path = 'gadm41_BEN_1.json'
        
        try:
            use_geopandas = False
            try:
                import geopandas as gpd
                use_geopandas = True
            except ImportError:
                pass
            
            if os.path.exists(geojson_path):
                if use_geopandas:
                    benin_gdf = gpd.read_file(geojson_path)
                    
                    # Find the department name column
                    name_column = None
                    for col in ['NAME_1', 'ADM1_NAME', 'name', 'Name', 'ADM1_EN']:
                        if col in benin_gdf.columns:
                            name_column = col
                            break
                    
                    if name_column:
                        # Map airtime data to departments
                        airtime_dict = dict(zip(regional_airtime['region'], regional_airtime[selected_col]))
                        benin_gdf['kpi_value'] = benin_gdf[name_column].map(airtime_dict)
                        benin_gdf['department'] = benin_gdf[name_column]
                        
                        # Create choropleth
                        fig_map = px.choropleth(
                            benin_gdf,
                            geojson=benin_gdf.geometry,
                            locations=benin_gdf.index,
                            color='kpi_value',
                            hover_name='department',
                            hover_data={'kpi_value': ':.2f'},
                            color_continuous_scale='YlOrRd',
                            labels={'kpi_value': airtime_map_kpi}
                        )
                else:
                    # Use regular JSON loading
                    with open(geojson_path) as f:
                        benin_geo = json.load(f)
                    
                    map_df = regional_airtime[['region', selected_col]].copy()
                    map_df = map_df.rename(columns={'region': 'department', selected_col: 'kpi_value'})
                    
                    fig_map = px.choropleth(
                        map_df,
                        geojson=benin_geo,
                        locations='department',
                        featureidkey='properties.NAME_1',
                        color='kpi_value',
                        hover_name='department',
                        hover_data={'kpi_value': ':.2f'},
                        color_continuous_scale='YlOrRd',
                        labels={'kpi_value': airtime_map_kpi}
                    )
                
                # Update layout
                fig_map.update_geos(
                    fitbounds='locations',
                    visible=False,
                    projection_type='mercator'
                )
                
                fig_map.update_layout(
                    height=450,
                    margin={'l': 10, 'r': 10, 't': 10, 'b': 40},
                    coloraxis_colorbar=dict(
                        title=airtime_map_kpi + "<br>(M XOF)",
                        orientation='h',
                        y=-0.15,
                        x=0.5,
                        xanchor='center',
                        thickness=12,
                        len=0.7,
                        tickfont=dict(size=9)
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(family='Segoe UI', size=10)
                )
                
                st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
                
                # Add quick stats below map - display sequentially to avoid nested columns
                st.markdown("<br>", unsafe_allow_html=True)
                
                top_region = regional_airtime.nlargest(1, selected_col)['region'].values[0]
                top_value = regional_airtime.nlargest(1, selected_col)[selected_col].values[0]
                avg_value = regional_airtime[selected_col].mean()
                total_value = regional_airtime[selected_col].sum()
                
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                        <div style="font-size: 10px; color: #666; margin-bottom: 4px;">🏆 Top Region</div>
                        <div style="font-size: 14px; font-weight: 600; color: #000;">{top_region}</div>
                        <div style="font-size: 12px; color: #4CAF50; font-weight: 600;">{top_value:.2f}M</div>
                    </div>
                    <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                        <div style="font-size: 10px; color: #666; margin-bottom: 4px;">📊 Average</div>
                        <div style="font-size: 14px; font-weight: 600; color: #000;">{avg_value:.2f}M</div>
                        <div style="font-size: 11px; color: #666;">Across regions</div>
                    </div>
                    <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                        <div style="font-size: 10px; color: #666; margin-bottom: 4px;">📈 Total</div>
                        <div style="font-size: 14px; font-weight: 600; color: #000;">{total_value:.2f}M</div>
                        <div style="font-size: 11px; color: #666;">National</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                raise FileNotFoundError("GeoJSON file not found")
                
        except Exception as e:
            # Fallback: Display simple message without chart
            st.warning("📍 Map visualization requires 'gadm41_BEN_1.json' file to display regional data.")
            
            # Show only the quick stats using HTML to avoid nested columns
            st.markdown("<br>", unsafe_allow_html=True)
            
            top_region = regional_airtime.nlargest(1, selected_col)['region'].values[0]
            top_value = regional_airtime.nlargest(1, selected_col)[selected_col].values[0]
            avg_value = regional_airtime[selected_col].mean()
            total_value = regional_airtime[selected_col].sum()
            
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 10px; color: #666; margin-bottom: 4px;">🏆 Top Region</div>
                    <div style="font-size: 14px; font-weight: 600; color: #000;">{top_region}</div>
                    <div style="font-size: 12px; color: #4CAF50; font-weight: 600;">{top_value:.2f}M</div>
                </div>
                <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 10px; color: #666; margin-bottom: 4px;">📊 Average</div>
                    <div style="font-size: 14px; font-weight: 600; color: #000;">{avg_value:.2f}M</div>
                    <div style="font-size: 11px; color: #666;">Across regions</div>
                </div>
                <div style="flex: 1; background: #F8F8F8; padding: 10px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 10px; color: #666; margin-bottom: 4px;">📈 Total</div>
                    <div style="font-size: 14px; font-weight: 600; color: #000;">{total_value:.2f}M</div>
                    <div style="font-size: 11px; color: #666;">National</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Daily Performance Table - Last 7 Days with All Channels
    st.markdown('<br><div class="chart-title">📋 Daily Performance - Select KPI (Last 7 Days)</div>', unsafe_allow_html=True)
    
    # KPI Selector
    col_kpi_selector, col_empty = st.columns([2, 3])
    with col_kpi_selector:
        selected_airtime_kpi = st.selectbox(
            "Select KPI to Display",
            ["Total Sales", "Total Volume", "MoMo", "EVD", "DTC", "DTR", "Xtratime"],
            index=0,
            key="airtime_daily_kpi_selector"
        )
    
    # Generate daily performance data
    last_7_days = pd.date_range(end=datetime.now(), periods=7, freq='D')
    
    # Map KPI selection to data generation and formatting
    kpi_data_map = {
        "Total Sales": {
            'values': np.random.uniform(5.0, 6.5, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        },
        "Total Volume": {
            'values': np.random.randint(2500, 3200, 7),
            'format': lambda x: f"{x:,.0f}",
            'suffix': ''
        },
        "MoMo": {
            'values': np.random.uniform(1.3, 1.8, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        },
        "EVD": {
            'values': np.random.uniform(1.1, 1.5, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        },
        "DTC": {
            'values': np.random.uniform(0.9, 1.3, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        },
        "DTR": {
            'values': np.random.uniform(0.8, 1.1, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        },
        "Xtratime": {
            'values': np.random.uniform(0.3, 0.5, 7),
            'format': lambda x: f"{x:.2f}M",
            'suffix': 'M XOF'
        }
    }
    
    kpi_config = kpi_data_map[selected_airtime_kpi]
    kpi_values = kpi_config['values']
    
    # Create daily performance DataFrame for selected KPI
    daily_performance = pd.DataFrame({
        'Date': last_7_days.strftime('%d %b'),
        selected_airtime_kpi: kpi_values,
        'DoD %': np.random.uniform(-5, 10, 7),
        'MoM %': np.random.uniform(-8, 12, 7),
    })
    
    # Format display DataFrame
    display_df = daily_performance.copy()
    
    # Format the KPI values
    display_df[selected_airtime_kpi] = display_df[selected_airtime_kpi].apply(kpi_config['format'])
    
    # Format the variance columns with +/- signs
    for col in ['DoD %', 'MoM %']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%")
    
    # Color function for variance columns (matching CBU dashboard)
    def get_color_for_percentage(value):
        """Return color based on percentage value"""
        if value >= 5:
            return '#107C10'  # Green
        elif value >= 2:
            return '#FFA500'  # Orange
        elif value >= -2:
            return '#FFD700'  # Yellow
        else:
            return '#D13438'  # Red
    
    def color_variance(val):
        """Apply color to variance cells"""
        if pd.isna(val) or val == '-':
            return ''
        try:
            # Extract numeric value from formatted string
            num_val = float(val.replace('%', '').replace('+', ''))
            color = get_color_for_percentage(num_val)
            return f'background-color: {color}; color: white; font-weight: bold; padding: 4px;'
        except:
            return ''
    
    # Apply styling only to variance columns
    styled_df = display_df.style.applymap(
        color_variance,
        subset=['DoD %', 'MoM %']
    ).set_properties(**{
        'text-align': 'center',
        'font-size': '11px',
        'border': '1px solid #E0E0E0'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#000000'),
            ('color', '#FFCB05'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('font-size', '10px'),
            ('padding', '8px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '6px')
        ]}
    ])
    
    st.dataframe(styled_df, use_container_width=True, height=350)


def render_float_management_content(data):
    """Render Float Management page content"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Float", f"{data['kpi_data']['float_distributed']:.1f}M XOF", "+7.5%")
    with col2:
        st.metric("Float - Agents", "145.8M XOF", "+6.2%")
    with col3:
        st.metric("Utilization Rate", "83.5%", "+3.2%")
    with col4:
        st.metric("Turnover", "4.7 Days", "-0.5")
    
    st.markdown('<div class="chart-title">📈 Float Distribution Trend</div>', unsafe_allow_html=True)
    
    fig_float = go.Figure()
    
    categories = ['Agents', 'Dealers', 'Retailers', 'Direct']
    colors = [MTN_YELLOW, MTN_BLACK, MTN_DARK_GRAY, MTN_GRAY]
    
    for i, category in enumerate(categories):
        fig_float.add_trace(go.Scatter(
            x=data['trend_data']['date'][-30:],
            y=np.random.uniform(2, 8, 30) * (4 - i),
            name=category,
            mode='lines',
            stackgroup='one',
            fillcolor=colors[i],
            line=dict(color=colors[i], width=0)
        ))
    
    fig_float.update_layout(
        height=380,
        **get_mtn_plotly_theme()['layout'],
        margin=dict(l=40, r=40, t=20, b=40)
    )
    
    st.plotly_chart(fig_float, use_container_width=True, config={'displayModeBar': False})

def render_agent_network_content(data):
    """Render Agent Network page content"""
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Agents", f"{data['kpi_data']['total_agents']:,}", "+125")
    with col2:
        st.metric("New Agents", "125", "+15")
    with col3:
        st.metric("Churn", "85", "-12")
    with col4:
        st.metric("Net Growth", "40", "+3")
    with col5:
        st.metric("Activation Rate", "87.2%", "+2.1%")
    with col6:
        st.metric("Per 1K Pop", "3.8", "+0.2")
    
    st.markdown('<div class="chart-title">🗺️ Agent Distribution</div>', unsafe_allow_html=True)
    
    # Simple bar chart for agent distribution instead of complex map
    fig_agents = px.bar(
        data['regional_data'].sort_values('agents', ascending=True),
        y='region',
        x='agents',
        orientation='h',
        color='agents',
        color_continuous_scale=[[0, '#D32F2F'], [0.5, '#FFEB3B'], [1, '#4CAF50']],
        text='agents'
    )
    
    fig_agents.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_agents.update_layout(
        height=500,
        **get_mtn_plotly_theme()['layout'],
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=100, r=40, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Number of Agents'),
        yaxis=dict(showgrid=False, title='')
    )
    
    st.plotly_chart(fig_agents, use_container_width=True, config={'displayModeBar': False})

def render_agent_performance_content(data):
    """Render Agent Performance page content"""
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Active", "3,850", "85.6%")
    with col2:
        st.metric("Selling Airtime", "92.3%", "+1.8%")
    with col3:
        st.metric("Registering SIMs", "78.5%", "+2.3%")
    with col4:
        st.metric("Multi-Service", "65.2%", "+4.1%")
    with col5:
        st.metric("Avg Revenue", "40.6K XOF", "+3.2K")
    with col6:
        st.metric("Productivity", "74.5", "+2.3")
    
    st.markdown('<div class="chart-title">🏆 Agent Performance by Tier</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_revenue = go.Figure(data=[go.Bar(
            y=data['agent_tiers']['tier'],
            x=data['agent_tiers']['avg_revenue'],
            orientation='h',
            marker=dict(color=[MTN_BLACK, MTN_YELLOW, MTN_DARK_GRAY, MTN_GRAY])
        )])
        
        fig_revenue.update_layout(
            height=320,
            **get_mtn_plotly_theme()['layout'],
            margin=dict(l=40, r=40, t=20, b=40)
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig_productivity = go.Figure(data=[go.Bar(
            y=data['agent_tiers']['tier'],
            x=data['agent_tiers']['productivity_score'],
            orientation='h',
            marker=dict(
                color=data['agent_tiers']['productivity_score'],
                colorscale=[[0, MTN_GRAY], [0.5, MTN_YELLOW], [1, MTN_BLACK]],
                showscale=False
            )
        )])
        
        fig_productivity.update_layout(
            height=320,
            **get_mtn_plotly_theme()['layout'],
            margin=dict(l=40, r=40, t=20, b=40)
        )
        
        st.plotly_chart(fig_productivity, use_container_width=True, config={'displayModeBar': False})

def render_acquisition_content(data):
    """Render Acquisition page content"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("New Additions", "25.15K", "+2.1%")
    with col2:
        st.metric("Net Addition", "10.55K", "-44.52%")
    with col3:
        st.metric("Churn", "36.55K", "-5.94%")
    with col4:
        st.metric("Net Churn", "19.15K", "-31.9%")
    
    st.markdown('<div class="chart-title">📈 Acquisition Trends</div>', unsafe_allow_html=True)
    
    # Simple line chart
    fig_acq = go.Figure()
    
    fig_acq.add_trace(go.Scatter(
        x=data['trend_data']['date'][-30:],
        y=np.random.uniform(20000, 30000, 30),
        name='New Additions',
        mode='lines+markers',
        line=dict(color=MTN_YELLOW, width=3)
    ))
    
    fig_acq.add_trace(go.Scatter(
        x=data['trend_data']['date'][-30:],
        y=np.random.uniform(30000, 45000, 30),
        name='Churn',
        mode='lines+markers',
        line=dict(color='#D32F2F', width=3)
    ))
    
    fig_acq.update_layout(
        height=400,
        **get_mtn_plotly_theme()['layout'],
        margin=dict(l=40, r=40, t=20, b=40)
    )
    
    st.plotly_chart(fig_acq, use_container_width=True, config={'displayModeBar': False})

def render_acquisition_content(data):
    """Render Acquisition page content - Enhanced with Power BI inspiration"""
    
    # Top KPI Cards Row - Using standard MTN card format
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_mtn_kpi_card(
            "New Additions",
            25150,
            "",
            7.5,
            {'ytd': '670.5K', 'wow': '+2.1%', 'mom': '+5.8%'}
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_mtn_kpi_card(
            "Net Adds",
            10550,
            "",
            5.5,
            {'ytd': '286.2K', 'wow': '+3.2%', 'mom': '+4.1%'}
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_mtn_kpi_card(
            "Churn",
            36550,
            "",
            -3.8,
            {'ytd': '2.08M', 'wow': '-2.4%', 'mom': '-3.8%'}
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_mtn_kpi_card(
            "Net Churn",
            19150,
            "",
            -4.2,
            {'ytd': '1.15M', 'wow': '-3.1%', 'mom': '-4.2%'}
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(create_mtn_kpi_card(
            "Reconnection",
            17400,
            "",
            16.0,
            {'ytd': '929.9K', 'wow': '+12.5%', 'mom': '+16.0%'}
        ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Content Row - Three Columns: Trend Chart, Market Share, Share of Gross Adds
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # KPI selector with title
        st.markdown('<div class="chart-title">📈 Monthly Trend - Acquisition & Drivers</div>', unsafe_allow_html=True)
        
        selected_kpi = st.selectbox(
            "Select KPI to view",
            ["New Addition", "Churn", "Net Adds", "Reconnection", "MPOS Active Agent"],
            key="acq_kpi_selector"
        )
        
        # Generate data for all KPIs
        months = pd.date_range(end=datetime.now(), periods=60, freq='D')
        
        kpi_data_map = {
            "New Addition": {
                'values': np.random.uniform(20000, 30000, 60),
                'color': '#FFCB05',
                'fill_color': 'rgba(255, 203, 5, 0.2)',
                'y_title': 'New Addition Count'
            },
            "Churn": {
                'values': np.random.uniform(30000, 45000, 60),
                'color': '#D32F2F',
                'fill_color': 'rgba(211, 47, 47, 0.15)',
                'y_title': 'Churn Count'
            },
            "Net Adds": {
                'values': np.random.uniform(-8000, 5000, 60),
                'color': '#0288D1',
                'fill_color': 'rgba(2, 136, 209, 0.15)',
                'y_title': 'Net Adds Count'
            },
            "Reconnection": {
                'values': np.random.uniform(15000, 20000, 60),
                'color': '#00897B',
                'fill_color': 'rgba(0, 137, 123, 0.15)',
                'y_title': 'Reconnection Count'
            },
            "MPOS Active Agent": {
                'values': np.random.uniform(800000, 950000, 60),
                'color': '#7B1FA2',
                'fill_color': 'rgba(123, 31, 162, 0.15)',
                'y_title': 'MPOS Active Agent Count'
            }
        }
        
        # Get selected KPI data
        kpi_config = kpi_data_map[selected_kpi]
        
        # Create single KPI trend chart
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=months,
            y=kpi_config['values'],
            name=selected_kpi,
            mode='lines+markers',
            line=dict(color=kpi_config['color'], width=4, shape='spline'),
            marker=dict(size=6, color=kpi_config['color'], line=dict(width=2, color='#FFF')),
            fill='tozeroy',
            fillcolor=kpi_config['fill_color'],
            hovertemplate=f'<b>{selected_kpi}</b><br>%{{y:,.0f}}<extra></extra>'
        ))
        
        fig_trend.update_layout(
            height=400,
            plot_bgcolor='rgba(248, 249, 250, 0.8)',
            paper_bgcolor='white',
            font=dict(color='#1A1A1A', size=11, family='Segoe UI'),
            margin=dict(l=60, r=40, t=30, b=50),
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(224, 224, 224, 0.5)',
                gridwidth=1,
                zeroline=False,
                title=dict(text='Date', font=dict(size=11, color='#4A4A4A')),
                tickfont=dict(size=10, color='#4A4A4A'),
                showline=True,
                linewidth=1,
                linecolor='#E0E0E0'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(224, 224, 224, 0.5)',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='#BDBDBD',
                zerolinewidth=2,
                title=dict(text=kpi_config['y_title'], font=dict(size=11, color='#4A4A4A')),
                tickfont=dict(size=10, color='#4A4A4A'),
                showline=True,
                linewidth=1,
                linecolor='#E0E0E0'
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=11,
                font_family="Segoe UI",
                bordercolor=kpi_config['color']
            ),
            # Add subtle gradient background
            shapes=[
                dict(
                    type='rect',
                    xref='paper',
                    yref='paper',
                    x0=0,
                    y0=0,
                    x1=1,
                    y1=1,
                    fillcolor='rgba(255, 203, 5, 0.03)',
                    layer='below',
                    line_width=0
                )
            ]
        )
        
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # Market Share Donut
        st.markdown('<div class="chart-title">📊 Market Share</div>', unsafe_allow_html=True)
        
        fig_market = go.Figure(data=[go.Pie(
            labels=['MTN', 'Moov', 'Others'],
            values=[43.83, 32.67, 23.50],
            hole=0.6,
            marker=dict(colors=[MTN_YELLOW, '#FF6B35', MTN_GRAY]),
            textinfo='label+percent',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>'
        )])
        
        fig_market.update_layout(
            height=400,
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(orientation="v", x=0, y=0, font=dict(size=9)),
            annotations=[dict(
                text='Latest Data:<br>10/7/2025',
                x=0.5, y=0.5,
                font_size=9,
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_market, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        # Regional Acquisition Map
        st.markdown('<div class="chart-title">🗺️ Acquisition by Region</div>', unsafe_allow_html=True)
        
        # KPI selector for the map
        acq_map_kpi = st.selectbox(
            "Select Acquisition KPI",
            ["New Additions", "Net Adds", "Churn", "Net Churn"],
            index=0,
            key="acq_map_kpi_selector"
        )
        
        # Generate regional acquisition data
        regions = ['Alibori', 'Atacora', 'Atlantique', 'Borgou', 'Collines', 'Couffo', 
                   'Donga', 'Littoral', 'Mono', 'Oueme', 'Plateau', 'Zou']
        
        regional_acq = pd.DataFrame({
            'region': regions,
            'New Additions': np.random.uniform(1500, 4500, 12),
            'Net Adds': np.random.uniform(-500, 2000, 12),
            'Churn': np.random.uniform(2000, 5000, 12),
            'Net Churn': np.random.uniform(800, 3000, 12)
        })
        
        # Map selection to data column
        acq_kpi_map = {
            "New Additions": 'New Additions',
            "Net Adds": 'Net Adds',
            "Churn": 'Churn',
            "Net Churn": 'Net Churn'
        }
        
        selected_acq_col = acq_kpi_map[acq_map_kpi]
        
        # Try to load and display map
        geojson_path = 'gadm41_BEN_1.json'
        
        try:
            use_geopandas = False
            try:
                import geopandas as gpd
                use_geopandas = True
            except ImportError:
                pass
            
            if os.path.exists(geojson_path):
                if use_geopandas:
                    benin_gdf = gpd.read_file(geojson_path)
                    
                    # Find the department name column
                    name_column = None
                    for col in ['NAME_1', 'ADM1_NAME', 'name', 'Name', 'ADM1_EN']:
                        if col in benin_gdf.columns:
                            name_column = col
                            break
                    
                    if name_column:
                        # Map acquisition data to departments
                        acq_dict = dict(zip(regional_acq['region'], regional_acq[selected_acq_col]))
                        benin_gdf['kpi_value'] = benin_gdf[name_column].map(acq_dict)
                        benin_gdf['department'] = benin_gdf[name_column]
                        
                        # Create choropleth
                        fig_map = px.choropleth(
                            benin_gdf,
                            geojson=benin_gdf.geometry,
                            locations=benin_gdf.index,
                            color='kpi_value',
                            hover_name='department',
                            hover_data={'kpi_value': ':.0f'},
                            color_continuous_scale='YlOrRd',
                            labels={'kpi_value': acq_map_kpi}
                        )
                else:
                    # Use regular JSON loading
                    with open(geojson_path) as f:
                        benin_geo = json.load(f)
                    
                    map_df = regional_acq[['region', selected_acq_col]].copy()
                    map_df = map_df.rename(columns={'region': 'department', selected_acq_col: 'kpi_value'})
                    
                    fig_map = px.choropleth(
                        map_df,
                        geojson=benin_geo,
                        locations='department',
                        featureidkey='properties.NAME_1',
                        color='kpi_value',
                        hover_name='department',
                        hover_data={'kpi_value': ':.0f'},
                        color_continuous_scale='YlOrRd',
                        labels={'kpi_value': acq_map_kpi}
                    )
                
                # Update layout
                fig_map.update_geos(
                    fitbounds='locations',
                    visible=False,
                    projection_type='mercator'
                )
                
                fig_map.update_layout(
                    height=400,
                    margin={'l': 5, 'r': 5, 't': 5, 'b': 30},
                    coloraxis_colorbar=dict(
                        title=acq_map_kpi,
                        orientation='h',
                        y=-0.15,
                        x=0.5,
                        xanchor='center',
                        thickness=10,
                        len=0.8,
                        tickfont=dict(size=8)
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(family='Segoe UI', size=9)
                )
                
                st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
            
            else:
                raise FileNotFoundError("GeoJSON file not found")
                
        except Exception as e:
            # Fallback: Display simple message
            st.warning("📍 Map requires 'gadm41_BEN_1.json' file.")
            
            # Show key stats
            top_region = regional_acq.nlargest(1, selected_acq_col)['region'].values[0]
            top_value = regional_acq.nlargest(1, selected_acq_col)[selected_acq_col].values[0]
            total_value = regional_acq[selected_acq_col].sum()
            
            st.markdown(f"""
            <div style="margin-top: 20px; text-align: center;">
                <div style="background: #F8F8F8; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                    <div style="font-size: 9px; color: #666;">🏆 Top Region</div>
                    <div style="font-size: 14px; font-weight: 600; color: #000;">{top_region}</div>
                    <div style="font-size: 12px; color: #4CAF50; font-weight: 600;">{top_value:.0f}</div>
                </div>
                <div style="background: #F8F8F8; padding: 12px; border-radius: 4px;">
                    <div style="font-size: 9px; color: #666;">📈 Total National</div>
                    <div style="font-size: 14px; font-weight: 600; color: #000;">{total_value:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Bottom Section - Last 7 Days Performance Table with KPI Selector
    st.markdown('<br><div class="chart-title">📋 Daily Performance - Last 7 Days</div>', unsafe_allow_html=True)
    
    # KPI Selector
    col_selector, col_empty = st.columns([2, 3])
    with col_selector:
        selected_acq_kpi = st.selectbox(
            "Select KPI to View",
            ["New Additions", "Net Adds", "Churn", "Net Churn", "Reconnection"],
            index=0,
            key="acq_daily_kpi_selector"
        )
    
    # Generate daily performance data for last 7 days
    last_7_days = pd.date_range(end=datetime.now(), periods=7, freq='D')
    
    # KPI data mapping with realistic values
    kpi_values_map = {
        "New Additions": np.random.uniform(20000, 30000, 7),
        "Net Adds": np.random.uniform(5000, 15000, 7),
        "Churn": np.random.uniform(30000, 45000, 7),
        "Net Churn": np.random.uniform(15000, 25000, 7),
        "Reconnection": np.random.uniform(10000, 20000, 7)
    }
    
    # Budget/target values
    budget_map = {
        "New Additions": 25000,
        "Net Adds": 10000,
        "Churn": 38000,
        "Net Churn": 20000,
        "Reconnection": 15000
    }
    
    # Create DataFrame
    selected_values = kpi_values_map[selected_acq_kpi]
    budget_value = budget_map[selected_acq_kpi]
    
    # Calculate variances
    dod_values = [(selected_values[i] - selected_values[i-1]) / selected_values[i-1] * 100 if i > 0 else np.nan 
                  for i in range(len(selected_values))]
    wow_values = [np.random.uniform(-5, 15, 1)[0] for _ in range(7)]  # Sample WoW data
    mom_values = [np.random.uniform(-10, 20, 1)[0] for _ in range(7)]  # Sample MoM data
    vs_budget = [(val - budget_value) / budget_value * 100 for val in selected_values]
    
    daily_performance = pd.DataFrame({
        'Date': last_7_days.strftime('%Y-%m-%d'),
        selected_acq_kpi: selected_values,
        'DoD': dod_values,
        'WoW': wow_values,
        'MoM': mom_values,
        'vs Budget': vs_budget
    })
    
    # Format display DataFrame
    display_df = daily_performance.copy()
    
    # Format the KPI value column
    display_df[selected_acq_kpi] = display_df[selected_acq_kpi].apply(lambda x: f"{x:,.0f}")
    
    # Format the variance columns with +/- signs
    for col in ['DoD', 'WoW', 'MoM', 'vs Budget']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "-")
    
    # Color function for variance columns (matching CBU dashboard)
    def get_color_for_percentage(value):
        """Return color based on percentage value"""
        if value >= 5:
            return '#107C10'  # Green
        elif value >= 2:
            return '#FFA500'  # Orange
        elif value >= -2:
            return '#FFD700'  # Yellow
        else:
            return '#D13438'  # Red
    
    def color_variance(val):
        """Apply color to variance cells"""
        if pd.isna(val) or val == '-':
            return ''
        try:
            # Extract numeric value from formatted string
            num_val = float(val.replace('%', '').replace('+', ''))
            color = get_color_for_percentage(num_val)
            return f'background-color: {color}; color: white; font-weight: bold; padding: 4px;'
        except:
            return ''
    
    # Apply styling only to variance columns
    styled_df = display_df.style.applymap(
        color_variance,
        subset=['DoD', 'WoW', 'MoM', 'vs Budget']
    ).set_properties(**{
        'text-align': 'center',
        'font-size': '11px',
        'border': '1px solid #E0E0E0'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#000000'),
            ('color', '#FFCB05'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('font-size', '10px'),
            ('padding', '8px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '6px')
        ]}
    ])
    
    st.dataframe(styled_df, use_container_width=True, height=350)
    
    st.markdown("<br>", unsafe_allow_html=True)

def render_customer_conversion_content(data):
    """Render Customer Conversion page content - Enhanced with comprehensive KPIs"""
    
    # Top KPI Cards Row - All Conversion Metrics
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(create_mtn_kpi_card(
            "MoMo Conv.",
            3120,
            "",
            7.7,
            {'ytd': '98.5K', 'wow': '+240', 'mom': '+6.8%'}
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_mtn_kpi_card(
            "MoMo Rate",
            19.2,
            "%",
            6.1,
            {'ytd': '18.5%', 'wow': '+1.2%', 'mom': '+0.9%'}
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_mtn_kpi_card(
            "Data Conv.",
            4020,
            "",
            8.5,
            {'ytd': '127K', 'wow': '+340', 'mom': '+7.5%'}
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_mtn_kpi_card(
            "Data Rate",
            24.7,
            "%",
            7.3,
            {'ytd': '23.8%', 'wow': '+1.8%', 'mom': '+1.2%'}
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(create_mtn_kpi_card(
            "Bundle Rate",
            35.8,
            "%",
            6.7,
            {'ytd': '34.2%', 'wow': '+2.4%', 'mom': '+1.8%'}
        ), unsafe_allow_html=True)
    
    with col6:
        st.markdown(create_mtn_kpi_card(
            "Multi-Service",
            13.4,
            "%",
            6.7,
            {'ytd': '12.8%', 'wow': '+0.9%', 'mom': '+0.6%'}
        ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Chart Section - Conversion Trends with KPI Selector
    col_chart_left, col_chart_right = st.columns([3, 2])
    
    with col_chart_left:
        st.markdown('<div class="chart-title">📈 Conversion Rate Trends</div>', unsafe_allow_html=True)
        
        # KPI selector
        selected_conversion_kpi = st.selectbox(
            "Select Conversion Metric to View",
            ["MoMo Conversion Rate", "Data Conversion Rate", "Bundle Rate", "Multi-Service Rate", "Xtratime Rate", "VAS Rate"],
            key="conversion_kpi_selector"
        )
        
        # Generate trend data for all conversion KPIs
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        
        conversion_data_map = {
            "MoMo Conversion Rate": {
                'values': np.random.uniform(17, 21, 90) + np.linspace(0, 2, 90),
                'color': '#9C27B0',
                'y_title': 'MoMo Conversion Rate (%)'
            },
            "Data Conversion Rate": {
                'values': np.random.uniform(22, 27, 90) + np.linspace(0, 2.5, 90),
                'color': '#2196F3',
                'y_title': 'Data Conversion Rate (%)'
            },
            "Bundle Rate": {
                'values': np.random.uniform(32, 38, 90) + np.linspace(0, 3, 90),
                'color': '#4CAF50',
                'y_title': 'Bundle Rate (%)'
            },
            "Multi-Service Rate": {
                'values': np.random.uniform(11, 15, 90) + np.linspace(0, 1.5, 90),
                'color': '#FF9800',
                'y_title': 'Multi-Service Rate (%)'
            },
            "Xtratime Rate": {
                'values': np.random.uniform(8, 12, 90) + np.linspace(0, 1, 90),
                'color': '#E91E63',
                'y_title': 'Xtratime Rate (%)'
            },
            "VAS Rate": {
                'values': np.random.uniform(15, 20, 90) + np.linspace(0, 2, 90),
                'color': '#00897B',
                'y_title': 'VAS Rate (%)'
            }
        }
        
        conversion_config = conversion_data_map[selected_conversion_kpi]
        
        # Create conversion trend chart
        fig_conversion = go.Figure()
        
        fig_conversion.add_trace(go.Scatter(
            x=dates,
            y=conversion_config['values'],
            name=selected_conversion_kpi,
            mode='lines+markers',
            line=dict(color=conversion_config['color'], width=3),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor=f'rgba({int(conversion_config["color"][1:3], 16)}, {int(conversion_config["color"][3:5], 16)}, {int(conversion_config["color"][5:7], 16)}, 0.2)'
        ))
        
        fig_conversion.update_layout(
            height=450,
            plot_bgcolor=MTN_WHITE,
            paper_bgcolor=MTN_WHITE,
            font=dict(family='Segoe UI', size=11, color=MTN_BLACK),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='x unified',
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title=conversion_config['y_title'])
        )
        
        st.plotly_chart(fig_conversion, use_container_width=True, config={'displayModeBar': False})
    
    with col_chart_right:
        st.markdown('<div class="chart-title">📊 Conversion Mix Distribution</div>', unsafe_allow_html=True)
        
        conversion_dist = pd.DataFrame({
            'Type': ['MoMo', 'Data', 'Bundle', 'Multi-Service', 'Xtratime', 'VAS'],
            'Rate': [19.2, 24.7, 35.8, 13.4, 10.5, 18.2]
        })
        
        fig_conv_mix = go.Figure(data=[go.Pie(
            labels=conversion_dist['Type'],
            values=conversion_dist['Rate'],
            hole=0.5,
            marker=dict(colors=['#9C27B0', '#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#00897B']),
            textinfo='label+percent',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
        )])
        
        fig_conv_mix.update_layout(
            height=450,
            plot_bgcolor=MTN_WHITE,
            paper_bgcolor=MTN_WHITE,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=10)),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig_conv_mix, use_container_width=True, config={'displayModeBar': False})
    
    # Daily Performance Table - Last 7 Days with All Conversion KPIs
    st.markdown('<br><div class="chart-title">📋 Daily Performance - Conversion Metrics (Last 7 Days)</div>', unsafe_allow_html=True)
    
    # Generate daily performance data
    last_7_days = pd.date_range(end=datetime.now(), periods=7, freq='D')
    
    daily_conversion = pd.DataFrame({
        'Date': last_7_days.strftime('%d %b'),
        'MoMo Rate (%)': np.random.uniform(18.0, 20.5, 7),
        'Data Rate (%)': np.random.uniform(23.0, 26.0, 7),
        'Bundle Rate (%)': np.random.uniform(33.0, 38.0, 7),
        'Multi-Service (%)': np.random.uniform(12.0, 15.0, 7),
        'Xtratime (%)': np.random.uniform(9.0, 12.0, 7),
        'VAS Rate (%)': np.random.uniform(16.0, 20.0, 7),
        'DoD %': np.random.uniform(-3, 8, 7),
        'MoM %': np.random.uniform(-5, 10, 7),
        'Target (%)': np.repeat(20.0, 7),
        'Actual vs Target %': np.random.uniform(-12, 8, 7)
    })
    
    st.dataframe(
        daily_conversion.style.format({
            'MoMo Rate (%)': '{:.2f}',
            'Data Rate (%)': '{:.2f}',
            'Bundle Rate (%)': '{:.2f}',
            'Multi-Service (%)': '{:.2f}',
            'Xtratime (%)': '{:.2f}',
            'VAS Rate (%)': '{:.2f}',
            'DoD %': '{:+.1f}',
            'MoM %': '{:+.1f}',
            'Target (%)': '{:.1f}',
            'Actual vs Target %': '{:+.1f}'
        }).background_gradient(
            cmap='Greens',
            subset=['MoMo Rate (%)', 'Data Rate (%)', 'Bundle Rate (%)', 'Multi-Service (%)', 'Xtratime (%)', 'VAS Rate (%)']
        ).background_gradient(
            cmap='RdYlGn',
            subset=['DoD %', 'MoM %', 'Actual vs Target %']
        ),
        use_container_width=True,
        height=280
    )
    
    # # Bottom Section - Conversion Funnel Analysis
    # st.markdown('<br><div class="chart-title">🔄 Conversion Funnel Analysis</div>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     # Funnel stages
    #     funnel_data = pd.DataFrame({
    #         'Stage': ['Total Customers', 'Active Users', 'Service Users', 'Multi-Service', 'High Value'],
    #         'Count': [100000, 78500, 58200, 32100, 15600],
    #         'Rate': [100, 78.5, 73.2, 55.2, 48.6]
    #     })
        
    #     fig_funnel = go.Figure(go.Funnel(
    #         y=funnel_data['Stage'],
    #         x=funnel_data['Count'],
    #         textposition="inside",
    #         textinfo="value+percent initial",
    #         marker=dict(color=['#9C27B0', '#2196F3', '#4CAF50', '#FF9800', '#FFCB05']),
    #         connector=dict(line=dict(color='rgb(200, 200, 200)', width=2))
    #     ))
        
    #     fig_funnel.update_layout(
    #         height=350,
    #         plot_bgcolor=MTN_WHITE,
    #         paper_bgcolor=MTN_WHITE,
    #         margin=dict(l=20, r=20, t=20, b=20)
    #     )
        
    #     st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})
    
    # with col2:
    #     # Month-over-Month Growth
    #     months_short = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
        
    #     fig_growth = go.Figure()
        
    #     fig_growth.add_trace(go.Bar(
    #         x=months_short,
    #         y=[18.2, 18.8, 19.5, 20.1, 19.8, 20.5],
    #         name='MoMo Conv Rate',
    #         marker_color='#9C27B0',
    #         text=[18.2, 18.8, 19.5, 20.1, 19.8, 20.5],
    #         texttemplate='%{text:.1f}%',
    #         textposition='outside'
    #     ))
        
    #     fig_growth.add_trace(go.Bar(
    #         x=months_short,
    #         y=[22.5, 23.2, 23.8, 24.5, 24.2, 25.0],
    #         name='Data Conv Rate',
    #         marker_color='#2196F3',
    #         text=[22.5, 23.2, 23.8, 24.5, 24.2, 25.0],
    #         texttemplate='%{text:.1f}%',
    #         textposition='outside'
    #     ))
        
    #     fig_growth.update_layout(
    #         height=350,
    #         barmode='group',
    #         plot_bgcolor=MTN_WHITE,
    #         paper_bgcolor=MTN_WHITE,
    #         xaxis=dict(title='Month', showgrid=False),
    #         yaxis=dict(title='Conversion Rate (%)', showgrid=True, gridcolor='#F0F0F0'),
    #         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    #         margin=dict(l=40, r=40, t=40, b=40)
    #     )
        
    #     st.plotly_chart(fig_growth, use_container_width=True, config={'displayModeBar': False})


# ==================== MAIN APP ====================
def main():
    data = generate_sample_data()
    
    # ==================== TOP HEADER WITH LOGO ====================
    st.markdown('<div style="margin-top: 0; position: relative; z-index: 100;">', unsafe_allow_html=True)
    
    # Create the header with three columns
    col1, col2, col3 = st.columns([1, 4, 1.8])
    
    with col1:
        # Use actual MTN logo image with base64 encoding
        import base64
        try:
            with open("MTN_Logo.PNG", "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
            <div style="background: #FFCB05; padding: 15px; border-radius: 0; height: 100px; display: flex; align-items: center; justify-content: center;">
                <img src="data:image/png;base64,{logo_data}" style="width: 120px; height: auto; object-fit: contain;">
            </div>
            """, unsafe_allow_html=True)
        except:
            # Fallback to text logo if image not found
            st.markdown("""
            <div style="background: #FFCB05; padding: 15px; height: 100px; display: flex; align-items: center; justify-content: center;">
                <div style="background: #000000; border-radius: 20px; padding: 8px 25px;">
                    <span style="color: #FFCB05; font-size: 22px; font-weight: 900; font-family: 'Arial Black', sans-serif;">MTN</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #FFFFFF; padding: 15px 30px; height: 100px; display: flex; align-items: center; border-bottom: 2px solid #E0E0E0;">
            <h1 style="color: #000000; font-size: 20px; font-weight: 600; margin: 0; font-family: 'Segoe UI', sans-serif;">
                Executive Dashboard | Sales & Distribution
            </h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #F8F8F8; padding: 12px 20px 0px 20px; border-bottom: 2px solid #E0E0E0; border-left: 1px solid #E0E0E0; height: 100px; display: flex; flex-direction: column; justify-content: flex-start;">
            <div style="color: #4A4A4A; font-size: 11px; font-weight: 600; margin-bottom: 8px; margin-top: 12px;">Report Date</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add the actual date input - positioned to overlay on the styled container
        selected_date = st.date_input(
            "Report Date",
            datetime.now(),
            label_visibility="collapsed",
            key="report_date"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== LAYOUT: FILTERS LEFT + CONTENT RIGHT ====================
    col_filter, col_content = st.columns([1, 5])
    
    # ==================== LEFT FILTER PANEL ====================
    with col_filter:
        st.markdown('<div class="filter-title">🎛 FILTERS</div>', unsafe_allow_html=True)
        
        # Date Range Filter
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">📅 Date Range</div>', unsafe_allow_html=True)
        date_option = st.selectbox(
            "date_range",
            ["MTD", "QTD", "YTD", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"],
            label_visibility="collapsed",
            key="date_filter"
        )
        
        if date_option == "Custom":
            st.date_input("From", datetime.now() - timedelta(days=30), key="start_date")
            st.date_input("To", datetime.now(), key="end_date")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Region Filter
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">🗺️ Region</div>', unsafe_allow_html=True)
        selected_region = st.selectbox(
            "region",
            ["All Regions"] + list(data['regional_data']['region']),
            label_visibility="collapsed",
            key="region_filter"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Channel Filter
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">📡 Channel</div>', unsafe_allow_html=True)
        selected_channel = st.selectbox(
            "channel",
            ["All Channels", "YC (Yellow Centers)", "DTC (MTN Shops)", "DTR (Dealers)", "Digital"],
            label_visibility="collapsed",
            key="channel_filter"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Agent Tier Filter
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">👥 Agent Tier</div>', unsafe_allow_html=True)
        selected_tier = st.selectbox(
            "tier",
            ["All Tiers", "Gold", "Silver", "Bronze", "Inactive"],
            label_visibility="collapsed",
            key="tier_filter"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 30px;">', unsafe_allow_html=True)
        
        # Action Buttons - Modified
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🏠 Back to Home", key="home_btn", use_container_width=True):
                st.info("Redirecting to home...")
        
        with col_btn2:
            if st.button("📥 Export", key="export_btn", use_container_width=True):
                st.info("Export functionality")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== RIGHT CONTENT AREA WITH TAB NAVIGATION ====================
    with col_content:
        # Tab Navigation - Power BI Style
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview",
            "💰 Airtime Sales",
            "💸 Float Management",
            "👥 Agent Network",
            "🏆 Agent Performance",
            "📈 Acquisition",
            "🔄 Customer Conversion"
        ])
        
        with tab1:
            render_overview_content(data)
        
        with tab2:
            render_airtime_sales_content(data)
        
        with tab3:
            render_float_management_content(data)
        
        with tab4:
            render_agent_network_content(data)
        
        with tab5:
            render_agent_performance_content(data)
        
        with tab6:
            render_acquisition_content(data)
        
        with tab7:
            render_customer_conversion_content(data)
    
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 16px 0;">
        <p style="color: #000000; font-weight: 600; margin: 0; font-size: 12px;">
            MTN Benin - Sales & Distribution Dashboard
        </p>
        <p style="color: #4A4A4A; font-size: 10px; margin: 6px 0 0 0;">
            Powered by Streamlit • Data refreshes every 15 minutes • © 2025 MTN Benin
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()