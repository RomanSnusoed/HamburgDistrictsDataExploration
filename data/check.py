import pandas as pd
df = pd.read_csv("data/2022_ready.csv", sep=",", header=0)
print(df.head())