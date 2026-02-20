# Change Log

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-02-19

### Added - Dashboard Outlier Insights
- Added **Outlier Highlights** section to dashboard summary area
  - Highest fine in loaded test data (with supporting violation/summons details when available)
  - Most-cited license identifier (prefers `plate_masked`, falls back to `plate`)
  - Rarest citation types table (fewest records, top 5)

### Changed - Map Legibility
- Updated choropleth map color encoding to use logarithmic scaling (`log1p(citations)`) for more even distribution
- Added human-readable log legend ticks (displaying actual citation counts)
- Added in-dashboard notes clarifying that hover values show real counts while colors are log-scaled

### Documentation
- Updated README feature descriptions to reflect new outlier panel and log-scaled map legend behavior

## [1.1.0] - 2026-02-11

### Added - Manhattan Congestion Analysis
- **manhattan_congestion_report.py**: Comprehensive Manhattan congestion pricing impact report
  - Before/After analysis (Dec 5, 2024 - Jan 4, 2025 vs Jan 5 - Feb 4, 2025)
  - Zone-specific analysis: In Zone, Out of Zone
  - **Out-of-state plate behavior analysis** comparing non-NY drivers in-zone vs out-of-zone
  - Top 5 out-of-state contributors by zone with before/after comparison
  - Precinct-level heatmaps showing top 20 precincts
  - Violation type analysis with change percentages
  - Hourly citation pattern comparisons
  - Self-contained HTML reports with embedded visualizations
  - Day-by-day data loading for API reliability

### Changed - Data Loading
- Enhanced Manhattan county filtering with multiple variations:
  - `NEW YORK`, `NY`, `MANHATTAN`, `NEW YORK COUNTY`, `MAN`, `MN`
  - Ensures comprehensive capture of all Manhattan citations
- Implemented day-by-day loading strategy to prevent API timeouts
- Added progress tracking for multi-day data loads

### Changed - Analysis Capabilities
- Extended congestion analysis to include registration state analysis
- Added detailed zone classification (11 in-zone, 11 out-of-zone precincts, including precincts 19 and 20)
- Enhanced visualization with dual-chart comparisons for out-of-state analysis

### Enhanced - Documentation
- Updated CONGESTION_ANALYSIS.md with new report generator details
- Updated PROJECT_STRUCTURE.md to include manhattan_congestion_report.py
- Added comprehensive data coverage documentation
- Documented analysis questions answered by new report

## [1.0.0] - 2026-02-07

### Added - Dashboard & Visualization
- Interactive Streamlit dashboard with landing page
- Hero section with NYC skyline image and overlay design
- Real-time data loading from NYC Open Data API
- Interactive choropleth maps with red-green color scale (RdYlGn_r)
- Multi-level analysis: Citywide → Borough → Precinct drill-down
- Click-to-explore functionality on precinct maps
- Quick select buttons for "Last Week" and "Last Month"
- Custom date range picker with calendar interface
- Latest available date auto-detection from API
- Progress indicators for data loading
- Automatic data cleaning pipeline integration
- Session state management for navigation

### Added - Styling & UX
- Custom Streamlit theme (`.streamlit/config.toml`)
  - Primary color: #FF6B6B
  - Background: #F8F9FA
  - Secondary background: #E9ECEF
- Custom CSS for typography and visual polish
- Gradient dividers between sections
- Hover effects on buttons
- Card-style metric displays
- Responsive layout with columns
- Colored section headers
- Input panel overlay design

### Added - Documentation
- **DEPLOYMENT.md**: Complete deployment guide for Streamlit Cloud
- **SUMMARY.md**: Comprehensive project overview and architecture
- **CHANGELOG.md**: This file
- Enhanced README.md with dashboard-first approach
- Updated SETUP.md with dashboard instructions
- Updated PROJECT_STRUCTURE.md with current architecture

