# Project Structure

## Directory Overview

```
nyc-parking-enforcement-analysis/
├── .git/                           # Git version control
├── .gitignore                      # Files to ignore in git
├── venv/                           # Virtual environment (auto-created, not tracked)
│   ├── Scripts/                    # Executables (python.exe, pip.exe)
│   └── Lib/                        # Python packages
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                 # Dashboard theme and settings
│
├── dashboard.py                    # Main Streamlit dashboard application (1000+ lines)
│   └── Features: Real-time data loading, interactive maps, multi-level drill-down
│
├── requirements.txt                # Python dependencies (Streamlit Cloud compatible)
│   └── Pandas 2.x, GeoPandas, Plotly, Streamlit, etc.
│
├── packages.txt                    # System packages (empty - pure Python deployment)
│
├── data/                           # Data storage (auto-created by scripts)
│   ├── raw/                        # Raw downloaded data (not modified)
│   │   └── parking_raw_*.csv       # Raw API downloads (temporary)
│   │
│   ├── processed/                  # Cleaned, analysis-ready data
│   │   ├── parking_cleaned_citations_week_*.csv
│   │   │   # 7-day combined datasets from analysis
│   │   ├── parking_cleaned_citations_month_*.csv
│   │   │   # 28-31 day combined datasets from analysis
│   │   └── parking_cleaned_*_records_*.csv
│   │       # Individual cleaned datasets
│   │
│   ├── archive/                    # Archived processed files (manual archiving)
│   │   └── Older versions of processed datasets
│   │
│   └── geospatial/                 # Geographic data
│       └── nyc_precincts.geojson  # NYC precinct boundaries (auto-downloaded)
│           # Downloaded from NYC ArcGIS API on first use
│
├── src/                            # Source code modules
│   ├── __pycache__/                # Python cache (auto-generated, not tracked)
│   │
│   ├── config.py                   # Configuration settings and constants
│   │   └── Contains: API URLs, data paths, field definitions
│   │
│   ├── data_loader.py              # NYC Open Data API integration (500+ lines)
│   │   └── Classes: NYCParkingDataLoader
│   │   └── Methods: load_by_day(), load_by_date_range(), save_data()
│   │   └── Features: Pagination, rate limiting, error handling
│   │
│   ├── data_cleaner.py             # Data cleaning and validation (900+ lines)
│   │   └── Classes: ParkingDataCleaner
│   │   └── Methods: clean_dataframe(), check_data_quality(), clean_dates()
│   │   └── Features: Type conversion, duplicate removal, validation
│   │
│   ├── generate_weekly_analysis.py # CLI: Weekly analysis with 6 visualizations
│   │   └── Interactive 7-day analysis tool
│   │   └── Output: HTML reports with embedded charts
│   │   └── Run: python src/generate_weekly_analysis.py
│   │
│   ├── generate_monthly_analysis.py # CLI: Monthly analysis with 8+ visualizations
│   │   └── Interactive full-month analysis tool
│   │   └── Includes: Choropleth maps and precinct analysis
│   │   └── Output: HTML reports with embedded charts and maps
│   │   └── Run: python src/generate_monthly_analysis.py
│   │
│   ├── preliminary_analysis.py     # Initial exploratory analysis (legacy)
│   │   └── Basic statistical analysis and data profiling
│   │
│   ├── diagnostic.py               # System diagnostics and verification
│   │   └── Checks: Python version, dependencies, API access
│   │   └── Run: python src/diagnostic.py
│   │
│   └── tests/                      # Test suite (unit tests)
│       ├── test_cleaner.py         # Tests for data cleaning
│       └── __pycache__/            # Test cache
│
├── outputs/                        # Analysis outputs and results
│   ├── reports/                    # HTML analysis reports
│   │   ├── analysis_report_citations_week_*.html
│   │   │   └── Weekly reports (6 visualizations, embedded charts)
│   │   └── analysis_report_citations_month_*.html
│   │       └── Monthly reports (8 visualizations + choropleth map)
│   │
│   └── figures/                    # Standalone figures (if generated)
│       └── Charts exported as PNG (embedded in HTML reports)
│
├── notebooks/                      # Jupyter notebooks (optional exploration)
│   └── For ad-hoc analysis and prototyping
│
├── Documentation Files
│   ├── README.md                   # Project overview, features, quick start
│   ├── SETUP.md                    # Installation, deployment, configuration
│   ├── PROJECT_STRUCTURE.md        # This file - directory layout
│   ├── DATA_DICTIONARY.md          # Field definitions and data types
│   ├── DATA_SOURCES.md             # API documentation and endpoints
│   └── LICENSE                     # Project license
│
└── Configuration Files
    ├── .gitignore                  # Git ignore patterns
    └── .env                        # Environment variables (optional, not tracked)
```

