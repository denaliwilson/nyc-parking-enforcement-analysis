# Setup and Installation Guide

## Quick Start

### Prerequisites
- Python 3.13+
- Git
- pip (Python package manager)
- Internet connection (for data API access)

### Installation Steps

#### 1. Clone or Download the Repository
```bash
# If using git
git clone <repository-url>
cd nyc-parking-enforcement-analysis
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If you get encoding errors during installation (Windows), ensure you're using the virtual environment:
```bash
# Windows - Make sure .venv is active first
.\.venv\Scripts\pip.exe install -r requirements.txt
```

---

## Running the Project

### Quick Start - Analysis Tools

The fastest way to analyze NYC parking data:

#### Weekly Analysis (7 days, ~50 seconds)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run weekly analysis
python src/generate_weekly_analysis.py
```
**Prompts:**
- Enter start date in YYYY-MM-DD format (e.g., 2025-12-30)
- Confirm to proceed

**Output:** `outputs/reports/analysis_report_citations_week_YYYY-MM-DD_to_YYYY-MM-DD_TIMESTAMP.html`

**Includes:**
- 6 visualizations (daily trend, day of week, violations, hourly, borough, fines)
- ~190k-300k records analyzed
- Data quality metrics

#### Monthly Analysis (28-31 days, 2-10 minutes)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run monthly analysis
python src/generate_monthly_analysis.py
```
**Prompts:**
- Enter year (YYYY format, e.g., 2026)
- Enter month (1-12, e.g., 1 for January)
- Confirm to proceed

**Output:** `outputs/reports/analysis_report_citations_month_YYYY-MM_TIMESTAMP.html`

**Includes:**
- 8 visualizations (all weekly charts plus precinct bar chart and geographic map)
- 800k-1.2M+ records analyzed
- Color-coded precinct choropleth map showing spatial distribution
- Daily averages and comprehensive statistics

---

### Option 1: Manual Data Pipeline

Run individual components step-by-step:

#### Step 1: Check System Configuration
```bash
.\.venv\Scripts\python.exe src/diagnostic.py
```
This verifies:
- Python version and location
- Required libraries installed
- Project structure
- API connectivity
- Module imports

#### Step 2: Load Raw Data
```bash
.\.venv\Scripts\python.exe src/data_loader.py
```
Output: `data/raw/nyc_parking_<records>_<timestamp>.csv`

#### Step 3: Clean and Process Data
```bash
.\.venv\Scripts\python.exe src/data_cleaner.py
```
Output: `data/processed/parking_cleaned_<records>_<timestamp>.csv`

### Option 2: Step-by-Step (Legacy)

---

## Configuration

### API Configuration
Edit `src/config.py` to customize:

```python
# Number of records to load (max 50,000)
DEFAULT_LIMIT = 10000

# Date range for filtering
DEFAULT_START_DATE = "2024-11-01"
DEFAULT_END_DATE = "2025-01-31"

# Fields to extract from API
ESSENTIAL_FIELDS = [
    "plate", "state", "license_type", 
    "summons_number", "issue_date", "violation_time",
    "violation", "fine_amount", "reduction_amount",
    "county", "issuing_agency"
]
```

### Optional: NYC Open Data API Token
For higher rate limits, set your API token:

```bash
# Windows PowerShell
$env:NYC_APP_TOKEN = "your_token_here"

# Windows Command Prompt
set NYC_APP_TOKEN=your_token_here

# macOS/Linux
export NYC_APP_TOKEN=your_token_here
```

Get token: https://data.cityofnewyork.us/profile/app_tokens

---

## Troubleshooting

### Issue: "Source not found" when importing pandas/requests

**Solution:** You're using global Python instead of the virtual environment.
```bash
# Always activate venv first
.\.venv\Scripts\activate

