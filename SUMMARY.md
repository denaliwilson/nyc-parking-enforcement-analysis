# Project Documentation Summary

## Overview

This document provides a complete overview of the NYC Parking Citations Analysis Dashboard project, including architecture, features, deployment status, and maintenance guidelines.

**Last Updated:** February 7, 2026

---

## Project Status

✅ **Production Ready**
- Dashboard fully functional with real-time data loading
- All visualizations working (maps, charts, drill-downs)
- Documentation complete and up-to-date
- Deployment-ready for Streamlit Community Cloud
- No syntax errors or linting issues

---

## Architecture

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Frontend** | Streamlit | 1.28+ | Interactive web dashboard |
| **Data Processing** | Pandas | 2.x | Data manipulation |
| **Geospatial** | GeoPandas | 0.14.1 | Geographic data handling |
| **Visualization** | Plotly | 5.17+ | Interactive charts and maps |
| **API Client** | Requests | 2.31+ | NYC Open Data integration |
| **Deployment** | Streamlit Cloud | Latest | Free hosting platform |

### Key Design Decisions

1. **Pure Python Geospatial Processing**
   - Uses JSON-based GeoJSON loading instead of GDAL
   - Avoids system dependencies for easier deployment
   - Eliminates apt package conflicts in cloud environments

2. **Pandas 2.x Constraint**
   - Streamlit 1.28 requires pandas < 3.0
   - Ensures compatibility with deployment platform

3. **Incremental Data Loading**
   - Loads data day-by-day to handle large date ranges
   - Progress bars for user feedback
   - Prevents memory overflow on free-tier hosting

4. **Multi-Level Caching**
   - `@st.cache_data` for expensive API calls (TTL: 1 hour)
   - `@st.cache_resource` for persistent objects (loader, cleaner)
   - Improves performance and reduces API requests

---

## Features

### Dashboard Capabilities

#### 1. Landing Page
- Hero section with NYC skyline image
- Automatic latest date detection from API
- Quick select buttons (Last Week, Last Month)
- Custom date range picker

#### 2. Citywide Overview
- Total citations across all boroughs
- Total fine amounts
- Average fine calculation
- Peak enforcement hour identification
- Borough comparison (interactive bar charts)

#### 3. Borough Analysis
- Interactive choropleth map (red-green color scale)
- Click-to-select precinct functionality
- Precinct-level citation counts
- Top violations by borough
- Hourly enforcement patterns

#### 4. Precinct Detail View
- Individual precinct statistics
- Top violation types
- Top streets with violations
- Hourly distribution
- Vehicle registration state analysis
- Day of week patterns

### Command Line Tools

#### Weekly Analysis Script
```bash
python src/generate_weekly_analysis.py
```
- Analyzes 7 consecutive days
- Generates 6 visualizations
- Execution time: ~50 seconds
- Output: HTML report

#### Monthly Analysis Script
```bash
python src/generate_monthly_analysis.py
```
- Analyzes full month (28-31 days)
- Generates 8+ visualizations
- Includes choropleth map
- Execution time: 2-10 minutes
- Output: HTML report

---

## Code Structure

### Dashboard Application (`dashboard.py`)

**Lines:** 1,006 total

**Key Sections:**
- Lines 1-30: Imports and module initialization
- Lines 40-60: Latest date detection from API
- Lines 65-100: GeoJSON loading with pure Python approach
- Lines 140-280: Custom CSS and styling
- Lines 290-410: Landing page and data loading interface
- Lines 420-600: Citywide overview and metrics
- Lines 610-780: Borough-level analysis and mapping
- Lines 790-1006: Precinct detail view

**Critical Functions:**
```python
get_latest_available_date()  # Query API for most recent data
load_geojson()               # Load precinct boundaries (no GDAL)
create_choropleth_map()      # Interactive Plotly maps
handle_drill_down()          # Borough → Precinct navigation
```

### Data Pipeline (`src/`)

**`config.py`** (100 lines)
- API endpoints and authentication
- Data directory paths
- Essential field definitions
- Default parameters

**`data_loader.py`** (550 lines)
- NYCParkingDataLoader class
- Pagination and rate limiting
- Error handling and retries
- Multiple loading methods (day, week, month, range)

**`data_cleaner.py`** (900 lines)
- ParkingDataCleaner class
- Type conversions (dates, numerics)
- Duplicate removal
- Data quality reporting
- Validation rules

---

## Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| README.md | Project overview, quick start | ✅ Updated |
| SETUP.md | Installation and deployment | ✅ Updated |
| PROJECT_STRUCTURE.md | Directory layout | ✅ Updated |
| DATA_DICTIONARY.md | Field definitions | ✅ Current |
| DATA_SOURCES.md | API documentation | ✅ Current |
| DEPLOYMENT.md | Deployment guide | ✅ New |
| SUMMARY.md | This file | ✅ New |

---

## Deployment Configuration

### requirements.txt
```txt
pandas>=2.0.0,<3.0.0     # Streamlit compatible version
numpy>=1.24.0,<2.0.0
requests>=2.31.0
geopandas==0.14.1
shapely>=2.0.0,<3.0.0
pyproj>=3.6.0,<4.0.0
plotly>=5.17.0
streamlit>=1.28.0
python-dotenv>=1.0.0
```

