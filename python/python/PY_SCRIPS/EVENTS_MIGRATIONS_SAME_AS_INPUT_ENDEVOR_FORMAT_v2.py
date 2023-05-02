import re
import sys
import pandas as pd
from datetime import datetime
start=datetime.now()
print("Program executing Please wait!")
try:
    file=open(sys.argv[1],"r")
except :
    print("ESP Source REPORT not found")
    sys.exit(1)
data=file.readlines()
if len(data)==0:
    print("ESP Source REPORT is empty")
    file.close()
    sys.exit(1)
file.close()
data=pd.DataFrame(data,columns=["line"])
data=data[data.line.str.contains("\/\*")==False]
count=[]

try:
    list_file=open(sys.argv[2],"r")
except :
    print("event list file not found")
    sys.exit(1)
ENV=sys.argv[3]
if ENV.upper() not in ["PROD_DEV","DEV_SIT2","DEV_SIT","SIT_UAT","UAT_IR","IR_PROD","PROD_FT","PROD_SIT","PROD_SIT2","FT_IR","SIT2_IR","SIT_IR"]:
    print()
    sys.exit(1)
data_events=list_file.readlines()
list_of_event_EXCEPT=[i[:-1].upper().split(",")[0] for i in data_events if len(i.strip())!=0 and len(i.split(","))!=1]
list_of_event_EXCEPTS="|".join(list_of_event_EXCEPT)
list_of_event=[i[:-1].upper() for i in data_events if len(i.strip())!=0 and "EXPECT" not in i.upper()]
list_of_events="|".join(list_of_event)
if len(list_of_events)==0:
    print("we don't have events in list of event file")
    list_file.close()
    sys.exit(1)
list_file.close()

# with open(sys.argv[3],"w") as f:
MISSED_EVENT=[]
def checkingEventsInReport(data,list_of_events,list_of_event):
    indexs=data.loc[data['line'].str.contains(list_of_events)].index
    for event in list_of_event:
        if event not in "".join(list(data.loc[indexs,'line'])):
            MISSED_EVENT.append(event)
    return indexs
expect_indexs=checkingEventsInReport(data,list_of_event_EXCEPTS,list_of_event_EXCEPT)
normal_indexs=checkingEventsInReport(data,list_of_events,list_of_event)
ENV=sys.argv[3]
if ENV.upper() not in ["DEV_SIT2","PROD_DEV","DEV_SIT","SIT_UAT","UAT_IR","IR_PROD","PROD_FT","PROD_SIT","PROD_SIT2","FT_IR","SIT2_IR","SIT_IR"]:
    print('Invalid environment for Migration ')
    sys.exit(1)
if len(MISSED_EVENT)!=0:
    with open("MISS_EVENT_"+ENV.upper()+".txt","w") as f:
        for i in MISSED_EVENT:
            f.write(i+"\n")
import numpy as np
def find_indices(list_to_check, item_to_find):
    array = np.array(list_to_check)
    indices = np.where(array == item_to_find)[0]
    return list(indices)

final_data=[]
ENV=sys.argv[3]
def lines(data,indexs,ENV,ex):
    for idx in indexs:
        sub_data=data.loc[idx:idx+10,'line']
        if ".SNMP" in list(sub_data)[0]:
            new_line=""
            for text in sub_data:
                if "XAPPL"in text or "XSUB_APPL" in text or "INVOKE" in text:
                    if  not ENV.upper().endswith("PROD"):
                        if "COM" in text:
                            new_line +=" "+text.strip(" ")
                        else:
                            new_line +=" COM "+text.strip(" ")
                    else:
                        new_line +=text.replace("COM","") 
                elif "EndProc" in text:
                    new_line +=text
                    break
                else:
                    new_line +=text
            final_data.append(new_line)
        else: 
            new_line=""   
            for text in sub_data:
                if "EndProc" in text or "CACHE" in text:
                    new_line +=text
                    break
                else:
                    if ENV.upper().endswith("PROD") and ex==0:
                        new_line +=text.replace(" EXPECT "," ")
                    else:
                        new_line +=text 
            if "CACHE" in new_line and "EXPECT " not in new_line and ex==1 and ENV.upper().endswith("PROD"):
                a_list = list(new_line)
                idx=find_indices(a_list, "\n")
                if len(idx)>3:
                    new_line=new_line[:idx[-3]+1]+" EXPECT"+new_line[idx[-3]+1:]          
            final_data.append(new_line)
