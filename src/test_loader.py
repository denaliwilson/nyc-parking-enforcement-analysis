#!/usr/bin/env python3
"""
Quick test script to verify data loading functionality
Run this to make sure everything is working before committing
"""

import sys
import os

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

print("Starting test script...")
print(f"Python path: {sys.path}")

try:
    from src.data_loader import NYCParkingDataLoader, display_summary
    print("✅ Successfully imported data_loader")
except ImportError as e:
    print(f"❌ Failed to import data_loader: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Looking for src in: {Path(__file__).parent.parent}")
    sys.exit(1)

import pandas as pd


def test_api_connection():
    """Test basic API connectivity"""
    print("\n" + "="*60)
    print("TEST 1: API Connection")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    try:
        loader = NYCParkingDataLoader()
        print("Loader created, attempting to fetch 10 records...")
        sys.stdout.flush()
        
        # Try to load just 10 records
        df = loader.load_sample(limit=10)
        
        if df is not None and len(df) > 0:
            print("✅ API connection successful!")
            print(f"   Loaded {len(df)} records")
            print(f"   Columns: {list(df.columns[:5])}...")
            sys.stdout.flush()
            return True
        else:
            print("❌ API connection failed - no data returned")
            sys.stdout.flush()
            return False
    except Exception as e:
        print(f"❌ API connection failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False


def test_data_structure():
    """Test data loading and structure"""
    print("\n" + "="*60)
    print("TEST 2: Data Structure")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    try:
        loader = NYCParkingDataLoader()
        print("Loading 100 records...")
        sys.stdout.flush()
        
        df = loader.load_sample(limit=100)
        
        if df is None:
            print("❌ Failed to load data")
            sys.stdout.flush()
            return False
        
        print(f"✅ Loaded {len(df):,} records")
        sys.stdout.flush()
        
        # Check for expected columns (from config.ESSENTIAL_FIELDS)
        expected_columns = ['summons_number', 'issue_date', 'violation']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠️  Missing expected columns: {missing_columns}")
            print(f"   Available columns: {list(df.columns)}")
        else:
            print("✅ All expected columns present")
        
        sys.stdout.flush()
        
        # Check for data
        print(f"\n📊 Sample data:")
        print(df.head(3))
        sys.stdout.flush()
        
        return True
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False


def test_date_filtering():
    """Test date-based filtering"""
    print("\n" + "="*60)
    print("TEST 3: Date Filtering")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    try:
        loader = NYCParkingDataLoader()
        print("Loading with date filter...")
        sys.stdout.flush()
        
        df = loader.load_sample(
            limit=100,
            start_date="01/01/2016",
            end_date="12/31/2016"
        )
        
        if df is None or len(df) == 0:
            print("⚠️  No data returned for date range")
            sys.stdout.flush()
            return False
        
        # Convert and check dates
        df['issue_date'] = pd.to_datetime(df['issue_date'])
        print(f"✅ Date filtering works")
        print(f"   Records: {len(df)}")
        print(f"   Date range: {df['issue_date'].min()} to {df['issue_date'].max()}")
        sys.stdout.flush()
        
        return True
    except Exception as e:
        print(f"❌ Date filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False


def test_borough_filtering():
    """Test borough-specific loading"""
    print("\n" + "="*60)
    print("TEST 4: Borough Filtering")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    try:
        loader = NYCParkingDataLoader()
        print("Loading Manhattan data...")
        sys.stdout.flush()
        
        df = loader.load_by_borough("NY", limit=100)
        
        if df is None or len(df) == 0:
            print("⚠️  No data returned for Manhattan")
            sys.stdout.flush()
            return False
        
        if 'county' in df.columns:
            unique_boroughs = df['county'].unique()
            print(f"✅ Borough filtering works")
            print(f"   Counties in data: {unique_boroughs}")
            print(f"   Records: {len(df)}")
            sys.stdout.flush()
        
        return True
    except Exception as e:
        print(f"❌ Borough filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "🔬"*30)
    print("NYC PARKING DATA LOADER - TEST SUITE")
    print("🔬"*30 + "\n")
    sys.stdout.flush()
    
    tests = [
        ("API Connection", test_api_connection),
        ("Data Structure", test_data_structure),
        ("Date Filtering", test_date_filtering),
        ("Borough Filtering", test_borough_filtering),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}...")
        sys.stdout.flush()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to commit.")
    else:
        print("⚠️  Some tests failed. Check configuration and API access.")
    
    print("="*60 + "\n")
    sys.stdout.flush()
    
    return passed == total


if __name__ == "__main__":
    print("="*60)
    print("Script started")
    print("="*60)
    sys.stdout.flush()
    
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(1)