import requests
from shapely.geometry import Point
from shapely.geometry import mapping
from pyproj import Transformer

# Define the ArcGIS Feature Service URL
service_url = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/USGS_Seismic_Data_v1/FeatureServer/1/query"

# Function to find the nearest earthquake incident to the point and return details
def get_world_recent_earthquakes(point_x, point_y):
    try:

        transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        # Transform the coordinates from EPSG:4326 (WGS84) to EPSG:3857 (Web Mercator)
        x_3857, y_3857 = transformer.transform(point_x, point_y)
        # Parameters for the ArcGIS API request
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{x_3857},{y_3857}",  # Use the point geometry in X,Y format
            "geometryType": "esriGeometryPoint",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "mag",  # Request specific fields: magnitude 
            "returnGeometry": "false",  # We don't need the geometry of the earthquake returned
            "orderByFields": "eventTime DESC",  # Order by most recent earthquakes
            "f": "json"  # Return the result in JSON format
        }

        # Make the request to the ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()
        # Initialize result variables
        earthquake_alert = "No"
        magnitude = None
        # Check for errors
        if 'error' in data:
            print(f"Error from API: {data['error']['message']}")
            return None
        
        # Check if any earthquakes are returned
        if data.get('features'):
            earthquake_alert = "Yes"
            magnitude = data['features'][0]['attributes']['mag']
        else:
            earthquake_alert = "No"
            magnitude = "N/A"

        # Return updated values
        return {
            "Earthquake Alert": earthquake_alert,
            "Magnitude": magnitude
        }
    
    except Exception as e:
        print(f"Error in get_world_recent_earthquakes: {e}")
        return None
