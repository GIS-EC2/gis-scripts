import requests
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd
from datetime import datetime

# ArcGIS Feature Service URL for USA Historical Fire Burned Areas
service_url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/MTBS_Polygons_v1/FeatureServer/0/query"

# Function to check if a point is within a historical fire burned area
def get_historical_fire_info(point_x, point_y):
    try:
        # Transform the coordinates from EPSG:4326 (WGS84) to EPSG:4269 (NAD 1983)
        transformer = Transformer.from_crs("epsg:4326", "epsg:4269", always_xy=True)
        x_3857, y_3857 = transformer.transform(point_x, point_y)
        point = Point(point_x, point_y)
        
        # Parameters for the ArcGIS API request
        params = {
            "where": "1=1",  # Select all features
            "geometry": f"{x_3857},{y_3857}",  # Use the point geometry
            "geometryType": "esriGeometryPoint",
            "spatialRel": "esriSpatialRelIntersects",  # Check if the point intersects with polygons
            "outFields": "FireType,StartDate",  # Fields to retrieve
            "returnGeometry": "true", 
            "f": "geojson"  # Return the result in GeoJSON format
        }

        # Make the request to the ArcGIS REST API
        response = requests.get(service_url, params=params)
        data = response.json()

        # Check for errors in the response
        if 'error' in data:
            print(f"Error from MTBS API: {data['error']['message']}")
            return None
        
        if not data.get('features'):
            print("No historical fire area found near the point.")
            return {
                "Historical Fire": "No"
            }
        
        # Load the GeoJSON response into a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(data['features'])

        gdf['distance'] = gdf.geometry.distance(point)
        # Find the feature with the minimum distance
        nearest_feature = gdf.loc[gdf['distance'].idxmin()]
        date_time = datetime.fromtimestamp(nearest_feature["StartDate"] / 1000)
        # Format the datetime object into the desired format: "3/28/2024 7:35:11.000 PM"
        formatted_date_time = date_time.strftime('%m/%d/%Y %I:%M:%S.%f %p')[:-3]
        # Return the result with the relevant field values
        return {
            "Historical Fire": "Yes",
            "Historical Fire Type": nearest_feature.get("FireType"),
            "Historical Fire Date": formatted_date_time
        }
    
    except Exception as e:
        print(f"Error in get_historical_fire_info: {e}")
        return None
