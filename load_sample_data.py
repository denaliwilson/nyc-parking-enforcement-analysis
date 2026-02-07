"""
Quick loader script for January 2026 sample data.

Use this as a reference for loading the pre-processed sample data
in your own analysis scripts or notebooks.
"""

import pandas as pd
from pathlib import Path

def load_jan_2026_sample():
    """
    Load January 2026 sample data.
    
    Returns:
        pd.DataFrame: Cleaned parking citation data with 859,885 records (Jan 1-31)
    
    Raises:
        FileNotFoundError: If sample data file doesn't exist
    """
    file_path = Path('data/processed/jan_2026_sample_data.csv')
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"Sample data not found at {file_path}.\n"
            "Run the Streamlit dashboard and click 'Load January 2026 Sample Data' "
            "to generate this file."
        )
    
    # Load data
    df = pd.read_csv(file_path)
    
    # Convert date columns
    if 'issue_date' in df.columns:
        df['issue_date'] = pd.to_datetime(df['issue_date'])
    
    return df


if __name__ == '__main__':
    # Example usage
    print("Loading January 2026 sample data...")
    df = load_jan_2026_sample()
    
    print(f"\n✅ Loaded {len(df):,} citations")
    print(f"📅 Date range: {df['issue_date'].min().date()} to {df['issue_date'].max().date()}")
    print(f"📊 Columns: {len(df.columns)}")
    print(f"💾 Memory usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
    
    print("\n🏙️ Citations by Borough:")
    print(df['county'].value_counts())
    
    print("\n🚗 Top 10 Violations:")
    print(df['violation'].value_counts().head(10))
    
    print("\n✅ Data loaded successfully!")
