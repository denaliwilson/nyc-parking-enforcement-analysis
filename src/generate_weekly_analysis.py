"""
NYC Parking Citations - Weekly Analysis Generator with Visualizations

Fast analysis tool for weekly date ranges using optimized data loading and cleaning.
Generates comprehensive HTML reports with matplotlib visualizations embedded as base64 images.

Usage:
    python src/generate_weekly_analysis.py
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
    """Generate 6 visualizations as base64 embedded images."""
    graphs_html = '<div class="grid-2col">'
    
    # 1. Daily citation trend
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        daily_counts = df.groupby('issue_date').size()
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=8, color='#667eea')
        ax.fill_between(daily_counts.index, daily_counts.values, alpha=0.3, color='#667eea')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Daily Citation Trend', fontsize=13, fontweight='bold', pad=15)
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
            ax.text(i, v + 50, str(int(v)), ha='center', va='bottom', fontweight='bold')
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Day of Week"></div>'
    except Exception as e:
        print(f"Warning: Could not generate day of week graph: {e}")
    
    # 3. Top violations
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_violations = df['violation'].value_counts().head(8)
        colors_grad = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_violations)))
        ax.barh(range(len(top_violations)), top_violations.values, color=colors_grad, edgecolor='black', linewidth=1.2)
        ax.set_yticks(range(len(top_violations)))
        ax.set_yticklabels([v[:40] + '...' if len(v) > 40 else v for v in top_violations.index], fontsize=10)
        ax.set_xlabel('Number of Citations', fontsize=11, fontweight='bold')
        ax.set_title('Top 8 Violations', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        for i, v in enumerate(top_violations.values):
            ax.text(v + 50, i, str(int(v)), va='center', fontweight='bold')
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
            ax.text(i, v + 20, str(int(v)), ha='center', va='bottom', fontweight='bold')
        img_base64 = figure_to_base64(fig)
        graphs_html += f'<div class="chart-container"><img src="data:image/png;base64,{img_base64}" alt="Fine Distribution"></div>'
    except Exception as e:
        print(f"Warning: Could not generate fine distribution graph: {e}")
    
    graphs_html += '</div>'
    return graphs_html


def get_week_dates():
    """Get week dates for analysis with user input."""
    print("\n" + "=" * 60)
    print("NYC PARKING WEEKLY ANALYSIS")
    print("=" * 60)
    print("\nThis tool analyzes one week (7 days) of parking citations.")
    print("Enter the start date of the week.\n")
    
    while True:
        date_input = input("Enter week start date (YYYY-MM-DD): ").strip()
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            if 2008 <= dt.year <= datetime.now().year:
                start_date = date_input
                break
            print(f"Please enter a date between 2008-01-01 and {datetime.now().year}-12-31")
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD (e.g., 2025-12-30)")
    
    dates = [(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    # Confirm with user
    print(f"\nWill analyze week from {start_date} to {dates[-1]}")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    return start_date, dates


def fetch_week_data(dates):
    """Fetch data for all 7 days in the week."""
    print("\n" + "=" * 60)
    print("FETCHING WEEKLY DATA")
    print("=" * 60)
    print(f"Fetching {len(dates)} days of data...\n")
    
    loader = NYCParkingDataLoader()
    all_dfs = []
    failed_dates = []
    total_start = time.time()
    
    for i, date_str in enumerate(dates, 1):
        date_start = time.time()
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        
        try:
            df = loader.load_by_day(date_str, limit=50000)
            if df is None or len(df) == 0:
                print(f"  [{i}/7] {date_str} ({day_name:9s}): No data")
                failed_dates.append(date_str)
                continue
            elapsed = time.time() - date_start
            all_dfs.append(df)
            print(f"  [{i}/7] {date_str} ({day_name:9s}): {len(df):6,} records in {elapsed:5.1f}s")
        except Exception as e:
            print(f"  [{i}/7] {date_str} ({day_name:9s}): Error - {str(e)[:50]}")
            failed_dates.append(date_str)
    
    total_elapsed = time.time() - total_start
    
    if not all_dfs:
        print("\nERROR: No data fetched for any day")
        return None, None
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n{'='*60}")
    print(f"SUCCESS: Fetched {len(all_dfs)}/7 days")
    print(f"   Total records: {len(combined_df):,}")
    print(f"   Total time: {total_elapsed:.1f}s")
    if failed_dates:
        print(f"   Missing: {', '.join(failed_dates)}")
    
    return combined_df, total_elapsed


def clean_week_data(raw_df, start_date):
    """Clean the combined week data."""
    print(f"\n{'='*60}")
    print("CLEANING WEEKLY DATA")
    print(f"{'='*60}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    week_name = f"week_{start_date}_to_{(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')}"
    
    raw_filename = f"parking_raw_citations_{week_name}_{len(raw_df)}-records_{timestamp}.csv"
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
    cleaned_filepath = cleaner.save_cleaned_data(date_str=week_name)
    cleaner.save_removal_report(date_str=week_name)
    
    print(f"\nCleaning time: {clean_elapsed:.1f}s")
    
    return cleaned_filepath, cleaner


def generate_weekly_report(cleaned_filepath, week_name, cleaner):
    """Generate comprehensive HTML report with embedded graphs."""
    print(f"\n{'='*60}")
    print("GENERATING REPORT WITH VISUALIZATIONS")
    print(f"{'='*60}\n")
    
    df = pd.read_csv(cleaned_filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"analysis_report_citations_{week_name}_{timestamp}.html"
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
    <title>NYC Parking Weekly Analysis</title>
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
        <h1>NYC Parking Citations Weekly Analysis</h1>
        
        <div class="header-info">
            <strong>Period:</strong> {date_range} ({week_name})<br>
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
    
    start_date, dates = get_week_dates()
    
    raw_df, fetch_time = fetch_week_data(dates)
    if raw_df is None:
        print("\nERROR: Failed to fetch data")
        return
    
    week_name = f"week_{start_date}_to_{dates[-1]}"
    cleaned_filepath, cleaner = clean_week_data(raw_df, start_date)
    report_filepath = generate_weekly_report(cleaned_filepath, week_name, cleaner)
    
    total_elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("SUCCESS: WEEKLY ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"\nResults:")
    print(f"   Report: {report_filepath.name}")
    print(f"\nPerformance:")
    print(f"   Total time:    {total_elapsed:.1f}s")
    print(f"   Fetch time:    {fetch_time:.1f}s ({fetch_time/total_elapsed*100:.0f}%)")
    print(f"   Processing:    {total_elapsed-fetch_time:.1f}s ({(total_elapsed-fetch_time)/total_elapsed*100:.0f}%)")
    print(f"\nOpen report: {report_filepath}")


if __name__ == "__main__":
    main()
