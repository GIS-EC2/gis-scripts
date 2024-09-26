import requests
from shapely.geometry import Point
import geopandas as gpd

# Define the ArcGIS Feature Service URL for Major Earthquakes
service_url = "https://services1.arcgis.com/VAI453sU9tG9rSmh/arcgis/rest/services/Major_Earthquakes_features/FeatureServer/0/query"

# Function to check if a point is within 1 km of a major earthquake and return results
def check_near_historical_earthquake(point_x, point_y):
    try:
        # Create a point from the input coordinates in WGS84 (EPSG:4326)
        point = Point(point_x, point_y)

        # Create a 500-meter buffer around the point (approximate degree conversion for buffer in WGS84)
        buffer_radius_degrees = 1000 / 111320  # 1 degree ~ 111.32 km
        point_buffer = point.buffer(buffer_radius_degrees)

        # Extract the bounding box (envelope) of the buffer polygon
        buffer_envelope = point_buffer.bounds  # Returns (minx, miny, maxx, maxy)

        # ArcGIS Feature Service query parameters
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{buffer_envelope[0]},{buffer_envelope[1]},{buffer_envelope[2]},{buffer_envelope[3]}",  # Use the bounding box as geometry
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",  # Check for intersection
            "outFields": "EQ_PRIMARY,INTENSITY_LBL,DEATHS_LABEL,DAMAGE_LABEL,EQ_DATE_LBL",  # Request specific fields
            "returnGeometry": "true",  # We need to return geometry to calculate distances
            "f": "geojson"  # Return results in JSON format
        }

        # Send request to ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()

        # Ensure there are features in the response
        if not data.get('features'):
            print("No Earthquakes found near the point.")
            return {
            "Near Historical Major Earthquake": "No",}
        # Convert the features into GeoDataFrame with Shapely geometries
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        print(gdf)
        # Ensure the GeoDataFrame has geometries to calculate distances
        if gdf.empty:
            print("No valid geometries found in the response.")
            return None

        # Calculate the distance between the point and all earthquake geometries
        gdf['distance'] = gdf.geometry.distance(point)

        # Find the feature with the minimum distance
        nearest_feature = gdf.loc[gdf['distance'].idxmin()]
        # Safely access attributes and check for None values
        near_earthquake = "Yes"
        magnitude = nearest_feature.get("EQ_PRIMARY")
        intensity = nearest_feature.get("INTENSITY_LBL")
        deaths = nearest_feature.get("DEATHS_LABEL")
        damage = nearest_feature.get("DAMAGE_LABEL")
        eq_date = nearest_feature.get("EQ_DATE_LBL")

        return {
            "Near Historical Major Earthquake": near_earthquake,
            "HE Magnitude": magnitude,
            "HE Intensity": intensity,
            "HE Deaths": deaths,
            "HE Damage": damage,
            "HE_Date": eq_date
        }

    except Exception as e:
        print(f"Error in check_near_historical_earthquake: {e}")
        return None
