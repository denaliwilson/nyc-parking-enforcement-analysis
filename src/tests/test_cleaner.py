"""
Test the cleaner on existing raw data
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_cleaner import ParkingDataCleaner
import pandas as pd

print("="*60)
print("TESTING DATA CLEANER")
print("="*60)

# Find a raw data file
from src.config import RAW_DATA_DIR
raw_files = list(RAW_DATA_DIR.glob("parking_raw_*.csv"))

if raw_files:
    raw_file = raw_files[0]
    print(f"\nUsing file: {raw_file.name}")
    
    # Load and clean
    cleaner = ParkingDataCleaner()
    success = cleaner.load_data(raw_file)
    
    if success:
        print("\n" + "="*60)
        print("Sample violation_time values BEFORE cleaning:")
        print("="*60)
        print(cleaner.raw_df['violation_time'].head(10).tolist())
        
        # Clean dates
        cleaner.clean_dates()
        
        print("\n" + "="*60)
        print("Results AFTER cleaning:")
        print("="*60)
        
        df = cleaner.raw_df
        print(f"\nTotal rows: {len(df)}")
        print(f"\nviolation_time_parsed samples:")
        print(df['violation_time_parsed'].head(10).tolist())
        print(f"\nviolation_hour samples:")
        print(df['violation_hour'].head(10).tolist())
        
        valid_hours = df['violation_hour'].notna().sum()
        print(f"\nValid violation_hour: {valid_hours}/{len(df)} ({valid_hours/len(df)*100:.1f}%)")
        
        if valid_hours > 0:
            print("\n✓ SUCCESS! violation_hour is populated")
            print(f"\nHour distribution:")
            hour_dist = df['violation_hour'].value_counts().sort_index()
            for hour, count in hour_dist.items():
                print(f"  Hour {hour:2d}: {count:4d} citations")
        else:
            print("\n✗ FAILED: violation_hour is empty")
else:
    print("No raw data files found")
