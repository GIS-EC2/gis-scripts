import requests
from shapely.geometry import Point
from pyproj import Transformer

# Define the ArcGIS Feature Service URL for the wildfire perimeters
service_url = "https://services6.arcgis.com/ubm4tcTYICKBpist/ArcGIS/rest/services/BCWS_FirePerimeters_PublicView/FeatureServer/0/query"

# Function to check if a geocoded point is within a wildfire perimeter
def is_point_within_wildfire_perimeter(point_x, point_y):
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
            "outFields": "OBJECTID",  # Request the OBJECTID or any other field (not needed in this case)
            "returnGeometry": "false",  # No need to return geometry
            "f": "json"  # Return results in JSON format
        }

        # Send request to ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()

        # Initialize wildfire perimeter status
        wildfire_status = "Not within a wildfire perimeter."

        # Check for errors in the API response
        if 'error' in data:
            print(f"Error from API: {data['error']['message']}")
            return None

        # If features are returned, the point is within a wildfire perimeter
        if data.get('features'):
            wildfire_status = "Within a wildfire perimeter."

        # Return wildfire perimeter status
        return {
            "Wildfire Status": wildfire_status
        }

    except Exception as e:
        print(f"Error in is_point_within_wildfire_perimeter: {e}")
        return None