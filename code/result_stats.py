import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

inputs = [f"Fossil_Fuels_{i}" for i in range(2001, 2018)]

for i in inputs:
    resultsISRM = gpd.read_file(os.path.join("..", "output", i, i) + ".shp")

    # resultsISRM.plot()
    # plt.show()

    deaths = pd.DataFrame.from_dict({
        "Model": ["ISRM"],
        "Krewski Deaths": [resultsISRM.deathsK.sum()],
        "LePeule Deaths": [resultsISRM.deathsL.sum()],
    })
    print(f"For year: {i}")
    print(deaths)

    vsl = 9.0e6

    pd.DataFrame.from_dict({
        "Model": ["ISRM"],
        "Krewski Damages": deaths["Krewski Deaths"] * vsl,
        "LePeule Damages": deaths["LePeule Deaths"] * vsl,
    })
