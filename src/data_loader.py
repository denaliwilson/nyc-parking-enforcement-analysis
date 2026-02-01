"""
NYC Parking Citations Data Loader

This script loads parking citation data from NYC Open Data API
with proper error handling, pagination, and progress tracking.
"""

import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import time
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from src.config import (
    API_BASE_URL, APP_TOKEN, RAW_DATA_DIR, 
    DEFAULT_LIMIT, DEFAULT_START_DATE, DEFAULT_END_DATE,
    ESSENTIAL_FIELDS, OUTPUT_FILE_PREFIX
)


class NYCParkingDataLoader:
    """
    Data loader for NYC Parking Citations from Open Data API
    """
    
    def __init__(self, app_token=None):
        """
        Initialize the data loader
        
        Parameters:
        -----------
        app_token : str, optional
            NYC Open Data API token for higher rate limits
        """
        self.base_url = API_BASE_URL
        self.app_token = app_token or APP_TOKEN
        self.session = requests.Session()
        
    def _make_request(self, params, max_retries=3):
        """
        Make API request with retry logic
        
        Parameters:
        -----------
        params : dict
            Query parameters
        max_retries : int
            Number of retry attempts
            
        Returns:
        --------
        dict : JSON response
        """
        if self.app_token:
            params['$$app_token'] = self.app_token
            
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.base_url, 
                    params=params, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                    
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 60 * (attempt + 1)
                    print(f"  Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    
                else:
                    print(f" Error {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"⏱  Timeout on attempt {attempt + 1}/{max_retries}")
                time.sleep(5)
                
            except Exception as e:
                print(f" Unexpected error: {e}")
                return None
                
        print(f" Failed after {max_retries} attempts")
        return None
    
    def load_sample(self, limit=DEFAULT_LIMIT, start_date=None, end_date=None):
        """
        Load a sample of parking citations
        
        Parameters:
        -----------
        limit : int
            Number of records to load (max 50,000)
        start_date : str
            Start date (YYYY-MM-DD format)
        end_date : str
            End date (YYYY-MM-DD format)
            
        Returns:
        --------
        pd.DataFrame : Citation data
        """
        print(f"\n{'='*60}")
        print(f"Loading {limit:,} parking citations from NYC Open Data")
        print(f"{'='*60}\n")
        
        params = {
            '$limit': min(limit, 50000),
            '$order': 'issue_date DESC'
        }
        
        # Build date filter
        where_clauses = []
        if start_date:
            where_clauses.append(f"issue_date >= '{start_date}'")
            print(f" Start date: {start_date}")
        if end_date:
            where_clauses.append(f"issue_date < '{end_date}'")
            print(f" End date: {end_date}")
            
        if where_clauses:
            params['$where'] = ' AND '.join(where_clauses)
        
        # Request specific fields to reduce data transfer
        if ESSENTIAL_FIELDS:
            params['$select'] = ','.join(ESSENTIAL_FIELDS)
        
        print(f"\n Fetching data...")
        start_time = time.time()
        
        data = self._make_request(params)
        
        if data:
            df = pd.DataFrame(data)
            elapsed = time.time() - start_time
            
            print(f" Successfully loaded {len(df):,} records in {elapsed:.2f}s")
            return df
        else:
            print(" Failed to load data")
            return None
    
    def load_by_date_range(self, start_date, end_date, limit=50000):
        """
        Load citations for a specific date range
        
        Parameters:
        -----------
        start_date : str
            Start date (YYYY-MM-DD format)
        end_date : str
            End date (YYYY-MM-DD format)
        limit : int
            Maximum number of records to load (default 50,000)
            
        Returns:
        --------
        pd.DataFrame : Citation data filtered to the date range
        """
        print(f"\n{'='*60}")
        print(f"Loading citations from {start_date} to {end_date}")
        print(f"{'='*60}\n")
        
        # Extract year from date range to narrow API query
        start_year = start_date.split('-')[0]
        end_year = end_date.split('-')[0]
        
        # Query by year only (API stores dates as text, complex date filtering doesn't work well)
        # Then filter precisely in pandas after loading
        if start_year == end_year:
            where_clause = f"issue_date like '%/{start_year}'"
        else:
            # Multiple years - use OR
            years = range(int(start_year), int(end_year) + 1)
            year_conditions = [f"issue_date like '%/{year}'" for year in years]
            where_clause = " OR ".join(year_conditions)
        
        params = {
            '$limit': min(limit, 50000),
            '$where': where_clause,
            '$order': 'issue_date DESC'
        }
        
        if ESSENTIAL_FIELDS:
            params['$select'] = ','.join(ESSENTIAL_FIELDS)
        
        print(f" Fetching data...")
        print(f" Filtering dates: {start_date} to {end_date}")
        start_time = time.time()
        
        data = self._make_request(params)
        
        if data:
            df = pd.DataFrame(data)
            
            # Convert issue_date to datetime for precise filtering
            df['issue_date_parsed'] = pd.to_datetime(df['issue_date'], format='%m/%d/%Y', errors='coerce')
            
            # Filter to exact date range
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df_filtered = df[(df['issue_date_parsed'] >= start_dt) & (df['issue_date_parsed'] <= end_dt)].copy()
            
            # Drop the temporary parsing column
            df_filtered = df_filtered.drop(columns=['issue_date_parsed'])
            
            elapsed = time.time() - start_time
            print(f" Successfully loaded {len(df):,} records, filtered to {len(df_filtered):,} in {elapsed:.2f}s")
            return df_filtered
        else:
            print(" Failed to load data")
            return None

    def load_by_day(self, date, limit=50000):
        """
        Load citations for a single day

        Parameters:
        -----------
        date : str
            Date in YYYY-MM-DD format
        limit : int
            Maximum number of records to load (default 50,000)

        Returns:
        --------
        pd.DataFrame : Citation data for that day
        """
        return self.load_by_date_range(date, date, limit=limit)
    
    def load_by_borough(self, borough, limit=DEFAULT_LIMIT):
        """
        Load citations for a specific borough
        
        Parameters:
        -----------
        borough : str
            Borough name (e.g., 'MANHATTAN', 'BROOKLYN')
        limit : int
            Number of records
            
        Returns:
        --------
        pd.DataFrame : Citation data
        """
        print(f"\n Loading {limit:,} citations from {borough}")
        
        params = {
            '$limit': min(limit, 50000),
            '$where': f"county = '{borough.upper()}'",
            '$order': 'issue_date DESC'
        }
        
        if ESSENTIAL_FIELDS:
            params['$select'] = ','.join(ESSENTIAL_FIELDS)
        
        data = self._make_request(params)
        
        if data:
            df = pd.DataFrame(data)
            print(f" Loaded {len(df):,} records from {borough}")
            return df
        else:
            return None
    
    def load_paginated(self, total_records, start_date=None, end_date=None, 
                       records_per_page=50000):
        """
        Load large datasets using pagination
        
        Parameters:
        -----------
        total_records : int
            Total number of records to fetch
        start_date : str
            Start date filter
        end_date : str
            End date filter
        records_per_page : int
            Records per API call (max 50,000)
            
        Returns:
        --------
        pd.DataFrame : Combined data
        """
        print(f"\n{'='*60}")
        print(f"Loading {total_records:,} records using pagination")
        print(f"{'='*60}\n")
        
        all_data = []
        offset = 0
        page = 1
        
        # Build base parameters
        base_params = {
            '$order': 'issue_date DESC'
        }
        
        where_clauses = []
        if start_date:
            where_clauses.append(f"issue_date >= '{start_date}'")
        if end_date:
            where_clauses.append(f"issue_date < '{end_date}'")
        if where_clauses:
            base_params['$where'] = ' AND '.join(where_clauses)
        
        if ESSENTIAL_FIELDS:
            base_params['$select'] = ','.join(ESSENTIAL_FIELDS)
        
        while len(all_data) < total_records:
            # Calculate how many records to fetch this iteration
            remaining = total_records - len(all_data)
            limit = min(remaining, records_per_page)
            
            params = base_params.copy()
            params['$limit'] = limit
            params['$offset'] = offset
            
            print(f" Page {page}: Fetching records {offset:,} to {offset + limit:,}")
            
            data = self._make_request(params)
            
            if not data:
                print(f"  No more data returned at offset {offset}")
                break
            
            all_data.extend(data)
            offset += len(data)
            page += 1
            
            # Progress update
            progress = (len(all_data) / total_records) * 100
            print(f"   Total records loaded: {len(all_data):,} ({progress:.1f}%)")
            
            # Small delay to be respectful of API
            time.sleep(0.5)
            
            # Break if we got fewer records than requested (reached end)
            if len(data) < limit:
                break
        
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n Total records loaded: {len(df):,}")
            return df
        else:
            print("\n Failed to load data")
            return None


def save_data(df, filename=None, output_dir=None):
    """
    Save DataFrame to CSV with timestamp
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data to save
    filename : str, optional
        Output filename (auto-generated if None)
    output_dir : Path, optional
        Output directory (default: RAW_DATA_DIR)
    """
    if df is None or len(df) == 0:
        print("  No data to save")
        return
    
    output_dir = output_dir or RAW_DATA_DIR
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_FILE_PREFIX}_{len(df)}_records_{timestamp}.csv"
    
    filepath = output_dir / filename
    
    try:
        df.to_csv(filepath, index=False)
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"\n Data saved to: {filepath}")
        print(f"   File size: {size_mb:.2f} MB")
        print(f"   Records: {len(df):,}")
        return filepath
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


