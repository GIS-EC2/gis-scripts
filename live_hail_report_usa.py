import requests
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd
from datetime import datetime

# ArcGIS Feature Service URL for NOAA storm reports
service_url = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/NOAA_storm_reports_v1/FeatureServer/0/query"

# Function to find the closest hail storm to the point and return details
def get_closest_hail_storm(point_x, point_y):
    try:
        # Transform the coordinates from EPSG:4326 (WGS84) to EPSG:3857 (Web Mercator)
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        x_3857, y_3857 = transformer.transform(point_x, point_y)
        point = Point(x_3857, y_3857)
        point_buffer = point.buffer(100)
        # Extract the bounding box (envelope) of the buffer polygon
        buffer_envelope = point_buffer.bounds  # Returns (minx, miny, maxx, maxy)
        # Parameters for the ArcGIS API request
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{buffer_envelope[0]},{buffer_envelope[1]},{buffer_envelope[2]},{buffer_envelope[3]}",  # Bounding box geometry
            "geometryType": "esriGeometryEnvelope",  # Envelope type geometry
            "spatialRel": "esriSpatialRelIntersects",  # Spatial relationship
            "outFields": "UTC_DATETIME,COMMENTS",  # Request relevant fields
            "returnGeometry": "true",  # Return geometry for distance calculations
            "f": "geojson"  # Return the result in GeoJSON format
        }

        # Make the request to the ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()
        print(data)
        # Check for errors in the response
        if 'error' in data:
            print(f"Error from NOAA storm reports API: {data['error']['message']}")
            return None
        
        if not data.get('features'):
            print("No Hail Storm found near the point.")
            return {
            "Recent Hail Storm": "No",}
        
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        gdf['distance'] = gdf.geometry.distance(point)
        # Find the feature with the minimum distance
        nearest_feature = gdf.loc[gdf['distance'].idxmin()]

        date_time = datetime.fromtimestamp(nearest_feature["UTC_DATETIME"] / 1000)
        # Format the datetime object into the desired format: "3/28/2024 7:35:11.000 PM"
        formatted_date_time = date_time.strftime('%m/%d/%Y %I:%M:%S.%f %p')[:-3]
        # Return the result as a dictionary
        return {
            "Recent Hail Storm": "Yes",
            "Date/Time": formatted_date_time,
            "Hail Report": nearest_feature.get("COMMENTS")
        }
    
    except Exception as e:
        print(f"Error in get_closest_hail_storm: {e}")
        return None
