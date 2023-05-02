import sys
import re
TEXT_File,APPLICATION,ENV=sys.argv[1],sys.argv[2],sys.argv[3]
data_file = open(TEXT_File)
data=[i.strip("\n") for i in data_file if i!=""]
data_file.close()
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
    
def DEV(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"D"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES400DP",'ES700DD').replace("SDM4","SDM7").replace("ESPP.ES4M.EDA.DX.PROD","ESPT.ES7M.EDA.DX.DEV").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"DEV")
def SIT(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"S"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES700DD",'ES700DS').replace("ESPT.ES7M.EDA.DX.DEV","ESPT.ES7M.EDA.DX.SIT").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"SIT")
def UAT(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"U"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES700DS",'ES700DU').replace("ESPT.ES7M.EDA.DX.SIT","ESPT.ES7M.EDA.DX.UAT").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"UAT")
def IR(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"P"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES700DU",'ES700DP').replace("ESPT.ES7M.EDA.DX.UAT","ESPT.ES7M.EDA.DX.IR").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"IR")
def PROD(l):
    l1=()
    for i in l:
        s=i.replace("ES700DP","ES400DP").replace("SDM7","SDM4").replace("ESPT.ES7M.EDA.DX.IR","ESPP.ES4M.EDA.DX.PROD")
        l1 +=(string_replacing(s),)
    savingfile(l1,"PROD")
def SIT2(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"2"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES700DD",'ES700D2').replace("ESPT.ES7M.EDA.DX.DEV","'ESPT.ES7M.EDA.DX.SIT2").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"SIT2")
def FT(l):
    l1=()
    for i in l:
        APPL_OLD=i[i.find('.')+1:i.find(")")].strip("CYC_")
        APPL_NEW=APPL_OLD[:1]+"F"+APPL_OLD[2:] if APPL_OLD.startswith('D') else APPL_OLD
        s=i.replace("ES400DP",'ES700DF').replace("SDM4","SDM7").replace("ESPP.ES4M.EDA.DX.PROD","ESPT.ES7M.EDA.DX.FT").replace(APPL_OLD,APPL_NEW)
        l1 +=(string_replacing(s),)
    savingfile(l1,"FT")
         
    
if re.findall('(?i)Dev', ENV):
    DEV(data)
elif re.findall('(?i)Sit2', ENV):
    SIT2(data)
elif re.findall('(?i)Sit', ENV):
    SIT(data)
elif re.findall('(?i)Uat', ENV):
    UAT(data)
elif re.findall('(?i)Ir', ENV):
    IR(data)
elif re.findall('(?i)Prod', ENV):
    PROD(data)
elif re.findall('(?i)Ft', ENV):
    FT(data)
else:
    print('Environment not found')
print("completed")
