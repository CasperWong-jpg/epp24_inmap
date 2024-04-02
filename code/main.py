import geopandas as gpd
import os
import pandas as pd
from shapely.geometry import Point
from relevant_plant_codes import relevant_plant_codes
from run_sr import run_sr

"""
See example (Chicago) here:
https://geopandas.org/en/stable/docs/user_guide/mapping.html
"""

# TODO: add relevant CSVs
inputs = [f"Fossil_Fuels_{i}" for i in range(2001, 2018)]
filetype = "shp"


def automate_run_sr(inputs, filetype):
    for i in inputs:
        if filetype == "csv":
            data = gpd.read_file(os.path.join("..", "data", i) + ".csv", encoding='utf-8')
            data['geometry'] = [Point(xy) for xy in zip(data.longitude, data.latitude)]
            gdf = gpd.GeoDataFrame(data, geometry=data['geometry'], crs="EPSG:4326")
            emis = gdf[['NOx', 'SOx', 'geometry']]  # necessary columns to make it run with inmap
        elif filetype == "shp":
            gdf = gpd.read_file(os.path.join("..", "data", i, i) + ".shp")
            emis = gdf[['PLANT_CODE', 'SO2 Mass (', 'NOx Mass (', 'geometry']].rename(
                columns={"SO2 Mass (": "SOx", 'NOx Mass (': "NOx"})
            # Filter to only include subset of plant code
            emis = emis[emis["PLANT_CODE"].isin(relevant_plant_codes)].reset_index().drop(columns=["index"])

        pd.options.mode.chained_assignment = None  # Turn off warnings for this section
        emis['SOx'] = emis['SOx'].astype(float)
        emis['NOx'] = emis['NOx'].astype(float)

        emis['PM2_5'] = 0  # WARNING: I set the other pollutants to 0. Confirm this is what we want
        emis['VOC'] = 0
        emis['NH3'] = 0
        pd.options.mode.chained_assignment = 'warn'

        # Run InMAP and see results
        resultsISRM = run_sr(emis, model="isrm", emis_units="tons/year")
        print("Results:")
        print(resultsISRM.head())  # we see the first few rows of output

        outdir = os.path.join("..", "output", i)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        resultsISRM.to_file(os.path.join(outdir, i) + ".shp")

        # import matplotlib.pyplot as plt
        # resultsISRM.plot()
        # plt.show()


if __name__ == '__main__':
    automate_run_sr(inputs, filetype)
