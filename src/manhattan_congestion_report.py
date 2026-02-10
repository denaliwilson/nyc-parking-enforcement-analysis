"""
Manhattan Congestion Pricing Analysis - Comprehensive Report Generator

Generates a detailed before/after comparison report for the Manhattan congestion pricing
implementation on January 5, 2025. Focuses exclusively on Manhattan data for efficiency
and includes zone-specific analysis (in-zone, border, out-of-zone).

Usage:
    python src/manhattan_congestion_report.py
"""

from pathlib import Path
import sys
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent.parent))
from src.config import REPORTS_DIR
from src.data_loader import NYCParkingDataLoader
from src.data_cleaner import ParkingDataCleaner

plt.style.use('seaborn-v0_8-darkgrid')

# ============================================================================
# CONSTANTS - Congestion Pricing Zone Configuration
# ============================================================================

CONGESTION_PRICING_START = date(2025, 1, 5)

# Manhattan precincts IN the congestion zone (below 60th Street)
CONGESTION_ZONE_PRECINCTS = [
    1,   # Financial District
    5,   # Chinatown
    6,   # Greenwich Village
    7,   # Lower East Side
    9,   # East Village
    10,  # Chelsea
    13,  # Gramercy
    14,  # Midtown South
    17,  # East 50s
    18,  # Midtown North
    19,  # Upper East Side (southern portion)
    20,  # Upper West Side (southern portion)
    22,  # Central Park (southern portion)
    23,  # East 100s
    24,  # Upper West Side
    25,  # East Harlem
    26,  # Morningside Heights
    28,  # Central Harlem
    30,  # West Harlem
    32,  # Harlem
    34,  # Washington Heights
]

# Border precincts (adjacent to congestion zone or on boundary)
# These precincts may see spillover effects
BORDER_PRECINCTS = [
    # Note: Some precincts in the main list above may actually be border
    # Refining based on actual 60th Street boundary:
    19,  # Upper East Side - crosses 60th St boundary
    20,  # Upper West Side - crosses 60th St boundary
]

# Out of zone precincts (above 60th Street in Manhattan)
OUT_OF_ZONE_PRECINCTS = [
    23, 24, 25, 26, 28, 30, 32, 33, 34  # Northern Manhattan
]

# Refined classifications based on 60th Street boundary
# IN ZONE: Below 60th Street (approximately precincts 1-18, 22)
IN_ZONE_PRECINCTS = [1, 5, 6, 7, 9, 10, 13, 14, 17, 18, 22]

# BORDER ZONE: On or near 60th Street boundary
BORDER_ZONE_PRECINCTS = [19, 20]  # These straddle the boundary

# OUT OF ZONE: Above 60th Street
OUT_OF_ZONE_PRECINCTS = [23, 24, 25, 26, 28, 30, 32, 33, 34]

# All Manhattan precincts (1-34, excluding 21 which doesn't exist)
ALL_MANHATTAN_PRECINCTS = list(range(1, 35))
ALL_MANHATTAN_PRECINCTS.remove(21)  # Precinct 21 doesn't exist


# ============================================================================
# DATA LOADING - Manhattan-Only Efficient Pipeline
# ============================================================================

