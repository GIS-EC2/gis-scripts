import requests
from shapely.geometry import Point
from pyproj import Transformer

# ArcGIS Image Service URL for USA Flood Hazard Areas
image_service_url = "https://apps.fs.usda.gov/fsgisx01/rest/services/RDW_Wildfire/RMRS_WRC_WildfireHazardPotential/ImageServer/identify"

# Function to check if a point is within a flood hazard zone and return details
def check_USA_Wildfire_Risk(point_x, point_y):
    try:
        # Transform the coordinates from EPSG:4326 (WGS84) to EPSG:3857 (Web Mercator)
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        x_3857, y_3857 = transformer.transform(point_x, point_y)
        
        # Parameters for the ArcGIS Image Service identify operation
        params = {
            "geometry": f"{x_3857},{y_3857}",  # Point geometry in Web Mercator
            "geometryType": "esriGeometryPoint",  # Geometry type is point
            "returnGeometry": "false",  # We don't need the returned geometry
            "returnCatalogItems": "false",  # We don't need catalog items
            "f": "json",  # Request the result in JSON format
        }

        # Make the request to the ArcGIS Image Service
        response = requests.get(image_service_url, params=params)
        data = response.json()

        # Check for errors in the response
        if 'error' in data:
            print(f"Error from USA Wildfire Risk Image Service: {data['error']['message']}")
            return None
        
        # Check if any flood hazard information is returned
        if not data.get('value'):
            return {
                "Wildfire Risk": "No",
            }

        return {
            "Wildfire Risk": "Yes",
            "Wildfire Risk Value": data.get('value')
        }

    except Exception as e:
        print(f"Error in check_flood_hazard_zone: {e}")
        return None