# Then run scripts
python src/data_loader.py
```

### Issue: UnicodeEncodeError on Windows

**Solution:** Ensure you're using UTF-8 encoding:
```bash
# This is already fixed in the codebase, but if needed:
set PYTHONIOENCODING=utf-8
```

### Issue: API returns 429 (Rate Limited)

**Solution:** The script automatically retries with exponential backoff. Wait 1-2 minutes and try again, or:
1. Set `NYC_APP_TOKEN` environment variable (see Configuration section)
2. Reduce `DEFAULT_LIMIT` in `src/config.py`

### Issue: No data files found in data/raw/

**Solution:** Run the data loader first:
```bash
.\.venv\Scripts\python.exe src/data_loader.py
```

### Issue: Tests fail with "Failed to import data_loader"

**Solution:** Clear Python cache and ensure venv is active:
```bash
Remove-Item -Recurse src\__pycache__ -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe src/test_loader.py
```

---

## Project Directory Structure

```
nyc-parking-enforcement-analysis/
├── .venv/                          # Virtual environment
├── data/
│   ├── raw/                        # Downloaded raw data
│   │   └── *.csv
│   ├── processed/                  # Cleaned/processed data
│   │   └── parking_cleaned_*.csv
│   └── dof_parking_camera_violations.schema.json
├── src/
│   ├── config.py                   # Configuration settings
│   ├── data_loader.py              # Download data from API
│   ├── data_cleaner.py             # Clean and process data
│   ├── test_loader.py              # Test suite
│   ├── diagnostic.py               # System diagnostic
│   └── __pycache__/                # Python cache (auto-generated)
├── outputs/
│   ├── reports/                    # Analysis reports
│   └── figures/                    # Charts and visualizations
├── notebooks/                      # Jupyter notebooks
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview
├── DATA_DICTIONARY.md              # Field definitions
├── SETUP.md                        # This file
├── DATA_SOURCES.md                 # Data source documentation
├── PROJECT_STRUCTURE.md            # Folder structure explained
└── LICENSE                         # License file
```

---

## Key Files Explained

### Core Scripts
- **data_loader.py** - Fetches parking citation data from NYC Open Data API
- **data_cleaner.py** - Cleans, validates, and creates derived features
- **test_loader.py** - Automated test suite to verify functionality
- **diagnostic.py** - Checks system setup and dependencies
- **config.py** - Central configuration for all scripts

### Data Files
- **data/raw/** - Raw CSV files downloaded from API (not cleaned)
- **data/processed/** - Clean CSV files ready for analysis
- **data/*.schema.json** - API schema documentation

### Output Directories
- **outputs/figures/** - Charts and visualizations
- **outputs/reports/** - Analysis reports and summaries
- **notebooks/** - Jupyter notebooks for exploratory analysis

---

## Common Tasks

### Run Weekly Analysis (Recommended)
```bash
# Activate venv and run
.\.venv\Scripts\Activate.ps1
python src/generate_weekly_analysis.py
```
Analyzes 7 consecutive days with 6 visualizations. Output: HTML report in `outputs/reports/`

### Run Monthly Analysis (Recommended)
```bash
# Activate venv and run
.\.venv\Scripts\Activate.ps1
python src/generate_monthly_analysis.py
```
Analyzes full month (28-31 days) with 8 visualizations + precinct map. Output: HTML report in `outputs/reports/`

### Download fresh data
```bash
.\.venv\Scripts\python.exe src/data_loader.py
```

### Clean the most recent raw data file
```bash
.\.venv\Scripts\python.exe src/data_cleaner.py
```

### Verify everything works
```bash
.\.venv\Scripts\python.exe src/diagnostic.py
```

### Check configuration
```bash
.\.venv\Scripts\python.exe -c "from src.config import *; print(ESSENTIAL_FIELDS)"
```

---

## Performance Notes

### Analysis Tools
- **Weekly Analysis:** 7 days, ~190k-300k records, ~50 seconds total
- **Monthly Analysis:** 28-31 days, ~800k-1.2M records, 2-10 minutes
- **Precinct Map Download:** ~2-3 seconds from NYC ArcGIS API

### Data Pipeline
- **Data Download:** 1,000 records takes ~0.5-1 second
- **Data Cleaning:** 1,000 records takes ~2-3 seconds
- **File Size:** Raw CSV (~1,000 records) ≈ 100-150 KB
- **Processed Size:** Cleaned CSV ≈ similar to raw

### Visualization
- **Charts Generated:** 6 (weekly) or 8 (monthly) matplotlib figures
- **Encoding:** Base64 PNG embedded in HTML
- **Report Size:** 2-5 MB depending on number of charts

---

## Next Steps

1. **Run the full pipeline:**
   ```bash
   .\.venv\Scripts\python.exe src/data_loader.py
   .\.venv\Scripts\python.exe src/data_cleaner.py
   ```

2. **Verify with tests:**
   ```bash
   .\.venv\Scripts\python.exe src/test_loader.py
   ```

3. **Explore the data:**
   - Open `data/processed/parking_cleaned_*.csv` in Excel or a data analysis tool
   - Or use Jupyter notebooks for analysis

4. **Refer to documentation:**
   - [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - Field definitions
   - [DATA_SOURCES.md](DATA_SOURCES.md) - Data source details
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Folder organization

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review [DATA_SOURCES.md](DATA_SOURCES.md) for API documentation
3. Run diagnostic: `.\.venv\Scripts\python.exe src/diagnostic.py`
4. Check Python version: `.\.venv\Scripts\python.exe --version`
