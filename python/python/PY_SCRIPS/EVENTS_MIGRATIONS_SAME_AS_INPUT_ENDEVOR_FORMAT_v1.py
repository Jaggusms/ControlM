import re
import sys
import pandas as pd
from datetime import datetime
start=datetime.now()
print("Program executing Please wait!")
try:
    file=open(sys.argv[1],"r")
except :
    print("ESP_REPORT not found")
data=file.readlines()
if len(data)==0:
    print("ESP_REPORT is empty")
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
list_of_event=[i[:-1].upper() for i in list_file.readlines() if len(i.strip())!=0]
list_of_events="|".join(list_of_event)
if len(list_of_events)==0:
    print("we don't have events in list of event file")
    list_file.close()
    sys.exit(1)
list_file.close()
final_data=[]
# with open(sys.argv[3],"w") as f:
indexs=data.loc[data['line'].str.contains(list_of_events)].index
MISSED_EVENT=[]
for event in list_of_event:
    if event not in "".join(list(data.loc[indexs,'line'])):
        MISSED_EVENT.append(event)
if len(MISSED_EVENT)!=0:
    with open("MISS_EVENT.txt","w") as f:
        for i in MISSED_EVENT:
            f.write(i+"\n")
#print("".join(list(data.loc[indexs,'line'])))
for idx in indexs:
    sub_data=data.loc[idx:idx+10,'line']
    if ".SNMP" in list(sub_data)[0]:
        new_line=""
        for text in sub_data:
            
            if "XAPPL"in text or "XSUB_APPL" in text or "INVOKE" in text:
                if "COM" in text:
                    new_line +=" "+text.strip(" ")
                else:
                    new_line +=" COM "+text.strip(" ")
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
                new_line +=text
        final_data.append(new_line)
def savingfile(l1,ENV):
    with open("EVENT_STRING_"+ENV+".txt", 'w') as fp:
        for item in l1:
            fp.write("%s\n" % item)
def string_replacing(s):
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
        APPLNAME_old=re.findall("\(([A-Za-z0-9@#%.]+)\)",i)[-1]
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
        s=string_replacing(s)
        S.append(s)
    savingfile(S,ENV.upper())
ENV=sys.argv[3]
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
elif "FT_PROD"==ENV.upper():
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
else:
    print('Environment not found')
print(f"completed in HH/MM/SS {datetime.now()-start}")



