from tkinter.tix import COLUMN
import pandas as pd
data=pd.read_csv("Retrofit_CrossWalk_File.csv")
COLUMN=data.columns
for i in COLUMN:
    data[i]=data[i].str.strip()
for idx,rows in data.iterrows():
    #print(rows[COLUMN[0]][-3],rows[COLUMN[1]].split(".")[-2],rows[COLUMN[0]][-1],rows[COLUMN[2]].split(".")[-2])
    if rows[COLUMN[1]].split(".")[-2].startswith(rows[COLUMN[0]][-3]) and rows[COLUMN[2]].split(".")[-2].startswith(rows[COLUMN[0]][-1]):
        print(1)
