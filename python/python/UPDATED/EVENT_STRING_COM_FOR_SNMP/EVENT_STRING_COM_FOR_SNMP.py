import sys
import re
from datetime import datetime
TEXT_File=sys.argv[1]
print("Program executing Please wait!")
start=datetime.now()
data=[]
original=[]
data_file = open(TEXT_File)
original=[i for i in data_file]
data_file.close()
count=[]
for i,line in enumerate(original):
    if "/*" not in line and i in count:
        continue
    else:
        if ".SNMP" in line:
            s=""
            for j,line1 in enumerate(original[i:i+15]):
                if "/*" in line1:
                    break
                if j>1 and "EndProc" not in line1 :
                    line2=line1.strip()
                    s +=" COM "+line2.strip("\n")+';'
                elif "EndProc" in line1:
                    s +=line1.strip("\n")+';'
                else:
                    s +=line1.strip("\n")+';'
                count.append(i+j)
            data.append(s)
            s=""
        else:
            s=""
            for j,line1 in enumerate(original[i:i+15]):
                if "/*" in line1:
                    break
                s +=line1.strip("\n")+';'
                count.append(i+j)
            data.append(s)
            s=""
data=[i.strip() for i in data if i!=""]
def savingfile(l1,ENV):
    with open("EVENT_STRING_"+ENV+".txt", 'w') as fp:
        for item in l1:
            fp.write("%s\n" % item)
savingfile(data,"COM_FOR_SNMP")