### Changed - Dependencies
- Constrained pandas to 2.x (`pandas>=2.0.0,<3.0.0`) for Streamlit compatibility
- Removed matplotlib, seaborn, scipy, tqdm (unused in dashboard)
- Added plotly>=5.17.0 for interactive visualizations
- Added streamlit>=1.28.0
- Removed system dependencies from packages.txt (pure Python deployment)
- Updated requirements.txt for Streamlit Cloud compatibility

### Changed - Code Structure
- Replaced emoji characters with text/Unicode arrows throughout dashboard
- Modified GeoJSON loading to use pure Python (json.load) instead of geopandas.read_file()
- Eliminated GDAL dependency for cloud deployment
- Fixed session state management for quick select buttons
- Changed chart colors from gradient scales to solid colors for visibility
  - Blues → #3498db (solid blue)
  - Greens → #27ae60 (solid green)
- Changed map color scheme from 'Reds' to 'RdYlGn_r' (red-green scale)
- Simplified date selection UI (removed radio buttons)
- Improved indentation and code style consistency

### Fixed - Bugs
- Quick select buttons (Last Week, Last Month) now load full date range
- Session state properly managed to avoid premature deletion
- Light colored bars in charts now visible with solid colors
- Landing page white box removed (fixed column layout)
- Indentation errors in dashboard.py corrected
- Empty packages.txt (was trying to install comment words as packages)

### Fixed - Deployment
- Removed all system package dependencies (libgdal-dev, libproj-dev, etc.)
- Empty packages.txt to avoid apt-get errors
- Pure Python geospatial processing for cloud compatibility
- Eliminated ODBC dependency cascade from broken libgdal32

### Documentation Improvements
- Enhanced README.md with dashboard features and deployment info
- Updated SETUP.md with Streamlit Cloud deployment steps
- Comprehensive PROJECT_STRUCTURE.md with file-by-file breakdown
- Added inline docstrings to main functions
- Module-level documentation with author and version info

## [0.9.0] - 2026-02-01 (Pre-Dashboard)

### Added
- Weekly analysis script (`generate_weekly_analysis.py`)
- Monthly analysis script (`generate_monthly_analysis.py`)
- HTML report generation with embedded charts
- Choropleth map generation for monthly reports
- Data loader with NYC Open Data API integration
- Data cleaner with validation and quality checks
- Configuration module with centralized settings
- Diagnostic script for system verification
- Data dictionary documentation
- Project structure documentation

### Changed
- Data pipeline to support incremental loading
- CSV output with timestamps

## [0.5.0] - 2026-01-15 (Initial Development)

### Added
- Initial project setup
- Basic data loading from NYC Open Data
- Preliminary analysis notebooks
- Requirements.txt
- README.md
- .gitignore

---

## Version Numbering

- **Major version (1.x.x)**: Breaking changes, major feature additions
- **Minor version (x.1.x)**: New features, non-breaking changes
- **Patch version (x.x.1)**: Bug fixes, documentation updates

## Links

- [Repository](https://github.com/yourusername/nyc-parking-enforcement-analysis)
- [Live Dashboard](https://your-app.streamlit.app)
- [Issue Tracker](https://github.com/yourusername/nyc-parking-enforcement-analysis/issues)

## Upcoming (Roadmap)

### Version 1.1.0 (Planned)
- [ ] Export data to CSV from dashboard
- [ ] Bookmark/share URLs for specific views
- [ ] Advanced filtering options
- [ ] Comparison mode (two time periods)
- [ ] Email report scheduling

### Version 1.2.0 (Planned)
- [ ] Time series forecasting
- [ ] Anomaly detection
- [ ] Heatmap animations
- [ ] Mobile app optimization
- [ ] API for external access

### Version 2.0.0 (Future)
- [ ] User authentication
- [ ] Save custom views/bookmarks
- [ ] Automated alerts
- [ ] Machine learning insights
- [ ] Multi-city expansion
