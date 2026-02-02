"""Non-interactive test for daily analysis generator."""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR
from src.data_loader import NYCParkingDataLoader, fetch_data_for_day
from src.data_cleaner import ParkingDataCleaner, clean_data_pipeline


def main():
    """Main execution flow for 3 days."""
    # Hardcoded 3-day range (using dates we know have data)
    start_date = "2025-12-30"
    end_date = "2025-12-31"
    
    # Build date list
    date_list = [d.strftime("%Y-%m-%d") for d in pd.date_range(start=start_date, end=end_date, freq="D")]
    
    print(f"\n{'='*60}")
    print("NYC PARKING ANALYSIS - 3 DAY TEST")
    print(f"{'='*60}")
    print(f"Will analyze {len(date_list)} days: {start_date} to {end_date}")
    print(f"Dates: {', '.join(date_list)}")
    
    generated = []
    
    for date_str in date_list:
        period_name = date_str
        
        # Fetch data for the day
        raw_filepath = fetch_data_for_day(date_str)
        if raw_filepath is None:
            print(f"Skipping {date_str} - no data")
            continue
        
        # Clean data with date for better filenames
        result = clean_data_pipeline(raw_filepath, date_str=date_str)
        if result is None:
            print(f"Skipping {date_str} - cleaning failed")
            continue
        
        cleaned_filepath, cleaner = result
        generated.append((raw_filepath, cleaned_filepath))
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")
    
    if not generated:
        print("\nNo data processed.")
        return
    
    print(f"\nSuccessfully processed {len(generated)} day(s):")
    for i, (raw_filepath, cleaned_filepath) in enumerate(generated, 1):
        print(f"\nDay {i}:")
        print(f"   Raw data: {raw_filepath.name}")
        print(f"   Cleaned data: {cleaned_filepath.name}")


if __name__ == "__main__":
    main()
