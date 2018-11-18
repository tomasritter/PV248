import pandas as pd
import sys
from math import ceil,isinf
import json
import numpy as np
from datetime import datetime as dt

def predict_date(points, ordinal_startdate, slope):
    return "inf" if slope == 0.0 else str(dt.fromordinal(ordinal_startdate + ceil(points / slope)).date())

df = pd.read_csv(sys.argv[1])
id = sys.argv[2]
ordinal_startdate = dt.strptime("2018-09-17",'%Y-%m-%d').date().toordinal()

if id == "average":
    df = df.drop(columns = "student").mean(axis=0)
elif id.isdigit():
    df = df.loc[df.student == int(id)].drop(columns = "student").sum(axis=0) # Just to get the same shape of dataframe
else:
    raise ValueError("Unrecognized id")

df_e = df.rename(index=lambda x: x[-2:]) # Data set of exercises
df_e = df_e.groupby(axis=0, level=0).sum()

df_d = df.rename(index=lambda x: x[:10]) # Data set of dates
df_d = df_d.groupby(axis=0, level=0).sum()
df_d = df_d.reindex(sorted(df_d.index), axis=0).cumsum()

values = df_d.values
dates = np.array([dt.strptime(x,'%Y-%m-%d').date().toordinal() - ordinal_startdate  \
         for x in df_d.index])

dates = dates[:, np.newaxis]
lm = np.linalg.lstsq(dates, values, rcond=None)[0]

d = {"mean" : df_e.mean(), "median" : df_e.median(), "total" : df_e.sum(), "passed" : int(df_e.astype(bool).sum(axis=0)),\
     "regression slope" : lm[0], "date 16" : predict_date(16, ordinal_startdate, lm),\
     "date 20" : predict_date(20, ordinal_startdate, lm)}

print(json.dumps(d, indent=4, ensure_ascii = False))