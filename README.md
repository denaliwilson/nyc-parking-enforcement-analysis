# NYC Parking Citations Analysis

A data analysis project focused on temporal patterns in New York City parking violations using the NYC Open Data API.

## Project Overview

This project analyzes millions of parking citations issued in New York City to uncover temporal and behavioral patterns in parking enforcement. The analysis emphasizes time-based trends, violation types, and borough-level summaries.

## Features

### Automated Data Pipeline
- **API Integration**: Direct connection to NYC Open Data (10M+ records daily)
- **Smart Data Cleaning**: Automatic validation, deduplication, and quality checks
- **Flexible Date Ranges**: Download data by day, week, or month

### Weekly Analysis Tool (`generate_weekly_analysis.py`)
- Interactive date selection with validation
- Analyzes 7 consecutive days (~190k-300k records)
- Execution time: ~50 seconds
- **6 Visualizations**:
  1. Daily citation trend line chart
  2. Day of week distribution
  3. Top 20 violation types
  4. Hourly distribution pattern
  5. Borough breakdown (pie chart)
  6. Fine amount distribution

### Monthly Analysis Tool (`generate_monthly_analysis.py`)
- Full month analysis (28-31 days)
- Processes 800k-1.2M+ records per month
- Execution time: 2-10 minutes depending on volume
- **8 Visualizations** (all weekly charts plus):
  7. Top 20 precincts by citation count (bar chart)
  8. **Geographic precinct map** - Color-coded choropleth showing spatial distribution

### HTML Reports
- Self-contained reports with embedded graphs (base64 PNG)
- Detailed statistics: total citations, daily averages, retention rates
- Data quality metrics and cleaning summaries
- Processing time breakdowns

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

**Programming & Analysis**
- Python 3.13+
- Pandas 3.0+ for data manipulation
- NumPy for numerical operations

**Visualization**
- Matplotlib 3.10+ for charts and graphs
- GeoPandas for choropleth maps
- Seaborn for statistical visualizations

**API Integration**
- Requests for HTTP/REST API calls
- NYC Open Data Socrata API (nc67-uf89)
- NYC ArcGIS REST API for precinct boundaries

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

4. **Set up directories**
```bash
mkdir -p data/{raw,processed} outputs/{figures,reports}
```

5. **(Optional) Get API token**
- Visit [NYC Open Data](https://data.cityofnewyork.us/)
- Create account and generate app token
- Add to `.env` file: `NYC_APP_TOKEN=your_token_here`

### Quick Start

**Run Weekly Analysis** (7-day analysis with visualizations):
```bash
python src/generate_weekly_analysis.py
```
You'll be prompted to enter a start date (YYYY-MM-DD format). The script generates an HTML report with 6 visualizations.

**Run Monthly Analysis** (full month analysis with geographic map):
```bash
python src/generate_monthly_analysis.py
```
You'll be prompted to enter year and month. The script generates an HTML report with 8 visualizations including a color-coded precinct map.

**Analysis Reports** are saved to:
```
outputs/reports/analysis_report_citations_week_*.html
outputs/reports/analysis_report_citations_month_*.html
```

## Project Structure

```
nyc-parking-analysis/
├── data/
│   ├── raw/                    # Raw API responses
│   └── processed/              # Cleaned datasets
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_temporal_analysis.ipynb
│   └── 03_visualization.ipynb
├── src/
│   ├── data_fetcher.py         # API interaction
│   └── data_cleaner.py         # Data preprocessing
├── outputs/
│   ├── figures/                # Charts and graphs
│   └── reports/                # Analysis reports
├── requirements.txt
├── README.md
└── .gitignore
```

## Analysis Objectives

### Phase 1: Exploratory Data Analysis
- [ ] Data quality assessment
- [ ] Temporal pattern analysis (hourly, daily, seasonal)
- [ ] Borough-level comparisons
- [ ] Violation type distribution

### Phase 2: Temporal and Categorical Analysis
- [ ] Time-of-day and day-of-week patterns
- [ ] Seasonal and year-over-year trends
- [ ] Agency and violation category comparisons

### Phase 3: Advanced Analytics
- [ ] Time series forecasting
- [ ] Violation type clustering
- [ ] Interactive dashboard development

## Key Findings

*[To be updated as analysis progresses]*

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