
import sys
m=sys.argv[1]
ESP=sys.argv[2]
APPL_file=sys.argv[3]
import xml.etree.ElementTree as et
parsexml=et.parse(m)
root=parsexml.getroot()
data=[[ 'PARENT_FOLDER','FOLDER_NAME','RBC','MAXWAIT']]    
for r in root:
    d=r.attrib
    FOLDER_NAME=d['FOLDER_NAME']
    try:
        PARENT_FOLDER=d['PARENT_FOLDER']
    except:
        PARENT_FOLDER=FOLDER_NAME
        pass
    RBC=r.findall('RULE_BASED_CALENDAR')
    if not RBC:
        data.append([PARENT_FOLDER,FOLDER_NAME,"",""])
    for a in RBC:
        value=list(a.attrib.values())
        data.append([PARENT_FOLDER,FOLDER_NAME,value[0],value[1]])
        
for r1 in root.findall("./SMART_FOLDER/"):
    JOB=r1.findall('JOB')
    for r in JOB:
        d=r.attrib
        JOBNAME=d['JOBNAME']       
        PARENT_FOLDER=d['PARENT_FOLDER'].split("/")[0]
        KEEPACTIVE=d['MAXWAIT']
        data.append([PARENT_FOLDER,JOBNAME,"",KEEPACTIVE])
for r1 in root:
    JOB=r1.findall('JOB')
    for r in JOB:
        d=r.attrib
        JOBNAME=d['JOBNAME']       
        PARENT_FOLDER=d['PARENT_FOLDER']
        KEEPACTIVE=d['MAXWAIT']
        data.append([PARENT_FOLDER,JOBNAME,"",KEEPACTIVE])
import pandas as pd
df1 = pd.DataFrame(columns=data[0], data=data[1:])
appl_name = pd.read_excel(APPL_file,sheet_name=0,usecols="H,K")
appl_name=appl_name.rename(columns={appl_name.columns[0]:"PARENT_FOLDER"})
new = pd.merge(df1, appl_name, on='PARENT_FOLDER', how='outer').fillna("")
new['max_keep_active']=['']*len(new.index)
new['max_keep_active_JOB']=['']*len(new.index)
new['ESP APPL Name']=['']*len(new.index)
df = pd.DataFrame(columns = new.columns)
grouped_df=new.groupby(['PARENT_FOLDER'])
for key, item in grouped_df:
    df2=grouped_df.get_group(key).reset_index().iloc[:,1:]
    m=['']*len(df2.index)
    job_keep_active=['']*len(df2.index)
    job_keep_active[0]=max([i for i in list(df2[df2.RBC==''].MAXWAIT)  if i!='' ],default='')
    m[0]=max(df2['MAXWAIT'])
    df2['max_keep_active']=m
    df2['max_keep_active_JOB']=job_keep_active
    df2['Both_keepactive_matched']=[int(m[0])==int(job_keep_active[0]) if i==0 and v!="" else v for i,v in enumerate(m)]
    m[0]=df2['APPL Name ( Max 8 Characters)'].loc[0]
    df2['ESP APPL Name']=m
    
    df=pd.concat([df,df2])
df=df.reset_index().iloc[:,1:]
del df['APPL Name ( Max 8 Characters)']
import re
def out(x,name):
    out_put=''
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    notwith_statement=[]
    for i, line in enumerate(x):
        for job_type in JOB_TYPES:
            if re.findall('^[ ]+'+job_type,line):
                JOBS.append(line[line.find(job_type)+len(job_type):-1].strip().split()[0])
                notwith_statement.append(False)
                for j in x[i:]:
                    if "NOTWITH (%ESPAPPL..WITHDRAW/%ESPAPPL) HOLD" in j :
                        notwith_statement[-1]=True
                    if re.findall('^[ ]+ENDJOB',j):
                        break
        if "JOB %ESPAPPL..WITHDRAW" in line:
            for j in range(i+3,i+1000):
                string=x[j]
                if string.find("/*")==-1:
                    out_put +=string
                if string.find("ENDJOB")>=0:
                    out_put +=''
                    break
    DAYS =[i.strip(' DAYS') for i in re.findall('[0-9]+ DAYS', out_put)[:2]]
    NOTWITH =name in [i.strip("-/") for i in re.findall('-/[A-Za-z0-9]+', out_put)]
    
    return out_put,DAYS,NOTWITH,JOBS,notwith_statement
