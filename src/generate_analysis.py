"""
NYC Parking Citations - Daily Analysis Generator

Interactive script that prompts for a date or date range, fetches data from the API
one day at a time, cleans it, and generates a comprehensive analysis report.

Usage:
    python src/generate_analysis.py
"""

from pathlib import Path
import sys
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner


def get_user_input():
    """Get start/end dates from user."""
    print("\n" + "=" * 60)
    print("NYC PARKING ANALYSIS GENERATOR")
    print("=" * 60)
    print("\nThis tool will fetch, clean, and analyze parking citation data")
    print("for specific days.\n")
    
    def parse_date(prompt):
        while True:
            date_input = input(prompt).strip()
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d")
                if 2008 <= dt.year <= datetime.now().year:
                    return date_input
                print(f"Please enter a date between 2008-01-01 and {datetime.now().year}-12-31")
            except ValueError:
                print("Invalid input. Use YYYY-MM-DD.")
    
    start_date = parse_date("Enter start date (YYYY-MM-DD): ")
    end_date = parse_date("Enter end date (YYYY-MM-DD): ")
    
    if end_date < start_date:
        print("End date is before start date. Swapping them.")
        start_date, end_date = end_date, start_date
    
    return start_date, end_date


def get_date_list(start_date, end_date):
    """Return list of dates (YYYY-MM-DD) between start and end, inclusive."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    return [d.strftime("%Y-%m-%d") for d in dates]


def fetch_data_for_day(date_str):
    """Fetch data from NYC API for a single day."""
    print("\n" + "=" * 60)
    print("FETCHING DATA FROM NYC OPEN DATA API")
    print("=" * 60)
    print(f"Date: {date_str}")
    print("\nThis may take a few minutes...")
    
    loader = NYCParkingDataLoader()
    
    try:
        df = loader.load_by_day(date_str, limit=50000)
        
        if df is None or len(df) == 0:
            print(f"\nNo data found for {date_str}")
            return None
        
        # Save raw data
        raw_filename = f"parking_raw_citations_{date_str}_{len(df)}-records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        raw_filepath = RAW_DATA_DIR / raw_filename
        df.to_csv(raw_filepath, index=False)
        
        print(f"\nFetched {len(df):,} records")
        print(f"Saved to: {raw_filepath}")
        
        return raw_filepath
    
    except Exception as e:
        print(f"\nError fetching data: {e}")
        return None


def clean_data(raw_filepath, date_str=None):
    """Clean the raw data file."""
    print("\n" + "=" * 60)
    print("CLEANING DATA")
    print("=" * 60)
    
    cleaner = ParkingDataCleaner()
    clean_df = cleaner.run_full_pipeline(raw_filepath)
    
    if clean_df is None:
        print("\nData cleaning failed")
        return None
    
    # Save cleaned data with date in filename
    cleaned_filepath = cleaner.save_cleaned_data(date_str=date_str)
    
    # Save removal report with date in filename
    cleaner.save_removal_report(date_str=date_str)
    
    return cleaned_filepath, cleaner


def generate_analysis_report(cleaned_filepath, period_name, cleaner):
    """Generate a comprehensive analysis report."""
    print("\n" + "=" * 60)
    print("GENERATING ANALYSIS REPORT")
    print("=" * 60)
    
    df = pd.read_csv(cleaned_filepath)
    
    # Prepare report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_filename = f"analysis_report_citations_{period_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_filepath = REPORTS_DIR / report_filename
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC Parking Analysis Report - {period_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>NYC Parking Analysis Report</h1>
        <p><strong>Period:</strong> {period_name}</p>
        <p><strong>Generated:</strong> {timestamp}</p>
        
        <h2>Dataset Overview</h2>
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
"""
    
    # Temporal patterns
    if "day_of_week" in df.columns:
        html += """
        <h2>Temporal Patterns</h2>
        <h3>Day of Week Distribution</h3>
        <table>
            <tr>
                <th>Day</th>
                <th>Citations</th>
                <th>Percentage</th>
            </tr>
"""
        day_counts = df["day_of_week"].value_counts()
        for day, count in day_counts.items():
            pct = (count / len(df)) * 100
            html += f"""
            <tr>
                <td>{day}</td>
                <td>{count:,}</td>
                <td>{pct:.1f}%</td>
            </tr>
"""
        html += """
        </table>
"""
    
    # Time of day
    if "time_of_day" in df.columns:
        html += """
        <h3>Time of Day Distribution</h3>
        <table>
            <tr>
                <th>Time Period</th>
                <th>Citations</th>
                <th>Percentage</th>
            </tr>
"""
        time_counts = df["time_of_day"].value_counts()
        for time_period, count in time_counts.items():
            pct = (count / len(df)) * 100
            html += f"""
            <tr>
                <td>{time_period}</td>
                <td>{count:,}</td>
                <td>{pct:.1f}%</td>
            </tr>
"""
        html += """
        </table>
"""
    
    # Top violations
    if "violation" in df.columns:
        html += """
        <h2>Top Violations</h2>
        <table>
            <tr>
                <th>Violation Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""
        violation_counts = df["violation"].value_counts().head(10)
        for violation, count in violation_counts.items():
            pct = (count / len(df)) * 100
            html += f"""
            <tr>
                <td>{violation}</td>
                <td>{count:,}</td>
                <td>{pct:.1f}%</td>
            </tr>
