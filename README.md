# NYC Parking Citations GIS Analysis

A comprehensive geospatial and data analysis project exploring patterns in New York City parking violations using the NYC Open Data API.

## Project Overview

This project analyzes millions of parking citations issued in New York City to uncover spatial, temporal, and behavioral patterns in parking enforcement. By leveraging GIS techniques and data science methodologies, this analysis provides insights into urban parking behavior and enforcement strategies.

## Dataset

- **Source**: [NYC Open Data Portal](https://data.cityofnewyork.us/)
- **Dataset**: Parking Violations Issued - Fiscal Year 2025
- **Records**: 10+ million citations annually
- **Update Frequency**: Daily
- **API Endpoint**: `https://data.cityofnewyork.us/resource/nc67-uf89.json`

### Key Variables
- Location data (street names, precincts, boroughs)
- Violation types and codes
- Temporal information (date, time)
- Vehicle characteristics
- Fine amounts

## Technologies Used

**Programming & Analysis**
- Python 3.9+
- Pandas, NumPy for data manipulation
- Jupyter Notebooks for analysis

**Geospatial Analysis**
- GeoPandas for spatial operations
- Shapely for geometric operations
- Folium/Plotly for interactive maps

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
mkdir -p data/{raw,processed,geospatial} outputs/{maps,reports}
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
│   ├── processed/              # Cleaned datasets
│   └── geospatial/             # Shapefiles, GeoJSON
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_spatial_analysis.ipynb
│   └── 03_visualization.ipynb
├── src/
│   ├── data_fetcher.py         # API interaction
│   ├── data_cleaner.py         # Data preprocessing
│   └── gis_utils.py            # GIS operations
├── outputs/
│   ├── maps/                   # Generated maps
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

### Phase 2: Geospatial Analysis
- [ ] Citation hotspot mapping (kernel density estimation)
- [ ] Spatial clustering (DBSCAN)
- [ ] Precinct-level analysis
- [ ] Street network integration

### Phase 3: Advanced Analytics
- [ ] Predictive modeling for high-violation zones
- [ ] Time series forecasting
- [ ] Socioeconomic correlation analysis
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