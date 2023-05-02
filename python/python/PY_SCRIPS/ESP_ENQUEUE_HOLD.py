from datetime import datetime
import re
import sys
import pandas as pd
print("Program Executing Please wait!")
start=datetime.now()
ESP=sys.argv[1]
def out(x,name):
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    jobs_enque =[]
    JOBS_HOLD=[]
    for i, line in enumerate(x):
        for job_type in JOB_TYPES:
            if re.findall('^[ ]+'+job_type,line):
                JOBS_HOLD.append("")
                new_line=str(line.strip("\n")+x[i+1].strip("\n")).replace("-","")
                if "HOLD" in new_line:
                    JOBS_HOLD[-1]="HOLD"
                JOBS.append(line[line.find(job_type)+len(job_type):-1].strip().split()[0])
                jobs_enque.append("")
                for j in x[i:]:
                    if re.findall("^[ ]+ENQUEUE ", j) :
                        jobs_enque[-1]=j.strip() 
                    if re.findall("^  ENDJOB",j):
                        break
    appl_ENQUEUE=""
    APPL_HOLD=""
    for line in x[:6]:
        if "ENQUEUE" in line:
            appl_ENQUEUE +=line.strip()
        if "HOLD" in line:
            APPL_HOLD='HOLD'
    return JOBS,jobs_enque,appl_ENQUEUE,APPL_HOLD,JOBS_HOLD
def APPL_DETAILS(original,name):
    appl,line_number,JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD=[],-1,[],[],"","",[]
    for l_no, line in enumerate(original):
        if './ ADD    NAME='+ name in line:
            line_number=l_no
        if './ ADD    NAME=' in line:
            appl.append(l_no)
    if appl[-1]==line_number and line_number>0:
        x = original[line_number+1:]
        o=out(x,name)
        JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD =o[0],o[1],o[2],o[3],o[4]
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        x = original[line_number:next_index]
        o=out(x,name)
        JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD =o[0],o[1],o[2],o[3],o[4]
    return JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD
l=[]
original=[]
with open(ESP, 'r') as fp:
    original=fp.readlines()
    for l_no, line in enumerate(original):
        if './ ADD    NAME=' in line:
            name=line.strip("./ ADD    NAME=")
            name=name.strip()
            l.append(name)            
enque_df=[]
HOLD_df=[]
def data(l):
    for name in l:
        APPL_=APPL_DETAILS(original,name)
        for i,a in enumerate(APPL_[0]):
            if i==0:
                enque_df.append([name,APPL_[2],a,APPL_[1][i]])
                HOLD_df.append([name,APPL_[3],a,APPL_[4][i]])
            else:
                enque_df.append([name,"",a,APPL_[1][i]])
                HOLD_df.append([name,"",a,APPL_[4][i]])
data(l)
enque_df = pd.DataFrame(enque_df,columns = ['APPL Name', 'ENQUEUE at APPL level', 'Job Name', 'ENQUEUE at JOB level'])
HOLD_df=pd.DataFrame(HOLD_df,columns = ['APPL Name', 'HOLD at APPL level', 'Job Name', 'HOLD at JOB level'])
with pd.ExcelWriter('ESP_ENQUEUE_Output.xlsx') as writer:
    enque_df.to_excel(writer, sheet_name='ESP-Control Resource',index=False)
    HOLD_df.to_excel(writer, sheet_name='ESP-HOLD',index=False)
print(f"Competed in DD/HH/MM/Sec {datetime.now()-start}")