# NYC Parking Enforcement - Data Dictionary

## Overview
This document describes all fields in the NYC Parking Citations dataset after loading and cleaning.

**Dataset Size:** 764 records (cleaned from 1,000 raw records)  
**Last Updated:** February 1, 2026  
**Data Source:** NYC Open Data API (dataset: nc67-uf89)

---

## Field Definitions

### Original/Raw Fields (from NYC Open Data API)

#### Vehicle Information

| Field | Type | Description | Sample Values | Notes |
|-------|------|-------------|---------------|----|
| `plate` | string | License plate number | HPK2083, FFZ7198 | Primary identifier for vehicle |
| `state` | string | State code of vehicle registration | NY, NJ, PA, MA, CA | Uppercase 2-letter codes |
| `license_type` | string | Type of vehicle license | PAS (Passenger), COM (Commercial), OMT, SRF | 14 unique types in dataset |

#### Citation Information

| Field | Type | Description | Sample Values | Notes |
|-------|------|-------------|---------------|----|
| `summons_number` | integer | Unique citation identifier | 8712553359 | Primary key, no nulls |
| `issue_date` | string | Date violation was issued | 09/15/2016 | Format: MM/DD/YYYY (after cleaning: datetime) |
| `violation_time` | string | Time violation was observed | 1045A, 0230P | Format: HHmmA (military-style with AM/PM) |
| `violation` | string | Description of violation | NO PARKING-STREET CLEANING | Standardized violation types |
| `violation_time_parsed` | float | Parsed time as decimal hours (0-23) | null (see Data Quality Notes) | Created during cleaning - parsing incomplete |
| `violation_hour` | float | Hour of day when violation occurred | null (see Data Quality Notes) | Extracted from parsed time - incomplete |

#### Penalty Information

| Field | Type | Description | Range | Notes |
|-------|------|-------------|-------|-------|
| `fine_amount` | float | Original fine amount | $30 - $650 | Mean: $100.69, Median: $65 |
| `reduction_amount` | float | Amount reduced from fine | $0 - $250 | 7.1% of records have reductions |
| `net_fine` | float | Fine after reduction applied | -$10 - $650 | Calculated field |
| `fine_amount_flag` | string | Data quality flag for fine | "normal", "zero", "high", "negative" | Flagged based on thresholds |

#### Agency Information

| Field | Type | Description | Sample Values | Notes |
|-------|------|-------------|---------------|----|
| `issuing_agency` | string | Government agency that issued citation | TRAFFIC, PARKING, DOT | 11 unique agencies |
| `county` | string | Borough/County where violation occurred | MANHATTAN, BROOKLYN, QUEENS, BRONX, STATEN ISLAND | Standardized from codes (NY=MAN, K=BK, Q=QN, etc.) |
| `is_ny_plate` | boolean | Whether vehicle is registered in NY | true, false | Derived from state field |

---

### Derived/Engineered Fields (created during cleaning)

#### Temporal Features

| Field | Type | Description | Sample Values | Notes |
|-------|------|-------------|---------------|----|
| `year` | integer | Year violation was issued | 2015, 2016 | Extracted from issue_date |
| `month` | integer | Month violation was issued | 1-12 | Extracted from issue_date |
| `month_name` | string | Month name | January, February, March... | Extracted from issue_date |
| `day` | integer | Day of month | 1-31 | Extracted from issue_date |
| `day_of_week` | string | Day of week | Monday, Tuesday... Sunday | Extracted from issue_date |
| `week_of_year` | integer | ISO week number | 1-53 | ISO standard week numbering |
| `quarter` | integer | Quarter of year | 1, 2, 3, 4 | Derived from month |
| `time_of_day` | string | Time period category | Morning (5-12), Afternoon (12-17), Evening (17-21), Night (21-5), Unknown | Based on violation_hour |
| `is_business_hours` | boolean | Whether violation occurred during business hours | true, false | 9 AM - 5 PM = business hours |
| `is_weekend` | boolean | Whether violation occurred on weekend | true, false | Saturday or Sunday |

#### Privacy/Security

| Field | Type | Description | Sample Values | Notes |
|-------|------|-------------|---------------|----|
| `plate_masked` | string | License plate with masking for privacy | ***2083, ***7198 | Last 3 digits only for analysis |

---

## Data Quality Notes

### Data Cleaning Results
- **Initial Records:** 1,000
- **Final Records:** 764
- **Retention Rate:** 76.4%
- **Records Removed:** 236

### Reasons for Record Removal