### packages.txt
```txt
(completely empty - no system dependencies)
```

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F8F9FA"
secondaryBackgroundColor = "#E9ECEF"
textColor = "#2C3E50"
font = "sans serif"
```

---

## Data Flow

```
NYC Open Data API
        ↓
 [data_loader.py]
        ↓
   Raw CSV Data
   (data/raw/)
        ↓
 [data_cleaner.py]
        ↓
  Cleaned CSV Data
  (data/processed/)
        ↓
  ┌──────────────────┐
  │  dashboard.py    │ ← User interacts with web UI
  │  (Streamlit)     │
  └──────────────────┘
        ↓
  Visualizations:
  - Choropleth maps
  - Bar charts
  - Line graphs
  - Statistics
```

---

## API Integration

### NYC Open Data API

**Endpoint:** `https://data.cityofnewyork.us/resource/nc67-uf89.json`

**Query Parameters:**
- `$select`: Field selection
- `$where`: Date filtering
- `$limit`: Records per request (max 50,000)
- `$offset`: Pagination
- `$order`: Sorting

**Rate Limits:**
- No token: 1,000 requests/hour
- With token: 5,000 requests/hour

**Sample Query:**
```python
params = {
    '$where': "issue_date='2026-01-15'",
    '$limit': 50000,
    '$offset': 0
}
response = requests.get(API_URL, params=params)
```

### NYC ArcGIS API (Precinct Boundaries)

**Endpoint:** `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Police_Precincts/FeatureServer/0/query`

**Purpose:** Download NYPD precinct polygons for choropleth maps

**Caching:** Downloaded once and cached in `data/geospatial/nyc_precincts.geojson`

---

## Performance Considerations

### Memory Management
- Dashboard loads data incrementally (day-by-day)
- Streamlit Cloud free tier: 1 GB RAM limit
- Typical dataset: 20-50 MB per day (25,000-33,000 records)
- Maximum recommended range: 30 days (~30 GB API data → ~1 GB cleaned)

### Caching Strategy
```python
# API call caching (1 hour TTL)
@st.cache_data(ttl=3600)
def get_latest_available_date():
    ...

# Resource caching (persistent)
@st.cache_resource
def get_loader():
    return NYCParkingDataLoader()
```

### Optimization Tips
1. Limit date ranges to reasonable periods (1-30 days)
2. Use quick select buttons for common ranges
3. Cache geospatial data (auto-handled)
4. Avoid re-fetching same date ranges

---

## Maintenance Guidelines

### Regular Updates

**Monthly:**
- Review API status and endpoints
- Check for Streamlit/Pandas version updates
- Monitor app performance metrics
- Review error logs

**Quarterly:**
- Update dependencies (if needed)
- Review and update documentation
- Check for NYC Open Data schema changes
- Performance optimization review

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade streamlit

# Regenerate requirements
pip freeze > requirements.txt

# Test locally before deploying
streamlit run dashboard.py
```

### Adding New Features

1. **Develop locally**
   ```bash
   git checkout -b feature/new-visualization
   # Make changes
   streamlit run dashboard.py  # Test
   ```

2. **Commit and push**
   ```bash
   git add .
   git commit -m "Add new visualization"
   git push origin feature/new-visualization
   ```

3. **Merge to main**
   - Create pull request
   - Review changes
   - Merge to main branch

4. **Auto-deploy**
   - Streamlit Cloud automatically deploys main branch

---

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Dependency conflict | Deployment fails | Check pandas version < 3.0 |
| Map not rendering | Blank map | Verify GeoJSON download |
| Slow data loading | Long wait times | Reduce date range |
| Memory error | App crashes | Use smaller datasets |
| API rate limit | 429 errors | Add delays between requests |

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View Streamlit logs:
```bash
streamlit run dashboard.py --logger.level=debug
```

---

## Testing

### Local Testing

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run dashboard
streamlit run dashboard.py

# Test with different date ranges
# Test borough drill-down
# Test precinct selection
# Verify all visualizations load
```

### Pre-Deployment Checklist

- [ ] Dashboard loads without errors
- [ ] All visualizations render correctly
- [ ] Date selection works (quick select + custom)
- [ ] Maps are interactive (click to drill down)
- [ ] Data loads incrementally with progress bars
- [ ] No console errors in browser dev tools
- [ ] Responsive on mobile (basic check)
- [ ] requirements.txt up to date
- [ ] packages.txt empty
- [ ] Documentation updated

---

## Future Enhancements

### Planned Features
- [ ] Export data to CSV from dashboard
- [ ] Bookmark/share specific views (URL parameters)
- [ ] Advanced filtering (violation type, fine amount)
- [ ] Time series forecasting
- [ ] Comparison mode (compare two time periods)
- [ ] Email reports (scheduled analysis)

### Technical Improvements
- [ ] Add unit tests for data pipeline
- [ ] Implement CI/CD with GitHub Actions
- [ ] Add Sentry error tracking
- [ ] Performance profiling and optimization
- [ ] A/B testing framework

---

## Resources

### Documentation Links
- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [GeoPandas Docs](https://geopandas.org/)
- [NYC Open Data Portal](https://opendata.cityofnewyork.us/)

### Repository Links
- GitHub: (add your repo URL)
- Live Dashboard: (add Streamlit Cloud URL)

### Contact
- Project Maintainer: (add your name/email)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

## License

MIT License - See LICENSE file for details

---

**Document Version:** 1.0  
**Last Review:** February 7, 2026  
**Next Review:** May 7, 2026
