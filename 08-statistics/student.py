import pandas as pd
import sys
import json

df = pd.read_csv(sys.argv[1])
id = sys.argv[2]
df.rename(columns=lambda x: x[-2:] if x[-2:].isdigit() else x, inplace=True)
df = df.groupby(axis=1, level=0).sum()
df = df.reindex(sorted(df.columns), axis=1)
if id == "average":
    df = df.drop(columns = "student").mean(axis=0)
elif id.isdigit():
    df = df.loc[df.student == int(id)].drop(columns = "student").sum(axis=0) # Just to get the same shape of dataframe
else:
    raise ValueError("Unrecognized id")

d = {"mean" : df.mean(), "median" : df.median(), "total" : df.sum(), "passed" : float(df.astype(bool).sum(axis=0))}
print(json.dumps(d, indent=4, ensure_ascii = False))