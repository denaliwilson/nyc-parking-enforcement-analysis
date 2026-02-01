# NYC Parking Citations Temporal Analysis

A data analysis project focused on temporal patterns in New York City parking violations using the NYC Open Data API.

## Project Overview

This project analyzes millions of parking citations issued in New York City to uncover temporal and behavioral patterns in parking enforcement. The analysis emphasizes time-based trends, violation types, and borough-level summaries.

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
- Python 3.9+
- Pandas, NumPy for data manipulation
- Jupyter Notebooks for analysis

**Visualization**
- Matplotlib, Seaborn for static plots
- Plotly for interactive dashboards

**API Integration**
- Requests, Sodapy for data retrieval

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

Run the data fetcher:
```bash
python nyc_parking_fetcher.py
```

Or start with the Jupyter notebook:
```bash
jupyter notebook 01_data_exploration.ipynb
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