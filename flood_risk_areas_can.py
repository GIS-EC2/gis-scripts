import rasterio
from rasterio.windows import Window

# Path to the binary file
raster_path = './SHP/CAN/Hydro/flood_risk_areas.tif'

def flood_risk_areas_can(point_x, point_y):
    try:
        with rasterio.open(raster_path) as src:
            # Get the row and column in the raster corresponding to the point
            row, col = src.index(point_x, point_y)

            # Define a small window around the point to read
            window = Window(col_off=col, row_off=row, width=1, height=1)

            # Read the raster value from the small window
            raster_value = src.read(1, window=window)[0, 0]

            # Map the raster value to flood risk levels
            if raster_value == 1:
                return "Lowest"
            elif raster_value == 2:
                return "Low"
            elif raster_value == 3:
                return "Medium-Low"
            elif raster_value == 4:
                return "Medium-High"
            elif raster_value == 5:
                return "High"
            elif raster_value == 6:
                return "Highest"
            else:
                return "Unknown risk level"  # Handle any unexpected values

    except Exception as e:
        print(f"Error in flood_risk_areas: {e}")
        return None
