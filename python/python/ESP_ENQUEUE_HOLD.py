from datetime import datetime
import re
from tkinter import ON
import xml.etree.ElementTree as et
import sys
import pandas as pd
print("Program Executing Please wait!")
start=datetime.now()
ESP,xml,appl_rename_file,Impacted_file=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
def out(x,name):
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    jobs_enque =[]
    JOBS_HOLD=[]
    
    for i, line in enumerate(x):
        
        for job_type in JOB_TYPES:
            if re.findall('^[ ]+'+job_type,line):
                JOBS_HOLD.append("")
                new_line="".join(x[i:i+3])
                #print(new_line)
                new_line=new_line.replace("-","")
                new_line=new_line[:new_line.find("NOTWITH")]
                #print(name+"   "+new_line)
                if " HOLD" in new_line or " HOL" in new_line:
                    JOBS_HOLD[-1]="YES"
                jobs_=line[line.find(job_type)+len(job_type):-1].strip().split()[0]
                JOBS.append(jobs_[:jobs_.find('.')])
                jobs_enque.append("")
                enq=[]
                for j in x[i:]:
                    if re.findall("^[ ]+ENQUEUE ", j) :
                        enq.append(j.strip())
                    if re.findall("^  ENDJOB",j):
                        break
                jobs_enque[-1]=enq
    appl_ENQUEUE=[]
    APPL_HOLD=""
    for line in x:
        if line.strip().split()[0] in JOB_TYPES or "ENDJOB" in line:
            break
        if line.endswith("EXCLUSIVE") or line.endswith("SHARED") :
            appl_ENQUEUE.append(line.strip())
        if " HOLD" in line:
            APPL_HOLD='YES'
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
        #print(x)
        o=out(x,name)
        JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD =o[0],o[1],o[2],o[3],o[4]
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        x = original[line_number:next_index]
        #print(x)
        o=out(x,name)
        JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD =o[0],o[1],o[2],o[3],o[4]
    return JOBS,SCHEDULE,APPL_SCHEDULE,APPL_HOLD,JOBS_HOLD

original1=[]
with open(ESP, 'r') as fp:
    original1=fp.readlines()
dfe= pd.DataFrame(original1, columns= ['Lines'])
df=dfe[dfe.Lines.str.contains('ADD    NAME|AIX_JOB|EXTERNAL |JOB|APPLSTART|DBSP_JOB|FILE_TRIGGER|LINUX_JOB|NT_JOB|INFORMATICA_JOB|SPARK_JOB|ENQUEUE NAME| HOLD|LD|OLD')]
df=df[df.Lines.str.contains('\/\*| \%ESPAPPL|APPLEND|APPLSTRT|MULTSETR| TAIL_JOB|_OC -|RESOURCE |ESPNOMSG|APPLUNTIL')==False].replace('\n','', regex= True)
original=list(df.Lines)
l=list([str(line)[str(line).find("=")+1:] for  line in original if ' NAME=' in str(line)]) 
#l=['BPBLCNFU','FPRJ5EA1']
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
                enque_df.append([name,[],a,APPL_[1][i]])
                HOLD_df.append([name,'',a,APPL_[4][i]])
