import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

import pydeck as pdk
import h3pandas
import json

inputs = [f"Fossil_Fuels_{i}" for i in range(2001, 2018)]

for i in inputs:
    resultsISRM = gpd.read_file(os.path.join("..", "output", i, i) + ".shp")

    # Stats
    deaths = pd.DataFrame.from_dict({
        "Model": ["ISRM"],
        "Krewski Deaths": [resultsISRM.deathsK.sum()],
        "LePeule Deaths": [resultsISRM.deathsL.sum()],
    })
    print(f"For year: {i}")
    print(deaths)

    # vsl = 9.0e6
    # economic_damages = pd.DataFrame.from_dict({
    #     "Model": ["ISRM"],
    #     "Krewski Damages": deaths["Krewski Deaths"] * vsl,
    #     "LePeule Damages": deaths["LePeule Deaths"] * vsl,
    # })

    # Plots
    # geolist = resultsISRM[["TotalPM25", "geometry"]]
    # res = geolist.h3.polyfill(5)
    # my_data = res.rename(columns={'h3_polyfill': 'hexIds'})[['TotalPM25', 'hexIds']]
    #
    # # Define a layer to display on a map
    # layer = pdk.Layer(
    #     "H3ClusterLayer",
    #     my_data,
    #     pickable=True,
    #     stroked=True,
    #     filled=True,
    #     extruded=False,
    #     get_hexagons="hexIds",
    #     get_fill_color="[255, TotalPM25 / 1.5 * 255, 0, 100]",
    #     get_line_color=[255, 255, 255],
    #     line_width_min_pixels=0,
    # )
    #
    # # Set the viewport location
    # view_state = pdk.ViewState(latitude=37.7749295, longitude=-95.4194155, zoom=2, bearing=0, pitch=30)
    #
    # # Render
    # r = pdk.Deck(layers=[layer], initial_view_state=view_state,
    #              tooltip={"text": "TotalPM25: {TotalPM25}"})
    # r.to_html("h3_cluster_layer.html")
