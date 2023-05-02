import sys,re
from datetime import datetime
import pandas as pd

if len(sys.argv)!=2:
    print("please pass correct params 1. ESP_Report_File")
    sys.exit(1)
esp_file=sys.argv[1]

print("Program Executing Please wait!")
start=datetime.now()

original=[]
#esp data reading 
with open(esp_file, 'r') as fp:
    original=fp.readlines()
dfe= pd.DataFrame(original, columns= ['Lines'])
df=dfe[dfe.Lines.str.contains('ADD    NAME|WAIT|Table Name|AIX_JOB|EXTERNAL |JOB|APPLSTART|DBSP_JOB|FILE_TRIGGER|LINUX_JOB|NT_JOB|INFORMATICA_JOB|SPARK_JOB')].replace('\n','', regex= True).reset_index(drop=True)
original=list(df.Lines)
appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
appl_names=list(appls_df.Lines)
appl_index=list(appls_df.index)
dictonary_with=dict(zip(appl_names,appl_index))
l=list([str(line)[str(line).find("=")+1:] for line in appl_names]) 
#esp data reading 
def out(x):
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    idx=0
    folder_name=""
    for i,line in enumerate(x):
        line_string=line.strip().split()
        try:
            job_type=line_string[0]
        except:
            job_type=" "
            pass
        if job_type in JOB_TYPES:
            idx=i
            break
        if "Table Name" in line:
            folder_name=line.split(":")[1]
            folder_name=folder_name[:folder_name.find("*/")].strip()
    return len(re.findall("  WAIT","".join(x[:idx]).upper())),folder_name
def APPL_DETAILS(original,name,dictonary_with):
    appl,line_number=[],-1
    line_number=dictonary_with.get("./ ADD    NAME="+name)
    appl=list(dictonary_with.values())
    if appl[-1]==line_number and line_number>0:
        return out(original[line_number+1:])   
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        return out(original[line_number:next_index])
wait=[]
#esp data reading 
def data(l,original,dictonary_with):
    for name in l:
        APPL_=APPL_DETAILS(original,name,dictonary_with)
        wait.append([name,APPL_[1],APPL_[0]])
#l=['BPPIET36','BPPICI68','BPPICI68','BPPIXT70','BPPIMCMB','BPPIPC69','BPNGCA10','BPPITGED','BPCVHMH2','BPCVVSH2','BPCVVAH3','BPCVHCH1','BPCVHMH3']
#esp data reading 
data(l,original,dictonary_with)
wait=pd.DataFrame(wait,columns=["APPL_NAME","FOLDER_NAME","wait>2"])
wait=wait[wait["wait>2"]>1]
wait.to_excel("wait.xlsx",sheet_name="WAIT",index=False)

print(f"Competed in HH/MM/Sec/Milli Sec {datetime.now()-start}")