"""
NYC Parking Citations - Preliminary Analysis Script

This script performs a lightweight, console-based analysis on the most recent
cleaned data file in data/processed/.

Usage:
    python src/preliminary_analysis.py
"""

from pathlib import Path
import sys
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import PROCESSED_DATA_DIR


def load_latest_cleaned_file():
    """Load the most recent cleaned CSV from data/processed."""
    processed_files = list(PROCESSED_DATA_DIR.glob("*.csv"))
    if not processed_files:
        print("No cleaned data files found in data/processed/")
        print("Run data_cleaner.py first to generate a cleaned file.")
        return None

    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    print(f"Using cleaned file: {latest_file.name}")
    return pd.read_csv(latest_file)


def print_basic_summary(df):
    print("\n" + "=" * 60)
    print("BASIC SUMMARY")
    print("=" * 60)
    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    if "issue_date" in df.columns:
        dates = pd.to_datetime(df["issue_date"], errors="coerce")
        print(f"Date range: {dates.min().date()} to {dates.max().date()}")


def print_temporal_patterns(df):
    print("\n" + "=" * 60)
    print("TEMPORAL PATTERNS")
    print("=" * 60)

    if "day_of_week" in df.columns:
        print("\nTop days of week:")
        print(df["day_of_week"].value_counts().head(7).to_string())

    if "month_name" in df.columns:
        print("\nTop months:")
        print(df["month_name"].value_counts().head(12).to_string())

    if "time_of_day" in df.columns:
        print("\nTime of day distribution:")
        print(df["time_of_day"].value_counts().to_string())


def print_violation_patterns(df):
    print("\n" + "=" * 60)
    print("VIOLATION PATTERNS")
    print("=" * 60)

    if "violation" in df.columns:
        print("\nTop violations:")
        print(df["violation"].value_counts().head(10).to_string())

    if "issuing_agency" in df.columns:
        print("\nTop issuing agencies:")
        print(df["issuing_agency"].value_counts().head(10).to_string())

    if "county" in df.columns:
        print("\nBorough distribution:")
        print(df["county"].value_counts().to_string())


def print_financial_summary(df):
    print("\n" + "=" * 60)
    print("FINANCIAL SUMMARY")
    print("=" * 60)

    if "fine_amount" in df.columns:
        fine = pd.to_numeric(df["fine_amount"], errors="coerce")
        print(f"Min fine: ${fine.min():,.2f}")
        print(f"Max fine: ${fine.max():,.2f}")
        print(f"Mean fine: ${fine.mean():,.2f}")
        print(f"Median fine: ${fine.median():,.2f}")

    if "net_fine" in df.columns:
        net = pd.to_numeric(df["net_fine"], errors="coerce")
        print(f"Mean net fine: ${net.mean():,.2f}")
        print(f"Median net fine: ${net.median():,.2f}")


def run_preliminary_analysis():
    df = load_latest_cleaned_file()
    if df is None:
        return

    print_basic_summary(df)
    print_temporal_patterns(df)
    print_violation_patterns(df)
    print_financial_summary(df)

    print("\n" + "=" * 60)
    print("PRELIMINARY ANALYSIS COMPLETE")
    print("=" * 60)


def main():
    run_preliminary_analysis()


if __name__ == "__main__":
    main()