---

## Key Components

### Dashboard Application

**`dashboard.py`** - Interactive Streamlit web application (1006 lines)

**Architecture:**
- **Landing Page**: Hero image with NYC skyline, date selection interface
- **Data Loading**: Real-time API fetching with progress indicators
- **Multi-level Views**: Citywide → Borough → Precinct drill-down
- **Caching**: Smart caching for performance (`@st.cache_data`, `@st.cache_resource`)

**Key Functions:**
```python
get_latest_available_date()     # Query API for latest data
load_geojson()                   # Load NYC precinct boundaries
create_choropleth_map()         # Generate interactive maps
handle_precinct_selection()     # Click interaction logic
```

**Technologies:**
- Streamlit for UI framework
- Plotly for interactive charts and maps
- Pandas for data manipulation
- GeoPandas for geographic operations

### Data Pipeline Modules

**`src/config.py`** - Configuration and constants
- API URLs and endpoints
- Data directory paths
- Field definitions and essential columns
- Default parameters

**`src/data_loader.py`** - NYC Open Data API integration
- Handles API authentication and rate limiting
- Supports pagination for large datasets
- Implements retry logic and error handling
- Can load by day, week, month, or custom range

**`src/data_cleaner.py`** - Data cleaning and validation
- Type conversions (dates, numerics, categoricals)
- Duplicate detection and removal
- Data quality reporting
- Missing value handling
- Validation rules enforcement

### Analysis Scripts

**`src/generate_weekly_analysis.py`** - 7-day analysis reports
- Interactive CLI prompts for date selection
- Generates 6 visualizations
- Execution time: ~50 seconds
- Output: Self-contained HTML with embedded charts

**`src/generate_monthly_analysis.py`** - Monthly analysis reports
- Full month coverage (28-31 days)
- Generates 8+ visualizations including choropleth map
- Execution time: 2-10 minutes
- Output: HTML with geographic maps

---

## Directory Descriptions

### `/data` - Data Management
Stores all project data organized by processing stage.

**Subdirectories:**
- **`raw/`** - Temporary raw data from API (not tracked in git)
  - Never modify files here
  - Auto-cleaned after processing

- **`processed/`** - Clean, analysis-ready data
  - Output from data cleaning pipeline
  - All quality checks applied
  - Deduplicated and validated
  - Safe to use for analysis

- **`geospatial/`** - Geographic boundary files
  - `nyc_precincts.geojson` - NYPD precinct polygons
  - Auto-downloaded from NYC ArcGIS on first use
  - Cached for performance

### `/src` - Source Code
Python modules and scripts for the project.

**Module Overview:**

| File | Purpose | Type | Lines | Key Features |
|------|---------|------|-------|--------------|
| config.py | Configuration | Module | 100 | Paths, API settings, constants |
| data_loader.py | API integration | Module/Script | 550 | Pagination, rate limiting, retry logic |
| data_cleaner.py | Data processing | Module/Script | 900 | Type conversion, validation, quality checks |
| generate_weekly_analysis.py | 7-day reports | Script | 800 | 6 visualizations, HTML output |
| generate_monthly_analysis.py | Monthly reports | Script | 900 | 8 visualizations, choropleth maps |
| diagnostic.py | System checks | Script | 200 | Dependency verification |

**Usage Patterns:**
1. **Import as module**: `from src.config import ESSENTIAL_FIELDS`
2. **Execute as script**: `python src/data_loader.py`
3. **Dashboard imports**: All modules imported and reloaded by dashboard.py
4. **Analysis tools generate HTML reports with embedded visualizations**

### `/outputs` - Results and Artifacts
Contains all generated analysis outputs.

**Subdirectories:**
- **`reports/`** - Narrative analysis reports
- **`figures/`** - Charts, graphs, and statistical plots

**Organization Tip:** Name outputs with dates/versions:
```
outputs/
├── reports/
│   └── quarterly_analysis_q1_2026.pdf
└── figures/
    ├── fine_distribution_20260201.png
    └── time_series_violations_20260201.png
```

### `/notebooks` - Interactive Analysis
Jupyter notebooks for exploratory data analysis.

**Purpose:** 
- Quick prototyping and exploration
- Visualization and presentation
- Documented analysis workflows

**Naming Convention:**
```
notebooks/
├── 01_data_exploration.ipynb
├── 02_temporal_patterns.ipynb
├── 03_violation_distribution.ipynb
└── 04_financial_impact.ipynb
```

---

## Data Flow

