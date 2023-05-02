import time,sys
import pandas as pd
start_time = time.time()
ESP=sys.argv[1]
import re
def out(x,name):
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    SCHEDULE=[]
    APPL_SCHEDULE=""
    for i, line in enumerate(x):
        for job_type in JOB_TYPES:
            if re.findall('^[ ]+'+job_type,line):
                JOBS.append(line[line.find(job_type)+len(job_type):-1].strip().split()[0])
                SCHEDULE.append("")
                for j in x[i:]:
                    if re.findall("^[ ]+RUN ", j) :
                        SCHEDULE[-1]=j[j.find('RUN')+len('RUN '):].strip()
                    if re.findall("^  ENDJOB",j):
                        break
        if re.findall('^  SCHED_RBC',line):
            for j in x[i:]:
                APPL_SCHEDULE +=j
                if re.findall('^  ENDDO',j):
                    break
    return JOBS,SCHEDULE,APPL_SCHEDULE
def APPL_DETAILS(original,name,dictonary_with):
    appl=[]
    line_number=-1
    JOBS=[]
    SCHEDULE=[]
    APPL_SCHEDULE=""
    line_number=dictonary_with.get("./ ADD    NAME="+name)
    appl=list(dictonary_with.values())
    if appl[-1]==line_number and line_number>0:
        x = original[line_number+1:]
        o=out(x,name)
        JOBS =o[0]
        SCHEDULE=o[1]
        APPL_SCHEDULE=o[2]
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        x = original[line_number:next_index]
        o=out(x,name)
        JOBS =o[0]
        SCHEDULE=o[1]
        APPL_SCHEDULE=o[2]
    return JOBS,SCHEDULE,APPL_SCHEDULE
original=[]
with open(ESP, 'r') as fp:
    original=fp.readlines()
df= pd.DataFrame(original, columns= ['Lines']).replace('\n','', regex= True)
appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
#appls_df.to_excel("appls_df.xlsx")
appl_names=list(appls_df.Lines)
appl_index=list(appls_df.index)
dictonary_with=dict(zip(appl_names,appl_index))
l=list([str(line)[str(line).find("=")+1:] for line in appl_names])            
esp_df = []

for name in l:
    APPL_=APPL_DETAILS(original,name,dictonary_with)
    for i,a in enumerate(APPL_[0]):
        if i==0:
            esp_df.append([name,APPL_[2],a,APPL_[1][i]])
        else:
            esp_df.append([name,'',a,APPL_[1][i]])  
esp_df=pd.DataFrame(esp_df,columns = ['APPL Name', 'Schedule at APPL level', 'Job Name', 'Schedule at JOB level']) 
with pd.ExcelWriter('ESP_SCHEDULE_Output.xlsx') as writer:
   esp_df.to_excel(writer, sheet_name='ESP-Schedules',index=False)
print("--- %s seconds ---" % (time.time() - start_time))