import geopandas as gpd
import os
from shapely.geometry import Point

def get_coniferous_forest_proximity(point):
    try:
        # Base path for shapefiles
        base_path = r"G:\1. Projects\hazard-reports-app\SHP\GEN"

        # List of coniferous forest shapefiles and their corresponding types
        forest_types = [
            {"file": "BorealForests_Taiga.shp", "type": "Boreal Forest/Taiga"},
            {"file": "Temperate_Coniferous_Forests.shp", "type": "Temperate Coniferous Forest"},
            {"file": "TropicalSubtropical_Conifer.shp", "type": "Tropical or Subtropical Coniferous Forest"}
        ]

        closest_distance = float('inf')
        closest_forest_type = None
        closest_ecoregion = None

        # Create a Point geometry in GeoPandas format
        point_geom = Point(point["x"], point["y"])
        point_gdf = gpd.GeoDataFrame(geometry=[point_geom], crs="EPSG:4326")

        # Loop through each shapefile and calculate the distance to the nearest forest
        for forest in forest_types:
            shapefile_path = os.path.join(base_path, forest["file"])

            # Load the shapefile
            if os.path.exists(shapefile_path):
                forest_gdf = gpd.read_file(shapefile_path)
            else:
                print(f"Shapefile not found at {shapefile_path}")
                continue

            # Reproject the point to match the CRS of the forest layer (if necessary)
            if forest_gdf.crs != point_gdf.crs:
                point_gdf = point_gdf.to_crs(forest_gdf.crs)

            # Calculate the distance to the nearest forest in the current shapefile
            forest_gdf["distance"] = forest_gdf.geometry.apply(lambda geom: point_geom.distance(geom))
            min_distance = forest_gdf["distance"].min()

            # Find the nearest forest and get its ECO_NAME
            nearest_forest = forest_gdf.loc[forest_gdf["distance"].idxmin()]
            ecoregion_name = nearest_forest.get("ECO_NAME", "Unknown")

            # Update the closest forest type, ecoregion, and distance if this one is closer
            if min_distance < closest_distance:
                closest_distance = min_distance
                closest_forest_type = forest["type"]
                closest_ecoregion = ecoregion_name

        if closest_forest_type:
            print(f"Distance to nearest coniferous forest: {closest_distance} meters. Forest Type: {closest_forest_type}, Ecoregion: {closest_ecoregion}")
            return closest_distance, closest_forest_type, closest_ecoregion
        else:
            print("No coniferous forest found.")
            return None, None, None

    except Exception as e:
        print(f"Error in get_coniferous_forest_proximity: {e}")
        return None, None, None
