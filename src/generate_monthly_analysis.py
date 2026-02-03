"""
NYC Parking Citations - Monthly Analysis Generator with Visualizations

Analyzes an entire month of parking citation data with comprehensive visualizations.
Uses optimized data loading and cleaning pipeline.

Usage:
    python src/generate_monthly_analysis.py
"""

from pathlib import Path
import sys
from datetime import datetime, timedelta
import pandas as pd
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import calendar

sys.path.append(str(Path(__file__).parent.parent))
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner

plt.style.use('seaborn-v0_8-darkgrid')
import warnings
warnings.filterwarnings('ignore')


def figure_to_base64(fig):
    """Convert matplotlib figure to base64 for HTML embedding."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return image_base64


def generate_graphs(df):
    """Generate visualizations for monthly data."""
    graphs_html = '<div class="grid-2col">'
    
    # 1. Daily citation trend
    try:
        fig, ax = plt.subplots(figsize=(12, 5))
        daily_counts = df.groupby('issue_date').size()
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6, color='#667eea')
        ax.fill_between(daily_counts.index, daily_counts.values, alpha=0.3, color='#667eea')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Daily Citation Trend Throughout Month', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Daily Trend"></div>'
    except Exception as e:
        print(f"Warning: Could not generate daily trend graph: {e}")
    
    # 2. Day of week distribution
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df['day_of_week'].value_counts().reindex(day_order)
        colors = ['#667eea' if day not in ['Saturday', 'Sunday'] else '#764ba2' for day in day_order]
        ax.bar(range(len(day_counts)), day_counts.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_xticks(range(len(day_counts)))
        ax.set_xticklabels(day_order, rotation=45, ha='right')
        ax.set_ylabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Citations by Day of Week', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(day_counts.values):
            ax.text(i, v + max(day_counts.values)*0.02, f'{int(v):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Day of Week"></div>'
    except Exception as e:
        print(f"Warning: Could not generate day of week graph: {e}")
    
    # 3. Top violations
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_violations = df['violation'].value_counts().head(10)
        colors_grad = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_violations)))
        ax.barh(range(len(top_violations)), top_violations.values, color=colors_grad, edgecolor='black', linewidth=1.2)
        ax.set_yticks(range(len(top_violations)))
        ax.set_yticklabels([v[:45] + '...' if len(v) > 45 else v for v in top_violations.index], fontsize=9)
        ax.set_xlabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Top 10 Violations', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        for i, v in enumerate(top_violations.values):
            ax.text(v + max(top_violations.values)*0.01, i, f'{int(v):,}', va='center', fontweight='bold', fontsize=8)
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Top Violations"></div>'
    except Exception as e:
        print(f"Warning: Could not generate violations graph: {e}")
    
    # 4. Hourly distribution
    try:
        if 'violation_hour' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 5))
            hourly_counts = df['violation_hour'].value_counts().sort_index()
            colors_hour = ['#764ba2' if h in [0, 1, 2, 3, 4, 5, 23] else '#667eea' for h in hourly_counts.index]
            ax.bar(hourly_counts.index, hourly_counts.values, color=colors_hour, alpha=0.8, width=0.8, edgecolor='black', linewidth=0.5)
            ax.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
            ax.set_ylabel('Number of Citations', fontsize=11, fontweight='bold')
            ax.set_title('Citations by Hour (Night hours in purple)', fontsize=13, fontweight='bold', pad=15)
            ax.set_xticks(range(0, 24))
            ax.grid(True, alpha=0.3, axis='y')
            img_base64 = figure_to_base64(fig)
            graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Hourly Distribution"></div>'
    except Exception as e:
        print(f"Warning: Could not generate hourly graph: {e}")
    
    # 5. Borough distribution (pie chart)
    try:
        if 'county' in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            borough_counts = df['county'].value_counts()
            colors_borough = plt.cm.Set3(np.linspace(0, 1, len(borough_counts)))
            ax.pie(borough_counts.values, labels=borough_counts.index, autopct='%1.1f%%', 
                   colors=colors_borough, startangle=90, 
                   textprops={'fontsize': 10, 'fontweight': 'bold'})
            ax.set_title('Citations by Borough', fontsize=13, fontweight='bold', pad=15)
            img_base64 = figure_to_base64(fig)
            graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Borough Distribution"></div>'
    except Exception as e:
        print(f"Warning: Could not generate borough graph: {e}")
    
    # 6. Fine amount distribution
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        fine_bins = [0, 50, 100, 150, 200, 300, 500, 10000]
        fine_labels = ['0-50', '50-100', '100-150', '150-200', '200-300', '300-500', '500+']
        df_copy = df.copy()
        df_copy['fine_bin'] = pd.cut(df_copy['fine_amount'], bins=fine_bins, labels=fine_labels)
        fine_dist = df_copy['fine_bin'].value_counts().sort_index()
        ax.bar(range(len(fine_dist)), fine_dist.values, color='#667eea', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_xticks(range(len(fine_dist)))
        ax.set_xticklabels(fine_dist.index, rotation=45, ha='right')
        ax.set_ylabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Fine Amount Distribution ($)', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(fine_dist.values):
            ax.text(i, v + max(fine_dist.values)*0.02, f'{int(v):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Fine Distribution"></div>'
    except Exception as e:
        print(f"Warning: Could not generate fine distribution graph: {e}")
    
    # 7. Precinct distribution bar chart
    try:
        if 'precinct' in df.columns and df['precinct'].notna().sum() > 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            precinct_counts = df[df['precinct'] != 0]['precinct'].value_counts().head(20)
            colors_precinct = plt.cm.viridis(np.linspace(0.2, 0.9, len(precinct_counts)))
            y_pos = np.arange(len(precinct_counts))
            ax.barh(y_pos, precinct_counts.values, color=colors_precinct, alpha=0.8, edgecolor='black', linewidth=0.5)
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f'Precinct {int(p)}' for p in precinct_counts.index])
            ax.set_xlabel('Number of Citations', fontsize=11, fontweight='bold')
            precinct_0_count = (df['precinct'] == 0).sum()
            title = f'Top 20 Precincts by Citation Count\\n(Excludes {precinct_0_count:,} entries with missing precinct data)'
            ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3, axis='x')
            for i, v in enumerate(precinct_counts.values):
                ax.text(v + max(precinct_counts.values)*0.01, i, f'{int(v):,}', va='center', fontweight='bold', fontsize=9)
            img_base64 = figure_to_base64(fig)
            graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Precinct Distribution"></div>'
    except Exception as e:
        print(f"Warning: Could not generate precinct bar chart: {e}")
    
    # 8. Precinct choropleth map
    try:
        if 'precinct' in df.columns and df['precinct'].notna().sum() > 0:
            import geopandas as gpd
            import requests
            
            print("  Downloading precinct boundaries...")
            url = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Police_Precincts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                geojson_data = response.json()
                gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
                
                # Find precinct column
                precinct_col = None
                for col in gdf.columns:
                    if 'precinct' in col.lower():
                        precinct_col = col
                        break
                
                if precinct_col:
                    # Aggregate citations by precinct
                    precinct_citations = df[df['precinct'] != 0].groupby('precinct').size().reset_index(name='citations')
                    precinct_citations['precinct'] = precinct_citations['precinct'].astype(int)
                    
                    # Merge with geodata
                    gdf[precinct_col] = gdf[precinct_col].astype(int)
                    gdf = gdf.merge(precinct_citations, left_on=precinct_col, right_on='precinct', how='left')
                    gdf['citations'] = gdf['citations'].fillna(0)
                    
                    # Create choropleth
                    fig, ax = plt.subplots(figsize=(12, 10))
                    gdf.plot(column='citations', ax=ax, legend=True, cmap='YlOrRd', 
                            edgecolor='black', linewidth=0.5,
                            legend_kwds={'label': 'Number of Citations', 'orientation': 'horizontal', 'shrink': 0.8})
                    
                    # Add precinct labels
                    for idx, row in gdf.iterrows():
                        if row['citations'] > 0:
                            centroid = row.geometry.centroid
                            ax.text(centroid.x, centroid.y, f"{int(row[precinct_col])}", 
                                   fontsize=8, ha='center', va='center', fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))
                    
                    ax.set_title('Citations by Police Precinct - Color-Coded Map', fontsize=14, fontweight='bold', pad=15)
                    ax.axis('off')
                    
                    img_base64 = figure_to_base64(fig)
                    graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Precinct Map"></div>'
                    print("  Map generated successfully")
    except Exception as e:
        print(f"Warning: Could not generate precinct map: {e}")
    
    graphs_html += '</div>'
    return graphs_html


def get_month_dates():
    """Get all dates in selected month with user input."""
    print("\n" + "=" * 60)
    print("NYC PARKING MONTHLY ANALYSIS")
    print("=" * 60)
    print("\nThis tool analyzes one full month of parking citations.")
    print("Data available from 2008 to present.\n")
    
    while True:
        year_input = input("Enter year (YYYY): ").strip()
        try:
            year = int(year_input)
            if 2008 <= year <= datetime.now().year:
                break
            print(f"Please enter a year between 2008 and {datetime.now().year}")
        except ValueError:
            print("Invalid year. Use 4-digit format (e.g., 2025)")
    
    while True:
        month_input = input("Enter month (1-12): ").strip()
        try:
            month = int(month_input)
            if 1 <= month <= 12:
                break
            print("Please enter a month between 1 and 12")
        except ValueError:
            print("Invalid month. Use number 1-12")
    
    # Generate all dates in month
    num_days = calendar.monthrange(year, month)[1]
    dates = [
        datetime(year, month, day).strftime("%Y-%m-%d")
        for day in range(1, num_days + 1)
    ]
    
    month_name = datetime(year, month, 1).strftime("%B %Y")
    print(f"\nWill analyze {month_name} ({num_days} days)")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    return dates, year, month


def fetch_month_data(dates):
    """Fetch data for all days in the month."""
    print("\n" + "=" * 60)
    print(f"FETCHING MONTHLY DATA ({len(dates)} days)")
    print("=" * 60)
    
    loader = NYCParkingDataLoader()
    all_dfs = []
    failed_dates = []
    total_start = time.time()
    
    for i, date_str in enumerate(dates, 1):
        date_start = time.time()
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")
        
        try:
            df = loader.load_by_day(date_str, limit=50000)
            if df is None or len(df) == 0:
                print(f"  [{i:2d}/{len(dates)}] {date_str} ({day_name}): No data")
                failed_dates.append(date_str)
                continue
            elapsed = time.time() - date_start
            all_dfs.append(df)
            print(f"  [{i:2d}/{len(dates)}] {date_str} ({day_name}): {len(df):6,} records in {elapsed:5.1f}s")
        except Exception as e:
            print(f"  [{i:2d}/{len(dates)}] {date_str} ({day_name}): Error - {str(e)[:50]}")
            failed_dates.append(date_str)
    
    total_elapsed = time.time() - total_start
    
    if not all_dfs:
        print("\nERROR: No data fetched for any day")
        return None, None
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n{'='*60}")
    print(f"SUCCESS: Fetched {len(all_dfs)}/{len(dates)} days")
    print(f"   Total records: {len(combined_df):,}")
    print(f"   Total time: {total_elapsed:.1f}s")
    if failed_dates:
        print(f"   Missing days: {len(failed_dates)}")
    
    return combined_df, total_elapsed


def clean_month_data(raw_df, year, month):
    """Clean the combined month data."""
    print(f"\n{'='*60}")
    print("CLEANING MONTHLY DATA")
    print(f"{'='*60}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    month_name = f"month_{year}-{month:02d}"
    
    raw_filename = f"parking_raw_citations_{month_name}_{len(raw_df)}-records_{timestamp}.csv"
    raw_filepath = RAW_DATA_DIR / raw_filename
    raw_df.to_csv(raw_filepath, index=False)
    
    print(f"Raw data saved: {raw_filename}")
    print(f"   Records: {len(raw_df):,}")
    
    clean_start = time.time()
    cleaner = ParkingDataCleaner()
    cleaner.raw_df = raw_df
    cleaner.cleaning_report['initial_records'] = len(raw_df)
    
    cleaner.check_data_quality()
    cleaner.clean_dates()
    cleaner.clean_categorical_fields()
    cleaner.clean_numeric_fields()
    cleaner.remove_duplicates()
    cleaner.create_derived_features()
    cleaner.finalize_cleaning()
    
    clean_elapsed = time.time() - clean_start
    cleaned_filepath = cleaner.save_cleaned_data(date_str=month_name)
    cleaner.save_removal_report(date_str=month_name)
    
    print(f"\nCleaning time: {clean_elapsed:.1f}s")
    
    return cleaned_filepath, cleaner


def generate_monthly_report(cleaned_filepath, year, month, cleaner):
    """Generate comprehensive HTML report with embedded graphs."""
    print(f"\n{'='*60}")
    print("GENERATING REPORT WITH VISUALIZATIONS")
    print(f"{'='*60}\n")
    
    df = pd.read_csv(cleaned_filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    month_name = datetime(year, month, 1).strftime("%B_%Y")
    report_filename = f"analysis_report_citations_month_{year}-{month:02d}_{timestamp}.html"
    report_filepath = REPORTS_DIR / report_filename
    
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    date_range = f"{df['issue_date'].min().strftime('%Y-%m-%d')} to {df['issue_date'].max().strftime('%Y-%m-%d')}"
    
    print("  Generating visualizations...")
    graphs_html = generate_graphs(df)
    print("  SUCCESS: Graphs created")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC Parking Monthly Analysis - {month_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 35px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        .header-info {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.95;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .grid-2col {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            font-size: 12px;
            color: #7f8c8d;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>NYC Parking Citations Monthly Analysis</h1>
        
        <div class="header-info">
            <strong>Period:</strong> {month_name.replace('_', ' ')} ({date_range})<br>
            <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        
        <h2>Key Metrics</h2>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Total Citations</div>
                <div class="stat-value">{len(df):,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Unique Violations</div>
                <div class="stat-value">{df['violation'].nunique() if 'violation' in df.columns else 'N/A'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Fines</div>
                <div class="stat-value">${df['fine_amount'].sum():,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Fine</div>
                <div class="stat-value">${df['fine_amount'].mean():.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Daily Average</div>
                <div class="stat-value">{len(df)/df['issue_date'].nunique():,.0f}</div>
            </div>
        </div>
        
        <h2>Visualizations</h2>
        {graphs_html}
"""
    
    # Day of week table
    if 'day_of_week' in df.columns:
        html += "<h2>Day of Week Distribution</h2><table><tr><th>Day</th><th>Citations</th><th>Percentage</th><th>Avg Fine</th></tr>"
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in day_order:
            day_data = df[df['day_of_week'] == day]
            if len(day_data) > 0:
                count = len(day_data)
                pct = (count / len(df)) * 100
                avg_fine = day_data['fine_amount'].mean()
                html += f"<tr><td><strong>{day}</strong></td><td>{count:,}</td><td>{pct:.1f}%</td><td>${avg_fine:.2f}</td></tr>"
        html += "</table>"
    
    # Top violations table
    if 'violation' in df.columns:
        html += "<h2>Top 10 Violations</h2><table><tr><th>Violation Type</th><th>Count</th><th>Percentage</th><th>Avg Fine</th></tr>"
        for violation, count in df['violation'].value_counts().head(10).items():
            pct = (count / len(df)) * 100
            avg_fine = df[df['violation'] == violation]['fine_amount'].mean()
            html += f"<tr><td>{violation}</td><td>{count:,}</td><td>{pct:.1f}%</td><td>${avg_fine:.2f}</td></tr>"
        html += "</table>"
    
    # Borough table
    if 'county' in df.columns:
        html += "<h2>Borough Distribution</h2><table><tr><th>Borough</th><th>Citations</th><th>Percentage</th><th>Avg Fine</th></tr>"
        for borough, count in df['county'].value_counts().items():
            pct = (count / len(df)) * 100
            avg_fine = df[df['county'] == borough]['fine_amount'].mean()
            html += f"<tr><td>{borough}</td><td>{count:,}</td><td>{pct:.1f}%</td><td>${avg_fine:.2f}</td></tr>"
        html += "</table>"
    
    # Data quality
    html += f"""
        <h2>Data Quality Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Initial Records</td><td>{cleaner.cleaning_report['initial_records']:,}</td></tr>
            <tr><td>Records Removed</td><td>{cleaner.cleaning_report['initial_records'] - cleaner.cleaning_report['final_records']:,}</td></tr>
            <tr><td>Final Clean Records</td><td>{cleaner.cleaning_report['final_records']:,}</td></tr>
            <tr><td>Retention Rate</td><td>{(cleaner.cleaning_report['final_records'] / cleaner.cleaning_report['initial_records'] * 100):.2f}%</td></tr>
        </table>
        
        <div class="footer">
            <p>Report: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Data: NYC Open Data (nc67-uf89)</p>
            <p>File: {cleaned_filepath.name}</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"SUCCESS: Report saved to {report_filename}")
    return report_filepath


def main():
    """Main workflow."""
    start_time = time.time()
    
    dates, year, month = get_month_dates()
    
    raw_df, fetch_time = fetch_month_data(dates)
    if raw_df is None:
        print("\nERROR: Failed to fetch data")
        return
    
    cleaned_filepath, cleaner = clean_month_data(raw_df, year, month)
    report_filepath = generate_monthly_report(cleaned_filepath, year, month, cleaner)
    
    total_elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("SUCCESS: MONTHLY ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"\nResults:")
    print(f"   Report: {report_filepath.name}")
    print(f"\nPerformance:")
    print(f"   Total time:    {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"   Fetch time:    {fetch_time:.1f}s ({fetch_time/60:.1f} minutes)")
    print(f"   Processing:    {total_elapsed-fetch_time:.1f}s")
    print(f"\nOpen report: {report_filepath}")


if __name__ == "__main__":
    main()
