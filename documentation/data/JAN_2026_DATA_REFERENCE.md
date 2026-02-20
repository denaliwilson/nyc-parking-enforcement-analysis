# January 2026 Sample Data - Quick Reference

## File Location
```
data/processed/jan_2026_sample_data.csv
```

## Overview
- **Total Records**: 859,885 parking violations
- **Date Range**: January 1-31, 2026 (Complete Month)
- **File Size**: 154.27 MB
- **Status**: Fully cleaned and processed

## Quick Stats

### By Borough
- Manhattan: ~400K citations
- Brooklyn: ~200K citations  
- Queens: ~150K citations
- Bronx: ~70K citations
- Staten Island: ~30K citations

### Top Violations
1. No Parking - Street Cleaning
2. No Standing - Day/Time Limits
3. Fire Hydrant
4. Expired Meter
5. No Parking - Day/Time Limits

### Peak Activity
- **Busiest Hour**: 8-9 AM (morning street cleaning)
- **Busiest Day**: Thursday
- **Most Active Precinct**: Precinct 19 (Manhattan)

## Data Fields (29 columns)

### Core Fields
- `plate` - Masked license plate (last 3 chars visible)
- `state` - Standardized 2-letter state code
- `summons_number` - Unique violation ID
- `issue_date` - Citation date (YYYY-MM-DD)
- `violation_time` - Time of violation (HH:MM format)
- `violation` - Violation description
- `fine_amount` - Original fine in dollars

### Geographic Fields
- `precinct` - Police precinct number
- `county` - NYC borough name
- `issuing_agency` - Agency that issued citation

### Derived/Calculated Fields
- `violation_time_parsed` - 24-hour time (HH:MM)
- `violation_hour` - Hour of day (0-23)
- `time_of_day` - Category: Morning/Afternoon/Evening/Night
- `is_business_hours` - Boolean (9 AM - 5 PM, weekdays)
- `is_weekend` - Boolean (Saturday/Sunday)
- `is_ny_plate` - Boolean (state == 'NY')
- `day_of_week` - Day name (Monday-Sunday)
- `month_name` - "January"
- `week_of_year` - ISO week number
- `quarter` - Calendar quarter (1)
- `net_fine` - fine_amount - reduction_amount
- `precinct_numeric` - Integer precinct number
- `fine_amount_flag` - Category: normal/high/low

## Data Quality

### Cleaned Features
✅ **State codes validated** - Only valid US states + territories  
✅ **Time parsing** - All violation times converted to 24-hour format  
✅ **Precinct normalization** - Numeric codes extracted from strings  
✅ **Date consistency** - All dates in ISO format (YYYY-MM-DD)  
✅ **Privacy protection** - Plate numbers masked (first chars hidden)  

### Known Limitations
- ~2% of records have state = 'UNKNOWN' (invalid/missing state codes)
- Some violation times may be approximate (rounded to nearest 5 minutes)
- Reduction amounts mostly zero (few contested violations in dataset)

## Usage Examples

### Load in Python
```python
import pandas as pd

# Load the data
df = pd.read_csv('data/processed/jan_2026_sample_data.csv')
print(f"Loaded {len(df):,} citations")

# Convert date column
df['issue_date'] = pd.to_datetime(df['issue_date'])

# Filter examples
manhattan = df[df['county'] == 'MANHATTAN']
ny_plates = df[df['is_ny_plate'] == True]
weekend_violations = df[df['is_weekend'] == True]
```

### Common Queries
```python
# Top 10 violations
top_violations = df['violation'].value_counts().head(10)

# Citations by hour
hourly = df.groupby('violation_hour').size()

# NY vs Out-of-State
state_comparison = df.groupby('is_ny_plate').agg({
    'summons_number': 'count',
    'fine_amount': 'sum'
})

# Business hours vs After hours
business_hrs = df.groupby('is_business_hours')['fine_amount'].mean()
```

### In Streamlit Dashboard
The dashboard automatically loads this file when clicking **"Load January 2026 Sample Data"** button on the landing page.

## Data Source
NYC Department of Finance - Parking Camera Violations  
**Dataset**: nc67-uf89  
**Fetched**: February 3, 2026  
**API**: https://data.cityofnewyork.us/resource/nc67-uf89.json

## Notes
- This is a **sample/reference dataset** for development and testing
- For production analysis, use the dashboard's date picker to fetch current data
- File is **excluded from git** (see `.gitignore`) due to size
- Dashboard will auto-fetch and create this file if missing (Streamlit Cloud deployment)

## Related Files
- Full data dictionary: [DATA_DICTIONARY.md](../DATA_DICTIONARY.md)
- Data processing scripts: [src/data_cleaner.py](../src/data_cleaner.py)
- Dashboard application: [dashboard.py](../dashboard.py)