#l=['BPBUCAD0','BPIDADH1','BPIDUPB1','BPIDUPP1','BPASOQ09','BPASOQ07','BPASOQ01','BPASOM01','BPASOW00','BPHNIIW7','BPBUFXA2','BPBUFXA1','BPLLHVA1','BPHARRM0','BPHNCA1','BPHNEA2','BPHNEA3','BPHAUAA1','BPHAUAA2','BPPIDXD1','BPPIDXD2','BPPIDXD3','BPPILAA1','BPPILFA1','BPPILPA1','BPPILPA2','BPPIPMA1','BPPIPRA1','BPPIUTD1','BPPIERA1','BPERINA1','BPERMPA1','BPERUIA1','BPERUIA2','BPERUXA2','BPPCAH01','BPPCAD01','BPPCAD02','BPPCAD03','BPPCAD04','BPPCAD05','BPPCAD06','BPCCECD1','BPCCMCW1','BPMSCMY1','BPMSMCY1','BPMSMIM1','BPPCHD05','BPIASIA1','BPIASIA2','BPIASIA3','BPIASIA4','BPPMINA1','BPPMUNA1','BPPCAR01','BPPCAR02','BPPCAR03','BPPCAR04']
data(l)
enque_df = pd.DataFrame(enque_df,columns = ['APPL Name', 'ENQUEUE at APPL level', 'Job Name', 'ENQUEUE at JOB level']).fillna("")
enque_df['APPL Name']=[i.upper() for i in enque_df['APPL Name']]
enque_df['Job Name']=[i.upper() for i in enque_df['Job Name']]
# enque_df.to_excel("enque_df.xlsx",sheet_name='enque_df', index=False)
# enque_df=pd.read_excel("enque_df.xlsx").fillna("")
HOLD_df=pd.DataFrame(HOLD_df,columns = ['APPL Name', 'HOLD at APPL level', 'Job Name', 'HOLD at JOB level']).fillna("")
HOLD_df['APPL Name']=[i.upper() for i in HOLD_df['APPL Name']]
HOLD_df['Job Name']=[i.upper() for i in HOLD_df['Job Name']]
HOLD_df=HOLD_df.drop_duplicates().reset_index().iloc[:,1:]
#HOLD_df.to_excel("HOLD_df.xlsx",sheet_name='HOLD_df', index=False)
# HOLD_df=pd.read_excel("HOLD_df.xlsx").fillna("")
enque_df['folder_len']=enque_df[enque_df.columns[1]].apply(lambda x: len(x))
enque_df['Job_len']=enque_df[enque_df.columns[3]].apply(lambda x: len(x))
ESP_APPL_CR=enque_df[enque_df[enque_df.columns[4]]>0].iloc[:,[0,1]]
ESP_APPL_CR['RE']=ESP_APPL_CR[ESP_APPL_CR.columns[1]].apply(lambda x: [re.findall("\(([A-Za-z0-9_@]+)\)",i)[0][5:] for i in x])
ESP_JOBS_CR=enque_df[enque_df[enque_df.columns[5]]>0].iloc[:,[0,2,3]]
ESP_JOBS_CR['RE']=ESP_JOBS_CR[ESP_JOBS_CR.columns[2]].apply(lambda x: [re.findall("\(([A-Za-z0-9_@]+)\)",i)[0][5:] for i in x])

ESP_APPL_UserConfirm=HOLD_df[HOLD_df[HOLD_df.columns[1]]=="YES"].iloc[:,[0,1]].fillna("")
ESP_JOBS_UserConfirm=HOLD_df[HOLD_df[HOLD_df.columns[3]]=="YES"].iloc[:,[0,2,3]].fillna("")
#appl_rename=appl_rename.rename(columns={appl_rename.columns[1]:enque_df.columns[0]})
# ESP_APPL_CR_rename=pd.merge(ESP_APPL_CR,appl_rename,on=appl_rename.columns[1],how='left')
# ESP_APPL_CR_rename=ESP_APPL_CR_rename.rename(columns={ESP_APPL_CR_rename.columns[-1]:"Folder_Name"})

# ESP_JOBS_CR_rename=pd.merge(ESP_JOBS_CR,appl_rename,on=appl_rename.columns[1],how='left')
# ESP_JOBS_CR_rename=ESP_JOBS_CR_rename.rename(columns={ESP_JOBS_CR_rename.columns[-1]:"Folder_Name"})

# ESP_APPL_UserConfirm_rename=pd.merge(ESP_APPL_UserConfirm,appl_rename,on=appl_rename.columns[1],how='left')
# ESP_APPL_UserConfirm_rename=ESP_APPL_UserConfirm_rename.rename(columns={ESP_APPL_UserConfirm_rename.columns[-1]:"Folder_Name"})

# ESP_JOBS_UserConfirm_rename=pd.merge(ESP_APPL_CR,appl_rename,on=appl_rename.columns[1],how='left')
# ESP_JOBS_UserConfirm_rename=ESP_JOBS_UserConfirm_rename.rename(columns={ESP_JOBS_UserConfirm_rename.columns[-1]:"Folder_Name"})