1. **Invalid Dates:** 96 records (9.6%)
   - Could not be parsed to valid datetime format
   - Removed during date cleaning step

2. **Missing Critical Fields:** 140 records (14%)
   - Null values in summons_number, issue_date, or county
   - Removed during finalization step

### Known Issues

1. **Time Parsing Problems** (All Records Affected)
   - `violation_time_parsed` and `violation_hour` fields are **all null/empty**
   - Original `violation_time` values don't parse correctly with current logic
   - Likely time format issue (expected HHmmA, actual format may differ)
   - Status: NEEDS FIX - manual inspection and parsing logic update required

2. **County Field Standardization**
   - Some records still contain abbreviated codes (MN) instead of full names
   - Mapping rules may need expansion for complete standardization

3. **Issue Date Field**
   - Historical data only (2008-2017 range)
   - No recent data available (2024-2025 tested in analysis but not present)

4. **State Field Anomalies**
   - 11 non-standard state codes found (AL, IL, GA, DP, OR, MI, SC, LA, MN, NC)
   - Likely data entry errors or special codes

### Missing Value Summary

| Field | Count | Percentage | Action Taken |
|-------|-------|-----------|--------------|
| violation_time_parsed | 764 | 100% | Flagged for investigation - parsing failure |
| violation_hour | 764 | 100% | Flagged for investigation - parsing failure |
| All Others | 0 | 0% | No missing values after cleaning |

---

## Field Descriptions by Use Case

### For Borough-Level Summaries
- `county` - Borough/county code (standardized to full names during cleaning)
- `issue_date` - Temporal dimension for aggregation
- `plate_masked` - Vehicle identifier (masked for privacy)

### For Enforcement Pattern Analysis
- `violation` - Type of violation committed
- `issuing_agency` - Which agency made citation
- `time_of_day` - When violations typically occur
- `day_of_week` - Day patterns
- `is_business_hours` - Business vs. after-hours violations

### For Financial Analysis
- `fine_amount` - Revenue impact
- `reduction_amount` - Discount/negotiation impact
- `net_fine` - Actual collected amount
- `fine_amount_flag` - Data quality indicators

### For Vehicle Analysis
- `state` - Registration location
- `is_ny_plate` - In-state vs. out-of-state vehicles
- `license_type` - Vehicle classification

---

## Data Type Conversion Notes

### Fields Converted During Cleaning

1. **issue_date:** string → datetime
   - Original format: MM/DD/YYYY
   - After: Python datetime object
   - Invalid dates removed

2. **fine_amount:** string → float
   - Coerced to numeric type
   - Used `pd.to_numeric(..., errors='coerce')`

3. **reduction_amount:** string → float
   - Coerced to numeric type
   - Null values filled with 0

### Derived Boolean Fields
- `is_ny_plate` - True if state == 'NY'
- `is_weekend` - True if day_of_week in ['Saturday', 'Sunday']
- `is_business_hours` - True if 9 <= hour <= 17

---

## Unique Value Counts

| Field | Unique Values | Notes |
|-------|---------------|-------|
| state | 23 | Includes non-standard codes |
| license_type | 14 | PAS (73.9%) is dominant |
| violation | Variable | Multiple violation types |
| county | 9 | After standardization (NY, BK, Q, BX, R, MN, etc.) |
| issuing_agency | 11 | TRAFFIC, PARKING, DOT most common |
| time_of_day | 5 | Morning, Afternoon, Evening, Night, Unknown |
| day_of_week | 7 | All days represented |
| month_name | 12 | All months represented |
| fine_amount_flag | 4 | normal, zero, high, negative |

---

## Recommended Next Steps

### Priority 1 - Critical Issues
1. **Fix time parsing** - Investigate actual `violation_time` format and update parsing logic
2. **Verify county mapping** - Ensure all borough codes are correctly mapped

### Priority 2 - Data Quality
1. Investigate non-standard state codes
2. Identify why ~10% of date values cannot be parsed
3. Check for date format variations in source data

### Priority 3 - Analysis Enhancements
1. Create geographic coordinates for mapping (latitude/longitude)
2. Link to DOF parking dataset for additional enrichment
3. Calculate violation rates by agency, borough, time period

---

## Contact & Maintenance

- **Last Updated:** February 1, 2026
- **Data Location:** `data/processed/parking_cleaned_*.csv`
- **Source API:** NYC Open Data (https://data.cityofnewyork.us/resource/nc67-uf89.json)
- **Related Files:** 
  - Data Loading: `src/data_loader.py`
  - Data Cleaning: `src/data_cleaner.py`
  - Configuration: `src/config.py`
