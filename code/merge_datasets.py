"""
https://geopandas.org/en/stable/docs/user_guide/mergingdata.html
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

years = [i for i in range(2001, 2018)]

for year in years:
    df = pd.read_csv(os.path.join("..", "plant_locations", "original_data", f"FINAL PLANT DATA .xlsx - {year}.csv"))
    gdf = gpd.read_file(os.path.join("..", "plant_locations", "original_data", "Fossil_Fuels_All.shp"))

    gdf["PLANT_CODE"] = gdf["PLANT_CODE"].astype(int)
    merged_gdf = gdf.merge(df, left_on="PLANT_CODE", right_on="Facility ID")

    outdir = os.path.join("..", "plant_locations", f"Fossil_Fuels_{year}")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    merged_gdf.to_file(os.path.join(outdir, f"Fossil_Fuels_{year}.shp"))
