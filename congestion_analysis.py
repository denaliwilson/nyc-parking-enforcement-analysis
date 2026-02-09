"""
NYC Congestion Pricing Impact Analysis Dashboard

A dedicated Streamlit application analyzing the impact of Manhattan's congestion 
pricing implementation (January 5, 2025) on parking citations and enforcement patterns.

Features:
- Before/After comparison analysis (2024 vs 2025-2026)
- Congestion zone vs non-zone impact assessment
- Time series trends with implementation date marked
- Violation type and behavioral pattern changes
- Revenue impact analysis

Author: NYC Parking Enforcement Analysis
Version: 1.0
Last Updated: February 9, 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime, timedelta, date
import sys

# Add project path
sys.path.append(str(Path(__file__).parent))

# Import modules
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner
from src.config import PROCESSED_DATA_DIR

# Page configuration
st.set_page_config(
    page_title="NYC Congestion Pricing Impact Analysis",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile responsiveness
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    h1 {
        color: #1f77b4;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
CONGESTION_PRICING_START = date(2025, 1, 5)  # Congestion pricing implementation date
CONGESTION_ZONE_PRECINCTS = [
    1, 5, 6, 7, 9, 10, 13, 14, 17, 18, 19, 20, 22, 23, 24, 25, 26, 28, 30, 32, 34
]  # Manhattan precincts below 60th Street (approximate)

# Initialize loaders
@st.cache_resource
def get_loader():
    return NYCParkingDataLoader()

@st.cache_resource
def get_cleaner():
    return ParkingDataCleaner()

@st.cache_data(ttl=3600)
def load_comparison_data(period_type='month', custom_before=None, custom_after=None):
    """
    Load comparison data for before/after congestion pricing analysis.
    
    Args:
        period_type: 'month', 'quarter', or 'custom'
        custom_before: tuple of (start_date, end_date) for before period
        custom_after: tuple of (start_date, end_date) for after period
    
    Returns:
        tuple: (before_df, after_df)
    """
    loader = get_loader()
    cleaner = get_cleaner()
    
    if period_type == 'month':
        # Compare January 2024 vs January 2026
        before_start = date(2024, 1, 1)
        before_end = date(2024, 1, 31)
        after_start = date(2026, 1, 1)
        after_end = date(2026, 1, 31)
    elif period_type == 'quarter':
        # Compare Q1 2024 vs Q1 2025
        before_start = date(2024, 1, 1)
        before_end = date(2024, 3, 31)
        after_start = date(2025, 1, 1)
        after_end = date(2025, 3, 31)
    else:  # custom
        before_start, before_end = custom_before
        after_start, after_end = custom_after
    
    # Load before period
    st.info(f"📥 Loading BEFORE period: {before_start} to {before_end}")
    before_dfs = []
    current_date = before_start
    while current_date <= before_end:
        day_df = loader.load_by_day(current_date.strftime('%Y-%m-%d'))
        if day_df is not None and len(day_df) > 0:
            before_dfs.append(day_df)
        current_date += timedelta(days=1)
    
    before_df = None
    if before_dfs:
        before_raw = pd.concat(before_dfs, ignore_index=True)
        before_df = cleaner.clean_dataframe(before_raw)
        st.success(f"✅ Loaded {len(before_df):,} citations from BEFORE period")
    
    # Load after period
    st.info(f"📥 Loading AFTER period: {after_start} to {after_end}")
    after_dfs = []
    current_date = after_start
    while current_date <= after_end:
        day_df = loader.load_by_day(current_date.strftime('%Y-%m-%d'))
        if day_df is not None and len(day_df) > 0:
            after_dfs.append(day_df)
        current_date += timedelta(days=1)
    
    after_df = None
    if after_dfs:
        after_raw = pd.concat(after_dfs, ignore_index=True)
        after_df = cleaner.clean_dataframe(after_raw)
        st.success(f"✅ Loaded {len(after_df):,} citations from AFTER period")
    
    return before_df, after_df

def classify_congestion_zone(df):
    """Add congestion zone classification to dataframe."""
    df = df.copy()
    df['precinct_num'] = pd.to_numeric(df['precinct'], errors='coerce')
    df['in_congestion_zone'] = df['precinct_num'].isin(CONGESTION_ZONE_PRECINCTS)
    df['zone_type'] = df['in_congestion_zone'].map({
        True: 'Congestion Zone',
        False: 'Outside Zone'
    })
    return df

# Header
st.title("🚦 NYC Congestion Pricing Impact Analysis")
st.markdown(f"""
<div class="highlight-box">
    <h3>📍 Manhattan Congestion Pricing Program</h3>
    <p><strong>Implementation Date:</strong> January 5, 2025</p>
    <p><strong>Zone:</strong> Manhattan below 60th Street (Central Business District)</p>
    <p><strong>Analysis Focus:</strong> Impact on parking citations and enforcement patterns</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Quick Comparison (Jan 2024 vs Jan 2026)", "Quarterly Comparison", "Custom Date Range", "Time Series Trend"]
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📊 About This Analysis
    
    This dashboard compares parking citation patterns before and after 
    Manhattan's congestion pricing implementation.
    
    **Key Questions:**
    - Did citation volumes change?
    - Did violations shift outside the zone?
    - How did enforcement patterns change?
    - What's the revenue impact?
    """)
    
    st.markdown("---")
    st.info("💡 **Tip:** Run the main dashboard separately with `streamlit run dashboard.py`")

# Main content based on analysis type
if analysis_type == "Quick Comparison (Jan 2024 vs Jan 2026)":
    st.header("📊 Quick Comparison: January 2024 vs January 2026")
    
    if st.button("🔄 Load Comparison Data", type="primary", use_container_width=True):
        with st.spinner("Loading comparison data..."):
            before_df, after_df = load_comparison_data(period_type='month')
            
            if before_df is not None and after_df is not None:
                # Classify zones
                before_df = classify_congestion_zone(before_df)
                after_df = classify_congestion_zone(after_df)
                
                # Store in session state
                st.session_state.before_df = before_df
                st.session_state.after_df = after_df
                st.session_state.comparison_loaded = True
                st.rerun()
    
    # Show analysis if data is loaded
    if 'comparison_loaded' in st.session_state and st.session_state.comparison_loaded:
        before_df = st.session_state.before_df
        after_df = st.session_state.after_df
        
        st.success("✅ Data loaded successfully!")
        
        # Overall metrics
        st.markdown("### 📈 Overall Impact Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        before_total = len(before_df)
        after_total = len(after_df)
        pct_change = ((after_total - before_total) / before_total) * 100
        
        with col1:
            st.metric(
                "Before (Jan 2024)",
                f"{before_total:,}",
                help="Total citations in January 2024"
            )
        
        with col2:
            st.metric(
                "After (Jan 2026)",
                f"{after_total:,}",
                delta=f"{pct_change:+.1f}%",
                help="Total citations in January 2026"
            )
        
        before_revenue = before_df['fine_amount'].sum()
        after_revenue = after_df['fine_amount'].sum()
        revenue_change = ((after_revenue - before_revenue) / before_revenue) * 100
        
        with col3:
            st.metric(
                "Revenue Before",
                f"${before_revenue/1e6:.2f}M",
                help="Total fine revenue January 2024"
            )
        
        with col4:
            st.metric(
                "Revenue After",
                f"${after_revenue/1e6:.2f}M",
                delta=f"{revenue_change:+.1f}%",
                help="Total fine revenue January 2026"
            )
        
        # Zone comparison
        st.markdown("---")
        st.markdown("### 🗺️ Congestion Zone vs Outside Zone")
        
        before_zone = before_df.groupby('zone_type').size().reset_index(name='citations')
        before_zone['period'] = 'Before (Jan 2024)'
        
        after_zone = after_df.groupby('zone_type').size().reset_index(name='citations')
        after_zone['period'] = 'After (Jan 2026)'
        
        combined_zone = pd.concat([before_zone, after_zone])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = px.bar(
                combined_zone,
                x='zone_type',
                y='citations',
                color='period',
                barmode='group',
                title='Citations by Zone: Before vs After Congestion Pricing',
                labels={'zone_type': 'Zone Type', 'citations': 'Number of Citations'},
                color_discrete_map={
                    'Before (Jan 2024)': '#e74c3c',
                    'After (Jan 2026)': '#27ae60'
                }
            )
            fig.update_traces(texttemplate='%{y:,}', textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Zone Statistics")
            
            # Calculate zone-specific changes
            before_in_zone = before_df[before_df['in_congestion_zone']].shape[0]
            after_in_zone = after_df[after_df['in_congestion_zone']].shape[0]
            zone_change = ((after_in_zone - before_in_zone) / before_in_zone) * 100
            
            before_out_zone = before_df[~before_df['in_congestion_zone']].shape[0]
            after_out_zone = after_df[~after_df['in_congestion_zone']].shape[0]
            out_zone_change = ((after_out_zone - before_out_zone) / before_out_zone) * 100
            
            st.metric("In Zone Change", f"{zone_change:+.1f}%")
            st.metric("Outside Zone Change", f"{out_zone_change:+.1f}%")
            
            if zone_change < 0 and out_zone_change > 0:
                st.info("📊 Citations decreased in congestion zone but increased outside - potential displacement effect")
            elif zone_change < 0 and out_zone_change < 0:
                st.info("📊 Citations decreased in both zones - overall reduction in violations")
            else:
                st.info("📊 Citations increased - may indicate increased enforcement or other factors")
        
        # Top violations comparison
        st.markdown("---")
        st.markdown("### 🚗 Top Violation Types: Before vs After")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### January 2024 (Before)")
            before_violations = before_df['violation'].value_counts().head(10).reset_index()
            before_violations.columns = ['Violation', 'Count']
            
            fig = px.bar(
                before_violations,
                y='Violation',
                x='Count',
                orientation='h',
                color='Count',
                color_continuous_scale='Reds'
            )
            fig.update_traces(texttemplate='%{x:,}', textposition='outside')
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### January 2026 (After)")
            after_violations = after_df['violation'].value_counts().head(10).reset_index()
            after_violations.columns = ['Violation', 'Count']
            
            fig = px.bar(
                after_violations,
                y='Violation',
                x='Count',
                orientation='h',
                color='Count',
                color_continuous_scale='Greens'
            )
            fig.update_traces(texttemplate='%{x:,}', textposition='outside')
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time of day analysis
        st.markdown("---")
        st.markdown("### ⏰ Time of Day Patterns")
        
        if 'time_of_day' in before_df.columns and 'time_of_day' in after_df.columns:
            before_time = before_df['time_of_day'].value_counts().reset_index()
            before_time.columns = ['Time of Day', 'Count']
            before_time['Period'] = 'Before (Jan 2024)'
            
            after_time = after_df['time_of_day'].value_counts().reset_index()
            after_time.columns = ['Time of Day', 'Count']
            after_time['Period'] = 'After (Jan 2026)'
            
            combined_time = pd.concat([before_time, after_time])
            
            fig = px.bar(
                combined_time,
                x='Time of Day',
                y='Count',
                color='Period',
                barmode='group',
                title='Citation Patterns by Time of Day',
                color_discrete_map={
                    'Before (Jan 2024)': '#e74c3c',
                    'After (Jan 2026)': '#27ae60'
                }
            )
            fig.update_traces(texttemplate='%{y:,}', textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Issuing agency comparison
        st.markdown("---")
        st.markdown("### 🏛️ Enforcement Agency Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            before_agency = before_df['issuing_agency'].value_counts().head(5).reset_index()
            before_agency.columns = ['Agency', 'Count']
            before_agency['Period'] = 'Before'
            
            fig = px.pie(
                before_agency,
                values='Count',
                names='Agency',
                title='January 2024 (Before)',
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            after_agency = after_df['issuing_agency'].value_counts().head(5).reset_index()
            after_agency.columns = ['Agency', 'Count']
            after_agency['Period'] = 'After'
            
            fig = px.pie(
                after_agency,
                values='Count',
                names='Agency',
                title='January 2026 (After)',
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Time Series Trend":
    st.header("📈 Time Series Trend Analysis")
    st.info("🚧 Coming soon: Detailed time series showing trends from 2024 through 2026 with congestion pricing implementation date marked.")
    
    st.markdown("""
    This section will show:
    - Monthly citation trends from Jan 2024 to present
    - Vertical line marking congestion pricing implementation (Jan 5, 2025)
    - Separate trend lines for congestion zone vs outside zone
    - Moving averages to smooth out seasonal variations
    """)

elif analysis_type == "Quarterly Comparison":
    st.header("📊 Quarterly Comparison")
    st.info("🚧 Coming soon: Q1 2024 vs Q1 2025 comparison for more comprehensive analysis.")

else:  # Custom Date Range
    st.header("📅 Custom Date Range Analysis")
    st.info("🚧 Coming soon: Select your own before/after date ranges for comparison.")

# Footer
st.markdown("---")
st.caption("🚦 NYC Congestion Pricing Impact Analysis | Data source: NYC Open Data Portal | Built with Streamlit")
