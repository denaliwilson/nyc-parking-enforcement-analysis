# Data Sources Documentation

## Primary Data Source: NYC Open Data

### Dataset Information

| Property | Value |
|----------|-------|
| **Dataset Name** | DOF Parking Camera Violations |
| **Dataset ID** | nc67-uf89 |
| **Publisher** | NYC Department of Finance (DOF) |
| **Platform** | Socrata (NYC Open Data) |
| **API Endpoint** | https://data.cityofnewyork.us/resource/nc67-uf89.json |
| **Data Format** | JSON (API), CSV (downloaded) |
| **Update Frequency** | Regularly updated |
| **License** | Public Domain (CC0) |

### Dataset Overview

This dataset contains parking violations issued by NYC parking enforcement agents through automated camera systems. The data includes:

- Vehicle information (plate, state, license type)
- Citation details (summons number, issue date, violation type)
- Penalty information (fine amount, reductions)
- Geographic information at the borough/county level
- Agency information (issuing agency)

**Dataset Size:** Millions of records  
**Coverage Period:** Historical data from 2008 onwards  
**Geographies:** All five NYC boroughs (Manhattan, Brooklyn, Queens, Bronx, Staten Island)

### Data Dictionary (API Fields)

The raw API returns these fields:

```json
{
  "plate": "4JF374",
  "state": "MA",
  "license_type": "PAS",
  "summons_number": "8712553359",
  "issue_date": "12/20/2018",
  "violation_time": "11:57A",
  "violation": "NO PARKING-STREET CLEANING",
  "fine_amount": "65",
  "penalty_amount": "0",
  "interest_amount": "0",
  "reduction_amount": "0",
  "payment_amount": "65",
  "amount_due": "0",
  "precinct": "020",
  "county": "NY",
  "issuing_agency": "TRAFFIC",
  "summons_image": {
    "url": "http://nycserv.nyc.gov/...",
    "description": "View Summons"
  }
}
```

### How to Access the Data

#### Option 1: Through the Web Interface
1. Visit: https://data.cityofnewyork.us/resource/nc67-uf89
2. Browse, filter, and download directly
3. Limited to 10,000 rows per export

#### Option 2: Using the Socrata Open Data API
```bash
# Get 100 records
curl "https://data.cityofnewyork.us/resource/nc67-uf89.json?$limit=100"

# Filter by county
curl "https://data.cityofnewyork.us/resource/nc67-uf89.json?$where=county=%27NY%27&$limit=1000"

# Filter by date range
curl "https://data.cityofnewyork.us/resource/nc67-uf89.json?$where=issue_date>=%272016-01-01%27&$limit=1000"
```

#### Option 3: Using Python (This Project)
```python
from src.data_loader import NYCParkingDataLoader

loader = NYCParkingDataLoader()
df = loader.load_sample(limit=10000)
```

### API Documentation

#### Query Parameters

| Parameter | Type | Example | Notes |
|-----------|------|---------|-------|
| `$select` | string | `$select=plate,summons_number,fine_amount` | Specify fields to retrieve |
| `$where` | string | `$where=issue_date>='2016-01-01'` | Filter records using SOQL |
| `$limit` | integer | `$limit=50000` | Maximum 50,000 records per request |
| `$offset` | integer | `$offset=50000` | For pagination (combined with limit) |
| `$order` | string | `$order=issue_date DESC` | Sort results |
| `$$app_token` | string | From profile settings | Authentication for higher rate limits |

#### Date/Time Formats

- **Issue Date:** MM/DD/YYYY (e.g., "01/15/2016")
- **Violation Time:** HHmmA format (e.g., "0930A" = 9:30 AM, "0230P" = 2:30 PM)

#### Example Queries

**Get recent Manhattan violations:**
```
https://data.cityofnewyork.us/resource/nc67-uf89.json?
$where=county='NY' AND issue_date>='2016-01-01'
&$order=issue_date DESC
&$limit=1000
```

**Get high-value fines:**
```
https://data.cityofnewyork.us/resource/nc67-uf89.json?
$where=fine_amount > 100
&$select=plate,summons_number,fine_amount,county
&$limit=5000
```

**Get citations by agency:**
```
https://data.cityofnewyork.us/resource/nc67-uf89.json?
$select=issuing_agency,COUNT(*)
&$group=issuing_agency
&$limit=100
```

### Rate Limits

- **Without API Token:** ~5 requests per minute, 20 MB data limit
- **With API Token:** Significantly higher limits
- **Bulk Downloads:** Not recommended through API; use website export

**Get API Token:**
1. Create free account at https://data.cityofnewyork.us
2. Visit https://data.cityofnewyork.us/profile/app_tokens
3. Generate application token
4. Use with `$$app_token=YOUR_TOKEN` in API calls

