#!/usr/bin/env python3
"""
Simple diagnostic script to check your setup
Run this first if test_loader.py isn't working
"""

import sys
import os

print("="*60)
print("NYC PARKING PROJECT - DIAGNOSTIC CHECK")
print("="*60)

# 1. Check Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Location: {sys.executable}")

# 2. Check current directory
print(f"\n2. Current Directory: {os.getcwd()}")

# 3. Check if we're in the right place
from pathlib import Path
project_root = Path.cwd()
print(f"\n3. Project Structure Check:")

important_paths = {
    "src directory": project_root / "src",
    "data directory": project_root / "data",
    "config.py": project_root / "src" / "config.py",
    "data_loader.py": project_root / "src" / "data_loader.py",
    "requirements.txt": project_root / "requirements.txt",
}

for name, path in important_paths.items():
    exists = "✅" if path.exists() else "❌"
    print(f"   {exists} {name}: {path}")

# 4. Try importing requests
print(f"\n4. Testing Required Libraries:")
try:
    import requests
    print(f"   ✅ requests: {requests.__version__}")
except ImportError:
    print(f"   ❌ requests: NOT INSTALLED - Run: pip install requests")

try:
    import pandas
    print(f"   ✅ pandas: {pandas.__version__}")
except ImportError:
    print(f"   ❌ pandas: NOT INSTALLED - Run: pip install pandas")

# 5. Try importing config
print(f"\n5. Testing Module Imports:")
sys.path.insert(0, str(project_root))
try:
    from src import config
    print(f"   ✅ config module imported successfully")
    print(f"   API URL: {config.API_BASE_URL}")
except ImportError as e:
    print(f"   ❌ Failed to import config: {e}")
except Exception as e:
    print(f"   ⚠️  Config imported but error: {e}")

# 6. Test API connectivity
print(f"\n6. Testing NYC Open Data API:")
try:
    import requests
    url = "https://data.cityofnewyork.us/resource/nc67-uf89.json"
    params = {"$limit": 5}
    
    print(f"   Attempting to fetch 5 records...")
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API connection successful!")
        print(f"   Retrieved {len(data)} records")
        if data:
            print(f"   Sample keys: {list(data[0].keys())[:5]}")
    else:
        print(f"   ❌ API returned status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"   ❌ Connection timed out")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Connection error - check internet connection")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Try importing data_loader
print(f"\n7. Testing Data Loader Import:")
try:
    from src.data_loader import NYCParkingDataLoader
    print(f"   ✅ NYCParkingDataLoader imported successfully")
    
    # Try creating an instance
    loader = NYCParkingDataLoader()
    print(f"   ✅ Loader instance created")
    print(f"   Base URL: {loader.base_url}")
    
except ImportError as e:
    print(f"   ❌ Failed to import: {e}")
except Exception as e:
    print(f"   ❌ Error creating loader: {e}")

# 8. Environment check
print(f"\n8. Environment Variables:")
app_token = os.getenv("NYC_APP_TOKEN")
if app_token:
    print(f"   ✅ NYC_APP_TOKEN is set (length: {len(app_token)})")
else:
    print(f"   ⚠️  NYC_APP_TOKEN not set (optional - will use default rate limits)")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)

# Summary
print("\nQuick fixes if you see ❌:")
print("1. If modules not found → Run: pip install -r requirements.txt")
print("2. If wrong directory → cd to project root (where requirements.txt is)")
print("3. If import errors → Make sure src/config.py and src/data_loader.py exist")
print("4. If API errors → Check internet connection")
print("\nTo run tests: python src/test_loader.py")
print("To load data: python src/data_loader.py")