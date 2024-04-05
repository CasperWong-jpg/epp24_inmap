from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import time
import numpy as np
import zarr
from shapely.geometry import Polygon
import pandas as pd
import geopandas as gpd
import s3fs


def rect(i, w, s, e, n):
    x = [w[i], e[i], e[i], w[i], w[i]]
    y = [s[i], s[i], n[i], n[i], s[i]]
    return x, y


def poly(sr):
    ret = []
    w = sr["W"][:]
    s = sr["S"][:]
    e = sr["E"][:]
    n = sr["N"][:]
    for i in range(52411):
        x, y = rect(i, w, s, e, n)
        ret.append(Polygon([[x[0],y[0]],[x[1],y[1]],[x[2],y[2]],
                            [x[3],y[3]],[x[4],y[4]]]))
    return ret


# define the run_sr function
def run_sr(emis, model, crs_coords, emis_units="tons/year"):
    start = time.time()
    url = 's3://inmap-model/isrm_v1.2.1.zarr/'
    fs = s3fs.S3FileSystem(anon=True, client_kwargs=dict(
        region_name='us-east-1'))  # QUESTION: What are the other regions available?
    sr = zarr.open(s3fs.S3Map(url, s3=fs, check=False), mode="r")
    #     the following line is used when we access the SR matrix from local files
    #     sr = zarr.open("isrm_v1.2.1.zarr", mode="r")

    # build the geometry
    p = poly(sr)
    print("Making polygons as geometry.")

    # took the emis geopandas dataframe
    df = pd.DataFrame({'Location': range(52411)})
    gdf = gpd.GeoDataFrame(df, geometry=p)

    # join the emis dataframe into the grid dataframe
    emis.crs = "+proj=longlat"
    gdf.crs = crs_coords

    emis = emis.to_crs(gdf.crs)
    join_right_df = gdf.sjoin(emis, how="right")
    print("Finished joining the dataframes.")

    index = join_right_df.Location.tolist()

    ppl = np.unique(join_right_df.Location.tolist())  # QUESTION: What does ppl stand for in this case?

    num = range(0, len(ppl))

    dictionary = dict(zip(ppl, num))

    SOA = sr['SOA'].get_orthogonal_selection(([0], ppl, slice(None)))
    print("SOA data is allocated.")
    pNO3 = sr['pNO3'].get_orthogonal_selection(([0], ppl, slice(None)))
    print("pNO3 data is allocated.")
    pNH4 = sr['pNH4'].get_orthogonal_selection(([0], ppl, slice(None)))
    print("pNH4 data is allocated.")
    pSO4 = sr['pSO4'].get_orthogonal_selection(([0], ppl, slice(None)))
    print("pSO4 data is allocated.")
    PM25 = sr['PrimaryPM25'].get_orthogonal_selection(([0], ppl, slice(None)))
    print("PrimaryPM25 data is allocated.")

    SOA_data, pNO3_data, pNH4_data, pSO4_data, PM25_data = 0.0, 0.0, 0.0, 0.0, 0.0
    for i in range(len(index)):
        SOA_data += SOA[0, dictionary[index[i]], :] * emis.VOC[i]
        pNO3_data += pNO3[0, dictionary[index[i]], :] * emis.NOx[i]
        pNH4_data += pNH4[0, dictionary[index[i]], :] * emis.NH3[i]
        pSO4_data += pSO4[0, dictionary[index[i]], :] * emis.SOx[i]
        PM25_data += PM25[0, dictionary[index[i]], :] * emis.PM2_5[i]
    data = SOA_data + pNO3_data + pNH4_data + pSO4_data + PM25_data

    print("Accessing the data.")
    if emis_units == "tons/year":
        fact = 28766.639  # QUESTION: Does this change?

    TotalPM25 = fact * data
    TotalPop = sr['TotalPop'][0:52411]
    MortalityRate = sr['MortalityRate'][0:52411]
    deathsK = (np.exp(
        np.log(1.06) / 10 * TotalPM25) - 1) * TotalPop * 1.0465819687408728 * MortalityRate / 100000 * 1.025229357798165
    deathsL = (np.exp(
        np.log(1.14) / 10 * TotalPM25) - 1) * TotalPop * 1.0465819687408728 * MortalityRate / 100000 * 1.025229357798165

    ret = gpd.GeoDataFrame(pd.DataFrame({'SOA': fact * SOA_data,
                                         'pNO3': fact * pNO3_data,
                                         'pNH4': fact * pNH4_data,
                                         'pSO4': fact * pSO4_data,
                                         'PrimaryPM25': fact * PM25_data,
                                         'TotalPM25': TotalPM25,
                                         'deathsK': deathsK,
                                         'deathsL': deathsL}), geometry=p[0:52411])

    print("Finished (%.0f seconds)               " % (time.time() - start))
    return ret
