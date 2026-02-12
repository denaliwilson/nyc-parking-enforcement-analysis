# NYC Parking Citations Analysis Dashboard

An interactive web dashboard for analyzing New York City parking citations with real-time data from the NYC Open Data API. Explore temporal patterns, geographic distributions, and enforcement trends across all five boroughs.

🌐 **[Live Dashboard](https://your-app-url.streamlit.app)** | 📊 **[Data Source](https://data.cityofnewyork.us/resource/nc67-uf89)**

## Project Overview

This project provides an interactive Streamlit dashboard to analyze millions of parking citations issued in New York City. Users can select custom date ranges, explore borough-level patterns, drill down to individual precincts, and visualize enforcement trends through interactive maps and charts.

## Features

### 🎯 Interactive Dashboard
- **Real-time Data Loading**: Fetch latest citations directly from NYC Open Data API
- **Custom Date Ranges**: Select any date range or use quick options (last week/month)
- **Latest Data Detection**: Automatically identifies most recent available data
- **Responsive Design**: Modern UI with custom theming and gradient accents

### 📊 Multi-Level Analysis
- **Citywide Overview**: Total citations, fines, and key metrics at a glance
- **Borough Comparison**: Compare enforcement patterns across all five boroughs
- **Precinct Drill-Down**: Click any precinct on the interactive map for detailed analysis
- **Time-Based Insights**: Daily trends, hourly patterns, and day-of-week distributions

### 🗺️ Geographic Visualization
- **Interactive Choropleth Maps**: Color-coded precinct maps showing citation density
- **Click-to-Explore**: Click any precinct to view detailed statistics
- **Red-Green Color Scale**: Intuitive visualization from low (green) to high (red) enforcement
- **Borough-Level Zoom**: Automatic map centering for focused analysis

### 📈 Rich Visualizations
- Daily citation trend lines
- Top violation types (bar charts)
- Hourly enforcement patterns
- Day of week distributions
- Fine amount analysis
- Vehicle registration state breakdowns
- Top streets by citations

### 🔧 Analysis Tools (Command Line)
- **Manhattan Congestion Report** (`manhattan_congestion_report.py`): Comprehensive congestion pricing impact analysis
  - Before/after comparison (1 month each side of Jan 5, 2025 implementation)
  - Zone analysis (In Zone, Border, Out of Zone)
  - Out-of-state plate behavior analysis
  - Precinct heatmaps and violation analysis
  - Duration: ~15-20 minutes
- **Weekly Analysis** (`generate_weekly_analysis.py`): Analyze 7-day periods (~50 seconds)
- **Monthly Analysis** (`generate_monthly_analysis.py`): Full month reports with 8+ visualizations
- **HTML Reports**: Self-contained reports with embedded charts and statistics

## Dataset

- **Source**: [NYC Open Data Portal](https://data.cityofnewyork.us/)
- **Dataset**: Parking Violations Issued - Fiscal Year 2025
- **Records**: 10+ million citations annually
- **Update Frequency**: Daily
- **API Endpoint**: `https://data.cityofnewyork.us/resource/nc67-uf89.json`

### Key Variables
- Temporal information (date, time)
- Violation types and descriptions
- Vehicle characteristics
- Fine amounts and reductions
- Borough/county (aggregate only)

## Technologies Used

**Frontend & Dashboard**
- Streamlit 1.28+ for interactive web application
- Plotly 5.17+ for interactive visualizations
- Custom CSS for enhanced styling and theming

**Data Processing**
- Python 3.9+
- Pandas 2.x for data manipulation (Streamlit compatible)
- NumPy 1.24+ for numerical operations

**Geospatial Analysis**
- GeoPandas 0.14.1 for geographic data handling
- Shapely 2.x for geometry operations
- PyProj 3.6+ for coordinate transformations

**API Integration**
- Requests library for NYC Open Data API
- NYC Open Data Socrata API (nc67-uf89)
- NYC ArcGIS REST API for precinct boundaries

**Deployment**
- Streamlit Community Cloud (free hosting)
- Git-based continuous deployment
- No system dependencies required

## Getting Started

### Prerequisites
```bash
# Python 3.9 or higher
python --version

# pip for package management
pip --version
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nyc-parking-analysis.git
cd nyc-parking-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Quick Start

#### Option 1: Run the Dashboard (Recommended)

Launch the interactive web dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Features:**
- Select custom date ranges or use quick options (last week/month)
- Automatically fetches and cleans data from NYC Open Data
- Interactive maps with click-to-explore precinct details
- Real-time visualizations and statistics

#### Option 2: Generate Analysis Reports

**Manhattan Congestion Pricing Impact Report** (comprehensive, ~15-20 minutes):
```bash
python src/manhattan_congestion_report.py
```
- One-month before/after congestion pricing comparison
- Zone analysis (In Zone, Border, Out of Zone)
- Out-of-state plate behavior analysis
- Precinct heatmaps and hourly patterns
- Full HTML report with embedded visualizations

**Weekly Analysis** (7-day period, ~50 seconds):
```bash
python src/generate_weekly_analysis.py
```

**Monthly Analysis** (full month with geographic map, 2-10 minutes):
```bash
python src/generate_monthly_analysis.py
```

Reports are saved to `outputs/reports/` as self-contained HTML files.

### Deployment

Deploy your own dashboard to Streamlit Community Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy with one click

See [SETUP.md](SETUP.md) for detailed deployment instructions.

## Project Structure

```
nyc-parking-enforcement-analysis/
├── dashboard.py                # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies (Streamlit compatible)
├── packages.txt                # System packages (empty - pure Python)
├── .streamlit/
│   └── config.toml            # Dashboard theme configuration
├── data/
│   ├── raw/                   # Raw API responses (auto-generated)
│   ├── processed/             # Cleaned datasets (auto-generated)
│   └── geospatial/            # NYC precinct boundaries (GeoJSON)
├── src/
│   ├── config.py              # Configuration and constants
│   ├── data_loader.py         # NYC Open Data API integration
│   ├── data_cleaner.py        # Data cleaning and validation
│   ├── manhattan_congestion_report.py # CLI: Congestion impact analysis
│   ├── generate_weekly_analysis.py    # CLI: 7-day reports
│   ├── generate_monthly_analysis.py   # CLI: monthly reports
│   └── diagnostic.py          # System diagnostics
├── outputs/
│   ├── figures/               # Generated charts (for reports)
│   └── reports/               # HTML analysis reports
├── notebooks/                 # Jupyter notebooks for exploration
└── Documentation/
    ├── README.md              # This file
    ├── SETUP.md               # Installation and deployment guide
    ├── DATA_DICTIONARY.md     # Field definitions
    ├── DATA_SOURCES.md        # API documentation
    └── PROJECT_STRUCTURE.md   # Detailed structure
```

## Usage Examples

### Dashboard Navigation

1. **Landing Page**: Select date range using quick options or custom calendar
2. **Citywide View**: Overview metrics and borough comparison charts
3. **Borough View**: Click any borough to see precinct-level map
4. **Precinct View**: Click any precinct on map for detailed statistics

### Analysis Workflow

```python
# Example: Programmatic data loading
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner

# Initialize
loader = NYCParkingDataLoader()
cleaner = ParkingDataCleaner()

# Load and clean data
raw_df = loader.load_by_day('2026-01-15')
clean_df = cleaner.clean_dataframe(raw_df)

print(f"Loaded {len(clean_df):,} citations")
```

### Data Output

All processed data is automatically saved to `data/processed/` with timestamps:
- `parking_cleaned_citations_week_YYYY-MM-DD_to_YYYY-MM-DD_*.csv`
- `parking_cleaned_citations_month_YYYY-MM_*.csv`

## Key Features & Insights

- **Real-time Data**: Always access the latest NYC parking citation data
- **Multi-level Analysis**: City → Borough → Precinct drill-down
- **Geographic Patterns**: Identify enforcement hotspots via interactive maps
- **Temporal Trends**: Understand daily, hourly, and weekly patterns
- **Violation Analysis**: Compare fine amounts and violation types
- **Deployment Ready**: One-click deploy to Streamlit Cloud

## Contributing

This is a portfolio project, but suggestions and feedback are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NYC Open Data Portal for providing public access to parking violation data
- [Any other resources or inspirations]

## Contact

**Your Name**
- Portfolio: https://github.com/denaliwilson
- LinkedIn: https://www.linkedin.com/in/denali-wilson/
- Email: denaliwilson@gmail.com

---

*Last Updated: January 2026*