def display_summary(df):
    """
    Display summary statistics of loaded data
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data to summarize
    """
    if df is None or len(df) == 0:
        print("No data to display")
        return
    
    print(f"\n{'='*60}")
    print("DATA SUMMARY")
    print(f"{'='*60}\n")
    
    print(f" Total records: {len(df):,}")
    print(f" Columns: {len(df.columns)}")
    
    if 'issue_date' in df.columns:
        df['issue_date'] = pd.to_datetime(df['issue_date'])
        print(f"\n Date Range:")
        print(f"   Earliest: {df['issue_date'].min()}")
        print(f"   Latest: {df['issue_date'].max()}")
    
    if 'county' in df.columns:
        print(f"\n  Citations by County:")
        for county, count in df['county'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"   {county:20s}: {count:6,} ({pct:5.1f}%)")
    
    if 'violation' in df.columns:
        print(f"\n Top 5 Violation Types:")
        for violation, count in df['violation'].value_counts().head(5).items():
            print(f"   {violation}: {count:,}")
    
    print(f"\n Missing Values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if len(missing) > 0:
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            print(f"   {col:25s}: {count:6,} ({pct:5.1f}%)")
    else:
        print("   No missing values!")


def main():
    """
    Main execution function
    """
    print("\n" + "="*60)
    print("NYC PARKING CITATIONS DATA LOADER")
    print("="*60)
    
    # Initialize loader
    loader = NYCParkingDataLoader()
    
    # Example 1: Load recent sample
    print("\n\n--- Example 1: Loading Recent Sample ---")
    df = loader.load_sample(
        limit=10000,
        start_date=DEFAULT_START_DATE,
        end_date=DEFAULT_END_DATE
    )
    
    if df is not None:
        display_summary(df)
        save_data(df, filename="parking_sample_recent.csv")
    
    # Example 2: Load by borough (uncomment to run)
    # print("\n\n--- Example 2: Loading Manhattan Data ---")
    # manhattan_df = loader.load_by_borough("MANHATTAN", limit=5000)
    # if manhattan_df is not None:
    #     display_summary(manhattan_df)
    #     save_data(manhattan_df, filename="parking_manhattan.csv")
    
    # Example 3: Large paginated load (uncomment to run)
    # print("\n\n--- Example 3: Loading Large Dataset ---")
    # large_df = loader.load_paginated(
    #     total_records=100000,
    #     start_date="2024-11-01"
    # )
    # if large_df is not None:
    #     display_summary(large_df)
    #     save_data(large_df, filename="parking_large_dataset.csv")
    
    print("\n" + "="*60)
    print("Data loading complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()