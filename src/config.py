"""
Configuration settings for NYC Parking Citations project
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GEOSPATIAL_DATA_DIR = DATA_DIR / "geospatial"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
FIGURES_DIR = OUTPUTS_DIR / "figures"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, GEOSPATIAL_DATA_DIR, OUTPUTS_DIR, REPORTS_DIR, FIGURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# NYC Open Data API Configuration
API_BASE_URL = "https://data.cityofnewyork.us/resource/nc67-uf89.json"
DATASET_ID = "nc67-uf89"
API_DOMAIN = "data.cityofnewyork.us"

# API Token (optional - improves rate limits)
# Get your token from: https://data.cityofnewyork.us/profile/app_tokens
# Store in environment variable: export NYC_APP_TOKEN="your_token_here"
APP_TOKEN = os.getenv("NYC_APP_TOKEN", None)

# Data loading defaults
DEFAULT_LIMIT = 10000
MAX_RECORDS_PER_REQUEST = 50000

# Date range for initial data load (adjust as needed)
DEFAULT_START_DATE = "2024-11-01"
DEFAULT_END_DATE = "2025-01-31"

# Borough names (for filtering)
BOROUGHS = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]

# Fields to select (reduces data transfer)
# Note: These must match the actual API field names (snake_case)
ESSENTIAL_FIELDS = [
    "plate",
    "state",
    "license_type",
    "summons_number",
    "issue_date",
    "violation_time",
    "violation",
    "fine_amount",
    "reduction_amount",
    "precinct",
    "county",
    "issuing_agency"
]

# Output file naming
OUTPUT_FILE_PREFIX = "nyc_parking"

print(f"Configuration loaded")
print(f"  Project root: {PROJECT_ROOT}")
print(f"  API Token: {'Set' if APP_TOKEN else 'Not set (using default rate limits)'}")