import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

fname = "data/sonoma.csv"

df = pd.read_csv(fname, parse_dates=["DATE"], index_col="DATE")

df_grouped = df.groupby("STATION")

groups = []
for ix, gr in df_grouped:
    groups.append(gr)

hpcp = {}

for data in groups:
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

    hpcp[data["STATION"].iloc[0]] = precip_h

df_qc = pd.concat(hpcp, axis=1)

df_qc.to_csv("sonoma_qc.csv")
