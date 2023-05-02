
import re
import sys
import pandas as pd
from datetime import datetime
start=datetime.now()
print("Program executing Please wait!")
file=open(sys.argv[1],"r")
data=file.readlines()
file.close()
data=pd.DataFrame(data,columns=["line"])
data=data[data.line.str.contains("\/\*")==False]
count=[]
list_file=open(sys.argv[2],"r")
list_of_events="|".join([i[:-1] for i in list_file.readlines()])
list_file.close()

final_data=[]
# with open(sys.argv[3],"w") as f:
indexs=data.loc[data['line'].str.contains(list_of_events)].index
for idx in indexs:
    sub_data=data.loc[idx:idx+10,'line']
    if ".SNMP" in list(sub_data)[0]:
        new_line=""
        for text in sub_data:
            
            if "XAPPL"in text or "XSUB_APPL" in text or "INVOKE" in text:
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
        if "CALENDAR SYSTEM; EXPECT" in s:
            string=s
        else:
            s=s[:s.find("CALENDAR SYSTEM; ")+len('CALENDAR SYSTEM; ')]+"EXPECT"+s[s.find("CALENDAR SYSTEM; ")+len('CALENDAR SYSTEM; '):]
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
if re.findall('(?i)Dev', ENV):
    REPLACE(final_data,ENV,'P','D',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".DEV.")
elif re.findall('(?i)Sit2', ENV):
    REPLACE(final_data,ENV,'D','2','','','','',"","",".DEV.",".SIT2.")
elif re.findall('(?i)Sit', ENV):
    REPLACE(final_data,ENV,'D','S','','','','',"","",".DEV.",".SIT.")
elif re.findall('(?i)Uat', ENV):
    REPLACE(final_data,ENV,'S','U','','','','',"","",".SIT.",".UAT.")
elif re.findall('(?i)Ir', ENV):
    REPLACE(final_data,ENV,'U','P','','','','',"","",".UAT.",".IR.")
elif re.findall('(?i)Prod', ENV):
    REPLACE(final_data,ENV,'P','P','$ES7','$ES4','SDM7','SDM4',"ESPT.ES7M","ESPP.ES4M",".IR.",".PROD.")
elif re.findall('(?i)Ft', ENV):
    REPLACE(final_data,ENV,'P','F',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".FT.")
else:
    print('Environment not found')
print(f"completed in HH/MM/SS {datetime.now()-start}")