def APPL_DETAILS(name):
    appl=[]
    line_number=-1
    output=''
    DAYS=('','')
    NOTWITH=False
    JOBS=[]
    notwith_statement=[]
    with open(ESP, 'r') as fp:
        original=fp.readlines()
        #last_line_number=len(fp.readlines())
        for l_no, line in enumerate(original):
            if './ ADD    NAME='+ name in line:
                line_number=l_no
            if './ ADD    NAME=' in line:
                appl.append(l_no)
        if appl[-1]==line_number and line_number>0:
            x = original[line_number+1:]
            o=out(x,name)
            output +=o[0]
            DAYS=o[1]
            NOTWITH=o[2]
            JOBS=o[3]
            notwith_statement=o[4]
        if appl[-1]!=line_number and line_number>=0:
            next_index=appl[appl.index(line_number)+1]
            x = original[line_number:next_index]
            o=out(x,name)
            output +=o[0]
            DAYS=o[1]
            NOTWITH=o[2]
            JOBS=o[3]
            notwith_statement=o[4]
    return output,DAYS,NOTWITH,JOBS,notwith_statement
l=[]
with open(ESP, 'r') as fp:
    original=[line for line in fp.readlines() if "/*" not in line and len(line.strip())!=0]
    #last_line_number=len(fp.readlines())
    for l_no, line in enumerate(original):
        if './ ADD    NAME=' in line:
            name=line.strip("./ ADD    NAME=")
            name=name.strip()
            l.append(name)
esp_df = pd.DataFrame(columns = ['APPL Name ( Max 8 Characters)','WITHDRAW Job Text','DELAYSUB or EARLYSUB','ABANDON DEPENDENCIES',' NOTWITH (-/'])
esp_df1=pd.DataFrame(columns =['APPL Name','Job Name','NOTWITH (%ESPAPPL..WITHDRAW/%ESPAPPL) HOLD'])
for name in l:
    APPL_=APPL_DETAILS(name)
    if len(APPL_[1])!=2:
        esp_df.loc[len(esp_df.index)]=[name,str(APPL_[0]),'','',APPL_[2]]
        for a,i in enumerate(APPL_[3]):
            if a==0:
                esp_df1.loc[len(esp_df1.index)]=[name,i,APPL_[4][a]]
            else:
                esp_df1.loc[len(esp_df1.index)]=[name,i,APPL_[4][a]]
    else:
        esp_df.loc[len(esp_df.index)]=[name,str(APPL_[0]),APPL_[1][0],APPL_[1][1],APPL_[2]]
        for a,i in enumerate(APPL_[3]):
            if a==0:
                esp_df1.loc[len(esp_df1.index)]=[name,i,APPL_[4][a]]
            else:
                esp_df1.loc[len(esp_df1.index)]=[name,i,APPL_[4][a]]

Keep_active_matching=df.iloc[:,[6,5]][df.iloc[:,[6,5]].max_keep_active_JOB !=""].fillna("")
Keep_active_matching['max_keep_active_JOB_updated']=[int(i)+1 if i!="" else i for i in Keep_active_matching.max_keep_active_JOB ]
esp_df_new=esp_df.iloc[:,[0,2]].rename(columns={"APPL Name ( Max 8 Characters)":"ESP APPL Name"})
Keep_active_matching=pd.merge(Keep_active_matching,esp_df_new,how="left",on="ESP APPL Name").fillna("")
Keep_active_matching["ctm/esp"]=[int(ck)==int(ek) if ck!="" and ek!="" else "FALSE" for ck,ek in zip(list(Keep_active_matching.max_keep_active_JOB_updated),Keep_active_matching['DELAYSUB or EARLYSUB'])]
with pd.ExcelWriter('WITHDRAW_Output.xlsx') as writer:
    df.to_excel(writer, sheet_name='CTM-Output',index=False)
    esp_df.to_excel(writer, sheet_name='ESP--Output',index=False)
    esp_df1.to_excel(writer, sheet_name='ESP-NOTWITH',index=False)
    Keep_active_matching.to_excel(writer, sheet_name='Keep_active_matching',index=False)
print("Completed")
