# Processed Data Files

This directory contains cleaned and processed parking violation citation data from NYC Open Data.

## Quick Reference Files

### **jan_2026_sample_data.csv**
- **Description**: Complete January 2026 parking violation citations (cleaned)
- **Records**: 859,885 citations
- **Date Range**: January 1-31, 2026
- **Size**: ~154 MB
- **Use Case**: Pre-loaded sample data for dashboard analysis and testing
- **Columns**: 29 fields including plate, state, issue_date, violation, fine_amount, precinct, borough, etc.
- **Status**: Fully cleaned with standardized state codes, parsed violation times, and derived fields

### Key Features of Cleaned Data:
- ✅ State codes validated and standardized (50 US states + territories)
- ✅ Violation times parsed into hour/time-of-day categories
- ✅ Business hours flag (9 AM - 5 PM, weekdays)
- ✅ Weekend indicator
- ✅ Precinct numeric codes extracted
- ✅ Masked plate numbers (privacy protection)
- ✅ Net fine calculated (fine_amount - reduction_amount)
- ✅ NY plate indicator for local vs. out-of-state analysis

## File Naming Convention

Other files in this directory follow the pattern:
```
parking_cleaned_citations_[period]_[date-range]_[count]-records_[timestamp].csv
```

Example: `parking_cleaned_citations_month_2026-01_859376-records_20260203_120623.csv`

## Data Dictionary

See [DATA_DICTIONARY.md](../../DATA_DICTIONARY.md) in the root directory for complete field descriptions.

## Usage

### In Dashboard
The dashboard's "Load January 2026 Sample Data" button automatically loads `jan_2026_sample_data.csv` for instant analysis.

### In Scripts
```python
import pandas as pd
from pathlib import Path

# Load January 2026 sample data
df = pd.read_csv('data/processed/jan_2026_sample_data.csv')
print(f"Loaded {len(df):,} citations from January 2026")
```

## Data Source

All data originates from the NYC Department of Finance Parking Camera Violations dataset via NYC Open Data API.

**Dataset ID**: nc67-uf89  
**API Endpoint**: https://data.cityofnewyork.us/resource/nc67-uf89.json

## Notes

- CSV files are excluded from git tracking (see `.gitignore`)
- The dashboard's `load_sample_data()` function will automatically fetch and cache January 2026 data if this file is missing
- For Streamlit Cloud deployment, the data is fetched on first load and cached for 24 hours
