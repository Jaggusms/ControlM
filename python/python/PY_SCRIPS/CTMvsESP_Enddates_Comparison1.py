import sys,re
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as et
from collections import Counter

if len(sys.argv)!=5:
    print("please pass correct params")
    sys.exit(1)
xml_file,esp_file,imp_jobs_file,appl_rename_file=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
if ["xml","txt","xlsx","xlsx"]!=[xml_file.split(".")[1].lower(),esp_file.split(".")[1].lower(),imp_jobs_file.split(".")[1].lower(),appl_rename_file.split(".")[1].lower()]:
    print("Please pass valide params 1. xml_file 2. esp_file 3. imp_jobs_file 4. appl_rename_file")
    sys.exit(1)

print("Program Executing Please wait!")
start=datetime.now()

#xml data reading  
def RBC1(RBC):
    ACTIVE_FROM_RBC_NAME={}
    ACTIVE_TILL_RBC_NAME={}
    for a in RBC:
        ACTIVE_TILL=a.attrib.get("ACTIVE_TILL","")
        ACTIVE_FROM=a.attrib.get("ACTIVE_FROM","")
        ACTIVE_FROM_RBC_NAME[a.get("NAME","")]=ACTIVE_FROM
        ACTIVE_TILL_RBC_NAME[a.get("NAME","")]=ACTIVE_TILL
    return ACTIVE_FROM_RBC_NAME,ACTIVE_TILL_RBC_NAME

