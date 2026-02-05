"""
NYC Parking Citations - Interactive Dashboard
Loads data incrementally from NYC Open Data API by day
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
    return NYCParkingDataLoader()

@st.cache_resource
def get_cleaner():
    return ParkingDataCleaner()

@st.cache_data
def load_geojson():
    """Load and cache NYC precinct GeoJSON data"""
    import geopandas as gpd
    import requests
    
    geospatial_dir = GEOSPATIAL_DATA_DIR
    precinct_file = geospatial_dir / 'nyc_precincts.geojson'
    
    if precinct_file.exists():
        gdf = gpd.read_file(precinct_file)
    else:
        url = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Police_Precincts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            geojson_data = response.json()
            gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
            gdf.to_file(precinct_file, driver='GeoJSON')
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
    # No data loaded - show prominent date selector landing page
    st.title("NYC Parking Citations Dashboard")
    st.markdown("### Select Date Range to Begin")
    st.markdown("Load NYC parking citation data to explore interactive maps and analytics.")
    
    st.markdown("---")
    
    # Center the date selection in main area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Default dates
        default_date = datetime(2025, 12, 30).date()
        max_available_date = datetime.now().date() - timedelta(days=2)
        
        st.info("**Tip:** NYC data is typically 2-3 days behind. Try dates from 2025.")
        
        # Quick selection buttons in a more prominent way
        st.markdown("#### Quick Select:")
        quick_cols = st.columns(2)
        
        with quick_cols[0]:
            if st.button("Last Week", use_container_width=True, type="secondary"):
                st.session_state.quick_select = "week"
        
        with quick_cols[1]:
            if st.button("Last Month", use_container_width=True, type="secondary"):
                st.session_state.quick_select = "month"
        
        st.markdown("#### Or Choose Custom:")
        
        # Handle quick select first
        if 'quick_select' in st.session_state:
            if st.session_state.quick_select == "week":
                end_date = default_date
                start_date = end_date - timedelta(days=6)
                st.info(f"Will load: {start_date} to {end_date}")
                date_option = "quick_week"
            elif st.session_state.quick_select == "month":
                end_date = default_date
                start_date = end_date - timedelta(days=29)
                st.info(f"Will load: {start_date} to {end_date}")
                date_option = "quick_month"
        else:
            # Date selection
            date_option = st.radio(
                "Select mode:",
                options=["Single day", "Last 3 days", "Custom range"],
                horizontal=True
            )
        
        if date_option == "Single day":
            selected_date = st.date_input(
                "Select date:",
                value=default_date,
                max_value=max_available_date,
                help="Choose a date from 2019-2025 for best results"
            )
            start_date = end_date = selected_date
            
        elif date_option == "Last 3 days":
            end_date = default_date
            start_date = end_date - timedelta(days=2)
            st.info(f"Will load: {start_date} to {end_date}")
            
        elif date_option == "quick_week":
            # Already set by quick select, just pass through
            pass
            
        elif date_option == "quick_month":
            # Already set by quick select, just pass through
            pass
            
        else:  # Custom range
            date_range = st.date_input(
                "Select custom range:",
                value=(default_date - timedelta(days=2), default_date),
                max_value=max_available_date,
                help="NYC data is most complete for dates before today"
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = default_date
        
        st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
        
        # Load button - prominent and centered
        if st.button("Load Data & Start Analysis", type="primary", use_container_width=True):
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
            if 'quick_select' in st.session_state:
                del st.session_state.quick_select
            st.rerun()
    
    # Stop execution to show landing page
    st.stop()

# Top metrics
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

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

# Create two columns for map and time chart
map_col, time_col = st.columns([3, 2])

with map_col:
    st.subheader("NYC Parking Citations Map")
    
    # Determine what level we're viewing
    if st.session_state.selected_precinct:
        view_level = "Precinct"
        selected_area = f"Precinct {st.session_state.selected_precinct}"
        # Convert precinct to numeric for proper filtering
        filtered_df = df[pd.to_numeric(df['precinct'], errors='coerce') == st.session_state.selected_precinct] if 'precinct' in df.columns else df
    elif st.session_state.selected_borough:
        view_level = "Borough (Precincts)"
        selected_area = st.session_state.selected_borough
        filtered_df = df[df['county'] == st.session_state.selected_borough] if 'county' in df.columns else df
    else:
        view_level = "NYC (Boroughs)"
        selected_area = "All NYC"
        filtered_df = df
    
    st.caption(f"Viewing: **{selected_area}** | Level: {view_level}")
    
    # Add reset button if we've drilled down
    if st.session_state.selected_borough or st.session_state.selected_precinct:
        if st.button("← Reset to NYC View"):
            st.session_state.selected_borough = None
            st.session_state.selected_precinct = None
            st.rerun()
    
    # Borough-level view (city-wide)
    if not st.session_state.selected_borough and not st.session_state.selected_precinct and 'county' in df.columns:
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
            
            # Create borough aggregation
            borough_data = df.groupby('county').size().reset_index(name='citations')
            
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
                    # Merge citation data with geodata
                    precinct_citations = df[pd.to_numeric(df['precinct'], errors='coerce').notna()].copy()
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
    elif st.session_state.selected_borough and not st.session_state.selected_precinct and 'precinct' in df.columns:
        try:
            # Back button
            if st.button("← Back to City View", key="back_btn"):
                st.session_state.selected_borough = None
                st.session_state.selected_precinct = None
                st.rerun()
            
            # Load cached GeoJSON
            gdf = load_geojson()
            
            borough_df = df[df['county'] == st.session_state.selected_borough]
            precinct_data = borough_df.groupby('precinct').size().reset_index(name='citations')
            
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
    elif st.session_state.selected_precinct and 'precinct' in df.columns:
        try:
            # Back button
            if st.button("← Back to Borough View", key="back_precinct_btn"):
                st.session_state.selected_precinct = None
                st.rerun()
            
            precinct_num = st.session_state.selected_precinct
            st.markdown(f"## Precinct {precinct_num} - Detailed Analysis")
            st.caption(f"Borough: {st.session_state.selected_borough}")
            
            # Filter data for this precinct
            precinct_df = df[pd.to_numeric(df['precinct'], errors='coerce') == precinct_num].copy()
            
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

# Data preview
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
with st.expander("View Raw Data"):
    st.dataframe(filtered_df.head(1000), use_container_width=True)
    st.caption(f"Showing first 1,000 of {len(filtered_df):,} records for {selected_area}")

# Footer
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
st.caption("Data source: NYC Open Data Portal | Dashboard built with Streamlit")
