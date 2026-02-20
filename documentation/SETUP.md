# Setup and Installation Guide

## Quick Start

### Prerequisites
- Python 3.9 or higher (Python 3.11+ recommended)
- Git (for version control)
- pip (Python package manager)
- Internet connection (for NYC Open Data API access)

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
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If you encounter errors on Windows, ensure your virtual environment is activated:
```bash
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt
```

---

## Running the Dashboard

### Launch the Interactive Dashboard

The Streamlit dashboard is the primary interface for exploring NYC parking citation data:

```bash
# Ensure virtual environment is activated
streamlit run dashboard.py
```

The dashboard will automatically:
1. Open in your default browser at `http://localhost:8501`
2. Detect the latest available data from NYC Open Data
3. Provide interactive date selection and data loading
4. Generate real-time visualizations and maps

**Dashboard Features:**
- ✅ Select custom date ranges or quick options (last week/month)
- ✅ Real-time data fetching and cleaning
- ✅ Interactive choropleth maps with click-to-explore
- ✅ Multi-level analysis (City → Borough → Precinct)
- ✅ Automatic caching for performance

### Stopping the Dashboard

Press `Ctrl+C` in the terminal to stop the Streamlit server.

---

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
## Command Line Analysis Tools (Optional)

For generating standalone HTML reports without the dashboard:

#### Weekly Analysis (7 days, ~50 seconds)
```bash
# Activate virtual environment first
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
# Activate virtual environment first
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

## Deployment to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Repository pushed to GitHub
3. Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Deployment Steps

1. **Prepare Your Repository**
   - Ensure `requirements.txt` is up to date
   - Verify `packages.txt` is empty (no system dependencies needed)
   - Make sure `.streamlit/config.toml` exists for theme settings
   - Push all changes to GitHub

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `dashboard.py`
   - Click "Deploy"

3. **Monitor Deployment**
   - Watch the deployment logs
   - Initial deployment takes 2-5 minutes
   - Your app will be available at `https://your-app-name.streamlit.app`

4. **Troubleshooting**
   - **If deployment fails**: Check the logs for errors
   - **Dependency issues**: Ensure `requirements.txt` uses compatible versions
   - **Environment reset**: Delete and recreate the app for a fresh environment
   - **Data loading errors**: Verify NYC Open Data API is accessible

### Automatic Redeployment

Once deployed, Streamlit Cloud automatically redeploys when you push to GitHub:
```bash\ngit add .\ngit commit -m \"Update dashboard\"\ngit push\n```\n\nThe app will automatically update within 1-2 minutes.\n\n---

## Configuration

### Dashboard Theme Customization

Edit `.streamlit/config.toml` to customize colors and appearance:

```toml
[theme]
primaryColor = \"#FF6B6B\"              # Accent color for buttons and highlights
backgroundColor = \"#F8F9FA\"           # Main background color
secondaryBackgroundColor = \"#E9ECEF\" # Sidebar and secondary elements
textColor = \"#2C3E50\"                 # Primary text color
font = \"sans serif\"                  # Font family
```

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