#xml data reading  
def xml_data(xml_file):
    parsexml=et.parse(xml_file)
    root=parsexml.getroot()
    xml_folder_data=[]
    xml_jobs_data=[]
    for r in root:
        Folder_name=r.attrib.get('FOLDER_NAME',"")
        RULE_BASED_CALENDAR=r.findall('RULE_BASED_CALENDAR')
        rbc=RBC1(RULE_BASED_CALENDAR)
        xml_folder_data.append([Folder_name,rbc[0],rbc[1]])
        for r1 in r.findall("./SMART_FOLDER/SUB_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                xml_jobs_data.append([Folder_name,j.attrib.get("JOBNAME",""),j.attrib.get("ACTIVE_FROM",""),j.attrib.get("ACTIVE_TILL","")])

        for r1 in r.findall("./SMART_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                xml_jobs_data.append([Folder_name,j.attrib.get("JOBNAME",""),j.attrib.get("ACTIVE_FROM",""),j.attrib.get("ACTIVE_TILL","")])
        JOB=r.findall('JOB')
        for j in JOB:
            xml_jobs_data.append([Folder_name,j.attrib.get("JOBNAME",""),j.attrib.get("ACTIVE_FROM",""),j.attrib.get("ACTIVE_TILL","")])
    return xml_folder_data,xml_jobs_data

#xml data reading  
xml_folder_data,xml_jobs_data=xml_data(xml_file)  
xml_folder_data=pd.DataFrame(xml_folder_data,columns=["Folder_Name","ACTIVE_FROM","ACTIVE_TILL"])
xml_folder_data["Folder_Name"]=xml_folder_data["Folder_Name"].apply(lambda x: x.replace(".","_").replace(" ","_").upper())
xml_folder_data["ACTIVE_FROM1"]=xml_folder_data["ACTIVE_FROM"].apply(lambda x:"".join(list(x.values())))
xml_folder_data["ACTIVE_TILL1"]=xml_folder_data["ACTIVE_TILL"].apply(lambda x:"".join(list(x.values())))

xml_folder_data_ACTIVE_FROM=xml_folder_data[xml_folder_data.ACTIVE_FROM1 !=""].iloc[:,:2]
xml_folder_data_ACTIVE_TILL=xml_folder_data[xml_folder_data.ACTIVE_TILL1 !=""].iloc[:,[0,2]]
# xml_folder_data_ACTIVE_FROM.to_excel("xml_folder_data_ACTIVE_FROM.xlsx",index=False)
# xml_folder_data_ACTIVE_TILL.to_excel("xml_folder_data_ACTIVE_TILL.xlsx",index=False)

#print(xml_folder_data_ACTIVE_FROM.iloc[:5,:])
#print(xml_folder_data_ACTIVE_TILL.iloc[:5,:])
xml_jobs_data=pd.DataFrame(xml_jobs_data,columns=["Folder_Name","XML_JOBNAME","ACTIVE_FROM","ACTIVE_TILL"])
for i in xml_jobs_data.columns[[0,2]]:
    xml_jobs_data[i]=xml_jobs_data[i].apply(lambda x: x.replace(".","_").replace(" ","_").upper())
xml_jobs_data_ACTIVE_FROM=xml_jobs_data[xml_jobs_data.ACTIVE_FROM !=""].iloc[:,:-1]
xml_jobs_data_ACTIVE_TILL=xml_jobs_data[xml_jobs_data.ACTIVE_TILL !=""].iloc[:,[0,1,3]]
#print(xml_jobs_data_ACTIVE_FROM.iloc[:5,:])
#print(xml_jobs_data_ACTIVE_TILL.iloc[:5,:])


#esp data reading  
def out(x,name):
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    idx=[]
    jobs_date=[]
    for i,line in enumerate(x):
        line_string=line.strip().split()
        try:
            job_type=line_string[0]
        except:
            job_type=" "
            pass
        if job_type in JOB_TYPES:
            idx.append(i)
            JOBS.append(line_string[1].split(".")[0])
            jobs_string="".join(x[i:])
            jobs_string=jobs_string[:jobs_string.find("ENDJOB")] 
            if "IF DAYS_TO" in jobs_string:
                date=re.findall("\('([A-Za-z0-9,' ]+)'\)",jobs_string[jobs_string.find("IF DAYS_TO")+len("IF DAYS_TO")-1:])
                jobs_date.append(date[0] if date else "")
            else:
                jobs_date.append("")            
    folder_rbcname_date={} 
    if_days_string="".join(x[:0 if len(idx)==0 else idx[0]]) 
    if "IF DAYS_TO" in if_days_string:
        if_days_string=if_days_string
        rbc_name=[i[i.find("SCHED_RBC_"+name+"_")+len("SCHED_RBC_"+name+"_"):-1] for i in list(Counter(re.findall("SCHED_RBC_"+name+"_[A-Za-z\#_ .0-9]+"+"=",if_days_string)))]
        date=re.findall("\('([A-Za-z0-9,' ]+)'\)",if_days_string[if_days_string.find("IF DAYS_TO")+len("IF DAYS_TO")-1:])
        folder_rbcname_date=dict(zip(rbc_name,date))
    return JOBS,folder_rbcname_date,jobs_date
original=[]
#esp data reading 
with open(esp_file, 'r') as fp:
    original=fp.readlines()
dfe= pd.DataFrame(original, columns= ['Lines'])
df=dfe[dfe.Lines.str.contains('ADD    NAME|AIX_JOB|EXTERNAL |JOB|APPLSTART|DBSP_JOB|FILE_TRIGGER|LINUX_JOB|NT_JOB|INFORMATICA_JOB|SPARK_JOB|IF DAYS_TO|SCHED_RBC')]
df=df[df.Lines.str.contains('\/\*|%ESPAPPL|APPLEND|APPLSTRT|MULTSETR| TAIL_JOB|_OC -|ESPNOMSG|APPLUNTIL| EXTERNAL ')==False].replace('\n','', regex= True).reset_index(drop=True)
original=list(df.Lines)
appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
appl_names=list(appls_df.Lines)
appl_index=list(appls_df.index)
dictonary_with=dict(zip(appl_names,appl_index))
l=list([str(line)[str(line).find("=")+1:] for line in appl_names]) 
#esp data reading 
def APPL_DETAILS(original,name,dictonary_with):
    appl,line_number=[],-1
    line_number=dictonary_with.get("./ ADD    NAME="+name)
    appl=list(dictonary_with.values())
    if appl[-1]==line_number and line_number>0:
        return out(original[line_number+1:],name)   
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        return out(original[line_number:next_index],name)
folder_esp_data=[]
jobs_esp_data=[]
#esp data reading 
def data(l,original,dictonary_with):
    for name in l:
        APPL_=APPL_DETAILS(original,name,dictonary_with)
        folder_esp_data.append([name,APPL_[1]])
        for idx,jobs in enumerate(APPL_[0]):
            jobs_esp_data.append([name,jobs,APPL_[2][idx]])
#l=['BPPIET36','BPPICI68','BPPICI68','BPPIXT70','BPPIMCMB','BPPIPC69','BPNGCA10','BPPITGED','BPCVHMH2','BPCVVSH2','BPCVVAH3','BPCVHCH1','BPCVHMH3']
#esp data reading 
data(l,original,dictonary_with)
esp_folder_data=pd.DataFrame(folder_esp_data,columns=["APPL_NAME","RBC_NAME_Dates"])
esp_jobs_data=pd.DataFrame(jobs_esp_data,columns=["APPL_NAME","ESP_JOBNAME","jobs_date"])
# esp_folder_data.to_excel("esp_folder_data.xlsx",index=False)
# esp_jobs_data.to_excel("esp_jobs_data.xlsx",index=False)

dates_esp_folder=esp_folder_data[(esp_folder_data.RBC_NAME_Dates.str.len() !=0) ]
dates_esp_jobs=esp_jobs_data[esp_jobs_data.jobs_date !=""]
dates_dict={"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06","JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}
dates_esp_jobs["jobs_date"]=dates_esp_jobs["jobs_date"].apply(lambda value:value[-4:]+dates_dict.get(value[:3])+(("0"+value[4]) if value[5]=="," else value[4:6]))
#print(dates_esp_folder.iloc[:5,:])
#print(dates_esp_jobs.iloc[:5,:])

#imp_jobs_data reading 
def imp_jobs_data(imp_jobs_file):
    Impacted=pd.read_excel(imp_jobs_file,sheet_name=0,usecols="E,F,H").fillna("")
    for c in Impacted.columns:
        Impacted[c]=Impacted[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
    Impacted=Impacted.drop_duplicates().reset_index(drop=True)
    Impacted['F_J']=Impacted[Impacted.columns[0]]+Impacted[Impacted.columns[1]]
    return Impacted
imp_jobs_data_updated=imp_jobs_data(imp_jobs_file)
#print(imp_jobs_data_updated.iloc[:5,:])



#appl_rename_data reading
def appl_rename_data(appl_rename_file):
    appl_rename=pd.read_excel(appl_rename_file,sheet_name=0,usecols='H,K').fillna("")
    for c in appl_rename.columns:
        appl_rename[c]=appl_rename[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
    appl_rename=appl_rename.drop_duplicates().reset_index(drop=True)
    return appl_rename
appl_rename_updated=appl_rename_data(appl_rename_file)
appl_rename_columns=appl_rename_updated.columns
appl_rename_updated=appl_rename_updated.rename(columns={appl_rename_columns[0]:"Folder_Name",appl_rename_columns[1]:"APPL_NAME"})
#print(appl_rename_updated.iloc[:5,:])

xml_fd_ATL_rename=pd.merge(xml_folder_data_ACTIVE_TILL,appl_rename_updated, on="Folder_Name",how="left").fillna("")
esp_xml_fd_ATL_rename=pd.merge(dates_esp_folder,xml_fd_ATL_rename,on="APPL_NAME",how="outer").fillna("")
#esp_xml_fd_ATL_rename.to_excel("esp_xml_fd_ATL_rename.xlsx",sheet_name="esp_xml_fd_ATL_rename",index=False)
def dict_string_sortig(d,dates_dict):
    new_dict={}
    if type(d)==dict:
        for key,value in d.items():
            new_dict[key]=value[-4:]+dates_dict.get(value[:3])+(("0"+value[4]) if value[5]=="," else value[4:6])
        return dict(sorted(new_dict.items(),key= lambda x:x[0]))
    else:
        return ""
esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[1]]=esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[1]].apply(dict_string_sortig,dates_dict=dates_dict)
def dict_string_replacing(d):
    new_dict={}
    if type(d)==dict:
        for key,value in d.items():
            key=key.replace("-","_")
            new_dict[key]=value
        return dict(sorted(new_dict.items(),key= lambda x:x[0]))
    else:
        return ""
esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[3]]=esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[3]].apply(dict_string_replacing)
esp_xml_fd_ATL_rename["MATCHED"]=(esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[1]]==esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[-1]])




