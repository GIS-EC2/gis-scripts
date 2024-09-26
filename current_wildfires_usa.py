import requests
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import mapping
from shapely.ops import nearest_points
from pyproj import Transformer
import geopandas as gpd
from datetime import datetime
# Define the ArcGIS Feature Service URL
service_url = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/USA_Wildfires_v1/FeatureServer/0/query"

# Function to find the nearest fire incident to the point and return details
def get_nearest_fire_incident(point_x, point_y):
    try:
        # Create a point from the input coordinates in WGS84 (EPSG:4326)
        point = Point(point_x, point_y)

        # Create a 500-meter buffer around the point (approximate degree conversion for buffer in WGS84)
        buffer_radius_degrees = 500 / 111320  # 1 degree ~ 111.32 km
        point_buffer = point.buffer(buffer_radius_degrees)

        # Extract the bounding box (envelope) of the buffer polygon
        buffer_envelope = point_buffer.bounds  # Returns (minx, miny, maxx, maxy)

        # Define the query parameters for the ArcGIS service
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{buffer_envelope[0]},{buffer_envelope[1]},{buffer_envelope[2]},{buffer_envelope[3]}",  # Use the bounding box as geometry
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",  # Only return incidents that intersect with the buffer
            "outFields": "*",  # Request all fields
            "returnGeometry": "true",  # Return geometry to calculate the nearest point
            "f": "geojson"  # Return the result in GeoJSON format
        }

        # Make the request to the ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()
        # Check if any incidents are returned
        if not data.get('features'):
            return {
                "Current Wildfire Nearby": "No",
                "Message": "No wildfires within 500 meters."
            }

        # Convert the features into GeoDataFrame to easily handle geometry and attributes
        gdf = gpd.GeoDataFrame.from_features(data['features'])

       # Calculate the distance between the point and all fire incident geometries
        gdf['distance'] = gdf.geometry.distance(point)

        # Find the feature with the minimum distance
        nearest_feature = gdf.loc[gdf['distance'].idxmin()]

        date_time = datetime.fromtimestamp(nearest_feature["FireDiscoveryDateTime"] / 1000)
        # Format the datetime object into the desired format: "3/28/2024 7:35:11.000 PM"
        formatted_date_time = date_time.strftime('%m/%d/%Y %I:%M:%S.%f %p')[:-3]
        # Extract necessary information from the nearest feature
        incident_info = {
            "Current Wildfire Nearby": "Yes",
            "Fire Incident Name": nearest_feature["IncidentName"],
            "Fire Incident Type": nearest_feature["IncidentTypeCategory"],
            "Fire Discovery Date Time": formatted_date_time,
            "Fire Percent Contained": nearest_feature["PercentContained"],
            "Fire Incident Cause": nearest_feature["FireCause"],
            "Fire Primary Fuel": nearest_feature["PrimaryFuelModel"],
            "Residences Destroyed": nearest_feature["ResidencesDestroyed"],
            "Other Structures Destroyed": nearest_feature["OtherStructuresDestroyed"],
            "Fire Incident Injuries": nearest_feature["Injuries"],
            "Fire Incident Fatalities": nearest_feature["Fatalities"]
        }

        return incident_info

    except Exception as e:
        print(f"Error in get_nearest_fire_incident: {e}")
        return None
