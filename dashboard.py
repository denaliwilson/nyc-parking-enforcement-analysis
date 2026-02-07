"""
NYC Parking Citations - Interactive Dashboard

A Streamlit web application for analyzing NYC parking citation data with real-time
loading from NYC Open Data API. Features include:

- Interactive date selection with latest data detection
- Multi-level analysis (Citywide → Borough → Precinct)
- Interactive choropleth maps with click-to-explore
- Real-time data fetching, cleaning, and visualization
- Automatic caching for performance optimization

Author: [Your Name]
Version: 1.0
Last Updated: February 7, 2026
Repository: [Your GitHub URL]
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import sys
import importlib
import json

# Add project path
sys.path.append(str(Path(__file__).parent))

# Import and reload modules to ensure latest code is used
import src.config
import src.data_loader
import src.data_cleaner

importlib.reload(src.config)
importlib.reload(src.data_loader)
importlib.reload(src.data_cleaner)

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, GEOSPATIAL_DATA_DIR
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner

# Initialize loader and cleaner
@st.cache_resource
def get_loader():
    """
    Initialize and cache the NYC Parking Data Loader.
    
    Returns:
        NYCParkingDataLoader: Configured API client for NYC Open Data
    
    Note:
        Cached as a resource to persist across sessions and reruns
    """
    return NYCParkingDataLoader()

@st.cache_resource
def get_cleaner():
    """
    Initialize and cache the Parking Data Cleaner.
    
    Returns:
        ParkingDataCleaner: Configured data cleaning pipeline
    
    Note:
        Cached as a resource to persist across sessions and reruns
    """
    return ParkingDataCleaner()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_latest_available_date():
    """
    Query NYC Open Data API to determine the most recent date with available data.
    
    Returns:
        date: Most recent date with parking citation data available
    
    Load and cache NYC Police precinct boundary geometries.
    
    Returns:
        GeoDataFrame: NYC precinct polygons with columns:
            - Precinct (int): Precinct number
            - borough (str): Borough name
            - geometry: Polygon geometries in EPSG:4326
    
    Data Source:
        NYC ArcGIS REST API - Police Precincts Feature Layer
        https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/...
    
    Caching Strategy:
        1. Check for local file: data/geospatial/nyc_precincts.geojson
        2. If not found, download from ArcGIS API
        3. Save locally for future use
        4. Load using pure Python (json.load) to avoid GDAL dependency
    
    Borough Mapping:
        - MANHATTAN: Precincts 1-34
        - BRONX: Precincts 40-52
        - BROOKLYN: Precincts 60-94
        - QUEENS: Precincts 100-115
        - STATEN ISLAND: Precincts 120-123
    
    Note:
        Uses geopandas but avoids read_file() to eliminate system
        dependency requirements (GDAL, PROJ). This enables pure Python
        deployment to Streamlit Cloud without apt packages.
    
    Note:
        - Cached for 1 hour to avoid excessive API calls
        - Falls back to (today - 2 days) if API query fails
        - NYC Open Data typically has a 1-2 day delay for data availability
    
    API Query:
        Executes: SELECT MAX(issue_date) FROM parking_violations
    """
    try:
        import requests
        url = "https://data.cityofnewyork.us/resource/nc67-uf89.json"
        params = {
            '$select': 'MAX(issue_date) as max_date',
            '$limit': 1
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0 and 'max_date' in data[0]:
                # Parse the date string
                date_str = data[0]['max_date'].split('T')[0]
                return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception as e:
        print(f"Error fetching latest date: {e}")
    
    # Fallback to estimated date (today - 2 days)
    return datetime.now().date() - timedelta(days=2)

@st.cache_data
def load_geojson():
    """Load and cache NYC precinct GeoJSON data"""
    import geopandas as gpd
    import requests
    import json
    from shapely.geometry import shape
    
    geospatial_dir = GEOSPATIAL_DATA_DIR
    precinct_file = geospatial_dir / 'nyc_precincts.geojson'
    
    if precinct_file.exists():
        # Read GeoJSON directly without geopandas I/O (avoids GDAL dependency)
        with open(precinct_file, 'r') as f:
            geojson_data = json.load(f)
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs='EPSG:4326')
    else:
        url = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Police_Precincts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            geojson_data = response.json()
            gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs='EPSG:4326')
            # Save for future use (using JSON instead of geopandas writer)
            with open(precinct_file, 'w') as f:
                json.dump(geojson_data, f)
        else:
            return None
    
    # Add borough mapping
    borough_precinct_map = {
        'MANHATTAN': list(range(1, 35)),
        'BRONX': list(range(40, 53)),
        'BROOKLYN': list(range(60, 95)),
        'QUEENS': list(range(100, 116)),
        'STATEN ISLAND': list(range(120, 124))
    }
    
    def get_borough(precinct):
        try:
            p = int(precinct)
            for borough, precincts in borough_precinct_map.items():
                if p in precincts:
                    return borough
        except:
            pass
        return None
    
    gdf['borough'] = gdf['Precinct'].apply(get_borough)
    gdf['Precinct'] = pd.to_numeric(gdf['Precinct'], errors='coerce')
    
    return gdf

def clean_state_field(state_series):
    """
    Clean and standardize state abbreviations.
    
    Args:
        state_series: Pandas series of state values
    
    Returns:
        Pandas series with cleaned state values
    """
    # Valid US state abbreviations
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'VI', 'GU', 'AS', 'MP'  # Territories
    }
    
    def clean_state(val):
        if pd.isna(val):
            return 'UNKNOWN'
        
        # Convert to string and uppercase
        val = str(val).strip().upper()
        
        # Remove common prefixes/suffixes
        val = val.replace('US-', '').replace('USA-', '')
        
        # Handle numeric codes or invalid entries
        if val.isdigit() or len(val) > 3 or len(val) == 0:
            return 'UNKNOWN'
        
        # Check if valid state
        if val in valid_states:
            return val
        
        # Common typos/variations
        state_map = {
            'N.Y': 'NY', 'N.J': 'NJ', 'PENN': 'PA', 'PENNA': 'PA',
            'MASS': 'MA', 'CONN': 'CT', 'FLA': 'FL', 'CALIF': 'CA',
            'N Y': 'NY', 'N J': 'NJ', 'P A': 'PA'
        }
        
        if val in state_map:
            return state_map[val]
        
        # If 3 characters, try first 2
        if len(val) == 3:
            first_two = val[:2]
            if first_two in valid_states:
                return first_two
        
        return 'UNKNOWN'
    
    return state_series.apply(clean_state)

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_sample_data():
    """
    Load preloaded January 2026 sample data.
    
    If the file doesn't exist locally, fetches from NYC Open Data API
    for January 2026 and caches it.
    
    Returns:
        DataFrame: Cleaned parking citation data for January 2026 (~860K records, Jan 1-31)
    """
    sample_file = PROCESSED_DATA_DIR / 'jan_2026_sample_data.csv'
    
    # Try loading existing file first
    if sample_file.exists():
        try:
            st.info(f"📂 Loading from local file: {sample_file.name}")
            df = pd.read_csv(sample_file)
            if 'issue_date' in df.columns:
                df['issue_date'] = pd.to_datetime(df['issue_date'])
            st.success(f"✅ Loaded {len(df):,} citations from January 2026 (local file)")
            return df
        except Exception as e:
            st.warning(f"⚠️ Could not load local file: {e}")
            st.info("Falling back to API fetch...")
    
    # If file doesn't exist, fetch from API and cache
    st.warning("⚠️ Local sample file not found. Fetching from NYC Open Data API...")
    st.info("This may take a few minutes. Data will be cached for future use.")
    
    try:
        # Fetch January 2026 data from API
        from datetime import date
        loader_temp = NYCParkingDataLoader()
        cleaner_temp = ParkingDataCleaner()
        
        # Load January 2026 (days 1-31)
        all_dfs = []
        start_date = date(2026, 1, 1)
        end_date = date(2026, 1, 31)
        current_date = start_date
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        days_total = (end_date - start_date).days + 1
        day_count = 0
        
        while current_date <= end_date:
            day_count += 1
            date_str = current_date.strftime('%Y-%m-%d')
            status_text.text(f"Fetching day {day_count}/{days_total}: {date_str}")
            
            day_df = loader_temp.load_by_day(date_str)
            if day_df is not None and len(day_df) > 0:
                all_dfs.append(day_df)
            
            current_date = current_date + timedelta(days=1)
            progress_bar.progress(day_count / days_total)
        
        progress_bar.empty()
        status_text.empty()
        
        if all_dfs:
            st.info("Cleaning and processing data...")
            raw_df = pd.concat(all_dfs, ignore_index=True)
            df = cleaner_temp.clean_dataframe(raw_df)
            
            # Save for future use
            st.info("Saving to local cache...")
            PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(sample_file, index=False)
            st.success(f"✅ Fetched and cached {len(df):,} citations")
            
            return df
        else:
            st.error("❌ No data found for January 2026")
            return None
    except Exception as e:
        st.error(f"❌ Error fetching sample data from API: {e}")
        return None

loader = get_loader()
cleaner = get_cleaner()

# Page configuration
st.set_page_config(
    page_title="NYC Parking Citations Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for typography and visual polish
st.markdown("""
<style>
    /* Typography improvements */
    .stMetric {
        font-family: 'Arial', sans-serif;
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h1 {
        padding-bottom: 20px;
        padding-top: 10px;
        font-weight: 600;
    }
    
    h2 {
        padding-top: 15px;
        padding-bottom: 10px;
        font-weight: 600;
        color: #2C3E50;
    }
    
    h3 {
        padding-top: 10px;
        padding-bottom: 8px;
        font-weight: 600;
        color: #34495E;
    }
    
    /* Visual polish - colored dividers */
    .stDivider {
        background: linear-gradient(to right, #FF6B6B, #4ECDC4);
        height: 2px;
        margin: 20px 0;
    }
    
    /* Card effect for sections */
    .stPlotlyChart {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for drill-down and data persistence
if 'selected_borough' not in st.session_state:
    st.session_state.selected_borough = None
if 'selected_precinct' not in st.session_state:
    st.session_state.selected_precinct = None
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None
if 'selected_agency' not in st.session_state:
    st.session_state.selected_agency = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None

# Check if data is already loaded
if st.session_state.data_loaded and st.session_state.df is not None:
    # Data is loaded - show compact header with reload button
    st.title("NYC Parking Citations Dashboard")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{len(st.session_state.df):,} citations loaded**")
    with col2:
        if st.button("Load New Dates", type="primary", use_container_width=True):
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.session_state.selected_borough = None
            st.session_state.selected_precinct = None
            if 'quick_select' in st.session_state:
                del st.session_state.quick_select
            st.rerun()
    
    df = st.session_state.df
else:
    # No data loaded - show prominent date selector landing page with NYC image overlay
    
    # Custom CSS for image overlay effect
    st.markdown("""
    <style>
    .hero-container {
        position: relative;
        width: 100%;
        height: 600px;
        background-image: url('https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1600&h=600&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.4) 100%);
    }
    .hero-content {
        position: relative;
        z-index: 2;
        padding: 40px;
        color: white;
    }
    .hero-title {
        font-size: 3em;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 1.3em;
        color: #f0f0f0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }
    .input-panel {
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-top: 30px;
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero section with image background
    st.markdown("""
    <div class="hero-container">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="hero-title">NYC Parking Citations Dashboard</h1>
            <p class="hero-subtitle">Explore real-time parking enforcement data across New York City</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get latest available date from API
    latest_date = get_latest_available_date()
    
    # Use latest available date as default
    default_date = latest_date
    max_available_date = latest_date
    
    st.markdown(f"#### 📊 Latest Data Available: **{latest_date.strftime('%B %d, %Y')}**")
    
    st.markdown("#### Quick Start:")
    
    # Button to load preloaded monthly data
    if st.button("📂 Load January 2026 Sample Data (860K citations)", use_container_width=True, type="primary"):
        with st.spinner("Loading January 2026 sample data..."):
            df = load_sample_data()
            
            if df is not None and len(df) > 0:
                st.session_state.data_loaded = True
                st.session_state.df = df
                st.rerun()
            else:
                st.error("Unable to load sample data. Please try custom date range below.")
    
    st.markdown("#### Or Choose Custom Date Range:")
    
    # Always show date range picker
    date_range = st.date_input(
        "Select start and end dates:",
        value=(default_date - timedelta(days=6), default_date),
        max_value=max_available_date,
        help="Click the calendar to select your start date, then select your end date"
    )
    
    # Determine start and end dates
    if len(date_range) == 2:
        start_date, end_date = date_range
        num_days = (end_date - start_date).days + 1
        st.info(f"📅 {num_days} day(s) selected: {start_date} to {end_date}")
        show_load_button = True
    elif len(date_range) == 1:
        # User selected only start date so far
        start_date = end_date = date_range[0]
        st.warning("⚠️ Please select an end date to complete your date range")
        show_load_button = False
    else:
        start_date = end_date = default_date
        show_load_button = True
    
    st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
    
    # Load button - only show if date range is complete
    if show_load_button:
        if st.button("🔄 Load Custom Date Range from API", type="secondary", use_container_width=True):
            loading_container = st.empty()
            
            with loading_container.container():
                # Calculate number of days
                num_days = (end_date - start_date).days + 1
                
                if num_days == 1:
                    # Single day - load directly
                    with st.spinner(f"Fetching citations for {start_date}..."):
                        date_str = start_date.strftime('%Y-%m-%d')
                        raw_df = loader.load_by_day(date_str)
                    
                    if raw_df is not None and len(raw_df) > 0:
                        with st.spinner(f"Cleaning {len(raw_df):,} citations..."):
                            df = cleaner.clean_dataframe(raw_df)
                    else:
                        st.error("No data found for this date.")
                        st.stop()
                else:
                    # Multiple days - load day by day
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    all_dfs = []
                    current_date = start_date
                    
                    for i in range(num_days):
                        status_text.text(f"Loading day {i+1}/{num_days}: {current_date}")
                        date_str = current_date.strftime('%Y-%m-%d')
                        
                        day_df = loader.load_by_day(date_str)
                        if day_df is not None and len(day_df) > 0:
                            all_dfs.append(day_df)
                        
                        current_date += timedelta(days=1)
                        progress_bar.progress((i + 1) / num_days)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if all_dfs:
                        raw_df = pd.concat(all_dfs, ignore_index=True)
                        
                        with st.spinner(f"Cleaning {len(raw_df):,} citations..."):
                            df = cleaner.clean_dataframe(raw_df)
                    else:
                        st.error("No data found for this date range.")
                        st.stop()
            
            # Clear loading messages and show success
            loading_container.empty()
            st.session_state.data_loaded = True
            st.session_state.df = df
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close input-panel
    
    # Stop execution to show landing page
    st.stop()

# Active Filters Banner - Prominent notification
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)

active_filters = []
if st.session_state.selected_borough:
    active_filters.append(f"📍 {st.session_state.selected_borough}")
if st.session_state.selected_precinct:
    active_filters.append(f"🏢 Precinct {st.session_state.selected_precinct}")
if st.session_state.selected_state:
    active_filters.append(f"🚗 State: {st.session_state.selected_state}")
if st.session_state.selected_agency:
    active_filters.append(f"🏛️ {st.session_state.selected_agency}")

if active_filters:
    st.info(f"**🔍 Active Filters:** {' | '.join(active_filters)} — *Click 'Clear All Filters' button in the map section to reset*")
    st.caption("💡 **Tip:** You can drill down by clicking on the map, state bars, or agency bars. All charts update automatically with your filters!")
else:
    st.success("✨ **No filters active** — Showing all data. Click the map or charts to drill down!")

# Top metrics
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)

# Responsive columns for mobile
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.metric("Total Citations", f"{len(df):,}")

with col2:
    if 'fine_amount' in df.columns:
        total_fines = df['fine_amount'].sum()
        st.metric("Total Fines", f"${total_fines:,.0f}")
    else:
        st.metric("Unique Dates", df['issue_date'].nunique() if 'issue_date' in df.columns else "N/A")

with col3:
    if 'fine_amount' in df.columns:
        avg_fine = df['fine_amount'].mean()
        st.metric("Average Fine", f"${avg_fine:,.2f}")
    else:
        st.metric("Average Fine", "N/A")

with col4:
    if 'violation_hour' in df.columns and df['violation_hour'].notna().any():
        # Get the most common hour, excluding NaN values
        hour_counts = df['violation_hour'].value_counts()
        if len(hour_counts) > 0:
            most_common_hour = hour_counts.index[0]
            st.metric("Peak Hour", f"{int(most_common_hour):02d}:00")
        else:
            st.metric("Peak Hour", "N/A")
    else:
        st.metric("Peak Hour", "N/A")

st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)

# Use responsive columns - stacks on mobile
map_col, time_col = st.columns([3, 2], gap="medium")

with map_col:
    st.subheader("🗺️ NYC Parking Citations Map")
    
    # Determine what level we're viewing and apply filters
    filtered_df = df.copy()
    filter_labels = []
    
    # Geographic filters
    if st.session_state.selected_precinct:
        view_level = "Precinct"
        selected_area = f"Precinct {st.session_state.selected_precinct}"
        filtered_df = filtered_df[pd.to_numeric(filtered_df['precinct'], errors='coerce') == st.session_state.selected_precinct] if 'precinct' in filtered_df.columns else filtered_df
    elif st.session_state.selected_borough:
        view_level = "Borough (Precincts)"
        selected_area = st.session_state.selected_borough
        filtered_df = filtered_df[filtered_df['county'] == st.session_state.selected_borough] if 'county' in filtered_df.columns else filtered_df
    else:
        view_level = "NYC (Boroughs)"
        selected_area = "All NYC"
    
    # State filter
    if st.session_state.selected_state and 'state' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['state'] == st.session_state.selected_state]
        filter_labels.append(f"State: {st.session_state.selected_state}")
    
    # Agency filter
    if st.session_state.selected_agency and 'issuing_agency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['issuing_agency'] == st.session_state.selected_agency]
        filter_labels.append(f"Agency: {st.session_state.selected_agency}")
    
    # Update selected_area with filters
    if filter_labels:
        selected_area = f"{selected_area} ({', '.join(filter_labels)})"
    
    st.caption(f"📊 Viewing: **{selected_area}** | Level: {view_level}")
    st.caption(f"📈 Showing {len(filtered_df):,} of {len(df):,} total citations")
    
    # Add prominent reset button if any filters are active
    if (st.session_state.selected_borough or st.session_state.selected_precinct or 
        st.session_state.selected_state or st.session_state.selected_agency):
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("🔄 Clear All Filters", type="primary", use_container_width=True):
                st.session_state.selected_borough = None
                st.session_state.selected_precinct = None
                st.session_state.selected_state = None
                st.session_state.selected_agency = None
                st.rerun()
        with col_btn2:
            st.caption("💡 Tip: Click map or charts to drill down further")
    
    # Add reset button if any filters are active
    if (st.session_state.selected_borough or st.session_state.selected_precinct or 
        st.session_state.selected_state or st.session_state.selected_agency):
        if st.button("← Clear All Filters"):
            st.session_state.selected_borough = None
            st.session_state.selected_precinct = None
            st.session_state.selected_state = None
            st.session_state.selected_agency = None
            st.rerun()
    
    # Borough-level view (city-wide)
    if not st.session_state.selected_borough and not st.session_state.selected_precinct and 'county' in filtered_df.columns:
        try:
            # Add toggle for view type
            view_type = st.radio(
                "Map View:",
                ["Borough Aggregate", "Precinct Detail"],
                horizontal=True,
                key="city_view_type"
            )
            
            # Load cached GeoJSON
            gdf = load_geojson()
            
            # Create borough aggregation using filtered data
            borough_data = filtered_df.groupby('county').size().reset_index(name='citations')
            
            # Create a choropleth map using plotly
            if gdf is not None and 'Precinct' in gdf.columns:
                borough_precinct_map = {
                    'MANHATTAN': list(range(1, 35)),
                    'BRONX': list(range(40, 53)),
                    'BROOKLYN': list(range(60, 95)),
                    'QUEENS': list(range(100, 116)),
                    'STATEN ISLAND': list(range(120, 124))
                }
                
                if view_type == "Borough Aggregate":
                    # Create borough-level geometries by dissolving precincts
                    # Fix any topology issues first by buffering with 0
                    gdf_clean = gdf[gdf['borough'].notna()].copy()
                    gdf_clean['geometry'] = gdf_clean['geometry'].buffer(0)
                    
                    # Dissolve by borough with grid_size to handle topology issues
                    gdf_borough = gdf_clean.dissolve(by='borough', as_index=False)
                    
                    # Merge with citation data
                    gdf_borough = gdf_borough.merge(borough_data, left_on='borough', right_on='county', how='left')
                    gdf_borough['citations'] = gdf_borough['citations'].fillna(0)
                    
                    # Create borough choropleth
                    fig = px.choropleth_mapbox(
                        gdf_borough,
                        geojson=gdf_borough.geometry.__geo_interface__,
                        locations=gdf_borough.index,
                        color='citations',
                        hover_name='borough',
                        hover_data={'citations': ':,', gdf_borough.index.name: False},
                        color_continuous_scale='RdYlGn_r',
                        mapbox_style='carto-positron',
                        center={'lat': 40.7128, 'lon': -74.0060},
                        zoom=9.5,
                        opacity=0.7,
                        title='NYC Parking Citations by Borough - Click a borough to drill down'
                    )
                    fig.update_layout(
                        height=600,
                        margin=dict(l=0, r=0, t=50, b=0)
                    )
                    
                    # Use Plotly events to capture clicks
                    selected = st.plotly_chart(fig, use_container_width=True, key="nyc_choropleth", on_select="rerun")
                    
                    # Handle click selection
                    if selected and 'selection' in selected and 'points' in selected['selection']:
                        points = selected['selection']['points']
                        if points:
                            clicked_idx = points[0]['location']
                            clicked_borough = gdf_borough.iloc[clicked_idx]['borough']
                            if pd.notna(clicked_borough):
                                st.session_state.selected_borough = clicked_borough
                                st.rerun()
                else:
                    # Precinct Detail View
                    # Merge citation data with geodata using filtered data
                    precinct_citations = filtered_df[pd.to_numeric(filtered_df['precinct'], errors='coerce').notna()].copy()
                    precinct_citations['precinct'] = pd.to_numeric(precinct_citations['precinct'], errors='coerce').astype(int)
                    precinct_agg = precinct_citations.groupby('precinct').size().reset_index(name='citations')
                    
                    gdf_merged = gdf.merge(precinct_agg, left_on='Precinct', right_on='precinct', how='left')
                    gdf_merged['citations'] = gdf_merged['citations'].fillna(0)
                    
                    # Create interactive choropleth with plotly
                    fig = px.choropleth_mapbox(
                        gdf_merged,
                        geojson=gdf_merged.geometry.__geo_interface__,
                        locations=gdf_merged.index,
                        color='citations',
                        hover_name='Precinct',
                        hover_data={'citations': ':,', 'borough': True, gdf_merged.index.name: False},
                        color_continuous_scale='RdYlGn_r',
                        mapbox_style='carto-positron',
                        center={'lat': 40.7128, 'lon': -74.0060},
                        zoom=9.5,
                        opacity=0.7,
                        title='NYC Parking Citations by Precinct - Click a precinct to drill down'
                    )
                    fig.update_layout(
                        height=600,
                        margin=dict(l=0, r=0, t=50, b=0)
                    )
                    
                    # Use Plotly events to capture clicks
                    selected = st.plotly_chart(fig, use_container_width=True, key="nyc_choropleth", on_select="rerun")
                    
                    # Handle click selection
                    if selected and 'selection' in selected and 'points' in selected['selection']:
                        points = selected['selection']['points']
                        if points:
                            clicked_idx = points[0]['location']
                            clicked_precinct = gdf_merged.iloc[clicked_idx]['Precinct']
                            clicked_borough = gdf_merged.iloc[clicked_idx]['borough']
                            if pd.notna(clicked_borough):
                                st.session_state.selected_borough = clicked_borough
                                st.rerun()
            else:
                # Fallback to bar chart if map fails
                borough_data = borough_data.sort_values('citations', ascending=True)
                
                fig = px.bar(
                    borough_data,
                    y='county',
                    x='citations',
                    orientation='h',
                    title='Citations by Borough - Click button below to drill down',
                    labels={'county': 'Borough', 'citations': 'Number of Citations'},
                    color='citations',
                    color_continuous_scale='RdYlGn_r'
                )
                fig.update_traces(
                    text=borough_data['citations'],
                    texttemplate='%{text:,}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Citations: %{x:,}<extra></extra>'
                )
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Number of Citations',
                    yaxis_title='',
                    coloraxis_showscale=False,
                    margin=dict(l=150, r=50, t=50, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True, key="borough_map")
            
            # No buttons needed - click the map to drill down
        except Exception as e:
            st.error(f"Error displaying borough map: {e}")
            st.write("Debug info:")
            st.write(f"Columns in df: {df.columns.tolist()}")
            st.write(f"Shape: {df.shape}")
            import traceback
            st.code(traceback.format_exc())
    
    # Precinct-level view (when borough is selected, but no specific precinct)
    elif st.session_state.selected_borough and not st.session_state.selected_precinct and 'precinct' in filtered_df.columns:
        try:
            # Back button
            if st.button("← Back to City View", key="back_btn"):
                st.session_state.selected_borough = None
                st.session_state.selected_precinct = None
                st.rerun()
            
            # Load cached GeoJSON
            gdf = load_geojson()
            
            # Use filtered_df instead of df for precinct data
            precinct_data = filtered_df.groupby('precinct').size().reset_index(name='citations')
            
            # Convert precinct to numeric and filter out invalid ones
            precinct_data['precinct'] = pd.to_numeric(precinct_data['precinct'], errors='coerce')
            precinct_data = precinct_data[precinct_data['precinct'].notna()]
            precinct_data = precinct_data[precinct_data['precinct'] > 0]  # Filter out invalid precincts
            precinct_data['precinct'] = precinct_data['precinct'].astype(int)
            
            # Create choropleth map
            if gdf is not None and 'Precinct' in gdf.columns:
                gdf['Precinct'] = pd.to_numeric(gdf['Precinct'], errors='coerce')
                
                # Merge citation data with geodata
                gdf_merged = gdf.merge(precinct_data, left_on='Precinct', right_on='precinct', how='left')
                gdf_merged['citations'] = gdf_merged['citations'].fillna(0)
                
                # Filter to only show precincts in selected borough
                borough_precinct_map = {
                    'MANHATTAN': list(range(1, 35)),
                    'BRONX': list(range(40, 53)),
                    'BROOKLYN': list(range(60, 95)),
                    'QUEENS': list(range(100, 116)),
                    'STATEN ISLAND': list(range(120, 124))
                }
                
                if st.session_state.selected_borough in borough_precinct_map:
                    valid_precincts = borough_precinct_map[st.session_state.selected_borough]
                    gdf_merged = gdf_merged[gdf_merged['Precinct'].isin(valid_precincts)]
                
                # Reset index after filtering to ensure click selection works correctly
                gdf_merged = gdf_merged.reset_index(drop=True)
                
                # Calculate center coordinates for the borough
                center_coords = {
                    'MANHATTAN': {'lat': 40.7831, 'lon': -73.9712},
                    'BRONX': {'lat': 40.8448, 'lon': -73.8648},
                    'BROOKLYN': {'lat': 40.6782, 'lon': -73.9442},
                    'QUEENS': {'lat': 40.7282, 'lon': -73.7949},
                    'STATEN ISLAND': {'lat': 40.5795, 'lon': -74.1502}
                }
                
                center = center_coords.get(st.session_state.selected_borough, {'lat': 40.7128, 'lon': -74.0060})
                
                # Create choropleth map - use reset index for locations
                fig = px.choropleth_mapbox(
                    gdf_merged,
                    geojson=gdf_merged.geometry.__geo_interface__,
                    locations=gdf_merged.index,
                    color='citations',
                    hover_name='Precinct',
                    hover_data={
                        'citations': ':,',
                        'Precinct': False  # Hide the index column
                    },
                    color_continuous_scale='RdYlGn_r',
                    mapbox_style='carto-positron',
                    center=center,
                    zoom=10.5,
                    opacity=0.7,
                    title=f'{st.session_state.selected_borough} - Click a precinct for details'
                )
                fig.update_layout(
                    height=600,
                    margin=dict(l=0, r=0, t=50, b=0)
                )
                
                # Enable click to select precinct
                selected = st.plotly_chart(fig, use_container_width=True, key="precinct_map", on_select="rerun")
                
                # Handle click selection - locations corresponds to the index we set
                if selected and 'selection' in selected and 'points' in selected['selection']:
                    points = selected['selection']['points']
                    if points and len(points) > 0:
                        # Try multiple possible keys for the index
                        point = points[0]
                        clicked_idx = point.get('pointNumber', point.get('pointIndex', point.get('location')))
                        
                        if clicked_idx is not None and clicked_idx < len(gdf_merged):
                            clicked_precinct = gdf_merged.iloc[clicked_idx]['Precinct']
                            if pd.notna(clicked_precinct):
                                st.session_state.selected_precinct = int(clicked_precinct)
                                st.rerun()
            else:
                # Fallback to bar chart if map fails
                precinct_data = precinct_data.sort_values('citations', ascending=True)
                precinct_data['precinct_str'] = precinct_data['precinct'].astype(str)
                
                fig = px.bar(
                    precinct_data,
                    y='precinct_str',
                    x='citations',
                    orientation='h',
                    title=f'Citations by Precinct in {st.session_state.selected_borough}',
                    labels={'precinct_str': 'Precinct', 'citations': 'Number of Citations'},
                    color='citations',
                    color_continuous_scale='RdYlGn_r'
                )
                fig.update_traces(
                    text=precinct_data['citations'],
                    texttemplate='%{text:,}',
                    textposition='outside',
                    hovertemplate='<b>Precinct %{y}</b><br>Citations: %{x:,}<extra></extra>'
                )
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Number of Citations',
                    yaxis_title='Precinct',
                    coloraxis_showscale=False,
                    margin=dict(l=80, r=50, t=50, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True, key="precinct_map")
            
            # Map interaction handles precinct selection
        except Exception as e:
            st.error(f"Error displaying precinct map: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Individual Precinct Detail View
    elif st.session_state.selected_precinct and 'precinct' in filtered_df.columns:
        try:
            # Back button
            if st.button("← Back to Borough View", key="back_precinct_btn"):
                st.session_state.selected_precinct = None
                st.rerun()
            
            precinct_num = st.session_state.selected_precinct
            st.markdown(f"## Precinct {precinct_num} - Detailed Analysis")
            st.caption(f"Borough: {st.session_state.selected_borough}")
            
            # Use filtered_df which already has precinct filter applied
            precinct_df = filtered_df.copy()
            
            if len(precinct_df) > 0:
                # Summary statistics in columns
                stat_cols = st.columns(5)
                
                total_citations = len(precinct_df)
                total_fines = precinct_df['fine_amount'].sum()
                avg_fine = precinct_df['fine_amount'].mean()
                
                # Peak hour
                if 'violation_hour' in precinct_df.columns:
                    peak_hour = precinct_df['violation_hour'].mode().iloc[0] if len(precinct_df['violation_hour'].mode()) > 0 else None
                else:
                    peak_hour = None
                
                # Top violation type
                if 'violation' in precinct_df.columns:
                    top_violation = precinct_df['violation'].mode().iloc[0] if len(precinct_df['violation'].mode()) > 0 else "N/A"
                else:
                    top_violation = "N/A"
                
                with stat_cols[0]:
                    st.metric("Total Citations", f"{total_citations:,}")
                with stat_cols[1]:
                    st.metric("Total Fines", f"${total_fines:,.0f}")
                with stat_cols[2]:
                    st.metric("Average Fine", f"${avg_fine:.0f}")
                with stat_cols[3]:
                    if peak_hour is not None:
                        st.metric("Peak Hour", f"{int(peak_hour)}:00")
                    else:
                        st.metric("Peak Hour", "N/A")
                with stat_cols[4]:
                    st.metric("Top Violation", top_violation[:15] if len(top_violation) > 15 else top_violation)
                
                # Time distribution charts
                st.markdown("### Time Distribution")
                chart_cols = st.columns(2)
                
                with chart_cols[0]:
                    # Hourly distribution
                    if 'violation_hour' in precinct_df.columns:
                        hourly_data = precinct_df.groupby('violation_hour').size().reset_index(name='citations')
                        
                        fig = px.bar(
                            hourly_data,
                            x='violation_hour',
                            y='citations',
                            title='Citations by Hour of Day',
                            labels={'violation_hour': 'Hour (24h)', 'citations': 'Citations'}
                        )
                        fig.update_traces(
                            marker_color='#3498db',  # Solid blue color
                            hovertemplate='<b>Hour %{x}:00</b><br>Citations: %{y:,}<extra></extra>'
                        )
                        fig.update_layout(
                            height=300,
                            showlegend=False,
                            xaxis_title='Hour of Day',
                            yaxis_title='Citations',
                            xaxis=dict(dtick=2, range=[-0.5, 23.5])
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with chart_cols[1]:
                    # Day of week distribution
                    if 'day_of_week' in precinct_df.columns:
                        dow_data = precinct_df.groupby('day_of_week').size().reset_index(name='citations')
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        dow_data['day_of_week'] = pd.Categorical(dow_data['day_of_week'], categories=day_order, ordered=True)
                        dow_data = dow_data.sort_values('day_of_week')
                        
                        fig = px.bar(
                            dow_data,
                            x='day_of_week',
                            y='citations',
                            title='Citations by Day of Week',
                            labels={'day_of_week': 'Day', 'citations': 'Citations'}
                        )
                        fig.update_traces(
                            marker_color='#27ae60',  # Solid green color
                            hovertemplate='<b>%{x}</b><br>Citations: %{y:,}<extra></extra>'
                        )
                        fig.update_layout(
                            height=300,
                            showlegend=False,
                            xaxis_title='',
                            yaxis_title='Citations'
                        )
                        fig.update_xaxes(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Top violations table
                st.markdown("### Top Violations")
                if 'violation' in precinct_df.columns:
                    violation_data = precinct_df.groupby('violation').agg({
                        'summons_number': 'count',
                        'fine_amount': 'sum'
                    }).reset_index()
                    violation_data.columns = ['Violation', 'Count', 'Total Fines']
                    violation_data = violation_data.sort_values('Count', ascending=False).head(10)
                    violation_data['Total Fines'] = violation_data['Total Fines'].apply(lambda x: f"${x:,.0f}")
                    st.dataframe(violation_data, use_container_width=True, hide_index=True)
            else:
                st.warning(f"No data available for Precinct {precinct_num}")
        except Exception as e:
            st.error(f"Error displaying precinct details: {e}")
            import traceback
            st.code(traceback.format_exc())

with time_col:
    st.subheader("Time Distribution")
    st.caption(f"For: **{selected_area}**")
    
    # Show hourly distribution for selected area
    if 'violation_hour' in filtered_df.columns:
        hourly_data = filtered_df.groupby('violation_hour').size().reset_index(name='citations')
        
        fig = px.bar(
            hourly_data,
            x='violation_hour',
            y='citations',
            title='Citations by Hour of Day',
            labels={'violation_hour': 'Hour (24h)', 'citations': 'Citations'}
        )
        fig.update_traces(
            marker_color='#3498db',  # Solid blue color
            hovertemplate='<b>Hour %{x}:00</b><br>Citations: %{y:,}<extra></extra>'
        )
        fig.update_layout(
            height=250,
            showlegend=False,
            xaxis_title='Hour of Day',
            yaxis_title='Citations',
            xaxis=dict(dtick=2, range=[-0.5, 23.5])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Show day of week distribution
    if 'issue_date' in filtered_df.columns:
        df_temp = filtered_df.copy()
        df_temp['day_of_week'] = df_temp['issue_date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = df_temp.groupby('day_of_week').size().reindex(day_order).fillna(0).reset_index(name='citations')
        
        fig = px.bar(
            dow_counts,
            x='day_of_week',
            y='citations',
            title='Citations by Day of Week',
            labels={'day_of_week': 'Day', 'citations': 'Citations'}
        )
        fig.update_traces(
            marker_color='#27ae60',  # Solid green color
            hovertemplate='<b>%{x}</b><br>Citations: %{y:,}<extra></extra>'
        )
        fig.update_layout(
            height=250,
            showlegend=False,
            xaxis_title='',
            yaxis_title='Citations',
            xaxis={'tickangle': -45}
        )
        st.plotly_chart(fig, use_container_width=True)

# Bottom section - summary stats for selected area
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
st.subheader(f"Summary Statistics: {selected_area}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Citations", f"{len(filtered_df):,}")

with col2:
    if 'fine_amount' in filtered_df.columns:
        total_fines = filtered_df['fine_amount'].sum()
        st.metric("Total Fines", f"${total_fines:,.0f}")

with col3:
    if 'issue_date' in filtered_df.columns:
        date_range = (filtered_df['issue_date'].max() - filtered_df['issue_date'].min()).days + 1
        st.metric("Date Range", f"{date_range} days")

with col4:
    if 'violation_description' in filtered_df.columns:
        top_violation = filtered_df['violation_description'].value_counts().index[0]
        st.metric("Top Violation", top_violation[:20] + "...")

# Top violations for selected area
if 'violation_description' in filtered_df.columns:
    st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
    st.subheader(f"Top 10 Violations in {selected_area}")
    top_violations = filtered_df['violation_description'].value_counts().head(10).reset_index()
    top_violations.columns = ['Violation', 'Count']
    
    fig = px.bar(
        top_violations,
        x='Count',
        y='Violation',
        orientation='h',
        color='Count',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False
    )
    fig.update_traces(
        texttemplate='%{x:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
    )
    st.plotly_chart(fig, use_container_width=True)

# State analysis (vehicle registration state)
if 'state' in filtered_df.columns:
    st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
    
    # Clean state field
    filtered_df['state'] = clean_state_field(filtered_df['state'])
    
    # Collapse section if state filter is active
    if st.session_state.selected_state:
        with st.expander(f"📊 Registration State Analysis (Filtered: {st.session_state.selected_state})", expanded=False):
            st.info(f"Currently viewing only citations from **{st.session_state.selected_state}** registered vehicles. Click 'Clear All Filters' to see all states.")
            st.metric("Citations from this state", f"{len(filtered_df):,}")
    else:
        st.subheader(f"📊 Top 15 Registration States in {selected_area}")
        st.caption("💡 Tip: Click any bar to filter by that state")
        
        # Get top 15 states
        top_states = filtered_df['state'].value_counts().head(15).reset_index()
        top_states.columns = ['State', 'Count']
        
        # Calculate percentage
        total_citations = len(filtered_df)
        top_states['Percentage'] = (top_states['Count'] / total_citations * 100).round(2)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart with solid color
            fig = px.bar(
                top_states,
                x='Count',
                y='State',
                orientation='h',
                title='Citation Count by Vehicle Registration State - Click a bar to filter'
            )
            fig.update_traces(
                marker_color='#3498db',  # Solid blue color
                texttemplate='%{x:,}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Citations: %{x:,}<br>👆 Click to filter<extra></extra>'
            )
            fig.update_layout(
                height=500,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Number of Citations',
                yaxis_title='State'
            )
            
            # Enable click interaction
            selected = st.plotly_chart(fig, use_container_width=True, key="state_chart", on_select="rerun")
            
            # Handle click to filter by state
            if selected and 'selection' in selected and 'points' in selected['selection']:
                points = selected['selection']['points']
                if points:
                    clicked_state = points[0]['y']
                    if clicked_state and clicked_state != 'UNKNOWN':
                        if st.session_state.selected_state == clicked_state:
                            # Click again to deselect
                            st.session_state.selected_state = None
                        else:
                            st.session_state.selected_state = clicked_state
                        st.rerun()
        
        with col2:
            # Summary statistics
            st.markdown("#### State Statistics")
            st.metric("Total States", filtered_df['state'].nunique())
            
            if len(top_states) > 0:
                st.metric("Top State", top_states.iloc[0]['State'])
                st.metric("Top State %", f"{top_states.iloc[0]['Percentage']:.1f}%")
                
                # Show top 5 with percentages
                st.markdown("**Top 5 States:**")
                for idx, row in top_states.head(5).iterrows():
                    st.write(f"**{row['State']}**: {row['Count']:,} ({row['Percentage']:.1f}%)")

# Issuing agency analysis
if 'issuing_agency' in filtered_df.columns:
    st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
    
    # Collapse section if agency filter is active
    if st.session_state.selected_agency:
        with st.expander(f"🏛️ Issuing Agency Analysis (Filtered: {st.session_state.selected_agency})", expanded=False):
            st.info(f"Currently viewing only citations issued by **{st.session_state.selected_agency}**. Click 'Clear All Filters' to see all agencies.")
            st.metric("Citations from this agency", f"{len(filtered_df):,}")
    else:
        st.subheader(f"🏛️ Citations by Issuing Agency in {selected_area}")
        st.caption("💡 Tip: Click any bar to filter by that agency")
        
        # Get agency breakdown
        agency_data = filtered_df['issuing_agency'].value_counts().reset_index()
        agency_data.columns = ['Agency', 'Count']
        
        # Calculate percentage
        total_citations = len(filtered_df)
        agency_data['Percentage'] = (agency_data['Count'] / total_citations * 100).round(2)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create visualization based on number of agencies
            if len(agency_data) <= 10:
                # Bar chart for few agencies with solid color
                fig = px.bar(
                    agency_data,
                    x='Count',
                    y='Agency',
                    orientation='h',
                    title='Citations by Issuing Agency - Click a bar to filter'
                )
                fig.update_traces(
                    marker_color='#27ae60',  # Solid green color
                    texttemplate='%{x:,}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Citations: %{x:,}<br>👆 Click to filter<extra></extra>'
                )
                fig.update_layout(
                    height=max(300, len(agency_data) * 60),
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Number of Citations',
                    yaxis_title='Agency'
                )
                
                # Enable click interaction
                selected = st.plotly_chart(fig, use_container_width=True, key="agency_chart_bar", on_select="rerun")
                
                # Handle click to filter by agency
                if selected and 'selection' in selected and 'points' in selected['selection']:
                    points = selected['selection']['points']
                    if points:
                        clicked_agency = points[0]['y']
                        if clicked_agency:
                            if st.session_state.selected_agency == clicked_agency:
                                # Click again to deselect
                                st.session_state.selected_agency = None
                            else:
                                st.session_state.selected_agency = clicked_agency
                            st.rerun()
            else:
                # Pie chart for many agencies (top 10 + Other)
                top_agencies = agency_data.head(10)
                other_count = agency_data.iloc[10:]['Count'].sum()
                
                if other_count > 0:
                    other_row = pd.DataFrame({'Agency': ['Other'], 'Count': [other_count], 'Percentage': [(other_count/total_citations*100)]})
                    plot_data = pd.concat([top_agencies, other_row], ignore_index=True)
                else:
                    plot_data = top_agencies
                
                fig = px.pie(
                    plot_data,
                    values='Count',
                    names='Agency',
                    title='Citations by Issuing Agency (Top 10) - Click a slice to filter',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Citations: %{value:,}<br>Percentage: %{percent}<br>👆 Click to filter<extra></extra>'
                )
                fig.update_layout(height=500)
                
                # Enable click interaction
                selected = st.plotly_chart(fig, use_container_width=True, key="agency_chart_pie", on_select="rerun")
                
                # Handle click to filter by agency
                if selected and 'selection' in selected and 'points' in selected['selection']:
                    points = selected['selection']['points']
                    if points:
                        clicked_agency = points[0]['label']
                        if clicked_agency and clicked_agency != 'Other':
                            if st.session_state.selected_agency == clicked_agency:
                                # Click again to deselect
                                st.session_state.selected_agency = None
                            else:
                                st.session_state.selected_agency = clicked_agency
                            st.rerun()
        
        with col2:
            # Summary statistics
            st.markdown("#### Agency Statistics")
            st.metric("Total Agencies", filtered_df['issuing_agency'].nunique())
            
            if len(agency_data) > 0:
                st.metric("Primary Agency", agency_data.iloc[0]['Agency'])
                st.metric("Primary %", f"{agency_data.iloc[0]['Percentage']:.1f}%")
                
                # Show all agencies with percentages
                st.markdown("**All Agencies:**")
                for idx, row in agency_data.iterrows():
                    st.write(f"**{row['Agency']}**: {row['Count']:,} ({row['Percentage']:.1f}%)")

# Footer
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
st.caption("Data source: NYC Open Data Portal | Dashboard built with Streamlit")
