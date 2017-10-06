import collections
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

StationInfo = collections.namedtuple("StationInfo",
                                     ["lat", "lon", "elev", "name"])

def latlon_converter(x):
    if x == 'unknown':
        return np.NaN
    return float(x)

fname = "data/sonoma.csv"

df = pd.read_csv(fname, parse_dates=["DATE"], index_col="DATE")

df_grouped = df.groupby("STATION")

groups = []
for ix, gr in df_grouped:
    groups.append(gr)

hpcp = {}
hpcp_info = {}


for data in groups:

    key = data["STATION"].iloc[0]

    missing_periods=[]
    deleted_periods=[]
    accum_periods=[]
    accum_quantities=[]

    missing = False
    deleted = False
    accum = False

    num_accum = 0
    num_accum_quant = 0
    for ix, row in data.iterrows():
        if missing and row["Measurement Flag"]=="]":
            missing_period[1] = ix
            missing_periods.append(missing_period)
            missing = False
            
        elif not missing and row["Measurement Flag"]=="[":
            missing_period = [ix, None]
            missing = True

        elif deleted and row["Measurement Flag"]=="}":
            deleted_period[1] = ix
            deleted_periods.append(deleted_period)
            deleted = False
            
        elif not accum and row["Measurement Flag"]=="a":
            accum_period = [ix, None]
            accum = True
            num_accum += 1

        elif accum and row["Measurement Flag"]=="A" and row["HPCP"] < 20000:
            accum_period[1] = ix
            accum_periods.append(accum_period)
            accum = False
            accum_quantities.append(row["HPCP"])
            num_accum_quant += 1
            
        elif not deleted and row["Measurement Flag"]=="{":
            deleted_period = [ix, None]
            deleted = True

    precip_h = data["HPCP"].resample("H").sum().fillna(0)

    lat = np.nanmean(map(latlon_converter, np.unique(data["LATITUDE"])))
    lon = np.nanmean(map(latlon_converter, np.unique(data["LONGITUDE"])))
    elev = np.nanmean(map(latlon_converter, np.unique(data["ELEVATION"])))
    name = data["STATION_NAME"].iloc[0]

    hpcp_info[key] = StationInfo(lat=lat, lon=lon, elev=elev, name=name)

    for start, end in missing_periods:
        precip_h.loc[start:end] = np.NaN
    for start, end in deleted_periods:
        precip_h.loc[start:end] = np.NaN
    for start, end in accum_periods:
        precip_h.loc[start:end] = np.NaN

    qf_ix = data.index[np.where((data["Measurement Flag"]=="M") |
                                (data["Measurement Flag"]=="A") |
                                (data["Quality Flag"]=="R") |
                                (data["Quality Flag"]=="Q") |
                                (data["Quality Flag"]=="q"))[0]]
    precip_h.loc[qf_ix] = np.NaN

    hpcp[key] = precip_h

df_qc = pd.concat(hpcp, axis=1)

df_qc.to_csv("sonoma_qc.csv")

station_data = pd.DataFrame.from_records(hpcp_info,
                                         index=StationInfo._fields).T

station_data.to_csv("sonoma_info.csv")
