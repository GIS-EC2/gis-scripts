import requests
from shapely.geometry import Point
from pyproj import Transformer

# Define the ArcGIS Feature Service URL for US Drought Intensity
service_url = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/US_Drought_Intensity_v1/FeatureServer/3/query"

# Mapping of drought condition numbers to descriptive text
drought_condition_map = {
    0: "Abnormally Dry",
    1: "Moderate Drought",
    2: "Severe Drought",
    3: "Extreme Drought",
    4: "Exceptional Drought"
}

# Function to update 'Drought Condition' based on the geocoded point location
def update_drought_condition(point_x, point_y):
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
            "outFields": "dm",  # Get the 'dm' field from the polygon
            "returnGeometry": "false",  # No need to return geometry
            "f": "json"  # Return results in JSON format
        }

        # Send request to ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()
        # Initialize drought condition
        drought_condition = "Not currently affected by drought."

        # Check for errors in the API response
        if 'error' in data:
            print(f"Error from Drought Condition API: {data['error']['message']}")
            return None

        # If features are returned, map the 'dm' field to drought condition
        if data.get('features'):
            dm_value = data['features'][0]['attributes']['dm']
            drought_condition = drought_condition_map.get(dm_value, "Unknown drought condition")

        # Return updated values
        return {
            "Drought Condition": drought_condition
        }

    except Exception as e:
        print(f"Error in update_drought_condition: {e}")
        return None