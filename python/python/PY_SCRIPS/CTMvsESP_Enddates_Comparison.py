import sys,re
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as et
from collections import Counter

if len(sys.argv)!=1:
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
df=dfe[dfe.Lines.str.contains('ADD    NAME|WAIT')]
df=df[df.Lines.str.contains('\/\*')==False].replace('\n','', regex= True).reset_index(drop=True)
original=list(df.Lines)
appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
appl_names=list(appls_df.Lines)
appl_index=list(appls_df.index)
dictonary_with=dict(zip(appl_names,appl_index))
l=list([str(line)[str(line).find("=")+1:] for line in appl_names]) 
#esp data reading 
def out(x):
    return len(re.findall("WAIT","".join(x).upper()))
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

xml_fd_ATL_rename=pd.merge(xml_folder_data_ACTIVE_TILL,appl_rename_updated, on="Folder_Name",how="left")
esp_xml_fd_ATL_rename=pd.merge(dates_esp_folder,xml_fd_ATL_rename,on="APPL_NAME",how="outer")
#esp_xml_fd_ATL_rename.to_excel("esp_xml_fd_ATL_rename.xlsx",sheet_name="esp_xml_fd_ATL_rename",index=False)
def dict_string_sortig(d,dates_dict):
    new_dict={}
    for key,value in d.items():
        new_dict[key]=value[-4:]+dates_dict.get(value[:3])+(("0"+value[4]) if value[5]=="," else value[4:6])
    return dict(sorted(new_dict.items(),key= lambda x:x[0]))
esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[1]]=esp_xml_fd_ATL_rename[esp_xml_fd_ATL_rename.columns[1]].apply(dict_string_sortig,dates_dict=dates_dict)
def dict_string_replacing(d):
    new_dict={}
    for key,value in d.items():
        key=key.replace("-","_")
        new_dict[key]=value
    return dict(sorted(new_dict.items(),key= lambda x:x[0]))
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