import geopandas as gpd
from shapely.geometry import Point
import os
# Path to the folder where the USA water features are stored (Hydro)
relative_path = "./SHP/USA/Fema/NRI_CensusTracts_Prod.shp"
script_dir = os.path.dirname(__file__)
shapefile_path = os.path.join(script_dir, relative_path)
NRI_CensusTracts_gdf = gpd.read_file(shapefile_path)

# Define the function to get the RISK_RATNG value for a point
def get_NRI_Index(point):
    try:
        # Create a Point geometry from the input coordinates
        point_geom = Point(point["x"], point["y"])
        
        # Create a GeoDataFrame from the point for spatial operations
        point_gdf = gpd.GeoDataFrame([{'geometry': point_geom}], crs=NRI_CensusTracts_gdf.crs)
        
        # Find the polygon that contains the point
        matching_polygon = NRI_CensusTracts_gdf[NRI_CensusTracts_gdf.contains(point_geom)]
        
        if not matching_polygon.empty:
            # Retrieve the RISK_RATNG value
            risk_rating = matching_polygon.iloc[0]["RISK_RATNG"]
            return risk_rating
        else:
            print("No polygon found containing the point.")
            return None
    except Exception as e:
        print(f"Error in get_NRI_Index: {e}")
        return None