"""
        html += """
        </table>
"""
    
    # Borough distribution
    if "county" in df.columns:
        html += """
        <h2>Borough Distribution</h2>
        <table>
            <tr>
                <th>Borough</th>
                <th>Citations</th>
                <th>Percentage</th>
            </tr>
"""
        borough_counts = df["county"].value_counts()
        for borough, count in borough_counts.items():
            pct = (count / len(df)) * 100
            html += f"""
            <tr>
                <td>{borough}</td>
                <td>{count:,}</td>
                <td>{pct:.1f}%</td>
            </tr>
"""
        html += """
        </table>
"""
    
    # Financial summary
    if "fine_amount" in df.columns:
        html += f"""
        <h2>Financial Summary</h2>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Total Fines</div>
                <div class="stat-value">${df['fine_amount'].sum():,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mean Fine</div>
                <div class="stat-value">${df['fine_amount'].mean():.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Median Fine</div>
                <div class="stat-value">${df['fine_amount'].median():.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Max Fine</div>
                <div class="stat-value">${df['fine_amount'].max():.2f}</div>
            </div>
        </div>
"""
    
    # Data quality summary
    html += f"""
        <h2>Data Quality</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Initial Records Fetched</td>
                <td>{cleaner.cleaning_report['initial_records']:,}</td>
            </tr>
            <tr>
                <td>Records Removed</td>
                <td>{cleaner.cleaning_report['initial_records'] - cleaner.cleaning_report['final_records']:,}</td>
            </tr>
            <tr>
                <td>Final Clean Records</td>
                <td>{cleaner.cleaning_report['final_records']:,}</td>
            </tr>
            <tr>
                <td>Retention Rate</td>
                <td>{(cleaner.cleaning_report['final_records'] / cleaner.cleaning_report['initial_records'] * 100):.2f}%</td>
            </tr>
        </table>
        
        <div class="footer">
            <p>Report generated: {timestamp}</p>
            <p>Data source: NYC Open Data (nc67-uf89)</p>
            <p>Cleaned data file: {cleaned_filepath.name}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save report
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nAnalysis report saved:")
    print(f"   {report_filepath}")
    print(f"   Open in browser to view")
    
    return report_filepath


def main():
    """Main execution flow."""
    # Get user input
    start_date, end_date = get_user_input()
    
    # Build date list
    date_list = get_date_list(start_date, end_date)
    
    # Confirm with user
    print(f"\nWill analyze {len(date_list)} day(s)")
    print(f"Date range: {start_date} to {end_date}")
    confirm = input("\nContinue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    generated = []
    
    for date_str in date_list:
        period_name = date_str
        
        # Fetch data for the day
        raw_filepath = fetch_data_for_day(date_str)
        if raw_filepath is None:
            continue
        
        # Clean data with date for better filenames
        result = clean_data(raw_filepath, date_str=date_str)
        if result is None:
            continue
        
        cleaned_filepath, cleaner = result
        
        # Generate analysis report
        report_filepath = generate_analysis_report(cleaned_filepath, period_name, cleaner)
        generated.append((raw_filepath, cleaned_filepath, report_filepath))
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    if not generated:
        print("\nNo reports generated.")
        return
    
    print(f"\nGenerated files ({len(generated)} day(s)):")
    for raw_filepath, cleaned_filepath, report_filepath in generated:
        print(f"   Raw data: {raw_filepath}")
        print(f"   Cleaned data: {cleaned_filepath}")
        print(f"   Analysis report: {report_filepath}")
    print(f"\nOpen the HTML report(s) in your browser to view results.")


if __name__ == "__main__":
    main()