imp_jobs_data_updated=imp_jobs_data_updated.rename(columns={imp_jobs_data_updated.columns[0]:"Folder_Name"})
def impact_matching(Impacted,mathing_df,indexes=[0,1]):
    new_jobs_with_impacted=[]
    for idx,row in mathing_df[mathing_df.columns[indexes]].iterrows():
        if len(row[1])<56:
            new_jobs_with_impacted.append(row[1])
        else:
            new_jobs_with_impacted.append(dict(zip(list(Impacted[Impacted.columns[3]]),list(Impacted[Impacted.columns[2]]))).get(row[0]+row[1],""))
    return new_jobs_with_impacted

xml_jobs_data_ACTIVE_TILL['new_jobs_with_Impacted']=impact_matching(imp_jobs_data_updated,xml_jobs_data_ACTIVE_TILL,indexes=[0,1])
xml_jobs_data_ACTIVE_TILL=pd.merge(xml_jobs_data_ACTIVE_TILL,appl_rename_updated, on="Folder_Name",how="left").fillna("")
xml_jobs_data_ACTIVE_TILL.loc[:,"A_J"]=xml_jobs_data_ACTIVE_TILL[xml_jobs_data_ACTIVE_TILL.columns[4]]+xml_jobs_data_ACTIVE_TILL[xml_jobs_data_ACTIVE_TILL.columns[1]]
#xml_jobs_data_ACTIVE_TILL.to_excel("xml_jobs_data_ACTIVE_TILL.xlsx",sheet_name="esp_xml_fd_ATL_rename",index=False)