### Known Data Issues

1. **Encoding Anomalies:**
   - Some date values may be malformed
   - Approximately 10% of records have unparseable dates

2. **Time Format Inconsistencies:**
   - Violation time format may vary
   - Some records missing violation time entirely

3. **State Code Variations:**
   - Non-standard state codes mixed with ISO state codes
   - Examples: "NY", "99", "DP", "MN"

4. **County Coding:**
   - Uses abbreviated county codes: NY (Manhattan), K (Brooklyn), Q (Queens), X (Bronx), R (Staten Island)
   - Some records may use alternative abbreviations

5. **Data Completeness:**
   - Not all records have all fields populated
   - Fine amount may be $0 (dismissed cases)
   - Reduction amount varies significantly

### Data Processing by This Project

The project includes custom processing to handle these issues:

1. **Date Validation**
   - Attempts to parse with multiple formats
   - Removes records with unparseable dates
   - Creates standardized datetime field

2. **Time Parsing**
   - Attempts to parse HHmmA format
   - Extracts hour for analysis
   - Categorizes into time periods (morning, afternoon, evening, night)

3. **County Standardization**
   - Maps abbreviated codes to full borough names
   - Handles alternative abbreviations

4. **Data Augmentation**
   - Creates temporal features (year, month, day of week)
   - Calculates net fine after reductions
   - Flags data quality issues

### Related NYC Open Data Datasets

For enrichment and context, these related datasets are available:

| Dataset | ID | Description |
|---------|----|----|
| Parking Violations Issued | k2np-d7i3 | All parking violations (broader dataset) |
| NYC Park Facilities | p546-ljs2 | Park locations and amenities |
| NYC Parking Garages | c2rq-f3kg | Public parking facility locations |
| Street Segments | 44jf-dvmh | NYC street network for GIS |
| NYC Boroughs | n8v6-gdp6 | Borough boundaries and information |

Note: These related datasets are optional and not used in the current workflow.

### How to Use Other Datasets

Similar API structure works for all Socrata datasets:

```bash
# Replace dataset ID (e.g., k2np-d7i3 for all violations)
https://data.cityofnewyork.us/resource/k2np-d7i3.json?$limit=1000
```

### Limitations and Considerations

1. **Historical Data Only**
   - Dataset focuses on past violations
   - Real-time updates may lag behind actual citations

2. **Privacy**
   - License plates included in raw data
   - Project masks plates to last 3 digits only for analysis
   - Never share full plate numbers

3. **Coverage**
   - Primarily camera-based violations
   - May not include hand-written citations
   - Some agencies/precincts may report incompletely

4. **Accuracy**
   - Subject to data entry errors
   - Some records may be corrected/disputed
   - Amounts may change due to appeals

### Citing This Data

**For academic/research use, cite as:**
> New York City Department of Finance. (2026). DOF Parking Camera Violations. NYC Open Data. https://data.cityofnewyork.us/resource/nc67-uf89.json

**License:** Public Domain (CC0 1.0 Universal)

---

## Secondary Data Sources

### Configuration Schema
- **File:** `data/dof_parking_camera_violations.schema.json`
- **Purpose:** Documents field definitions from NYC Open Data
- **Contains:** Field types, valid values, descriptions

### Optional Enrichment (Not Used)
- This project focuses on temporal analysis and summary statistics.
- If you later add external reference datasets, store them in a separate folder and document them explicitly.

---

## Data Access Best Practices

### For Analysis
1. Use processed data: `data/processed/parking_cleaned_*.csv`
2. This data is cleaned, validated, and deduplicated

### For New Data Loads
1. Update date range in `src/config.py`
2. Run `python src/data_loader.py` to download
3. Run `python src/data_cleaner.py` to clean
4. Review output statistics and quality flags

### For Large-Scale Analysis
1. Request data export directly from NYC Open Data website
2. Or use pagination with `$offset` parameter in API
3. Consider time-based filtering to reduce record count

### For Real-Time Monitoring
1. Not recommended - API is not designed for real-time use
2. Set up periodic tasks (daily/weekly) for fresh data loads
3. Store timestamped versions for historical comparison

---

## Contact & Support

- **NYC Open Data Support:** https://support.socrata.com
- **NYC Department of Finance:** https://www1.nyc.gov/site/finance/index.page
- **Dataset Publisher:** NYC DOF
- **Data Last Updated:** Check NYC Open Data website

---

## Change Log

| Date | Change | Impact |
|------|--------|--------|
| 2026-02-01 | Initial documentation | Project created |
| | Documented API integration | Configuration established |
| | Identified data quality issues | Added cleaning logic |

See [README.md](README.md) for project change history.
