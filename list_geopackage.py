import fiona

# Use Fiona directly to list the layers
file_path = r"G:\1. Projects\hazard-reports-app\GPKGs\NRI_CensusTracts.gpkg"

with fiona.Env():
    with fiona.open(file_path) as src:
        layers = src.schema['properties']
        print("Layer properties:", layers)

    layers = fiona.listlayers(file_path)
    print("Available layers:", layers)
