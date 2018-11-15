import pandas as pd
import sys
import json

df = pd.read_csv(sys.argv[1])
mode = sys.argv[2]
df = df.drop(columns = "student")

if mode == "exercises":
    df.rename(columns=lambda x: x[-2:], inplace=True)
    df = df.groupby(axis=1, level=0).sum()   
elif mode == "dates":
    df.rename(columns=lambda x: x[:10], inplace=True)
    df = df.groupby(axis=1, level=0).sum()   
elif mode != "deadlines":
    raise ValueError("Unrecognized mode")
    
dff = pd.concat([df.mean(), df.median(), df.quantile(q=0.25), df.quantile(q=0.75), df.astype(bool).sum(axis=0)], axis=1)
dff.columns=["mean", "median", "first", "last", "passed"]
print(json.dumps(dff.to_dict(orient="index"), indent=4, ensure_ascii = False))