def load_manhattan_data(start_date, end_date, period_name="Period"):
    """
    Load Manhattan-only parking citation data for specified date range.
    Loads data day-by-day to avoid API timeouts.
    
    Args:
        start_date: Start date (datetime.date or str 'YYYY-MM-DD')
        end_date: End date (datetime.date or str 'YYYY-MM-DD')
        period_name: Descriptive name for progress messages
        
    Returns:
        pd.DataFrame: Cleaned Manhattan parking citation data
    """
    print(f"\n{'='*70}")
    print(f"Loading {period_name}: {start_date} to {end_date}")
    print(f"{'='*70}")
    
    # Initialize loader
    loader = NYCParkingDataLoader()
    
    # Convert dates to date objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    print(f"\nDate range: {start_date} to {end_date}")
    print(f"County filter: Manhattan (multiple variations)")
    print("Loading data day-by-day to avoid API timeouts...")
    
    start_time = time.time()
    all_data = []
    
    # Load data day by day
    current_date = start_date
    day_count = 0
    total_days = (end_date - start_date).days + 1
    
    while current_date <= end_date:
        day_count += 1
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            print(f"\n  [{day_count}/{total_days}] Loading {date_str}...", end=" ")
            day_df = loader.load_by_day(date_str, limit=75000)
            
            if day_df is not None and len(day_df) > 0:
                # Filter for Manhattan immediately
                manhattan_counties = ['NEW YORK', 'NY', 'MANHATTAN', 'NEW YORK COUNTY', 'MAN', 'MN']
                if 'county' in day_df.columns:
                    day_df['county'] = day_df['county'].str.upper().str.strip()
                    day_df = day_df[day_df['county'].isin(manhattan_counties)]
                
                if len(day_df) > 0:
                    all_data.append(day_df)
                    print(f"✓ {len(day_df):,} Manhattan records")
                else:
                    print("(0 Manhattan records)")
            else:
                print("(no data)")
        except Exception as e:
            print(f"⚠ Error: {e}")
        
        current_date += timedelta(days=1)
        time.sleep(0.5)  # Small delay to be nice to the API
    
    load_time = time.time() - start_time
    
    if len(all_data) == 0:
        print(f"\n❌ No data found for {period_name}")
        return None
    
    # Combine all days
    print(f"\nCombining data from {len(all_data)} days...")
    df = pd.concat(all_data, ignore_index=True)
    
    print(f"✓ Loaded {len(df):,} Manhattan records in {load_time:.1f}s")
    
    # Clean data using standard pipeline
    print("\nCleaning data...")
    cleaner = ParkingDataCleaner(df)
    df_cleaned = cleaner.clean()
    
    if df_cleaned is None or len(df_cleaned) == 0:
        print(f"❌ No valid data after cleaning for {period_name}")
        return None
    
    print(f"✓ {len(df_cleaned):,} records after cleaning ({len(df) - len(df_cleaned):,} removed)")
    
    # Add congestion zone classification
    df_cleaned = classify_precinct_zones(df_cleaned)
    
    # Add period identifier
    df_cleaned['analysis_period'] = period_name
    
    return df_cleaned


def classify_precinct_zones(df):
    """
    Classify each citation by precinct zone type.
    
    Adds columns:
        - zone_type: 'In Zone', 'Border Zone', 'Out of Zone', 'Unknown'
        - in_congestion_zone: Boolean for primary zone
    """
    print("\nClassifying precinct zones...")
    
    def get_zone_type(precinct):
        if pd.isna(precinct):
            return 'Unknown'
        precinct = int(precinct)
        
        if precinct in IN_ZONE_PRECINCTS:
            return 'In Zone'
        elif precinct in BORDER_ZONE_PRECINCTS:
            return 'Border Zone'
        elif precinct in OUT_OF_ZONE_PRECINCTS:
            return 'Out of Zone'
        else:
            return 'Unknown'
    
    df['zone_type'] = df['violation_precinct'].apply(get_zone_type)
    df['in_congestion_zone'] = df['zone_type'] == 'In Zone'
    
    # Report distribution
    zone_dist = df['zone_type'].value_counts()
    print("\nZone Distribution:")
    for zone, count in zone_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {zone}: {count:,} ({pct:.1f}%)")
    
    return df


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def compare_overall_metrics(before_df, after_df):
    """Compare high-level metrics between periods."""
    
    metrics = {
        'Total Citations': {
            'Before': len(before_df),
            'After': len(after_df),
        },
        'Daily Average': {
            'Before': len(before_df) / 31,  # One month = ~31 days
            'After': len(after_df) / 31,
        },
        'In Zone Citations': {
            'Before': len(before_df[before_df['in_congestion_zone']]),
            'After': len(after_df[after_df['in_congestion_zone']]),
        },
        'Border Zone Citations': {
            'Before': len(before_df[before_df['zone_type'] == 'Border Zone']),
            'After': len(after_df[after_df['zone_type'] == 'Border Zone']),
        },
        'Out of Zone Citations': {
            'Before': len(before_df[before_df['zone_type'] == 'Out of Zone']),
            'After': len(after_df[after_df['zone_type'] == 'Out of Zone']),
        },
    }
    
    # Calculate changes
    results = []
    for metric, values in metrics.items():
        before_val = values['Before']
        after_val = values['After']
        change = after_val - before_val
        pct_change = ((after_val - before_val) / before_val * 100) if before_val > 0 else 0
        
        results.append({
            'Metric': metric,
            'Before': before_val,
            'After': after_val,
            'Change': change,
            'Change %': pct_change
        })
    
    return pd.DataFrame(results)


