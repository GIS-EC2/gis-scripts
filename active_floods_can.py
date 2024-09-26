import requests
from shapely.geometry import Point
from pyproj import Transformer

# Define the ArcGIS Feature Service URL for the active flood areas
service_url = "https://maps-cartes.services.geo.ca/egs_sgu/rest/services/Flood_Inondation/EGS_Flood_Product_Active_en/MapServer/1/query"

# Function to check if a geocoded point is within an active flood area
def is_point_within_flood(point_x, point_y):
    try:
        # Transform coordinates from EPSG:4326 to EPSG:3857
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        x_3857, y_3857 = transformer.transform(point_x, point_y)
        
        # ArcGIS Feature Service query parameters
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{x_3857},{y_3857}",  # Use the point geometry in EPSG:3857
            "geometryType": "esriGeometryPoint",
            "inSR": "3857",  # Input spatial reference EPSG:3857
            "spatialRel": "esriSpatialRelIntersects",  # Check if point intersects with any polygons
            "outFields": "OBJECTID",  # You can request any specific fields, here we just use 'OBJECTID'
            "returnGeometry": "false",  # No need to return geometry
            "f": "json"  # Return results in JSON format
        }

        # Send request to ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()

        # Initialize flood status
        flood_status = "Not within an active flood area."

        # Check for errors in the API response
        if 'error' in data:
            print(f"Error from API: {data['error']['message']}")
            return None

        # If features are returned, the point is within an active flood area
        if data.get('features'):
            flood_status = "Within an active flood area."

        # Return flood status
        return {
            "Flood Status": flood_status
        }

    except Exception as e:
        print(f"Error in is_point_within_flood: {e}")
        return None