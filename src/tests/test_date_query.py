"""Test date range query to debug the issue."""

from data_loader import NYCParkingDataLoader
import pandas as pd

def test_date_range():
    loader = NYCParkingDataLoader()
    
    # Test a small, historical window to verify range filtering
    start_date = "2016-01-01"
    end_date = "2016-01-15"
    print(f"Testing date range: {start_date} to {end_date}")
    print("=" * 60)
    
    df = loader.load_by_date_range(start_date, end_date, limit=50000)
    
    if df is not None and len(df) > 0:
        print(f"\nTotal records: {len(df)}")
        
        # Check unique dates
        print(f"\nUnique issue_date values:")
        print(df['issue_date'].value_counts().sort_index())
        
        # Parse dates and check range
        df['parsed_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
        print(f"\nDate range in results:")
        print(f"  Earliest: {df['parsed_date'].min()}")
        print(f"  Latest: {df['parsed_date'].max()}")
        
        # Check if any dates are outside the requested range
        expected_start = pd.to_datetime(start_date)
        expected_end = pd.to_datetime(end_date)
        
        outside_range = df[
            (df['parsed_date'] < expected_start) | 
            (df['parsed_date'] > expected_end)
        ]
        
        if len(outside_range) > 0:
            print(f"\n⚠️  WARNING: {len(outside_range)} records OUTSIDE requested range!")
            print(f"\nDates outside range:")
            print(outside_range['parsed_date'].value_counts().sort_index())
        else:
            print("\n✅ All records are within the requested range.")
    else:
        print("No data returned")

if __name__ == "__main__":
    test_date_range()