lines(data,expect_indexs,ENV,ex=1)
lines(data,normal_indexs,ENV,ex=0)
if len(final_data)==0:
    sys.exit(1)
def savingfile(l1,ENV):
    with open("EVENT_STRING_"+ENV+".txt", 'w') as fp:
        for item in l1:
            fp.write("%s\n" % item)

def string_replacing(s,ENV):
    string=s
    if ENV.startswith("PROD"):
        string=""
        if "CALENDAR SYSTEM" not in s:
                string=s
        else:
            if "CALENDAR SYSTEM" in s and  " EXPECT " in s:
                string=s    
            else:
                s=s[:s.find("CALENDAR SYSTEM")+len('CALENDAR SYSTEM')]+"\n EXPECT"+s[s.find("CALENDAR SYSTEM")+len('CALENDAR SYSTEM')+1:]
                string=s
    return string 
def REPLACE(l,ENV,APC_O,APC_N,ES_O,ES_N,SDM_O,SDM_N,ESPP_O,ESPP_N,ENV_O,ENV_N):
    S=[]
    for i in l:
        APPLNAME_old=[""]+re.findall("\(([A-Za-z0-9@#%.]+)\)",i)
        APPLNAME_old=APPLNAME_old[-1]
        APPLNAME_new=APPLNAME_old
        if APPLNAME_old.startswith("OM") or APPLNAME_old.startswith("S#") and len(APPLNAME_old)<9:
            if APPLNAME_old[2]==APC_O:
                APPLNAME_new=APPLNAME_old[:2]+APC_N+APPLNAME_old[3:]
        elif len(APPLNAME_old)<9 and  not APPLNAME_old.startswith("S"):
            if APPLNAME_old[1]==APC_O:
                APPLNAME_new=APPLNAME_old[:1]+APC_N+APPLNAME_old[2:]
        else:
            APPLNAME_new=APPLNAME_old
        ss=i.split(".")[0]
        ss=ss[:-1]+APC_N
        #s=str(ss+i[len(ss):]).replace("$ES4",'$ES7').replace("SDM4","SDM7").replace("ESPP.ES4M","ESPT.ES7M").replace(".PROD.",".DEV.").replace(APPLNAME_old,APPLNAME_new)
        s=str(ss+i[len(ss):]).replace(ES_O,ES_N).replace(SDM_O,SDM_N).replace(ESPP_O,ESPP_N).replace(ENV_O,ENV_N).replace(APPLNAME_old,APPLNAME_new)
        s=string_replacing(s,ENV.upper())
        S.append(s)
    savingfile(S,ENV.upper())

if "PROD_DEV"==ENV.upper():
    REPLACE(final_data,ENV,'P','D',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".DEV.")
elif "DEV_SIT2"==ENV.upper():
    REPLACE(final_data,ENV,'D','2','','','','',"","",".DEV.",".SIT2.")
elif "DEV_SIT"==ENV.upper():
    REPLACE(final_data,ENV,'D','S','','','','',"","",".DEV.",".SIT.")
elif "SIT_UAT"==ENV.upper():
    REPLACE(final_data,ENV,'S','U','','','','',"","",".SIT.",".UAT.")
elif "UAT_IR"==ENV.upper():
    REPLACE(final_data,ENV,'U','P','','','','',"","",".UAT.",".IR.")
elif "IR_PROD"==ENV.upper():
    REPLACE(final_data,ENV,'P','P','$ES7','$ES4','SDM7','SDM4',"ESPT.ES7M","ESPP.ES4M",".IR.",".PROD.")
elif "PROD_FT"==ENV.upper():
    REPLACE(final_data,ENV,'P','F',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".FT.")
elif "PROD_SIT"==ENV.upper():
    REPLACE(final_data,ENV,'P','S',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".SIT.")
elif "PROD_SIT2"==ENV.upper():
    REPLACE(final_data,ENV,'P','2',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".SIT2.")
elif "FT_IR"==ENV.upper():
    REPLACE(final_data,ENV,'F','P','','','','',"","",".FT.",".IR.")
elif "SIT2_IR"==ENV.upper():
    REPLACE(final_data,ENV,'2','P','','','','',"","",".SIT2.",".IR.")
elif "SIT_IR"==ENV.upper():
    REPLACE(final_data,ENV,'S','P','','','','',"","",".SIT.",".IR.")
print(f"completed in HH/MM/SS {datetime.now()-start}")



