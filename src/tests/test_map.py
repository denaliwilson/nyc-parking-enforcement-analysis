"""Quick test to download and visualize precinct map"""
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# Setup paths
geospatial_dir = Path('data/geospatial')
geospatial_dir.mkdir(parents=True, exist_ok=True)

print("Downloading NYC precinct boundaries...")

# Try ArcGIS source (most reliable)
url = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Police_Precincts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson"

try:
    response = requests.get(url, timeout=60)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        print(f"Loaded {len(gdf)} precincts")
        print(f"Columns: {list(gdf.columns)}")
        
        # Find precinct column
        for col in gdf.columns:
            if 'precinct' in col.lower():
                print(f"Precinct column: {col}")
                print(f"Sample: {gdf[col].head().tolist()}")
                break
        
        # Save test map
        fig, ax = plt.subplots(figsize=(10, 12))
        gdf.plot(ax=ax, edgecolor='black', facecolor='lightblue', linewidth=0.5)
        ax.set_title('NYC Police Precincts')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig('test_precinct_map.png', dpi=150, bbox_inches='tight')
        print("Saved: test_precinct_map.png")
        plt.close()
        
        # Save GeoJSON
        output_path = geospatial_dir / 'nyc_precincts.geojson'
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"Saved: {output_path}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
