import numpy as np
import pandas as pd
import os

filelist = os.listdir()
textlist = []
for filename in filelist:
    if ".txt" in filename:
        textlist.append(filename)

df  = pd.DataFrame()
for filename in textlist:
    text = open(filename).read()
    newline = pd.DataFrame([[filename,text]])
    df = df.append(newline)

df.rename(columns={0:"button name",1:"text"},inplace = True)
df.set_index("button name", inplace = True)

df.to_excel('help_text.xlsx')