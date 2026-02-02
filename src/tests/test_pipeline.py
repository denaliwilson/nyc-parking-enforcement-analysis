"""
Test the complete pipeline: load data, clean it, and verify violation_hour is populated
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner
import pandas as pd

print("="*60)
print("TESTING DATA PIPELINE")
print("="*60)

# Step 1: Load a small sample
print("\n1. Loading sample data from API...")
loader = NYCParkingDataLoader()
df_raw = loader.load_sample(limit=100, start_date="2025-12-30", end_date="2025-12-31")

if df_raw is not None:
    print(f"   Loaded {len(df_raw)} records")
    print(f"   Columns: {list(df_raw.columns)}")
    
    # Check if precinct is in the data
    if 'precinct' in df_raw.columns:
        print(f"   ✓ Precinct field is present")
        print(f"   Sample precinct values: {df_raw['precinct'].head(5).tolist()}")
    else:
        print(f"   ✗ Precinct field is missing")
    
    # Step 2: Clean the data
    print("\n2. Cleaning data...")
    cleaner = ParkingDataCleaner()
    cleaner.raw_df = df_raw
    cleaner.clean_dates()
    
    # Step 3: Check violation_hour
    print("\n3. Checking violation_hour field...")
    df_cleaned = cleaner.raw_df
    
    print(f"   Total rows: {len(df_cleaned)}")
    print(f"   violation_time samples: {df_cleaned['violation_time'].head(5).tolist()}")
    print(f"   violation_time_parsed samples: {df_cleaned['violation_time_parsed'].head(5).tolist()}")
    print(f"   violation_hour samples: {df_cleaned['violation_hour'].head(5).tolist()}")
    
    valid_hours = df_cleaned['violation_hour'].notna().sum()
    print(f"\n   Valid violation_hour values: {valid_hours}/{len(df_cleaned)} ({valid_hours/len(df_cleaned)*100:.1f}%)")
    
    if valid_hours > 0:
        print("   ✓ SUCCESS: violation_hour is being populated!")
        print(f"   Hour distribution: {df_cleaned['violation_hour'].value_counts().sort_index().to_dict()}")
    else:
        print("   ✗ FAILED: violation_hour is still empty")
else:
    print("   Failed to load data")