def CONTROL1(CONTROL):
    L_CONTROL=[]
    if CONTROL:
        for a in CONTROL:
            L_CONTROL.append(a.attrib['NAME'])
        return L_CONTROL
    else:
        return L_CONTROL

def xml_parse(xml_file):   
    parsexml=et.parse(xml_file)
    root=parsexml.getroot()
    xml_Folder_Control=[]
    xml_jobs_control=[]
    for r in root:
        Folder_name=r.attrib.get('FOLDER_NAME',"")
        CONTROL=r.findall('CONTROL')
        conform='NO'  if int(r.attrib.get("CONFIRM",0))==0 else 'YES'
        xml_Folder_Control.append([Folder_name,CONTROL1(CONTROL),conform])

        for r1 in r.findall("./SMART_FOLDER/SUB_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                var=j.attrib
                PARENT_FOLDER=var.get('PARENT_FOLDER',"")
                JOBNAME=var.get("JOBNAME","")
                CONTROL=j.findall('CONTROL')
                conform='NO'  if int(j.attrib.get("CONFIRM",0))==0 else 'YES'
                xml_jobs_control.append([PARENT_FOLDER,JOBNAME,CONTROL1(CONTROL),conform])
        for r1 in r.findall("./SMART_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                var=j.attrib
                PARENT_FOLDER=var.get('PARENT_FOLDER',"")
                JOBNAME=var.get("JOBNAME","")
                CONTROL=j.findall('CONTROL')
                conform=  'NO'  if int(j.attrib.get("CONFIRM",0))==0 else 'YES'
                xml_jobs_control.append([PARENT_FOLDER,JOBNAME,CONTROL1(CONTROL),conform])
        JOB=r.findall('JOB')
        for j in JOB:
            var=j.attrib
            PARENT_FOLDER=var.get('PARENT_FOLDER',"")
            JOBNAME=var.get("JOBNAME","")
            CONTROL=j.findall('CONTROL')
            conform='NO'  if int(j.attrib.get("CONFIRM",0))==0 else 'YES'
            xml_jobs_control.append([PARENT_FOLDER,JOBNAME,CONTROL1(CONTROL),conform])
    return xml_Folder_Control,xml_jobs_control
xml=xml_parse(xml)
xml_Folder_Control_data = pd.DataFrame(xml[0],columns = ['Folder_Name', 'Control_Resources','CONFIRM']).fillna("")
xml_Folder_Control_data['Folder_Name']=[i.replace(".","_").replace(" ","_").upper() for i in xml_Folder_Control_data['Folder_Name']]
xml_Folder_Control_data["len"]=xml_Folder_Control_data[xml_Folder_Control_data.columns[1]].apply(lambda x: len(x))
xml_Folder_Control=xml_Folder_Control_data[xml_Folder_Control_data[xml_Folder_Control_data.columns[3]]>0].iloc[:,:-2]
#xml_Folder_Control_data.to_excel("conform_folder.xlsx",sheet_name="asdf",index=False)
xml_jobs_control_data=pd.DataFrame(xml[1],columns = ['Folder_Name', 'JOBNAME', 'Control_Resources','CONFIRM']).fillna("")
xml_jobs_control_data['Folder_Name']=[i.replace(".","_").replace(" ","_").upper() for i in xml_jobs_control_data['Folder_Name']]
xml_jobs_control_data['JOBNAME']=[i.replace(".","_").replace(" ","_").upper() for i in xml_jobs_control_data['JOBNAME']]
xml_jobs_control_data["len"]=xml_jobs_control_data[xml_jobs_control_data.columns[2]].apply(lambda x: len(x))
xml_jobs_control=xml_jobs_control_data[xml_jobs_control_data[xml_jobs_control_data.columns[4]]>0].iloc[:,:-2]
#xml_jobs_control_data.to_excel("conform_jobs.xlsx",sheet_name="asdf",index=False)
#012 Folder_Name JOBNAME Control_Resources

appl_rename=pd.read_excel(appl_rename_file,sheet_name=0,usecols='H,K').fillna("")
appl_rename[appl_rename.columns[0]]=[i.strip().replace(".","_").replace(" ","_").upper() for i in appl_rename[appl_rename.columns[0]]]
appl_rename[appl_rename.columns[1]]=[i.strip().upper() for i in appl_rename[appl_rename.columns[1]]]
appl_rename=appl_rename.rename(columns={appl_rename.columns[0]:xml_Folder_Control.columns[0],appl_rename.columns[1]:ESP_APPL_CR.columns[0]})
xml_Folder_Control_rename=pd.merge(xml_Folder_Control,appl_rename,on=appl_rename.columns[0],how='left')
#xml_Folder_Control_rename.to_excel("xml_Folder_Control_rename.xlsx",sheet_name="xml_Folder_Control_rename",index=False)
#ESP_APPL_CR.to_excel("ESP_APPL_CR.xlsx",sheet_name="ESP_APPL_CR",index=False)
ESP_APPL_CR_rename_ctm=pd.merge(ESP_APPL_CR,xml_Folder_Control_rename,on=appl_rename.columns[1],how='outer').fillna("")
#ESP_APPL_CR_rename_ctm.to_excel("ESP_APPL_CR_rename_ctm.xlsx",sheet_name="ESP_APPL_CR_rename_ctm",index=False)

Impacted=pd.read_excel(Impacted_file,sheet_name=0,usecols="E,F,H").fillna("")
for c in Impacted.columns:
    Impacted[c]=[i.strip().replace(".","_").replace(" ","_").upper() for i in Impacted[c]]
Impacted['F_J']=Impacted[Impacted.columns[0]]+Impacted[Impacted.columns[1]]
def impact_matching(Impacted,mathing_df,indexes=[0,1]):
    new_jobs_with_impacted=[]
    for idx,row in mathing_df[mathing_df.columns[indexes]].iterrows():
        if len(row['JOBNAME'])<56:
            new_jobs_with_impacted.append(row['JOBNAME'])
        else:
            new_jobs_with_impacted.append(dict(zip(list(Impacted[Impacted.columns[3]]),list(Impacted[Impacted.columns[2]]))).get(row['Folder_Name']+row['JOBNAME'],""))
    return new_jobs_with_impacted

xml_jobs_control['new_jobs_with_Impacted']=impact_matching(Impacted,xml_jobs_control,indexes=[0,1])
#012 Folder_Name JOBNAME Control_Resources  new_jobs_with_Impacted
xml_jobs_control_rename=pd.merge(xml_jobs_control,appl_rename,on=appl_rename.columns[0],how='left').fillna("")
xml_jobs_control_rename["AplNm_ImpJob"]=xml_jobs_control_rename[xml_jobs_control_rename.columns[-1]] +"/"+xml_jobs_control_rename[xml_jobs_control_rename.columns[-2]]
#012 Folder_Name JOBNAME Control_Resources  new_jobs_with_Impacted esp_name AplNm_ImpJob
ESP_JOBS_CR['AplNm_ImpJob']=ESP_JOBS_CR[ESP_JOBS_CR.columns[0]]+'/'+ESP_JOBS_CR[ESP_JOBS_CR.columns[1]]


#xml_jobs_control_rename.to_excel("xml_jobs_control_rename.xlsx",sheet_name="ESP_JOBS_CR",index=False)
#ESP_JOBS_CR.to_excel("xml_jobs_control_rename.xlsx",sheet_name="ESP_JOBS_CR",index=False)
ESP_JOBS_CR_xml_jobs_control_rename=pd.merge(ESP_JOBS_CR,xml_jobs_control_rename,on=ESP_JOBS_CR.columns[-1],how='outer').fillna("")

#ESP_JOBS_CR_xml_jobs_control_rename.to_excel("ESP_JOBS_CR_xml_jobs_control_rename.xlsx",sheet_name="ESP_JOBS_CR",index=False)
def resource_matching(df1,ctm_idx,esp_idx):
    matched=[]
    extra_in_ctm=[]
    extra_in_ESP=[]
    for idx,data in df1.iterrows():
        matched.append("")
        extra_in_ctm.append("")
        extra_in_ESP.append("")
        ctm=list(sorted(data[df1.columns[ctm_idx]]))
        esp=list(sorted(data[df1.columns[esp_idx]]))
        if ctm==esp:
            matched[-1]='YES'
        else:
            ctm_resource=[]
            for resource in ctm:
                if resource not in esp:
                    ctm_resource.append(resource)
            extra_in_ctm[-1]="\n".join(ctm_resource)
            esp_resource=[]
            for resource in esp:
                if resource not in ctm:
                    esp_resource.append(resource)
            extra_in_ESP[-1]="\n".join(esp_resource)
    return matched,extra_in_ctm,extra_in_ESP
matched,extra_in_ctm,extra_in_ESP=resource_matching(ESP_APPL_CR_rename_ctm,4,2)
ESP_APPL_CR_rename_ctm['matched']=matched
ESP_APPL_CR_rename_ctm['extra_in_ctm']=extra_in_ctm
ESP_APPL_CR_rename_ctm['extra_in_ESP']=extra_in_ESP

matched,extra_in_ctm,extra_in_ESP=resource_matching(ESP_JOBS_CR_xml_jobs_control_rename,7,3)
ESP_JOBS_CR_xml_jobs_control_rename['matched']=matched
ESP_JOBS_CR_xml_jobs_control_rename['extra_in_ctm']=extra_in_ctm
ESP_JOBS_CR_xml_jobs_control_rename['extra_in_ESP']=extra_in_ESP




xml_Folder_Confirm=xml_Folder_Control_data.iloc[:,[0,2]]
xml_Folder_Confirm=xml_Folder_Confirm[xml_Folder_Confirm[xml_Folder_Confirm.columns[1]]=='YES']
appl_rename=appl_rename.rename(columns={appl_rename.columns[0]:xml_Folder_Confirm.columns[0],appl_rename.columns[1]:ESP_APPL_UserConfirm.columns[0]})
xml_Folder_Confirm_rename=pd.merge(xml_Folder_Confirm,appl_rename,on=appl_rename.columns[0],how='left').fillna("")
#xml_Folder_Confirm_rename.to_excel("xml_Folder_Confirm_rename.xlsx",sheet_name="ESP_JOBS_CR",index=False)
#ESP_APPL_UserConfirm.to_excel("ESP_APPL_UserConfirm.xlsx",sheet_name="ESP_JOBS_CR",index=False)
xml_Folder_Confirm_rename_esp=pd.merge(ESP_APPL_UserConfirm,xml_Folder_Confirm_rename,on=ESP_APPL_UserConfirm.columns[0],how='outer').fillna("")
#xml_Folder_Confirm_rename_esp.to_excel("xml_Folder_Confirm_rename_esp.xlsx",sheet_name="ESP_JOBS_CR",index=False)

xml_Folder_Confirm_rename_esp['Match']=(xml_Folder_Confirm_rename_esp[xml_Folder_Confirm_rename_esp.columns[1]]==xml_Folder_Confirm_rename_esp[xml_Folder_Confirm_rename_esp.columns[3]])

xml_jobs_Confirm_data=xml_jobs_control_data.iloc[:,[0,1,3]]
xml_jobs_Confirm_data=xml_jobs_Confirm_data[xml_jobs_Confirm_data[xml_jobs_Confirm_data.columns[2]]=="YES"]

xml_jobs_Confirm_data["new_impacted_jobs"]=impact_matching(Impacted,xml_jobs_Confirm_data,indexes=[0,1])
xml_jobs_Confirm_data_rename=pd.merge(xml_jobs_Confirm_data,appl_rename,on=appl_rename.columns[0],how='left').fillna("")
xml_jobs_Confirm_data_rename['Imp_appl']=xml_jobs_Confirm_data_rename[xml_jobs_Confirm_data_rename.columns[-1]]+xml_jobs_Confirm_data_rename[xml_jobs_Confirm_data_rename.columns[-2]]
#xml_jobs_Confirm_data_rename.to_excel("xml_jobs_Confirm_data_rename.xlsx",sheet_name="ESP_JOBS_CR",index=False)
ESP_JOBS_UserConfirm["Imp_appl"]=ESP_JOBS_UserConfirm[ESP_JOBS_UserConfirm.columns[0]]+ESP_JOBS_UserConfirm[ESP_JOBS_UserConfirm.columns[1]]

#ESP_JOBS_UserConfirm.to_excel("ESP_JOBS_UserConfirm.xlsx",sheet_name="ESP_JOBS_CR",index=False)
ESP_JOBS_UserConfirm_xml=pd.merge(ESP_JOBS_UserConfirm,xml_jobs_Confirm_data_rename,on=ESP_JOBS_UserConfirm.columns[-1],how="outer").fillna("")
#ESP_JOBS_UserConfirm_xml.to_excel("ESP_JOBS_UserConfirm_xml.xlsx",sheet_name="ESP_JOBS_CR",index=False)

ESP_JOBS_UserConfirm_xml=ESP_JOBS_UserConfirm_xml.drop(ESP_JOBS_UserConfirm_xml.columns[[3]],axis=1)
ESP_JOBS_UserConfirm_xml=ESP_JOBS_UserConfirm_xml.rename(columns={ESP_JOBS_UserConfirm_xml.columns[0]:"APPL_Name_in_ESP",ESP_JOBS_UserConfirm_xml.columns[7]:"APPL_Name_in_RENAME"})
ESP_JOBS_UserConfirm_xml["MATCH"]=["YES" if i=="YES"*2  else "NO" for i in ESP_JOBS_UserConfirm_xml[ESP_JOBS_UserConfirm_xml.columns[2]]+ESP_JOBS_UserConfirm_xml[ESP_JOBS_UserConfirm_xml.columns[-3]]]
ESP_JOBS_UserConfirm_xml_missed=ESP_JOBS_UserConfirm_xml.loc[(ESP_JOBS_UserConfirm_xml["MATCH"]=="NO") & (ESP_JOBS_UserConfirm_xml[ESP_JOBS_UserConfirm_xml.columns[0]]!="")].iloc[:,[0,1]]
ESP_JOBS_UserConfirm_xml_missed=ESP_JOBS_UserConfirm_xml_missed.rename(columns={ESP_JOBS_UserConfirm_xml_missed.columns[0]:"APLNAME"})
appl_rename=appl_rename.rename(columns={appl_rename.columns[1]:"APLNAME"})
ESP_JOBS_UserConfirm_xml_missed=pd.merge(ESP_JOBS_UserConfirm_xml_missed,appl_rename,on="APLNAME",how="left").fillna("")

ESP_APPL_CR_rename_ctm=ESP_APPL_CR_rename_ctm.drop("RE",axis=1)
ESP_JOBS_CR_xml_jobs_control_rename=ESP_JOBS_CR_xml_jobs_control_rename.drop(ESP_JOBS_CR_xml_jobs_control_rename.columns[[3,4]],axis=1)
ESP_JOBS_CR_xml_jobs_control_rename=ESP_JOBS_CR_xml_jobs_control_rename.rename(columns={ESP_JOBS_CR_xml_jobs_control_rename.columns[0]:"APPL_Name_in_ESP",ESP_JOBS_CR_xml_jobs_control_rename.columns[-4]:"APPL_Name_in_RENAME"})


with pd.ExcelWriter('ESP_ENQUEUEvsHOLD_Output.xlsx') as writer:
    ESP_APPL_CR_rename_ctm.to_excel(writer, sheet_name='ESP-APPL-CR',index=False)
    ESP_JOBS_CR_xml_jobs_control_rename.to_excel(writer, sheet_name='ESP-JOBS-CR',index=False)
    xml_Folder_Confirm_rename_esp.to_excel(writer, sheet_name='ESP-APPL-UserConfirm',index=False)
    ESP_JOBS_UserConfirm_xml.to_excel(writer,sheet_name="ESP-JOBS-UserConfirm",index=False)
    ESP_JOBS_UserConfirm_xml_missed.to_excel(writer,sheet_name="ESP-JOBS_Confirm_EXTRA",index=False)
print(f"Competed in DD/HH/MM/Sec {datetime.now()-start}")