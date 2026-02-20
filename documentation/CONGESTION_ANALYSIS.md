# NYC Congestion Pricing Analysis

## Analysis Tools

### 1. Interactive Dashboard (Streamlit)

The congestion pricing analysis is a **standalone dashboard** separate from the main citations dashboard.

#### Direct Access (Recommended)
```bash
streamlit run congestion_analysis.py
```

This runs independently on its own port (typically http://localhost:8502 if main dashboard is already running).

#### Running Both Dashboards Simultaneously
You can run both dashboards at the same time in separate terminal windows:

**Terminal 1 - Main Dashboard:**
```bash
streamlit run dashboard.py
```

**Terminal 2 - Congestion Analysis:**
```bash
streamlit run congestion_analysis.py --server.port 8502
```

Then access:
- Main Dashboard: http://localhost:8501
- Congestion Analysis: http://localhost:8502

### 2. Comprehensive HTML Report (Command Line)

**NEW**: Generate detailed Manhattan-focused congestion pricing impact reports with enhanced analysis.

```bash
python src/manhattan_congestion_report.py
```

**Features:**
- **One-month before/after comparison** (Dec 5, 2024 - Jan 4, 2025 vs Jan 5 - Feb 4, 2025)
- **Manhattan-focused analysis** with expanded county detection (NY, NEW YORK, MANHATTAN, etc.)
- **Zone-specific breakdown**: In Zone (below 60th St), Out of Zone (includes precincts 19 and 20)
- **Out-of-state plate behavior analysis**: Compare how non-NY drivers behaved in-zone vs out-of-zone
- **Precinct-level heatmaps** with top 20 precincts
- **Violation type analysis** with before/after comparisons
- **Time pattern analysis** with hourly trends
- **Interactive HTML output** with embedded visualizations
- **Day-by-day data loading** for reliability

**Output Location:** `outputs/reports/manhattan_congestion_report_YYYYMMDD_HHMMSS.html`

**Analysis Duration:** ~15-20 minutes (loads 62 days of Manhattan data)

## Dashboard Features

### 📊 Quick Comparison (Available Now)
- **January 2024 vs January 2026** side-by-side analysis
- **Overall metrics**: Citation volume and revenue changes
- **Zone analysis**: Congestion zone vs outside zone comparison
- **Top violations**: Before/after comparison
- **Time patterns**: Changes by time of day
- **Agency analysis**: Enforcement patterns by issuing agency

### 🚧 Coming Soon
- **Time Series Trend**: Monthly trends from 2024-2026 with implementation date marked
- **Quarterly Comparison**: Q1 2024 vs Q1 2025 analysis
- **Custom Date Range**: Select your own before/after periods

## Congestion Pricing Details

**Implementation Date:** January 5, 2025  
**Zone:** Manhattan below 60th Street (Central Business District)  
**Affected Precincts:** 1, 5, 6, 7, 9, 10, 13, 14, 17, 18, 19, 20, 22, 23, 24, 25, 26, 28, 30, 32, 34

## Analysis Questions Answered

### Dashboard Analysis
1. ✅ Did citation volumes change after implementation?
2. ✅ Did violations shift from congestion zone to outside areas?
3. ✅ What violation types changed most?
4. ✅ How did enforcement patterns change by agency?
5. ✅ What's the revenue impact?
6. ✅ Did time-of-day patterns shift?

### Enhanced Report Analysis (manhattan_congestion_report.py)
1. ✅ How did out-of-state driver behavior change in-zone vs out-of-zone?
2. ✅ Which states contribute most to citations in each zone?
3. ✅ What are the zone-specific citation patterns (In/Out)?
4. ✅ How did individual precincts respond to congestion pricing?
5. ✅ What are the top violation types in each zone?
6. ✅ How did hourly enforcement patterns change?
7. ✅ What is the geographic distribution of impacts across Manhattan?

## Data Coverage

### Manhattan County Detection
The analysis now uses **comprehensive county filtering** to capture all Manhattan citations:
- `NEW YORK` (standard county name)
- `NY` (abbreviation)
- `MANHATTAN` (common name)
- `NEW YORK COUNTY` (official name)
- `MAN` (short form)
- `MN` (abbreviation)

This ensures no Manhattan citations are missed due to data entry variations.

## Data Sources

The analysis compares:
- **Before Period**: January 2024 (pre-congestion pricing)
- **After Period**: January 2026 (14 months post-implementation)

Data is fetched in real-time from NYC Open Data API and cleaned using the same pipeline as the main dashboard.

## Technical Notes

- Data is cached for 1 hour to improve performance
- Congestion zone classification based on Manhattan precinct numbers
- All visualizations are interactive (hover, zoom, pan)
- Mobile-responsive design for phone/tablet viewing

## Navigation

- Both dashboards are **completely independent**
- No cross-navigation between dashboards
- Each can be deployed separately to Streamlit Cloud
- Both share the same data loading infrastructure (src/ modules)
- Session state is independent between dashboards

## Deployment Options

### Option 1: Deploy Main Dashboard Only
Deploy `dashboard.py` to Streamlit Cloud as usual. Congestion analysis remains local or separate deployment.

### Option 2: Deploy Congestion Analysis Only
Deploy `congestion_analysis.py` as a standalone app focused on impact analysis.

### Option 3: Deploy Both Separately
- App 1: `https://your-app-main.streamlit.app` (dashboard.py)
- App 2: `https://your-app-congestion.streamlit.app` (congestion_analysis.py)

Each app works independently with no dependencies on the other.
