import sys
import re
from datetime import datetime
TEXT_File=sys.argv[1]
print("Program executing Please wait!")
start=datetime.now()
data=[]
PROC_XAPPL_XSUBAPPL=[]
Proc_ESPNOMSG=[]
original=[]
data_file = open(TEXT_File)
original=[i for i in data_file]
data_file.close()
count=[]
for i,line in enumerate(original):
    if "/*" not in line and i in count:
        continue
    else:
        s=""
        for j,line1 in enumerate(original[i:i+15]):
            if "/*" in line1:
                break
            s +=line1.strip("\n")+';'
            count.append(i+j)
        if "EndProc" in s and "XAPPL=" in s or "XSUB_APPL=" in s:
            PROC_XAPPL_XSUBAPPL.append(s)
        elif "EndProc" in s and "ESPNOMSG" in s:
            Proc_ESPNOMSG.append(s)
        
        else:
            data.append(s)
        s=""
data=[i.strip() for i in data if i!=""]
def savingfile(l1,ENV):
    with open("EVENT_STRING_"+ENV+".txt", 'w') as fp:
        for item in l1:
            fp.write("%s\n" % item)
savingfile(data,"WITHOUT_PROC") 
savingfile(PROC_XAPPL_XSUBAPPL,"XAPPL_XSUBAPP")
savingfile(Proc_ESPNOMSG,"ESPNOMSG")
