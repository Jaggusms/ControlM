from itertools import count
import sys
import re
import pandas as pd
from datetime import datetime
start=datetime.now()
print("Program executing Please wait!")
#data=[]
file=open(sys.argv[1],"r")
data=file.readlines()
file.close()
data=pd.DataFrame(data,columns=["line"])
data=data[data.line.str.contains("\/\*")==False]
count=[]
with open(sys.argv[2],"w") as f:
    for idx,row in data.iterrows():
        if idx in count:
            continue
        if ".SNMP" in row.line:
            sample=data.loc[idx:idx+7,'line']
            count +=list(sample.index)
            for text in sample:
                if "XAPPL"in text or "XSUB_APPL" in text or "INVOKE" in text:
                    f.write(" COM "+text.strip(" "))
                elif "EndProc" in text:
                    f.write(text)
                    break
                else:
                    f.write(text)
        else:
            f.write(row.line)
print(f"completed in HH/MM/SS {datetime.now()-start}")