"""Debug script to check day_of_week calculation."""

import pandas as pd
from pathlib import Path

def main():
    # Check the 47804 records file from timestamp 162846 (should be 2025 Q4)
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    processed_file = processed_dir / "parking_cleaned_47804_records_20260201_162846.csv"
    
    if not processed_file.exists():
        print("Processed file not found")
        return
    
    print(f"Found file: {processed_file.name}\n")
    
    # Load the data
    df = pd.read_csv(processed_file)
    
    print(f"Total records: {len(df)}")
    print(f"\nColumns: {list(df.columns)}\n")
    
    # Check day_of_week distribution
    if 'day_of_week' in df.columns:
        print("Day of week distribution:")
        print(df['day_of_week'].value_counts())
        print(f"\nPercentages:")
        print(df['day_of_week'].value_counts(normalize=True) * 100)
    else:
        print("No day_of_week column found")
    
    # Check issue_date values
    if 'issue_date' in df.columns:
        print(f"\nSample issue_date values:")
        print(df['issue_date'].head(20))
        
        # Try to convert to datetime and check
        df['issue_date_parsed'] = pd.to_datetime(df['issue_date'], errors='coerce')
        print(f"\nDate range: {df['issue_date_parsed'].min()} to {df['issue_date_parsed'].max()}")
        
        # Calculate day of week from the parsed dates
        df['day_calc'] = df['issue_date_parsed'].dt.day_name()
        print(f"\nRecalculated day of week distribution:")
        print(df['day_calc'].value_counts())
    else:
        print("No issue_date column found")
    
    # Check raw file too
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    raw_file = raw_dir / "parking_raw_2025_Q4_50000_records_20260201_162846.csv"
    
    if raw_file.exists():
        print(f"\n\n=== CHECKING RAW FILE ===")
        print(f"Found raw file: {raw_file.name}\n")
        
        df_raw = pd.read_csv(raw_file)
        print(f"Total raw records: {len(df_raw)}")
        
        if 'Issue Date' in df_raw.columns or 'issue_date' in df_raw.columns:
            date_col = 'Issue Date' if 'Issue Date' in df_raw.columns else 'issue_date'
            print(f"\nSample {date_col} values from raw file:")
            print(df_raw[date_col].head(20))
            
            # Parse and check distribution
            df_raw['parsed_date'] = pd.to_datetime(df_raw[date_col], errors='coerce')
            df_raw['day_of_week'] = df_raw['parsed_date'].dt.day_name()
            print(f"\nDay of week distribution in RAW data:")
            print(df_raw['day_of_week'].value_counts())

if __name__ == "__main__":
    main()