```
┌─────────────────────────────────────────┐
│   NYC Open Data API                     │
│   (nc67-uf89 dataset)                   │
└──────────────────┬──────────────────────┘
                   │
                   v
         src/data_loader.py
         (Download & fetch)
                   │
                   v
        data/raw/*.csv
    (Raw, unmodified data)
                   │
                   v
        src/data_cleaner.py
        (Validate & clean)
                   │
                   v
        data/processed/*.csv
   (Clean, analysis-ready data)
                   │
         ┌─────────┴──────────┐
         v                    v
        Analysis              Visualization
    (*.ipynb)           (outputs/figures/)
         │                    │
         └─────────┬──────────┘
                   v
           outputs/reports/
         (Final findings)
```

---

## File Naming Conventions

### Data Files
```
Format: {dataset}_{count}_records_{timestamp}.csv
Example: parking_cleaned_764_records_20260201_151917.csv

Parts:
- {dataset}: parking, nyc, etc.
- {count}: number of records in file
- {timestamp}: YYYYMMDD_HHMMSS
```

### Output Files
```
Format: {analysis}_{scope}_{date}.{ext}
Example: violations_by_borough_20260201.html

Parts:
- {analysis}: what analysis was done
- {scope}: temporal or categorical scope
- {date}: YYYYMMDD
- {ext}: file extension (html, png, pdf)
```

### Notebook Files
```
Format: {order:02d}_{topic}.ipynb
Example: 01_data_exploration.ipynb

Parts:
- {order}: 01, 02, 03 for sequencing
- {topic}: descriptive analysis topic
```

---

## Python Module Organization

### Import Patterns

**Correct:**
```python
# Option 1: From venv (recommended)
.\.venv\Scripts\python.exe script.py

# Option 2: With imports
from src.config import ESSENTIAL_FIELDS, RAW_DATA_DIR
from src.data_loader import NYCParkingDataLoader
```

**Incorrect:**
```python
# DON'T do this - uses wrong Python
python script.py  # May use global Python, not venv
```

### Module Dependencies
```
config.py
    ├─ (no dependencies on other src modules)
    └─ (imports: pathlib, os)

data_loader.py
    ├─ Imports: config
    └─ External: requests, pandas

data_cleaner.py
    ├─ Imports: config
    └─ External: pandas, numpy, datetime, warnings

test_loader.py
    ├─ Imports: data_loader
    └─ External: pandas, sys, os

diagnostic.py
    ├─ Imports: config
    └─ External: pathlib, sys, os, requests
```

---

## Version Control (.git)

### What's Tracked
```
TRACKED (in git):
- *.py files (source code)
- *.md files (documentation)
- requirements.txt (dependencies)
- .gitignore (ignore rules)

NOT TRACKED (ignored):
- .venv/ (virtual environment)
- data/raw/* (raw data)
- data/processed/* (output data)
- outputs/* (analysis results)
- notebooks/*.ipynb (notebooks)
- __pycache__/ (Python cache)
- *.pyc (compiled Python)
- .env (environment variables)
```

