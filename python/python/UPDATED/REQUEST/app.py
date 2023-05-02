from datetime import datetime
from itertools import count
import sys
import pandas as pd
import xml.etree.ElementTree as et
pd.options.mode.chained_assignment = None
pd.set_option("display.max_colwidth", 10000)

if len(sys.argv)!=5:
    print("please pass correct params")
    sys.exit(1)
xml_file,esp_file,imp_jobs_file,appl_rename_file=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
if not (xml_file.endswith(".xml")or esp_file.endswith(".txt") or imp_jobs_file.endswith(".xlsx") or appl_rename_file.endswith(".xlsx")):
    print("Please pass valide params 1. xml_file 2. esp_file 3. imp_jobs_file 4. appl_rename_file")
    sys.exit(1)
print("Program Executing Please wait!")
start=datetime.now()


class DUMMY_JOBS_COMAPARISIONS:
    def __init__(self,xml_file,esp_file,imp_jobs_file,appl_rename_file):
       self.xml_file=xml_file
       self.esp_file=esp_file
       self.imp_jobs_file=imp_jobs_file
       self.appl_rename_file=appl_rename_file
    def xml(self):
        parsexml=et.parse(self.xml_file)
        root=parsexml.getroot()
        xml=[]
        for r in root:
            JOB=r.findall('JOB')
            for j in JOB:
                xml.append([j.attrib.get("PARENT_FOLDER",""),j.attrib.get("JOBNAME",""),j.attrib.get("TASKTYPE","")])
        for r1 in root.findall("./SMART_FOLDER/SUB_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                xml.append([j.attrib.get("PARENT_FOLDER",""),j.attrib.get("JOBNAME",""),j.attrib.get("TASKTYPE","")])

        for r1 in root.findall("./SMART_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                xml.append([j.attrib.get("PARENT_FOLDER",""),j.attrib.get("JOBNAME",""),j.attrib.get("TASKTYPE","")])
        return xml

    def ESP(self):
        original=[]
        #esp data reading 
        with open(self.esp_file, 'r') as fp:
            original=fp.readlines()
        dfe= pd.DataFrame(original, columns= ['Lines'])
        df=dfe[dfe.Lines.str.contains('ADD    NAME|AIX_JOB|EXTERNAL |JOB|APPLSTART|DBSP_JOB|FILE_TRIGGER|LINUX_JOB|NT_JOB|INFORMATICA_JOB|SPARK_JOB')]
        df=df[df.Lines.str.contains('\/\*|%ESPAPPL|APPLEND|APPLSTRT|MULTSETR| TAIL_JOB|_OC -|ESPNOMSG|APPLUNTIL| EXTERNAL ')==False].replace('\n','', regex= True).reset_index(drop=True)
        #df.to_excel("df.xlsx",sheet_name="esp",index=False)
        original=list(df.Lines)
        appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
        appl_names=list(appls_df.Lines)
        appl_index=list(appls_df.index)
        dictonary_with=dict(zip(appl_names,appl_index))
        l=list([str(line)[str(line).find("=")+1:] for line in appl_names]) 
        return self.data(l,original,dictonary_with)

    def data(self,l,original,dictonary_with):
        jobs_esp_data=[]
        for name in l:
            APPL_=self.APPL_DETAILS(original,name,dictonary_with)
            for idx,jobs in enumerate(APPL_[0]):
                jobs_esp_data.append([name,jobs,APPL_[1][idx]])
        return jobs_esp_data

    def APPL_DETAILS(self,original,name,dictonary_with):
        appl,line_number=[],-1
        line_number=dictonary_with.get("./ ADD    NAME="+name)
        appl=list(dictonary_with.values())
        if appl[-1]==line_number and line_number>0:
            return self.out(original[line_number+1:])   
        if appl[-1]!=line_number and line_number>=0:
            next_index=appl[appl.index(line_number)+1]
            return self.out(original[line_number:next_index])
    def out(self,x):
        JOBS=[]
        JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
        idx=[]
        REQUEST=[]
        for i,line in enumerate(x):
            line_string=line.strip().split()
            try:
                job_type=line_string[0]
            except:
                job_type=" "
                pass
            if job_type in JOB_TYPES:
                idx.append(i)
                j=line_string[1].split(".")[0]
                JOBS.append(j)
                jobs_string="".join(x[i:i+2])
                if " REQUEST" in jobs_string or " REQU-" in jobs_string or " REQUES-" in jobs_string or " REQUE-" in jobs_string or " REQ-" in jobs_string  :
                    REQUEST.append("YES")
                else:
                    REQUEST.append("NO")

        return JOBS,REQUEST

    def imp_jobs_data(self):
        Impacted=pd.read_excel(self.imp_jobs_file,sheet_name=0,usecols="E,F,H").fillna("")
        for c in Impacted.columns:
            Impacted[c]=Impacted[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
        Impacted=Impacted.drop_duplicates().reset_index(drop=True)
        Impacted['F_J']=Impacted[Impacted.columns[0]]+Impacted[Impacted.columns[1]]
        return Impacted
    
    def appl_rename_data(self):
        appl_rename=pd.read_excel(self.appl_rename_file,sheet_name=0,usecols='H,K').fillna("")
        for c in appl_rename.columns:
            appl_rename[c]=appl_rename[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
        appl_rename=appl_rename.drop_duplicates().reset_index(drop=True)
        return appl_rename


object=DUMMY_JOBS_COMAPARISIONS(xml_file,esp_file,imp_jobs_file,appl_rename_file)
xml_data=pd.DataFrame(object.xml(),columns=['PARENT_FOLDER',"JOBNAME_IN_CTM","TASKTYPE"])
xml_data=xml_data[xml_data.TASKTYPE=="Dummy"]
for c in xml_data.columns:
    xml_data[c]=xml_data[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
ESP_data=pd.DataFrame(object.ESP(),columns=['APPL_NAME_ESP',"JOBNAME_IN_ESP","REQUEST"])
ESP_data=ESP_data[ESP_data.REQUEST=="YES"]
for c in ESP_data.columns:
    ESP_data[c]=ESP_data[c].apply(lambda x:x.strip().replace(".","_").replace(" ","_").upper())
ESP_data["A_J"]=ESP_data[ESP_data.columns[0]]+ESP_data[ESP_data.columns[1]]
imp_jobs_data=object.imp_jobs_data()
appl_rename_data=object.appl_rename_data()


def impact_matching(Impacted,mathing_df,indexes=[0,1]):
    new_jobs_with_impacted=[]
    d=dict(zip(list(Impacted[Impacted.columns[3]]),list(Impacted[Impacted.columns[2]])))
    for idx,row in mathing_df[mathing_df.columns[indexes]].iterrows():
        new_jobs_with_impacted.append(d.get(row[0]+row[1],row[1]))
    return new_jobs_with_impacted

xml_data['new_jobs_with_Impacted']=impact_matching(imp_jobs_data,xml_data,indexes=[0,1])
appl_rename_columns=appl_rename_data.columns
appl_rename_updated=appl_rename_data.rename(columns={appl_rename_columns[0]:"PARENT_FOLDER",appl_rename_columns[1]:"APPL_NAME_IN_RENAME"})
xml_data_rename=pd.merge(xml_data,appl_rename_updated, on="PARENT_FOLDER",how="left").fillna("")
xml_data_rename["A_J"]=xml_data_rename[xml_data_rename.columns[-1]]+xml_data_rename[xml_data_rename.columns[3]]

xml_esp=pd.merge(ESP_data,xml_data_rename,on="A_J",how="outer").fillna("")
xml_esp=xml_esp.drop("A_J",axis=1)
xml_esp['MATCHED']=["YES" if "YESDUMMY"==i else 'NO' for i in xml_esp['REQUEST']+xml_esp['TASKTYPE']]

with pd.ExcelWriter("CTMvsESP_TASKTYPE_Comparison_Output"+str(datetime.now().strftime("%H%M%S"))+".xlsx") as w:
    xml_esp.to_excel(w,sheet_name="xml_esp",index=False)
    xml_data_rename.to_excel(w,sheet_name="xml_data",index=False)
    ESP_data.to_excel(w,sheet_name="ESP_data",index=False)
print(f"Competed in HH/MM/Sec/Milli Sec {datetime.now()-start}")