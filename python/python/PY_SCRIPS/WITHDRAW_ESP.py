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
for r1 in root:
    SUB_FOLDER=r1.findall('SUB_FOLDER')
    for r in SUB_FOLDER:
        d=r.attrib
        JOBNAME=d['JOBNAME']
        PARENT_FOLDER=d['PARENT_FOLDER']
        KEEPACTIVE=d['MAXWAIT']
        data.append([PARENT_FOLDER,JOBNAME,"",KEEPACTIVE])
        
for r1 in root.findall("./SMART_FOLDER/"):
    JOB=r1.findall('JOB')
    for r in JOB:
        d=r.attrib
        JOBNAME=d['JOBNAME']       
        PARENT_FOLDER=d['PARENT_FOLDER']
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
with pd.ExcelWriter('FOLDER.xlsx') as writer:
    df1.to_excel(writer, sheet_name='output',index=False)
df1['max_keep_active']=['']*len(df1.index)
df = pd.DataFrame(columns = data[0])
grouped_df=df1.groupby(['PARENT_FOLDER'])
for key, item in grouped_df:
    df2=grouped_df.get_group(key).reset_index().iloc[:,1:]
    m=['']*len(df2.index)
    m[0]=max(df2['MAXWAIT'])
    df2['max_keep_active']=m
    df=df.append(df2)
df=df.reset_index().iloc[:,1:]
#df['max_keep_active']=df.groupby(['PARENT_FOLDER'])['MAXWAIT'].transform('max'
folder=df['PARENT_FOLDER']
appl_name = pd.read_excel(APPL_file,usecols="H,K")
appl_name1=appl_name[appl_name['PARENT_FOLDER'].isin(df['PARENT_FOLDER'])]
new = pd.merge(df, appl_name1, on='PARENT_FOLDER', how='inner')
import re
def out(x):
    out_put=''
    for i, line in enumerate(x):
        if "JOB %ESPAPPL..WITHDRAW" in line:
            for j in range(i+3,i+1000):
                string=x[j]
                if string.find("/*")==-1:
                    out_put +=string
                if string.find("ENDJOB")>=0:
                    out_put +=''
                    break
    DAYS =[i.strip(' DAYS') for i in re.findall('[0-9]+ DAYS', out_put)[:2]]
    return out_put,DAYS
def APPL_DETAILS(original,name):
    appl=[]
    line_number=-1
    output=''
    DAYS=('','')    #last_line_number=len(fp.readlines())
    for l_no, line in enumerate(original):
        if './ ADD    NAME='+ name in line:
            line_number=l_no
        if './ ADD    NAME=' in line:
            appl.append(l_no)
    if appl[-1]==line_number and line_number>0:
        x = original[line_number+1:]
        o=out(x)
        output +=o[0]
        DAYS=o[1]
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        x = original[line_number:next_index]
        o=out(x)
        output +=o[0]
        DAYS=o[1]
    return output,DAYS
fp=open(ESP,"r")
original=fp.readlines()
fp.close()
appl_names=tuple(set(new['APPL Name ( Max 8 Characters)']))
esp_df = pd.DataFrame(columns = ['APPL Name ( Max 8 Characters)','ESP Text File','DELAYSUB or EARLYSUB','ABANDON DEPENDENCIES'])
for name in appl_names:
    APPL_=APPL_DETAILS(name)
    if len(APPL_[1])!=2:
        esp_df.loc[len(esp_df.index)]=[name,str(APPL_[0]),'','']
    else:
        esp_df.loc[len(esp_df.index)]=[name,str(APPL_[0]),APPL_[1][0],APPL_[1][1]]

final = pd.merge(new, esp_df, on='APPL Name ( Max 8 Characters)', how='inner')
with pd.ExcelWriter('APPL_Details.xlsx') as writer:
    final.to_excel(writer, sheet_name='output',index=False)
print(1)