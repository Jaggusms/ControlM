import sys
import re
from datetime import datetime
TEXT_File,ENV=sys.argv[1],sys.argv[2]
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

if re.findall('(?i)Dev', ENV):
    REPLACE(data,ENV,'P','D',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".DEV.")
elif re.findall('(?i)Sit2', ENV):
    REPLACE(data,ENV,'D','2','','','','',"","",".DEV.",".SIT2.")
elif re.findall('(?i)Sit', ENV):
    REPLACE(data,ENV,'D','S','','','','',"","",".DEV.",".SIT.")
elif re.findall('(?i)Uat', ENV):
    REPLACE(data,ENV,'S','U','','','','',"","",".SIT.",".UAT.")
elif re.findall('(?i)Ir', ENV):
    REPLACE(data,ENV,'U','P','','','','',"","",".UAT.",".IR.")
elif re.findall('(?i)Prod', ENV):
    REPLACE(data,ENV,'P','P','$ES7','$ES4','SDM7','SDM4',"ESPT.ES7M","ESPP.ES4M",".IR.",".PROD.")
elif re.findall('(?i)Ft', ENV):
    REPLACE(data,ENV,'P','F',"$ES4",'$ES7',"SDM4","SDM7","ESPP.ES4M","ESPT.ES7M",".PROD.",".FT.")
else:
    print('Environment not found')
print(f"completed in HH/MM/SS {datetime.now()-start}")