import json
import pandas as pd
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
import config

class GeoValidator:
    def __init__(self):
        with open(config.GEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
            self.features = []
            geometries = []
            
            for feat in geojson_data['features']:
                poly = shape(feat['geometry'])
                name = feat['properties'].get('name', 'N/A')
                self.features.append((poly, name))
                geometries.append(poly)
            
            # Create spatial index for faster lookup
            self.spatial_index = STRtree(geometries)
            print(f"✓ Loaded {len(self.features)} wards from GeoJSON with spatial indexing")
        
        try:
            self.lookup_df = pd.read_csv(config.CSV_LOOKUP_PATH, sep=None, engine='python', encoding='utf-8-sig')
        except:
            self.lookup_df = pd.DataFrame()

    def find_ward_geo(self, lat, lon):
        """Find ward using lat/lon with spatial indexing."""
        if lat is None or lon is None:
            return "N/A"
        
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return "N/A"
        
        p = Point(lon, lat)
        
        # Use spatial index to find candidate geometries
        candidate_indices = list(self.spatial_index.query(p))
        
        # Check if point is contained in any candidate geometry
        for idx in candidate_indices:
            poly, name = self.features[idx]
            if poly.contains(p):
                return name
        
        # If not found in candidates, do full check (edge case)
        for poly, name in self.features:
            if poly.contains(p):
                return name
        
        return "Outside Boundaries"

    def get_merging_note(self, ward_name):
        """Get merging notes for ward from lookup CSV."""
        if self.lookup_df.empty or not ward_name or ward_name == "N/A":
            return ""
        
        try:
            ward_name_lower = str(ward_name).lower().strip()
            match = self.lookup_df[self.lookup_df['Phường / Xã'].str.lower() == ward_name_lower]
            
            if not match.empty:
                note = str(match.iloc[0]['Ghi Chú']).strip()
                return note if note and note != "nan" else "No note"
            return "No note"
        except Exception as e:
            print(f"Error getting merging note for {ward_name}: {e}")
            return "Error"