### .gitignore Examples
```
# Virtual environment
.venv/
venv/

# Python cache
__pycache__/
*.pyc

# Data (large files)
data/raw/*
data/processed/*

# Outputs
outputs/*
notebooks/*.ipynb

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Common Tasks by Directory

### Adding New Data
1. Run: `python src/data_loader.py`
2. File appears in: `data/raw/`
3. Run: `python src/data_cleaner.py`
4. Cleaned file appears in: `data/processed/`

### Creating Analysis
1. Create notebook: `notebooks/05_new_analysis.ipynb`
2. Save figures to: `outputs/figures/`
3. Create report in: `outputs/reports/`

### Adding New Code
1. Create module: `src/new_module.py`
2. Import in other files: `from src.new_module import function`
3. Add dependencies to: `requirements.txt`

### Running Tests
```bash
python src/test_loader.py      # Run test suite
python src/diagnostic.py       # Check system setup
```

---

## Space Usage Guidelines

| Directory | Expected Size | Cleanup Frequency |
|-----------|---------------|-------------------|
| `data/raw/` | 100-500 MB | Monthly (archive old data) |
| `data/processed/` | 50-200 MB | Monthly (keep 3-5 versions) |
| `outputs/` | 10-100 MB | Quarterly (archive old reports) |
| `notebooks/` | 10-50 MB | Ongoing (convert to reports) |
| `.venv/` | 500 MB - 1 GB | Don't delete! Reinstall if needed |

---

## Maintenance

### Regular Tasks
- Keep `data/raw/` organized (date-based subfolders)
- Archive processed data versions
- Update documentation when adding features
- Clear `__pycache__/` if imports fail

### Before Deployment
1. Verify all tests pass: `python src/test_loader.py`
2. Run diagnostics: `python src/diagnostic.py`
3. Check data quality: Review cleaned data samples
4. Update documentation

---

## Analysis Tools

### Weekly Analysis (`generate_weekly_analysis.py`)

**Purpose:** Analyze 7 consecutive days of parking citations with interactive visualizations.

**Features:**
- Interactive date selection with validation (2008-present)
- Automatic data fetching for 7 consecutive days
- Single-pass data cleaning with quality metrics
- 6 matplotlib visualizations embedded in HTML

**Workflow:**
1. User enters start date (YYYY-MM-DD format)
2. Script fetches data for 7 days via NYC Open Data API
3. Data is cleaned and validated (deduplication, type checking)
4. Generates 6 visualizations:
   - Daily citation trend (line chart)
   - Day of week distribution (bar chart)
   - Top 20 violation types (horizontal bars)
   - Hourly distribution (bar chart)
   - Borough breakdown (pie chart)
   - Fine amount distribution (histogram)
5. Creates self-contained HTML report with embedded charts

**Output:**
- File: `outputs/reports/analysis_report_citations_week_YYYY-MM-DD_to_YYYY-MM-DD_TIMESTAMP.html`
- Data: `data/processed/parking_cleaned_citations_week_YYYY-MM-DD_to_YYYY-MM-DD_*.csv`

**Performance:** ~50 seconds for 7 days (~190k-300k records)

---

### Monthly Analysis (`generate_monthly_analysis.py`)

**Purpose:** Analyze a full month (28-31 days) of parking citations with geographic mapping.

**Features:**
- Interactive year/month selection
- Automatic handling of month lengths (28-31 days)
- Progress tracking for multi-day fetching
- 8 matplotlib visualizations including geographic map
- Daily average calculations

**Workflow:**
1. User enters year and month
2. Script calculates all dates in the month
3. Fetches data day-by-day with progress indicators
4. Data is cleaned and validated
5. Generates 8 visualizations:
   - Daily citation trend (line chart showing full month pattern)
   - Day of week distribution (bar chart)
   - Top 20 violation types (horizontal bars)
   - Hourly distribution (bar chart)
   - Borough breakdown (pie chart)
   - Fine amount distribution (histogram)
   - **Top 20 precincts** (bar chart with viridis colors)
   - **Geographic precinct map** (choropleth with YlOrRd heat gradient)
6. Creates self-contained HTML report with embedded charts and map

**Geographic Map Details:**
- Downloads NYC precinct boundaries from ArcGIS REST API
- Merges citation counts with precinct geometries using geopandas
- Color-coded choropleth (yellow=low, orange=medium, red=high citations)
- Precinct numbers labeled at centroids
- Black boundary lines for clarity
- Filters out invalid precincts (precinct 0)

**Output:**
- File: `outputs/reports/analysis_report_citations_month_YYYY-MM_TIMESTAMP.html`
- Data: `data/processed/parking_cleaned_citations_month_YYYY-MM_*.csv`

**Performance:** 2-10 minutes for full month (~800k-1.2M records)

**Data Sources:**
- Citation data: NYC Open Data Socrata API (nc67-uf89)
- Precinct boundaries: NYC ArcGIS REST API
  ```
  https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/
  NYC_Police_Precincts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson
  ```

---

## Future Structure Additions

As the project grows, consider adding:

```
├── tests/
│   ├── test_data_loader.py
│   ├── test_data_cleaner.py
│   └── test_analysis.py
│
├── config/
│   ├── development.env
│   ├── production.env
│   └── test.env
│
├── scripts/
│   ├── fetch_daily_data.py
│   ├── generate_reports.py
│   └── archive_old_data.py
│
└── docs/
    ├── api_reference.md
    ├── methodology.md
    └── findings.md
```

---

## Quick Reference

| What | Where | Command |
|------|-------|---------|
| **Weekly Analysis** | `src/generate_weekly_analysis.py` | `python src/generate_weekly_analysis.py` |
| **Monthly Analysis** | `src/generate_monthly_analysis.py` | `python src/generate_monthly_analysis.py` |
| Download data | `src/data_loader.py` | `python src/data_loader.py` |
| Clean data | `src/data_cleaner.py` | `python src/data_cleaner.py` |
| Check setup | `src/diagnostic.py` | `python src/diagnostic.py` |
| Raw data location | `data/raw/` | See files |
| Cleaned data location | `data/processed/` | See files |
| **HTML Reports** | `outputs/reports/` | **Open in browser** |
| Analysis results | `outputs/` | See subdirs |
| Configuration | `src/config.py` | Edit as needed |
