import json
import pandas as pd
from shapely.geometry import shape, Point
import config

class GeoValidator:
    def __init__(self):
        with open(config.GEOJSON_PATH, 'r', encoding='utf-8') as f:
            self.features = [(shape(feat['geometry']), feat['properties'].get('name', 'N/A')) 
                             for feat in json.load(f)['features']]
        try:
            self.lookup_df = pd.read_csv(config.CSV_LOOKUP_PATH, sep=None, engine='python', encoding='utf-8-sig')
        except:
            self.lookup_df = pd.DataFrame()

    def find_ward_geo(self, lat, lon):
        if lat is None or lon is None: return "N/A"
        p = Point(lon, lat)
        for poly, name in self.features:
            if poly.contains(p): return name
        return "Outside Boundaries"

    def get_merging_note(self, ward_name):
        if self.lookup_df.empty: return ""
        match = self.lookup_df[self.lookup_df['Phường / Xã'].str.lower() == str(ward_name).lower()]
        return str(match.iloc[0]['Ghi Chú']) if not match.empty else "No note"