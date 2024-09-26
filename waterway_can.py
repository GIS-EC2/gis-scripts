import geopandas as gpd
import os
from shapely.geometry import Point
from pyproj import Geod

# Dictionary that maps Canadian provinces/territories to their respective water features
province_water_features = {
    "Alberta": ["AlbertaWTR.shp", "AlbertaWTRWS.shp"],
    "British Columbia": ["BCWTR.shp", "BCWTRWS.shp"],
    "Manitoba": ["ManitobaWTR.shp", "ManitobaWTRWS.shp"],
    "New Brunswick": ["NewBrunswickWTR.shp", "NewBrunswickWTRWS.shp"],
    "New Foundland and Labrador": ["NewFoundlandANDLabradorWTR.shp", "NewFoundlandANDLabradorWTRWS.shp"],
    "Northwest Territories": ["NorthwestTerritoriesWTR.shp", "NorthwestTerritoriesWTRWS.shp"],
    "Nova Scotia": ["NovaWTR.shp", "NovaWTRWS.shp"],
    "Nunavut": ["NunavutWTR.shp", "NunavutWTRWS.shp"],
    "Ontario": ["OntarioWTR.shp", "OntarioWTRWS.shp"],
    "Prince Edward Island": ["PrinceEdwardIslandWTR.shp", "PrinceEdwardIslandWTRWS.shp"],
    "Quebec": ["QuebecWTR.shp", "QuebecWTRWS.shp"],
    "Saskatchewan": ["SaskatchewanWTR.shp", "SaskatchewanWTRWS.shp"],
    "Yukon": ["YukonWTR.shp", "YukonWTRWS.shp"]
}

# Updated path to the folder where the Canadian water features are stored
water_features_path = r"G:\1. Projects\hazard-reports-app\SHP\CAN\Hydro"
world_ocean_shapefile = r"G:\1. Projects\hazard-reports-app\SHP\GEN\World_Ocean.shp"

# Initialize geod for geodesic calculations
geod = Geod(ellps="WGS84")

def calculate_geodesic_distance(point_geom, water_geom):
    """
    Calculate geodesic distance between two geometries (point and water feature)
    :param point_geom: Point geometry (longitude, latitude)
    :param water_geom: Water feature geometry (in EPSG:4326)
    :return: Geodesic distance in meters
    """
    point_coords = point_geom.coords[0]  # Extract point coordinates
    min_distance = float('inf')

    # Iterate through all vertices of the water feature
    if water_geom.geom_type == 'Polygon' or water_geom.geom_type == 'LineString':
        for vertex in water_geom.exterior.coords if water_geom.geom_type == 'Polygon' else water_geom.coords:
            dist = geod.inv(point_coords[0], point_coords[1], vertex[0], vertex[1])[2]  # Geodesic distance
            if dist < min_distance:
                min_distance = dist
    return min_distance


def calculate_distance_to_ocean(point_geom):
    """
    Calculate distance to the nearest ocean feature.
    :param point_geom: Geocoded point geometry (longitude, latitude) in EPSG:4326
    :return: Minimum distance to the nearest ocean feature in meters
    """
    try:
        world_ocean_gdf = gpd.read_file(world_ocean_shapefile)
        
        # Ensure World Ocean is in EPSG:4326 for geodesic calculations
        if world_ocean_gdf.crs != "EPSG:4326":
            world_ocean_gdf = world_ocean_gdf.to_crs("EPSG:4326")

        # Filter out invalid or None geometries
        world_ocean_gdf = world_ocean_gdf[~world_ocean_gdf.is_empty & world_ocean_gdf.geometry.notnull()]

        # Calculate distance between the point and all valid ocean polygons
        world_ocean_gdf["distance"] = world_ocean_gdf.geometry.apply(lambda ocean_geom: calculate_geodesic_distance(point_geom, ocean_geom) if ocean_geom is not None else float('inf'))
        
        # Get the minimum distance
        closest_ocean_distance = world_ocean_gdf["distance"].min()

        return closest_ocean_distance
    except Exception as e:
        print(f"Error calculating distance to ocean: {e}")
        return float('inf')  # Return a very large number if there's an error


def get_nearest_water_body(point, province):
    """
    Calculate the nearest distance from a geocoded point to a water feature
    in the given province or territory in Canada, and include oceans.
    :param point: Dictionary with 'x' and 'y' coordinates (longitude, latitude)
    :param province: Name of the province or territory (state) in Canada
    :return: Distance to the nearest water body in meters, or None if not found
    """
    try:
        # Get the water features for the given province
        water_features = province_water_features.get(province)

        if not water_features:
            print(f"No water features found for province: {province}")
            return None

        # Create a Point geometry from the given coordinates (originally in EPSG:4326)
        point_geom = Point(point["x"], point["y"])
        print(f"Original Point (Longitude, Latitude): {point_geom}")

        closest_distance = float('inf')

        # Iterate over the two water features for the province
        for feature in water_features:
            shapefile_path = os.path.join(water_features_path, feature)

            # Load the water feature shapefile, which should also be in EPSG:4326
            if os.path.exists(shapefile_path):
                water_gdf = gpd.read_file(shapefile_path)
                print(f"Loaded water feature: {feature}, CRS: {water_gdf.crs}")
            else:
                print(f"Shapefile not found: {shapefile_path}")
                continue

            # Ensure water_gdf is in EPSG:4326 for geodesic calculations
            if water_gdf.crs != "EPSG:4326":
                water_gdf = water_gdf.to_crs("EPSG:4326")

            # Calculate geodesic distance to the nearest water feature
            water_gdf["distance"] = water_gdf.geometry.apply(lambda geom: calculate_geodesic_distance(point_geom, geom))
            min_distance = water_gdf["distance"].min()

            # Update the closest distance if this one is closer
            if min_distance < closest_distance:
                closest_distance = min_distance

        # Calculate distance to nearest ocean and compare
        ocean_distance = calculate_distance_to_ocean(point_geom)
        final_distance = min(closest_distance, ocean_distance)

        if final_distance < float('inf'):
            print(f"Nearest water body (including ocean) in {province}: {final_distance} meters")
            return final_distance
        else:
            print(f"No water bodies found in {province}")
            return None

    except Exception as e:
        print(f"Error in get_nearest_water_body: {e}")
        return None
