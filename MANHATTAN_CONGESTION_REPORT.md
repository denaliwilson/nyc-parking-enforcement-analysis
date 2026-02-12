# Manhattan Congestion Pricing Impact Report

## Overview

The Manhattan Congestion Report (`manhattan_congestion_report.py`) generates comprehensive HTML reports analyzing the impact of congestion pricing on parking citations in Manhattan.

## Quick Start

```bash
python src/manhattan_congestion_report.py
```

**Duration:** ~15-20 minutes (loads 62 days of data from NYC Open Data API)

**Output:** `outputs/reports/manhattan_congestion_report_YYYYMMDD_HHMMSS.html`

## Analysis Periods

- **Before Period:** December 5, 2024 - January 4, 2025 (31 days)
- **Implementation Date:** January 5, 2025
- **After Period:** January 5, 2025 - February 4, 2025 (31 days)

## Zone Classification

### In Zone (Below 60th Street) - 11 Precincts
Precincts: 1, 5, 6, 7, 9, 10, 13, 14, 17, 18, 22

### Border Zone (On/Near 60th Street) - 2 Precincts
Precincts: 19, 20

### Out of Zone (Above 60th Street) - 9 Precincts
Precincts: 23, 24, 25, 26, 28, 30, 32, 33, 34

## Report Sections

### 1. Executive Summary
- Analysis period details
- Zone classifications
- Implementation date

### 2. Key Findings
- Total citations (before vs after)
- Daily average citations
- In Zone citation changes
- Border Zone citation changes
- Out of Zone citation changes

### 3. Zone Analysis
- Citation counts by zone type
- Percentage changes
- Bar charts and percent change visualizations
- Zone-level statistics table

### 4. Precinct Analysis
- Heatmap of top 20 precincts
- Before/after citation counts
- Change percentages
- Top 15 precincts table

### 5. Violation Analysis
- Top 15 violation types
- Before/after comparison
- Change counts and percentages

### 6. Time Pattern Analysis
- Hourly citation patterns
- Before/after overlay charts
- Peak hour identification

### 7. Out-of-State Plate Behavior Analysis ⭐ NEW
**Key Insights:**
- How did non-NY drivers respond to congestion pricing?
- Did out-of-state citations increase/decrease in-zone vs out-of-zone?
- Which states are most affected?

**Visualizations:**
- Out-of-state citation counts by zone (before vs after)
- Out-of-state percentage share by zone
- Dual bar charts with labeled values

**Statistics Table:**
- Zone-by-zone breakdown
- Before/After out-of-state counts
- Before/After percentages
- Change in count (absolute)
- Change in percentage (percentage points)
- Percent change (relative)

**Top Contributors:**
- Top 5 out-of-state contributors per zone
- Before and after comparison
- Citation counts by state

## Data Collection Strategy

### Enhanced Manhattan County Filtering
To ensure comprehensive coverage, the report filters for multiple county name variations:
- `NEW YORK` (standard)
- `NY` (abbreviation)
- `MANHATTAN` (common name)
- `NEW YORK COUNTY` (official name)
- `MAN` (short form)
- `MN` (abbreviation)

### Day-by-Day Loading
- Loads data one day at a time to prevent API timeouts
- Progress tracking for all 62 days
- Automatic retry logic
- Combines all days at the end

## Features

✅ **Comprehensive Analysis**
- Multiple analysis perspectives (zones, precincts, violations, time, states)
- Before/after statistical comparisons
- Percentage changes and absolute changes

✅ **Rich Visualizations**
- Interactive bar charts
- Precinct heatmaps
- Line charts for hourly patterns
- Color-coded tables (red=increase, green=decrease)

✅ **Self-Contained HTML**
- All charts embedded as base64 images
- No external dependencies
- Can be shared via email or web hosting
- Professional styling with gradients and cards

✅ **Detailed Metadata**
- Report generation timestamp
- Data source information
- Record counts for transparency
- Analysis methodology

## Use Cases

1. **Policy Impact Assessment**
   - Measure citation volume changes
   - Identify geographic shifts in violations
   - Understand behavioral changes

2. **Revenue Analysis**
   - Track citation counts (proxy for revenue)
   - Zone-specific revenue impacts

3. **Enforcement Planning**
   - Identify precincts with significant changes
   - Understand time-of-day shifts
   - Plan resource allocation

4. **Public Communication**
   - Share impact results with stakeholders
   - Visualize policy outcomes
   - Support data-driven discussions

5. **Out-of-State Driver Analysis**
   - Understand how congestion pricing affects visitors
   - Identify which states are most impacted
   - Compare behavior in-zone vs out-of-zone

## Technical Details

### Data Processing
1. Load 62 days of Manhattan data (31 before + 31 after)
2. Filter for Manhattan using multiple county variations
3. Clean data using `ParkingDataCleaner`
4. Classify precincts by zone type
5. Analyze by multiple dimensions

### Analysis Functions
- `compare_overall_metrics()`: High-level before/after comparison
- `analyze_by_zone()`: Zone-specific analysis
- `analyze_by_precinct()`: Precinct-level comparison
- `analyze_violations()`: Violation type analysis
- `analyze_time_patterns()`: Hourly and daily patterns
- `analyze_out_of_state_behavior()`: Registration state analysis ⭐ NEW

### Visualization Functions
- `create_zone_comparison_chart()`: Bar charts for zones
- `create_precinct_heatmap()`: Heatmap of top precincts
- `create_hourly_comparison()`: Line chart for hourly patterns
- `create_out_of_state_chart()`: Dual bar charts for state analysis ⭐ NEW

### Output Format
- HTML with embedded CSS styling
- Base64-encoded PNG images
- Responsive design
- Color-coded metrics (increase=red, decrease=green)

## Requirements

### Python Packages
- pandas
- numpy
- matplotlib
- seaborn
- requests

### System Requirements
- Internet connection (for API access)
- ~500MB RAM
- ~100MB disk space for temporary data

## Troubleshooting

### API Timeouts
- Report automatically loads day-by-day to prevent timeouts
- If a specific day fails, it logs and continues
- Check internet connection if multiple days fail

### No Data Found
- Verify date range includes available data
- Check NYC Open Data API status
- Ensure internet connectivity

### Memory Issues
- Report processes data in chunks
- Close other applications if needed
- Consider smaller date ranges if issues persist

## Future Enhancements

- [ ] Add week-by-week trends over time
- [ ] Include statistical significance testing
- [ ] Add map visualizations with precinct boundaries
- [ ] Export data to CSV for further analysis
- [ ] Add command-line arguments for custom date ranges
- [ ] Include vehicle type analysis
- [ ] Add fine amount analysis

## Related Tools

- **congestion_analysis.py**: Streamlit dashboard for interactive exploration
- **generate_weekly_analysis.py**: Quick 7-day reports
- **generate_monthly_analysis.py**: Monthly reports with maps

## Support

For questions or issues:
1. Check documentation in `CONGESTION_ANALYSIS.md`
2. Review data sources in `DATA_SOURCES.md`
3. Verify setup in `SETUP.md`
