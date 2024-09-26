import requests
from shapely.geometry import Point
from pyproj import Transformer

# Define the ArcGIS Feature Service URL for landslide susceptibility
service_url = "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/US_Landslide_poly_v2/FeatureServer/1/query"

# Confidence values and their meanings
confidence_map = {
    8: "High confidence in extent or nature of landslide.",
    5: "Confident consequential landslide at this location.",
    3: "Likely landslide at or near this location.",
    2: "Probable landslide in the area.",
    1: "Possible landslide in the area."
}

# Function to check if a point intersects a landslide feature and write result to CSV
def landslide_susceptibility_analysis(point_x, point_y):
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
            "outFields": "Confidence",  # Request the Confidence field
            "returnGeometry": "false",  # No need to return geometry
            "f": "json"  # Return results in JSON format
        }

        # Send request to ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()

        # Initialize result
        landslide_status = "Not within a landslide feature."
        confidence_value = None

        # Check for errors in the API response
        if 'error' in data:
            print(f"Error from API: {data['error']['message']}")
            return None

        # If features are returned, the point is within a landslide feature
        if data.get('features'):
            confidence_value = data['features'][0]['attributes']['Confidence']
            landslide_status = confidence_map.get(confidence_value, "Unknown confidence value")

        return landslide_status

    except Exception as e:
        print(f"Error in landslide_susceptibility_analysis: {e}")
        return None
