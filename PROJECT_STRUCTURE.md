# Project Structure

## Directory Overview

```
nyc-parking-enforcement-analysis/
├── .git/                           # Git version control
├── .gitignore                      # Files to ignore in git
├── .venv/                          # Virtual environment (auto-created)
│   ├── Scripts/                    # Executables (python.exe, pip.exe)
│   └── Lib/                        # Python packages
│
├── data/                           # Data storage
│   ├── raw/                        # Raw downloaded data (not modified)
│   │   ├── parking_raw_*.csv       # Raw API downloads
│   │   └── *.csv                   # Additional raw data files
│   │
│   ├── processed/                  # Cleaned, analysis-ready data
│   │   ├── parking_cleaned_citations_week_*.csv
│   │   │   # 7-day combined datasets from weekly analysis
│   │   ├── parking_cleaned_citations_month_*.csv
│   │   │   # 28-31 day combined datasets from monthly analysis
│   │   └── parking_cleaned_*_records_*.csv
│   │       # Individual cleaned datasets from data_cleaner.py
│   │
│   ├── archive/                    # Archived processed files
│   │   └── Older versions of processed datasets
│   │
│   ├── geospatial/                 # Geographic data
│   │   └── nyc_precincts.geojson  # NYC precinct boundaries (optional)
│   │
│   └── dof_parking_camera_violations.schema.json
│       # API schema documentation from NYC Open Data
│
├── src/                            # Source code
│   ├── __pycache__/                # Python cache (auto-generated, not tracked)
│   │
│   ├── config.py                   # Configuration settings
│   │   └── Contains: paths, API settings, field definitions, defaults
│   │
│   ├── data_loader.py              # Download and load data from API
│   │   └── Classes: NYCParkingDataLoader
│   │   └── Functions: load_by_day(), save_data(), display_summary()
│   │
│   ├── data_cleaner.py             # Clean and process data
│   │   └── Classes: ParkingDataCleaner
│   │   └── Methods: check_data_quality(), clean_dates(), clean_numeric_fields()
│   │
│   ├── generate_weekly_analysis.py # Weekly analysis with 6 visualizations
│   │   └── Interactive 7-day analysis tool
│   │   └── Functions: get_week_dates(), fetch_week_data(), generate_graphs()
│   │   └── Output: HTML reports with embedded charts
│   │   └── Run: python src/generate_weekly_analysis.py
│   │
│   ├── generate_monthly_analysis.py # Monthly analysis with 8 visualizations
│   │   └── Interactive full-month analysis tool
│   │   └── Functions: get_month_dates(), fetch_month_data(), generate_graphs()
│   │   └── Includes: Precinct bar chart + geographic choropleth map
│   │   └── Output: HTML reports with embedded charts and maps
│   │   └── Run: python src/generate_monthly_analysis.py
│   │
│   ├── preliminary_analysis.py     # Initial exploratory analysis
│   │   └── Basic statistical analysis and data profiling
│   │
│   ├── diagnostic.py               # System diagnostics
│   │   └── Checks: Python version, dependencies, API access
│   │   └── Run: python src/diagnostic.py
│   │
│   └── tests/                      # Test suite
│       └── Unit tests for data loading and cleaning
│
├── outputs/                        # Analysis outputs and results
│   ├── reports/                    # Analysis reports and summaries
│   │   ├── analysis_report_citations_week_*.html
│   │   │   └── Weekly analysis reports with 6 visualizations
│   │   └── analysis_report_citations_month_*.html
│   │       └── Monthly analysis reports with 8 visualizations + map
│   │
│   └── figures/                    # Charts, graphs, and visualizations
│       └── [Graphs embedded in HTML reports as base64 PNG]
│
├── notebooks/                      # Jupyter notebooks for exploration
│   └── [future notebook files]
│   └── Example: analysis.ipynb, visualization.ipynb
│
├── Documentation Files
│   ├── README.md                   # Project overview and quick start
│   ├── DATA_DICTIONARY.md          # Field definitions and data types
│   ├── SETUP.md                    # Installation and setup instructions
│   ├── DATA_SOURCES.md             # Data source documentation
│   ├── PROJECT_STRUCTURE.md        # This file
│   ├── CHANGELOG.md                # Version history and changes
│   └── CONTRIBUTING.md             # Contributing guidelines (optional)
│
├── Configuration Files
│   ├── requirements.txt             # Python package dependencies
│   ├── .gitignore                  # Git ignore patterns
│   └── .env                        # Environment variables (if needed)
│
└── License & Metadata
    └── LICENSE                     # License file
```

---

## Directory Descriptions

### `/data` - Data Management
Stores all project data organized by processing stage.

**Subdirectories:**
- **`raw/`** - Original, unmodified data from external sources
  - Never modify files in this directory
  - Archive original data for reproducibility
  - Size: ~100-150 KB per 1,000 records

- **`processed/`** - Clean data ready for analysis
  - Output from data_cleaner.py
  - All quality checks and transformations applied
  - Deduplicated and validated
  - Use this for all analysis work

### `/src` - Source Code
Python modules and scripts for the project.

**Key Files:**

| File | Purpose | Type | Run Command |
|------|---------|------|-------------|
| config.py | Centralized configuration | Module | `python -c "from src.config import *"` |
| data_loader.py | API data retrieval | Module + Script | `python src/data_loader.py` |
| data_cleaner.py | Data processing | Module + Script | `python src/data_cleaner.py` |
| generate_weekly_analysis.py | 7-day analysis with 6 charts | Script | `python src/generate_weekly_analysis.py` |
| generate_monthly_analysis.py | Monthly analysis with 8 charts + map | Script | `python src/generate_monthly_analysis.py` |
| preliminary_analysis.py | Exploratory data analysis | Script | `python src/preliminary_analysis.py` |
| diagnostic.py | System checks | Script | `python src/diagnostic.py` |

**Usage Pattern:**
1. Modules can be imported: `from src.config import ESSENTIAL_FIELDS`
2. Scripts can be executed standalone: `python src/data_loader.py`
3. All scripts respect configuration in config.py
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