def analyze_by_zone(before_df, after_df):
    """Detailed analysis by zone type."""
    
    zones = ['In Zone', 'Border Zone', 'Out of Zone']
    results = []
    
    for zone in zones:
        before_zone = before_df[before_df['zone_type'] == zone]
        after_zone = after_df[after_df['zone_type'] == zone]
        
        before_count = len(before_zone)
        after_count = len(after_zone)
        change = after_count - before_count
        pct_change = ((after_count - before_count) / before_count * 100) if before_count > 0 else 0
        
        # Top violations in each zone
        before_top_viol = before_zone['violation'].value_counts().head(3).to_dict() if len(before_zone) > 0 else {}
        after_top_viol = after_zone['violation'].value_counts().head(3).to_dict() if len(after_zone) > 0 else {}
        
        results.append({
            'Zone': zone,
            'Before Citations': before_count,
            'After Citations': after_count,
            'Change': change,
            'Change %': pct_change,
            'Before Top 3 Violations': before_top_viol,
            'After Top 3 Violations': after_top_viol
        })
    
    return pd.DataFrame(results)


def analyze_by_precinct(before_df, after_df):
    """Detailed precinct-level comparison."""
    
    # Combine both periods
    before_precinct = before_df['violation_precinct'].value_counts().reset_index()
    before_precinct.columns = ['Precinct', 'Before_Count']
    
    after_precinct = after_df['violation_precinct'].value_counts().reset_index()
    after_precinct.columns = ['Precinct', 'After_Count']
    
    # Merge
    comparison = pd.merge(before_precinct, after_precinct, on='Precinct', how='outer').fillna(0)
    comparison['Change'] = comparison['After_Count'] - comparison['Before_Count']
    comparison['Change_Pct'] = (comparison['Change'] / comparison['Before_Count'] * 100).replace([np.inf, -np.inf], 0)
    
    # Add zone classification
    comparison['Zone_Type'] = comparison['Precinct'].apply(
        lambda p: 'In Zone' if p in IN_ZONE_PRECINCTS 
        else 'Border Zone' if p in BORDER_ZONE_PRECINCTS
        else 'Out of Zone' if p in OUT_OF_ZONE_PRECINCTS
        else 'Unknown'
    )
    
    # Sort by absolute change
    comparison = comparison.sort_values('Change', ascending=False)
    
    return comparison


def analyze_violations(before_df, after_df):
    """Compare violation types between periods."""
    
    before_viols = before_df['violation'].value_counts().head(15).reset_index()
    before_viols.columns = ['Violation', 'Before_Count']
    
    after_viols = after_df['violation'].value_counts().head(15).reset_index()
    after_viols.columns = ['Violation', 'After_Count']
    
    comparison = pd.merge(before_viols, after_viols, on='Violation', how='outer').fillna(0)
    comparison['Change'] = comparison['After_Count'] - comparison['Before_Count']
    comparison['Change_Pct'] = (comparison['Change'] / comparison['Before_Count'] * 100).replace([np.inf, -np.inf], 0)
    comparison = comparison.sort_values('After_Count', ascending=False)
    
    return comparison


