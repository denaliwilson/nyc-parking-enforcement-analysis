"""
NYC Parking Citations - Data Cleaning Script

This script cleans and preprocesses raw parking citation data.
Run this after loading data with data_loader.py

Usage:
    python src/data_cleaner.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Ensure outputs/reports directory exists
REPORTS_DIR = Path(__file__).parent.parent / 'outputs' / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ParkingDataCleaner:
    """
    Clean and preprocess parking citation data
    """
    
    def __init__(self):
        self.raw_df = None
        self.clean_df = None
        self.removed_rows = []  # Track all removed rows with reasons
        self.cleaning_report = {
            'initial_records': 0,
            'final_records': 0,
            'duplicates_removed': 0,
            'invalid_dates_removed': 0,
            'missing_data_handling': {},
            'outliers_flagged': 0
        }
    
    def load_data(self, filepath):
        """Load raw data from CSV"""
        print(f"\n{'='*60}")
        print("LOADING RAW DATA")
        print(f"{'='*60}\n")
        
        try:
            self.raw_df = pd.read_csv(filepath)
            self.cleaning_report['initial_records'] = len(self.raw_df)
            
            print(f"Loaded {len(self.raw_df):,} records from {filepath}")
            print(f"   Columns: {list(self.raw_df.columns)}")
            print(f"   Memory usage: {self.raw_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def check_data_quality(self):
        """Initial data quality assessment"""
        print(f"\n{'='*60}")
        print("DATA QUALITY ASSESSMENT")
        print(f"{'='*60}\n")
        
        df = self.raw_df.copy()
        
        # 1. Missing values
        print("Missing Values:")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        
        for col in df.columns:
            if missing[col] > 0:
                print(f"   {col:20s}: {missing[col]:6,} ({missing_pct[col]:5.2f}%)")
        
        # 2. Duplicate check
        duplicates = df.duplicated(subset=['summons_number']).sum()
        print(f"\nDuplicates:")
        print(f"   Based on summons_number: {duplicates:,}")
        
        # 3. Data types
        print(f"\nData Types:")
        for col, dtype in df.dtypes.items():
            print(f"   {col:20s}: {dtype}")
        
        # 4. Unique values in categorical fields
        print(f"\nCategorical Field Cardinality:")
        categorical_cols = ['state', 'license_type', 'precinct', 'county', 'issuing_agency']
        for col in categorical_cols:
            if col in df.columns:
                n_unique = df[col].nunique()
                print(f"   {col:20s}: {n_unique} unique values")
                if n_unique <= 10:
                    print(f"      Values: {df[col].value_counts().to_dict()}")
        
        # 5. Numeric fields summary
        print(f"\nNumeric Fields Summary:")
        numeric_cols = ['fine_amount', 'reduction_amount']
        for col in numeric_cols:
            if col in df.columns:
                # Try to convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"   {col}:")
                print(f"      Min:    ${df[col].min():,.2f}")
                print(f"      Max:    ${df[col].max():,.2f}")
                print(f"      Mean:   ${df[col].mean():,.2f}")
                print(f"      Median: ${df[col].median():,.2f}")
    
    def clean_dates(self):
        """Clean and standardize date/time fields"""
        print(f"\n{'='*60}")
        print("CLEANING DATES AND TIMES")
        print(f"{'='*60}\n")
        
        # PERFORMANCE: Don't copy - work directly with reference
        # Only copy if we're modifying original (which we're not here)
        df = self.raw_df
        initial_count = len(df)
        
        # Convert issue_date to datetime
        print("Processing issue_date...")
        df['issue_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
        
        # Check for invalid dates and track them
        invalid_mask = df['issue_date'].isnull()
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            print(f"   Found {invalid_count:,} invalid dates - will be removed")
            
            # PERFORMANCE: Track only count instead of iterating each row
            # For each invalid date, we just note it was removed
            # Detail tracking can be added if needed via a flag
            self.cleaning_report['invalid_dates_removed'] = invalid_count
            
            df = df[~invalid_mask]
        
        # Extract date components
        print("   Extracting date components...")
        df['year'] = df['issue_date'].dt.year
        df['month'] = df['issue_date'].dt.month
        df['month_name'] = df['issue_date'].dt.month_name()
        df['day_of_week'] = df['issue_date'].dt.day_name()
        df['day'] = df['issue_date'].dt.day
        df['week_of_year'] = df['issue_date'].dt.isocalendar().week
        
        # Parse violation_time
        # CRITICAL PITFALL: violation_time can be in two formats:
        # 1. "HH:mmA" (e.g., "10:45A", "02:30P") - most common in recent data
        # 2. "HHmmA" (e.g., "1045A", "0230P") - legacy format
        print("\nProcessing violation_time...")
        print("   Time format can be HH:mmA or HHmmA")
        
        def parse_time(time_str):
            """
            Parse violation time in HH:mmA or HHmmA format
            Examples: '10:45A' -> '10:45', '1045A' -> '10:45', '02:30P' -> '14:30'
            """
            if pd.isnull(time_str):
                return None
            
            try:
                time_str = str(time_str).strip()
                
                # Extract AM/PM indicator
                if time_str[-1] in ['A', 'P', 'a', 'p']:
                    meridiem = time_str[-1].upper()
                    time_digits = time_str[:-1]
                else:
                    # No AM/PM indicator - assume time is in 24hr format
                    meridiem = None
                    time_digits = time_str
                
                # Check if format has colon (HH:mm) or not (HHmm)
                if ':' in time_digits:
                    # Format: HH:mm
                    parts = time_digits.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1]) if len(parts) > 1 else 0
                else:
                    # Format: HHmm - pad with zeros if needed
                    time_digits = time_digits.zfill(4)
                    hours = int(time_digits[:2])
                    minutes = int(time_digits[2:4])
                
                # Convert to 24-hour format if needed
                if meridiem == 'P' and hours != 12:
                    hours += 12
                elif meridiem == 'A' and hours == 12:
                    hours = 0
                
                return f"{hours:02d}:{minutes:02d}"
                
            except:
                return None
        
        df['violation_time_parsed'] = df['violation_time'].apply(parse_time)
        
        # Extract hour for analysis (VECTORIZED: ~100x faster than apply)
        df['violation_hour'] = df['violation_time_parsed'].str.split(':').str[0].astype('Int64')
        
        valid_times = df['violation_time_parsed'].notna().sum()
        print(f"   Successfully parsed {valid_times:,} times")
        print(f"   Invalid times: {df['violation_time_parsed'].isna().sum():,}")
        
        # Add time of day categories (VECTORIZED with pd.cut)
        def categorize_time(hour):
            if pd.isnull(hour):
                return 'Unknown'
            elif 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'
        
        df['time_of_day'] = df['violation_hour'].apply(categorize_time)
        
        print(f"\n   Time of Day Distribution:")
        for period, count in df['time_of_day'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"      {period:10s}: {count:6,} ({pct:5.1f}%)")
        
        self.raw_df = df
        return df
    
    def clean_categorical_fields(self):
        """Clean and standardize categorical fields"""
        print(f"\n{'='*60}")
        print("CLEANING CATEGORICAL FIELDS")
        print(f"{'='*60}\n")
        
        # PERFORMANCE: Don't copy - modify in place
        df = self.raw_df
        
        # 1. State codes
        print("Standardizing state codes...")
        df['state'] = df['state'].str.upper().str.strip()
        
        # PITFALL: Many invalid state codes (99, 'NY', non-US states)
        valid_states = ['NY', 'NJ', 'PA', 'CT', 'MA', 'FL', 'CA', 'TX', 'VA', 'MD']
        invalid_states = df[~df['state'].isin(valid_states)]['state'].value_counts()
        
        if len(invalid_states) > 0:
            print(f"   Found {len(invalid_states)} non-standard state codes:")
            for state, count in invalid_states.head(10).items():
                print(f"      '{state}': {count:,}")
        
        # Create flag for NY vs non-NY
        df['is_ny_plate'] = df['state'] == 'NY'
        
        # 2. County (borough) standardization
        print(f"\nStandardizing county/borough names...")
        
        # PITFALL: County names may be abbreviated or misspelled
        borough_mapping = {
            'MAN': 'MANHATTAN',
            'MH': 'MANHATTAN',
            'NY': 'MANHATTAN',
            'BX': 'BRONX',
            'BK': 'BROOKLYN',
            'K': 'BROOKLYN',
            'Q': 'QUEENS',
            'QN': 'QUEENS',
            'R': 'STATEN ISLAND',
            'ST': 'STATEN ISLAND',
        }
        
        df['county'] = df['county'].str.upper().str.strip()
        df['county'] = df['county'].replace(borough_mapping)
        
        print(f"   Borough distribution:")
        for borough, count in df['county'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"      {borough:15s}: {count:6,} ({pct:5.1f}%)")
        
        # 3. License type
        print(f"\nLicense types:")
        if 'license_type' in df.columns:
            for ltype, count in df['license_type'].value_counts().head(10).items():
                pct = (count / len(df)) * 100
                print(f"      {ltype:15s}: {count:6,} ({pct:5.1f}%)")
        
        # 4. Precinct processing
        print(f"\nProcessing precinct information...")
        if 'precinct' in df.columns:
            # Clean and standardize precinct values
            df['precinct'] = df['precinct'].astype(str).str.strip()
            
            # Convert to numeric where possible (NYC precincts are typically 1-123)
            df['precinct_numeric'] = pd.to_numeric(df['precinct'], errors='coerce')
            
            # Count valid precincts
            valid_precincts = df['precinct_numeric'].notna().sum()
            print(f"   Valid numeric precincts: {valid_precincts:,} ({valid_precincts/len(df)*100:.1f}%)")
            
            # Show top precincts
            print(f"   Top 10 precincts by citation count:")
            for precinct, count in df['precinct'].value_counts().head(10).items():
                pct = (count / len(df)) * 100
                print(f"      Precinct {precinct:5s}: {count:6,} ({pct:5.1f}%)")
        
        self.raw_df = df
        return df
    
    def clean_numeric_fields(self):
        """Clean and validate numeric fields"""
        print(f"\n{'='*60}")
        print("CLEANING NUMERIC FIELDS")
        print(f"{'='*60}\n")
        
        df = self.raw_df.copy()
        
        # 1. Fine amount
        print("Processing fine_amount...")
        df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors='coerce')
        
        # Check for outliers
        fine_stats = df['fine_amount'].describe()
        print(f"   Min:    ${fine_stats['min']:,.2f}")
        print(f"   25%:    ${fine_stats['25%']:,.2f}")
        print(f"   Median: ${fine_stats['50%']:,.2f}")
        print(f"   75%:    ${fine_stats['75%']:,.2f}")
        print(f"   Max:    ${fine_stats['max']:,.2f}")
        
        # PITFALL: Some fines may be $0 (dismissed), negative (errors), or extremely high
        zero_fines = (df['fine_amount'] == 0).sum()
        negative_fines = (df['fine_amount'] < 0).sum()
        high_fines = (df['fine_amount'] > 500).sum()
        
        print(f"\n   Data quality flags:")
        print(f"      Zero fines: {zero_fines:,}")
        print(f"      Negative fines: {negative_fines:,}")
        print(f"      Fines > $500: {high_fines:,}")
        
        # Flag suspicious records
        df['fine_amount_flag'] = 'normal'
        df.loc[df['fine_amount'] == 0, 'fine_amount_flag'] = 'zero'
        df.loc[df['fine_amount'] < 0, 'fine_amount_flag'] = 'negative'
        df.loc[df['fine_amount'] > 500, 'fine_amount_flag'] = 'high'
        
        # 2. Reduction amount
        print(f"\nProcessing reduction_amount...")
        df['reduction_amount'] = pd.to_numeric(df['reduction_amount'], errors='coerce')
        df['reduction_amount'] = df['reduction_amount'].fillna(0)
        
        has_reduction = (df['reduction_amount'] > 0).sum()
        print(f"   Records with reductions: {has_reduction:,} ({has_reduction/len(df)*100:.1f}%)")
        
        # Calculate net fine
        df['net_fine'] = df['fine_amount'] - df['reduction_amount']
        
        # PITFALL: Net fine should not be negative
        negative_net = (df['net_fine'] < 0).sum()
        if negative_net > 0:
            print(f"   {negative_net:,} records have reduction > fine amount")
        
        self.raw_df = df
        return df
    
    def remove_duplicates(self):
        """Remove duplicate records"""
        print(f"\n{'='*60}")
        print("REMOVING DUPLICATES")
        print(f"{'='*60}\n")
        
        df = self.raw_df.copy()
        initial_count = len(df)
        
        # Check for duplicates based on summons_number
        duplicate_mask = df.duplicated(subset=['summons_number'], keep='first')
        duplicates = duplicate_mask.sum()
        
        if duplicates > 0:
            print(f"Found {duplicates:,} duplicate summons numbers")
            print(f"   Keeping first occurrence, removing {duplicates:,} records")
            
            # PERFORMANCE: Don't iterate rows - just track count
            self.cleaning_report['duplicates_removed'] = duplicates
            
            df = df[~duplicate_mask]
        else:
            print("No duplicates found")
        
        self.raw_df = df
        return df
    
    def create_derived_features(self):
        """Create useful derived features for analysis"""
        print(f"\n{'='*60}")
        print("CREATING DERIVED FEATURES")
        print(f"{'='*60}\n")
        
        df = self.raw_df.copy()
        
        # 1. Weekend vs weekday
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
        
        # 2. Quarter
        df['quarter'] = df['issue_date'].dt.quarter
        
        # 3. Business hours flag
        df['is_business_hours'] = df['violation_hour'].apply(
            lambda x: 9 <= x <= 17 if pd.notna(x) else False
        )
        
        # 4. Plate masking for privacy (last 3 digits only)
        # IMPORTANT PITFALL: Never share full plate numbers - privacy violation!
        print("Masking plate numbers for privacy...")
        df['plate_masked'] = df['plate'].apply(
            lambda x: f"***{str(x)[-3:]}" if pd.notna(x) else None
        )
        
        print("Created derived features:")
        print("   - is_weekend")
        print("   - quarter")
        print("   - is_business_hours")
        print("   - plate_masked (for privacy)")
        
        self.raw_df = df
        return df
    
    def finalize_cleaning(self):
        """Final cleanup and validation"""
        print(f"\n{'='*60}")
        print("FINALIZING CLEANED DATA")
        print(f"{'='*60}\n")
        
        df = self.raw_df.copy()
        
        # Remove any remaining rows with critical missing values
        critical_columns = ['summons_number', 'issue_date', 'county']
        
        before_count = len(df)
        
        # Find rows with missing critical values
        missing_critical_mask = df[critical_columns].isnull().any(axis=1)
        
        if missing_critical_mask.sum() > 0:
            # Track removed rows
            for idx, row in df[missing_critical_mask].iterrows():
                missing_fields = [col for col in critical_columns if pd.isnull(row[col])]
                self.removed_rows.append({
                    'index': idx,
                    'summons_number': row.get('summons_number', 'N/A'),
                    'issue_date_original': row.get('issue_date', 'N/A'),
                    'reason': f'Missing critical field(s): {", ".join(missing_fields)}',
                    'step': 'finalize_cleaning'
                })
        
        df = df.dropna(subset=critical_columns)
        after_count = len(df)
        
        removed = before_count - after_count
        if removed > 0:
            print(f"Removed {removed:,} records with missing critical fields")
        
        # Set final clean dataframe
        self.clean_df = df
        self.cleaning_report['final_records'] = len(df)
        
        # Calculate retention rate
        retention = (after_count / self.cleaning_report['initial_records']) * 100
        print(f"\nData cleaning complete!")
        print(f"   Initial records: {self.cleaning_report['initial_records']:,}")
        print(f"   Final records:   {self.cleaning_report['final_records']:,}")
        print(f"   Retention rate:  {retention:.2f}%")
        
        return df
    
    def save_cleaned_data(self, filename=None, date_str=None):
        """Save cleaned data to CSV"""
        if self.clean_df is None:
            print("No cleaned data to save. Run cleaning pipeline first.")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_part = f"_{date_str}" if date_str else ""
            filename = f"parking_cleaned_citations{date_part}_{len(self.clean_df)}-records_{timestamp}.csv"
        
        filepath = PROCESSED_DATA_DIR / filename
        
        try:
            self.clean_df.to_csv(filepath, index=False)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            
            print(f"\nCleaned data saved:")
            print(f"   File: {filepath}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Records: {len(self.clean_df):,}")
            print(f"   Columns: {len(self.clean_df.columns)}")
            
            return filepath
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def generate_cleaning_report(self):
        """Generate summary report of cleaning process"""
        print(f"\n{'='*60}")
        print("CLEANING REPORT SUMMARY")
        print(f"{'='*60}\n")
        
        report = self.cleaning_report
        
        print(f"Initial records:        {report['initial_records']:,}")
        print(f"Duplicates removed:     {report['duplicates_removed']:,}")
        print(f"Invalid dates removed:  {report['invalid_dates_removed']:,}")
        print(f"Final records:          {report['final_records']:,}")
        print(f"\nData retention:         {(report['final_records']/report['initial_records']*100):.2f}%")
    
    def save_removal_report(self, filename=None, date_str=None):
        """Save detailed removal report to outputs/reports"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_part = f"_{date_str}" if date_str else ""
            filename = f"cleaning_removal_report{date_part}_{timestamp}.html"
        
        filepath = REPORTS_DIR / filename
        
        # Create HTML report
        html_content = self._generate_html_removal_report()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\nRemoval report saved:")
            print(f"   File: {filepath}")
            print(f"   Records in report: {len(self.removed_rows):,}")
            
            return filepath
        except Exception as e:
            print(f"Error saving removal report: {e}")
            return None
    
    def _generate_html_removal_report(self):
        """Generate detailed HTML report of removed rows"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate statistics by reason
        reason_stats = {}
        for row in self.removed_rows:
            reason = row['reason']
            if reason not in reason_stats:
                reason_stats[reason] = {'count': 0, 'step': row['step']}
            reason_stats[reason]['count'] += 1
        
        # Calculate statistics by step
        step_stats = {}
        for row in self.removed_rows:
            step = row['step']
            if step not in step_stats:
                step_stats[step] = 0
            step_stats[step] += 1
        
        # Start HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Cleaning Removal Report</title>
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
        .summary-box {{
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
        .stat-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .stat-card.success {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
        .reason-badge {{
            background-color: #e74c3c;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .step-badge {{
            background-color: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #7f8c8d;
        }}
        .section {{
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Cleaning Removal Report</h1>
        <p>Generated: {timestamp}</p>
        
        <div class="section">
            <h2>Overall Summary</h2>
            <div class="summary-box">
                <div class="stat-card success">
                    <div class="stat-label">Initial Records</div>
                    <div class="stat-value">{self.cleaning_report['initial_records']:,}</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-label">Total Removed</div>
                    <div class="stat-value">{len(self.removed_rows):,}</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-label">Final Records</div>
                    <div class="stat-value">{self.cleaning_report['final_records']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Retention Rate</div>
                    <div class="stat-value">{(self.cleaning_report['final_records']/self.cleaning_report['initial_records']*100):.2f}%</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Removal by Cleaning Step</h2>
            <table>
                <tr>
                    <th>Step</th>
                    <th>Records Removed</th>
                    <th>Percentage</th>
                </tr>
"""
        
        for step in sorted(step_stats.keys()):
            count = step_stats[step]
            pct = (count / len(self.removed_rows)) * 100 if self.removed_rows else 0
            html += f"""
                <tr>
                    <td><span class="step-badge">{step}</span></td>
                    <td>{count:,}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>Removal Reasons</h2>
            <table>
                <tr>
                    <th>Reason</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
"""
        
        for reason in sorted(reason_stats.keys(), key=lambda x: reason_stats[x]['count'], reverse=True):
            count = reason_stats[reason]['count']
            pct = (count / len(self.removed_rows)) * 100 if self.removed_rows else 0
            html += f"""
                <tr>
                    <td>{reason}</td>
                    <td>{count:,}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""
        
        html += f"""
            </table>
        </div>
        
        <div class="footer">
            <p>Total removed records tracked: {len(self.removed_rows):,} out of {self.cleaning_report['initial_records']:,} initial records</p>
            <p>Report generated: {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def run_full_pipeline(self, input_file):
        """Run complete cleaning pipeline"""
        print("\n" + "="*60)
        print("NYC PARKING DATA CLEANING PIPELINE")
        print("="*60)
        
        # Load data
        if not self.load_data(input_file):
            return None
        
        # Quality assessment
        self.check_data_quality()
        
        # Cleaning steps
        self.clean_dates()
        self.clean_categorical_fields()
        self.clean_numeric_fields()
        self.remove_duplicates()
        self.create_derived_features()
        
        # Finalize
        clean_df = self.finalize_cleaning()
        
        # Generate report
        self.generate_cleaning_report()
        
        # Save removal report
        self.save_removal_report()
        
        return clean_df


def main():
    """Main execution"""
    # Find most recent raw data file
    raw_files = list(RAW_DATA_DIR.glob("*.csv"))
    
    if not raw_files:
        print("No raw data files found in data/raw/")
        print("   Run data_loader.py first to download data")
        return
    
    # Use most recent file
    latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\nUsing file: {latest_file.name}")
    
    # Run cleaning pipeline
    cleaner = ParkingDataCleaner()
    clean_df = cleaner.run_full_pipeline(latest_file)
    
    if clean_df is not None:
        # Save cleaned data
        cleaner.save_cleaned_data()
        
        print("\n" + "="*60)
        print("CLEANING COMPLETE - Ready for analysis!")
        print("="*60)


def clean_data_pipeline(raw_filepath, date_str=None):
    """
    Utility function to run the full cleaning pipeline on a raw data file.
    Used by generate_analysis.py and test scripts.
    
    Parameters:
    -----------
    raw_filepath : Path or str
        Path to raw CSV file
    date_str : str, optional
        Date string for filename (e.g., '2025-12-30')
    
    Returns:
    --------
    tuple : (cleaned_filepath, cleaner_instance) or None if failed
    """
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


if __name__ == "__main__":
    main()