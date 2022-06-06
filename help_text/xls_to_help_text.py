import numpy as np
import pandas as pd
import os

df = pd.read_excel('help_text.xlsx')
df.set_index('button name',inplace=True)

for filename in df.index.tolist():
    with open(filename, "w") as file:
        file.write(df.loc[filename]['text'])