def analyze_time_patterns(before_df, after_df):
    """Analyze time-based patterns."""
    
    # Hour of day
    before_hourly = before_df.groupby('violation_hour').size()
    after_hourly = after_df.groupby('violation_hour').size()
    
    # Day of week
    before_daily = before_df.groupby('day_of_week').size()
    after_daily = after_df.groupby('day_of_week').size()
    
    return {
        'hourly_before': before_hourly,
        'hourly_after': after_hourly,
        'daily_before': before_daily,
        'daily_after': after_daily
    }


def analyze_out_of_state_behavior(before_df, after_df):
    """Analyze out-of-state plate behavior in-zone vs out-of-zone."""
    
    # Define out-of-state (not NY)
    before_df['is_out_of_state'] = before_df['state'] != 'NY'
    after_df['is_out_of_state'] = after_df['state'] != 'NY'
    
    results = []
    
    # Analyze by zone type
    for zone in ['In Zone', 'Border Zone', 'Out of Zone']:
        # Before period
        before_zone = before_df[before_df['zone_type'] == zone]
        before_total = len(before_zone)
        before_out_of_state = len(before_zone[before_zone['is_out_of_state']])
        before_pct = (before_out_of_state / before_total * 100) if before_total > 0 else 0
        
        # After period
        after_zone = after_df[after_df['zone_type'] == zone]
        after_total = len(after_zone)
        after_out_of_state = len(after_zone[after_zone['is_out_of_state']])
        after_pct = (after_out_of_state / after_total * 100) if after_total > 0 else 0
        
        # Calculate change
        change_count = after_out_of_state - before_out_of_state
        change_pct = after_pct - before_pct
        pct_change = ((after_out_of_state - before_out_of_state) / before_out_of_state * 100) if before_out_of_state > 0 else 0
        
        results.append({
            'Zone': zone,
            'Before Total': before_total,
            'Before Out-of-State': before_out_of_state,
            'Before Out-of-State %': before_pct,
            'After Total': after_total,
            'After Out-of-State': after_out_of_state,
            'After Out-of-State %': after_pct,
            'Change in Count': change_count,
            'Change in %': change_pct,
            'Percent Change': pct_change
        })
    
    # Top out-of-state contributors by zone
    state_details = {}
    for zone in ['In Zone', 'Border Zone', 'Out of Zone']:
        before_zone = before_df[(before_df['zone_type'] == zone) & (before_df['is_out_of_state'])]
        after_zone = after_df[(after_df['zone_type'] == zone) & (after_df['is_out_of_state'])]
        
        # Top 5 states
        before_states = before_zone['state'].value_counts().head(5).to_dict() if len(before_zone) > 0 else {}
        after_states = after_zone['state'].value_counts().head(5).to_dict() if len(after_zone) > 0 else {}
        
        state_details[zone] = {
            'before_top_states': before_states,
            'after_top_states': after_states
        }
    
    return pd.DataFrame(results), state_details


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def figure_to_base64(fig):
    """Convert matplotlib figure to base64 for HTML embedding."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return image_base64


def create_zone_comparison_chart(zone_analysis):
    """Create bar chart comparing zones."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Absolute counts
    zones = zone_analysis['Zone']
    x = np.arange(len(zones))
    width = 0.35
    
    ax1.bar(x - width/2, zone_analysis['Before Citations'], width, label='Before', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, zone_analysis['After Citations'], width, label='After', color='#e74c3c', alpha=0.8)
    ax1.set_xlabel('Zone Type', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Number of Citations', fontweight='bold', fontsize=11)
    ax1.set_title('Citations by Zone: Before vs After', fontweight='bold', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels(zones)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Percent change
    colors = ['green' if x < 0 else 'red' for x in zone_analysis['Change %']]
    ax2.barh(zones, zone_analysis['Change %'], color=colors, alpha=0.7)
    ax2.set_xlabel('Percent Change (%)', fontweight='bold', fontsize=11)
    ax2.set_title('Percent Change by Zone', fontweight='bold', fontsize=13)
    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, v in enumerate(zone_analysis['Change %']):
        ax2.text(v + (2 if v > 0 else -2), i, f'{v:.1f}%', 
                va='center', ha='left' if v > 0 else 'right', fontweight='bold')
    
    plt.tight_layout()
    return figure_to_base64(fig)


def create_precinct_heatmap(precinct_comparison):
    """Create heatmap of precinct changes."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get top 20 precincts by total citations
    precinct_comparison['Total'] = precinct_comparison['Before_Count'] + precinct_comparison['After_Count']
    top_precincts = precinct_comparison.nlargest(20, 'Total')
    
    # Prepare data for heatmap
    data = top_precincts[['Before_Count', 'After_Count', 'Change']].T
    data.columns = [f"P{int(p)}" for p in top_precincts['Precinct']]
    
    # Create heatmap
    sns.heatmap(data, annot=True, fmt='.0f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Citations'}, ax=ax, linewidths=0.5)
    ax.set_title('Top 20 Precincts: Citation Patterns', fontweight='bold', fontsize=14, pad=15)
    ax.set_ylabel('Metric', fontweight='bold', fontsize=11)
    ax.set_xlabel('Precinct', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    return figure_to_base64(fig)


def create_hourly_comparison(time_patterns):
    """Create hourly pattern comparison."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    hours = range(24)
    before_vals = [time_patterns['hourly_before'].get(h, 0) for h in hours]
    after_vals = [time_patterns['hourly_after'].get(h, 0) for h in hours]
    
    ax.plot(hours, before_vals, marker='o', linewidth=2.5, markersize=6, 
            label='Before (Dec 5, 2024 - Jan 4, 2025)', color='#3498db')
    ax.plot(hours, after_vals, marker='s', linewidth=2.5, markersize=6, 
            label='After (Jan 5 - Feb 4, 2025)', color='#e74c3c')
    
    ax.set_xlabel('Hour of Day', fontweight='bold', fontsize=11)
    ax.set_ylabel('Number of Citations', fontweight='bold', fontsize=11)
    ax.set_title('Hourly Citation Patterns: Before vs After Congestion Pricing', 
                 fontweight='bold', fontsize=13, pad=15)
    ax.set_xticks(range(0, 24, 2))
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return figure_to_base64(fig)


def create_out_of_state_chart(oos_analysis):
    """Create visualization for out-of-state plate behavior by zone."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    zones = oos_analysis['Zone']
    x = np.arange(len(zones))
    width = 0.35
    
    # Chart 1: Out-of-state citation counts
    ax1.bar(x - width/2, oos_analysis['Before Out-of-State'], width, 
            label='Before', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, oos_analysis['After Out-of-State'], width, 
            label='After', color='#e74c3c', alpha=0.8)
    ax1.set_xlabel('Zone Type', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Out-of-State Citations', fontweight='bold', fontsize=11)
    ax1.set_title('Out-of-State Plate Citations by Zone', fontweight='bold', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels(zones)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Chart 2: Percentage of citations from out-of-state
    ax2.bar(x - width/2, oos_analysis['Before Out-of-State %'], width, 
            label='Before', color='#3498db', alpha=0.8)
    ax2.bar(x + width/2, oos_analysis['After Out-of-State %'], width, 
            label='After', color='#e74c3c', alpha=0.8)
    ax2.set_xlabel('Zone Type', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Out-of-State %', fontweight='bold', fontsize=11)
    ax2.set_title('Out-of-State Plate Share by Zone', fontweight='bold', fontsize=13)
    ax2.set_xticks(x)
    ax2.set_xticklabels(zones)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (before_pct, after_pct) in enumerate(zip(oos_analysis['Before Out-of-State %'], 
                                                      oos_analysis['After Out-of-State %'])):
        ax2.text(i - width/2, before_pct + 0.3, f'{before_pct:.1f}%', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax2.text(i + width/2, after_pct + 0.3, f'{after_pct:.1f}%', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    return figure_to_base64(fig)


# ============================================================================
# HTML REPORT GENERATION
# ============================================================================

def generate_html_report(before_df, after_df, output_path):
    """Generate comprehensive HTML report."""
    
    print("\n" + "="*70)
    print("GENERATING COMPREHENSIVE REPORT")
    print("="*70)
    
    # Run analyses
    print("\nAnalyzing overall metrics...")
    overall_metrics = compare_overall_metrics(before_df, after_df)
    
    print("Analyzing by zone...")
    zone_analysis = analyze_by_zone(before_df, after_df)
    
    print("Analyzing by precinct...")
    precinct_comparison = analyze_by_precinct(before_df, after_df)
    
    print("Analyzing violations...")
    violation_comparison = analyze_violations(before_df, after_df)
    
    print("Analyzing time patterns...")
    time_patterns = analyze_time_patterns(before_df, after_df)
    
    print("Analyzing out-of-state plate behavior...")
    oos_analysis, oos_state_details = analyze_out_of_state_behavior(before_df, after_df)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    zone_chart = create_zone_comparison_chart(zone_analysis)
    precinct_heatmap = create_precinct_heatmap(precinct_comparison)
    hourly_chart = create_hourly_comparison(time_patterns)
    oos_chart = create_out_of_state_chart(oos_analysis)
    
    # Build HTML
    print("Building HTML report...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manhattan Congestion Pricing Impact Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
                color: #2c3e50;
            }}
            h1 {{
                color: #1f77b4;
                text-align: center;
                border-bottom: 4px solid #1f77b4;
                padding-bottom: 15px;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #2c3e50;
                border-left: 5px solid #3498db;
                padding-left: 15px;
                margin-top: 40px;
                margin-bottom: 20px;
            }}
            h3 {{
                color: #34495e;
                margin-top: 25px;
            }}
            .summary-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                margin: 25px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .summary-box h2 {{
                color: white;
                border-left: none;
                margin-top: 0;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #3498db;
            }}
            .metric-card h4 {{
                margin: 0 0 10px 0;
                color: #7f8c8d;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }}
            .metric-change {{
                font-size: 1.1em;
                margin-top: 10px;
            }}
            .metric-change.positive {{
                color: #e74c3c;
            }}
            .metric-change.negative {{
                color: #27ae60;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ecf0f1;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            .chart-container {{
                background: white;
                padding: 25px;
                border-radius: 8px;
                margin: 25px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .chart-container img {{
                width: 100%;
                height: auto;
            }}
            .increase {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .decrease {{
                color: #27ae60;
                font-weight: bold;
            }}
            .section {{
                background: white;
                padding: 25px;
                border-radius: 8px;
                margin: 25px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .zone-badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.85em;
                font-weight: 600;
                margin: 0 5px;
            }}
            .zone-in {{
                background-color: #e74c3c;
                color: white;
            }}
            .zone-border {{
                background-color: #f39c12;
                color: white;
            }}
            .zone-out {{
                background-color: #27ae60;
                color: white;
            }}
            .metadata {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <h1>🚗 Manhattan Congestion Pricing Impact Report</h1>
        
        <div class="summary-box">
            <h2>Executive Summary</h2>
            <p><strong>Analysis Period:</strong> One month before and after congestion pricing implementation</p>
            <p><strong>Before Period:</strong> December 5, 2024 - January 4, 2025</p>
            <p><strong>After Period:</strong> January 5, 2025 - February 4, 2025</p>
            <p><strong>Implementation Date:</strong> January 5, 2025</p>
            <p><strong>Focus Area:</strong> Manhattan only (all precincts 1-34)</p>
            <p><strong>Zone Classification:</strong></p>
            <ul>
                <li><span class="zone-badge zone-in">In Zone</span> Below 60th Street (Precincts: {', '.join(map(str, IN_ZONE_PRECINCTS))})</li>
                <li><span class="zone-badge zone-border">Border Zone</span> On/near 60th Street (Precincts: {', '.join(map(str, BORDER_ZONE_PRECINCTS))})</li>
                <li><span class="zone-badge zone-out">Out of Zone</span> Above 60th Street (Precincts: {', '.join(map(str, OUT_OF_ZONE_PRECINCTS))})</li>
            </ul>
        </div>
        
        <h2>📊 Key Findings</h2>
        <div class="metric-grid">
    """
    
    # Add key metrics cards
    for _, row in overall_metrics.iterrows():
        change_class = 'positive' if row['Change'] > 0 else 'negative'
        change_symbol = '▲' if row['Change'] > 0 else '▼'
        
        html_content += f"""
            <div class="metric-card">
                <h4>{row['Metric']}</h4>
                <div class="metric-value">{row['After']:,.0f}</div>
                <div class="metric-change {change_class}">
                    {change_symbol} {abs(row['Change']):,.0f} ({row['Change %']:+.1f}%)
                </div>
                <div style="font-size: 0.85em; color: #95a5a6; margin-top: 8px;">
                    Before: {row['Before']:,.0f}
                </div>
            </div>
        """
    
    html_content += """
        </div>
        
        <h2>🗺️ Zone Analysis</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,""" + zone_chart + """" alt="Zone Comparison">
        </div>
        
        <div class="section">
            <h3>Zone-Level Statistics</h3>
    """
    
    # Zone analysis table
    html_content += zone_analysis.to_html(index=False, classes='table', escape=False, 
                                           formatters={
                                               'Before Citations': lambda x: f'{x:,.0f}',
                                               'After Citations': lambda x: f'{x:,.0f}',
                                               'Change': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+,.0f}</span>',
                                               'Change %': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+.1f}%</span>'
                                           })
    
    html_content += """
        </div>
        
        <h2>🏢 Precinct Analysis</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,""" + precinct_heatmap + """" alt="Precinct Heatmap">
        </div>
        
        <div class="section">
            <h3>Top 15 Precincts by Change</h3>
    """
    
    # Precinct table - top 15
    top_precincts_table = precinct_comparison.head(15)[['Precinct', 'Zone_Type', 'Before_Count', 'After_Count', 'Change', 'Change_Pct']]
    html_content += top_precincts_table.to_html(index=False, classes='table', escape=False,
                                                  formatters={
                                                      'Precinct': lambda x: f'<strong>Precinct {int(x)}</strong>',
                                                      'Before_Count': lambda x: f'{x:,.0f}',
                                                      'After_Count': lambda x: f'{x:,.0f}',
                                                      'Change': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+,.0f}</span>',
                                                      'Change_Pct': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+.1f}%</span>'
                                                  })
    
    html_content += """
        </div>
        
        <h2>🚨 Violation Analysis</h2>
        <div class="section">
            <h3>Top 15 Violations</h3>
    """
    
    html_content += violation_comparison.to_html(index=False, classes='table', escape=False,
                                                   formatters={
                                                       'Before_Count': lambda x: f'{x:,.0f}',
                                                       'After_Count': lambda x: f'{x:,.0f}',
                                                       'Change': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+,.0f}</span>',
                                                       'Change_Pct': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+.1f}%</span>'
                                                   })
    
    html_content += """
        </div>
        
        <h2>⏰ Time Pattern Analysis</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,""" + hourly_chart + """" alt="Hourly Patterns">
        </div>
        
        <h2>🚘 Out-of-State Plate Behavior Analysis</h2>
        <div class="section">
            <h3>Key Insight: Congestion Zone Impact on Out-of-State Drivers</h3>
            <p>This analysis examines how congestion pricing affected out-of-state driver behavior differently 
            in the congestion zone versus outside the zone. Changes in out-of-state plate citation patterns 
            can indicate whether the toll influenced out-of-state drivers to avoid the zone or park differently.</p>
        </div>
        
        <div class="chart-container">
            <img src="data:image/png;base64,""" + oos_chart + """" alt="Out-of-State Analysis">
        </div>
        
        <div class="section">
            <h3>Out-of-State Citation Statistics by Zone</h3>
    """
    
    # Out-of-state analysis table
    oos_display = oos_analysis[['Zone', 'Before Out-of-State', 'Before Out-of-State %', 
                                 'After Out-of-State', 'After Out-of-State %', 
                                 'Change in Count', 'Change in %', 'Percent Change']].copy()
    
    html_content += oos_display.to_html(index=False, classes='table', escape=False,
                                         formatters={
                                             'Before Out-of-State': lambda x: f'{x:,.0f}',
                                             'After Out-of-State': lambda x: f'{x:,.0f}',
                                             'Before Out-of-State %': lambda x: f'{x:.1f}%',
                                             'After Out-of-State %': lambda x: f'{x:.1f}%',
                                             'Change in Count': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+,.0f}</span>',
                                             'Change in %': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+.2f}pp</span>',
                                             'Percent Change': lambda x: f'<span class="{"increase" if x > 0 else "decrease"}">{x:+.1f}%</span>'
                                         })
    
    # Add top out-of-state contributors
    html_content += """
            <h3>Top Out-of-State Contributors by Zone</h3>
    """
    
    for zone in ['In Zone', 'Border Zone', 'Out of Zone']:
        details = oos_state_details[zone]
        before_states = details['before_top_states']
        after_states = details['after_top_states']
        
        html_content += f"""
            <h4>{zone}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <strong>Before (Top 5 States):</strong>
                    <ul>
        """
        
        for state, count in list(before_states.items())[:5]:
            html_content += f"<li>{state}: {count:,} citations</li>\n"
        
        html_content += """
                    </ul>
                </div>
                <div>
                    <strong>After (Top 5 States):</strong>
                    <ul>
        """
        
        for state, count in list(after_states.items())[:5]:
            html_content += f"<li>{state}: {count:,} citations</li>\n"
        
        html_content += """
                    </ul>
                </div>
            </div>
        """
    
    html_content += """
        </div>
        
        <div class="metadata">
            <strong>Report Generated:</strong> """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """<br>
            <strong>Data Source:</strong> NYC Open Data - Parking Violations Issued<br>
            <strong>Before Period Records:</strong> """ + f"{len(before_df):,}" + """<br>
            <strong>After Period Records:</strong> """ + f"{len(after_df):,}" + """<br>
            <strong>Total Records Analyzed:</strong> """ + f"{len(before_df) + len(after_df):,}" + """
        </div>
    </body>
    </html>
    """
    
    # Write to file
    output_path.write_text(html_content, encoding='utf-8')
    print(f"\n✓ Report saved to: {output_path}")
    
    return output_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    
    print("\n" + "="*70)
    print("MANHATTAN CONGESTION PRICING - COMPREHENSIVE ANALYSIS")
    print("="*70)
    print("\nThis analysis compares Manhattan parking citations one month before")
    print("and after the congestion pricing implementation on January 5, 2025.")
    print("\nZone Classification:")
    print(f"  • IN ZONE (below 60th St): {len(IN_ZONE_PRECINCTS)} precincts")
    print(f"  • BORDER ZONE (on/near 60th St): {len(BORDER_ZONE_PRECINCTS)} precincts")
    print(f"  • OUT OF ZONE (above 60th St): {len(OUT_OF_ZONE_PRECINCTS)} precincts")
    
    # Define analysis periods
    before_start = date(2024, 12, 5)
    before_end = date(2025, 1, 4)
    
    after_start = date(2025, 1, 5)
    after_end = date(2025, 2, 4)
    
    # Load data
    print("\n" + "="*70)
    print("STEP 1: LOADING DATA")
    print("="*70)
    
    before_df = load_manhattan_data(before_start, before_end, "BEFORE Period")
    after_df = load_manhattan_data(after_start, after_end, "AFTER Period")
    
    if before_df is None or after_df is None:
        print("\n❌ Failed to load required data. Exiting.")
        return
    
    # Generate report
    print("\n" + "="*70)
    print("STEP 2: GENERATING REPORT")
    print("="*70)
    
    # Create output directory
    reports_dir = Path(REPORTS_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = reports_dir / f'manhattan_congestion_report_{timestamp}.html'
    
    generate_html_report(before_df, after_df, output_file)
    
    print("\n" + "="*70)
    print("✓ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nReport saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print("\nOpen the HTML file in your browser to view the full report.")


if __name__ == '__main__':
    main()