dates_esp_jobs.loc[:,'A_J']=dates_esp_jobs[dates_esp_jobs.columns[0]]+dates_esp_jobs[dates_esp_jobs.columns[1]]
#dates_esp_jobs.to_excel("dates_esp_jobs.xlsx",sheet_name="dates_esp_jobs",index=False)

xml_jobs_till_esp=pd.merge(xml_jobs_data_ACTIVE_TILL,dates_esp_jobs,on="A_J",how="outer").fillna("")
xml_jobs_till_esp=xml_jobs_till_esp.drop("A_J",axis=1)
xml_jobs_till_esp["APPL_NAME"]=[a if a==b else a if a !="" else b for a,b in zip(xml_jobs_till_esp[xml_jobs_till_esp.columns[4]],xml_jobs_till_esp[xml_jobs_till_esp.columns[4]])]
xml_jobs_till_esp=xml_jobs_till_esp.drop(xml_jobs_till_esp.columns[[4,5]],axis=1)
#xml_jobs_till_esp=xml_jobs_till_esp.rename(xml_jobs_till_esp.columns[]:"")
#xml_jobs_till_esp[xml_jobs_till_esp.columns[-2]]=xml_jobs_till_esp[xml_jobs_till_esp.columns[-2]].apply(lambda value:value[-4:]+dates_dict.get(value[:3])+(("0"+value[4]) if value[5]=="," else value[4:6]))
xml_jobs_till_esp["MATCHED"]=(xml_jobs_till_esp[xml_jobs_till_esp.columns[2]]==xml_jobs_till_esp[xml_jobs_till_esp.columns[-2]])



with pd.ExcelWriter("CTMvsESP_Enddates_Comparison_Output.xlsx") as w:
    esp_xml_fd_ATL_rename.to_excel(w,sheet_name="Folder_active_till",index=False)
    xml_jobs_till_esp.to_excel(w,sheet_name="Job_active_till",index=False)
    xml_folder_data_ACTIVE_FROM.to_excel(w,sheet_name="Folder_active_FROM",index=False)
    xml_jobs_data_ACTIVE_FROM.to_excel(w,sheet_name="Job_active_FROM",index=False)
print(f"Competed in HH/MM/Sec/Milli Sec {datetime.now()-start}")