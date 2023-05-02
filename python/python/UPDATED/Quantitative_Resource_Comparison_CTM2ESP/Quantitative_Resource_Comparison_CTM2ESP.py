from datetime import datetime
import sys
import pandas as pd
import xml.etree.ElementTree as et
import re
xml_file,ESP,Impacted_file,APPL_Final_Rename_Sheet=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
print("Program executing Please wait!")
start=datetime.now()

def QUANTITATIVE1(QUA):
    L_QUA=[]
    if QUA:
        for a in QUA:
            L_QUA.append(a.attrib['NAME'])
        return L_QUA
    else:
        return ""
parsexml=et.parse(xml_file)
root=parsexml.getroot()
xml=[]
for r in root.findall("./SMART_FOLDER/"):
    JOB=r.findall('JOB')
    #finding the all attribuets of job
    for j in JOB:
        job_resourc=[]
        atrib=j.attrib
        job_resourc.append(atrib["PARENT_FOLDER"])
        job_resourc.append(atrib["JOBNAME"])
        QUA=j.findall('QUANTITATIVE')
        job_resourc.append(QUANTITATIVE1(QUA))
        xml.append(job_resourc)
for r in root:
    JOB=r.findall('JOB')
    #finding the all attribuets of job
    for j in JOB:
        job_resourc=[]
        atrib=j.attrib
        job_resourc.append(atrib["PARENT_FOLDER"])
        job_resourc.append(atrib["JOBNAME"])
        QUA=j.findall('QUANTITATIVE')
        job_resourc.append(QUANTITATIVE1(QUA))
        xml.append(job_resourc)

xml_df=pd.DataFrame(xml,columns=['Folder','Jobs in CTM',"Resource in CTM"])
xml_df['Folder']=[i.replace(".","_").replace(" ","_").upper() for i in xml_df['Folder']]
xml_df['Jobs in CTM']=[i.replace(".","_").replace(" ","_").upper() for i in xml_df['Jobs in CTM']]
#xml_df[xml_df.columns[1]]=["\n".join([j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")]) for  i in xml_esp_combined[xml_esp_combined.columns[1]]]
xml_df[xml_df.columns[2]]=[str(i).upper() for i in xml_df[xml_df.columns[2]]]
xml_df=xml_df.drop_duplicates().reset_index().iloc[:,1:]
xml_df[xml_df.columns[2]]=[[j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")] for  i in xml_df[xml_df.columns[2]]]
#xml_df.to_excel("xml_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

#xml_df["Resource in CTM"]=[str(i) for  i in xml_df["Resource in CTM"]]
#ESP_df=pd.DataFrame(ESP,columns=['APPL_NAME','Jobs in ESP',"Resource in ESP"])
#xml_df.to_excel("jobs.xlsx", sheet_name='JOB',index=False)
def out(x):
    JOBS=[]
    JOB_TYPES=['AIX_JOB', 'JOB', 'APPLSTART', 'DBSP_JOB', 'FILE_TRIGGER', 'LINUX_JOB', 'NT_JOB', 'INFORMATICA_JOB', 'SPARK_JOB']
    Resource_JOBS=[]
    count=[]
    for i,line in enumerate(x):
        if i not in count:
            line_string=line.strip().split()
            try:
                job_type=line_string[0]
            except:
                job_type=" "
                pass
            if job_type in JOB_TYPES:
                if "EXTERNAL " not in " ".join(x[i:i+3]):
                    JOBS.append(line_string[1].split(".")[0])
                else:
                    continue
                #JOBS.append(line_string[1].split(".")[0])
                Resource=[]
                for line1 in x[i:]:
                    count.append(i)
                    #difflib.get_close_matches(approval_string, ACTIVE_MSG, cutoff=0.7)
                    if re.findall("^[ ]+RESOURCE",line1):
                        res=line1.split(",")[1][:-1]
                        if res.find(")")!=-1:
                            Resource.append(res[:res.find(")")]) 
                        else:
                            Resource.append(res)
                    if re.findall("^[ ]+ENDJOB",line1):
                        break
                Resource_JOBS.append(Resource)         
    return JOBS,Resource_JOBS
def APPL_DETAILS(original,name):
    appl,line_number=[],-1
    for l_no, line in enumerate(original):
        if './ ADD    NAME='+ name in line:
            line_number=l_no
        if './ ADD    NAME=' in line:
            appl.append(l_no)
    if appl[-1]==line_number and line_number>0:
        return out(original[line_number+1:])   
    if appl[-1]!=line_number and line_number>=0:
        next_index=appl[appl.index(line_number)+1]
        return out(original[line_number:next_index])

original1=[]
with open(ESP, 'r') as fp:
    original1=fp.readlines()
dfe= pd.DataFrame(original1, columns= ['Lines'])
df=dfe[dfe.Lines.str.contains('  RESOURCE|ADD    NAME|AIX_JOB|EXTERNAL |JOB|APPLSTART|DBSP_JOB|FILE_TRIGGER|LINUX_JOB|NT_JOB|INFORMATICA_JOB|SPARK_JOB')]
df=df[df.Lines.str.contains('\/\*| \%ESPAPPL| APPLEND| APPLSTRT| TAIL_JOB|_OC -')==False].replace('\n','', regex= True)
original=list(df.Lines)
#df.to_excel("df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)
l=list([str(line)[str(line).find("=")+1:] for  line in original if ' NAME=' in str(line)]) 
Quantitative=[]
def data(l):
    for name in l:
        APPL_=APPL_DETAILS(original,name)
        #print(name+str(APPL_)+"\n")
        for idx,jobs in enumerate(APPL_[0]):
            Quantitative.append([name,jobs,APPL_[1][idx]])

data(l)
Quantitative_df = pd.DataFrame(Quantitative,columns = ['APPL Name in ESP', 'JOBNAME in ESP','Resources in ESP'])
Quantitative_df['APPL Name in ESP']=Quantitative_df['APPL Name in ESP'].apply(lambda x:x.upper())
Quantitative_df['JOBNAME in ESP']=Quantitative_df['JOBNAME in ESP'].apply(lambda x:x.upper())
Quantitative_df[Quantitative_df.columns[2]]=[str(i).upper() for i in Quantitative_df[Quantitative_df.columns[2]]]
Quantitative_df=Quantitative_df.drop_duplicates().reset_index().iloc[:,1:]
Quantitative_df["APPLname/Jobname in ESP"]=Quantitative_df[Quantitative_df.columns[0]]+"/"+Quantitative_df[Quantitative_df.columns[1]]
Quantitative_df["APPLname/Jobname"]=Quantitative_df["APPLname/Jobname in ESP"]
#Quantitative_df.to_excel("Quantitative_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)
grouped_df=Quantitative_df.groupby(["APPLname/Jobname"])
new_dff=pd.DataFrame(columns=Quantitative_df.columns)
for key, item in grouped_df:
    df2=grouped_df.get_group(key).reset_index().iloc[:,1:]
    if len(df2.index)==1:
        new_dff=pd.concat([new_dff,df2])
        continue
    else:
        df2_1stline_copy=df2.loc[0,:]
        df2=df2[df2[df2.columns[2]].str.contains("\[\]")==False]
        if len(df2.index)==0:
            new_dff=pd.concat([new_dff,df2_1stline_copy])
        else:
            new_dff=pd.concat([new_dff,df2])
Quantitative_df=new_dff
Quantitative_df[Quantitative_df.columns[2]]=[[j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")] for  i in Quantitative_df[Quantitative_df.columns[2]]]
#Quantitative_df.to_excel("Quantitative_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

Wave3_APPL_Final_df=pd.read_excel(APPL_Final_Rename_Sheet,sheet_name=0,usecols='H,K').fillna("")
Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[0]]=[i.strip().replace(".","_").replace(" ","_").upper() for i in Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[0]]]
Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[1]]=[i.strip().upper() for i in Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[1]]]
Wave3_APPL_Final_df=Wave3_APPL_Final_df.rename(columns={Wave3_APPL_Final_df.columns[0]:"Folder"})
Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[0]]=[i for i in Wave3_APPL_Final_df[Wave3_APPL_Final_df.columns[0]]]

#Wave3_APPL_Final_df.to_excel("Wave3_APPL_Final_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

Wave3_new_df=pd.merge(xml_df,Wave3_APPL_Final_df, on=["Folder"],how="left")

#Wave3_new_df.to_excel("Wave3_new_df xml_df Wave3_APPL_Final_df merged.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

#Wave3_Impacted_df.to_excel("Wave3_Impacted_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)
# new=[]
# for idx,row in Wave3_new_df[Wave3_new_df.columns[:2]].iterrows():
#     if len(row['Jobs in CTM'])<56:
#         new.append(row['Jobs in CTM'])
#     else:
#         l=list(Wave3_Impacted_df[Wave3_Impacted_df[Wave3_Impacted_df.columns[0]].str.contains(row['Folder'])][Wave3_Impacted_df.columns[1]])
#         if len(l)!=0:
#             new.append(l[0])
#         else:
#             new.append("")

Impacted=pd.read_excel(Impacted_file,sheet_name=0,usecols="E,F,H").fillna("")
for c in Impacted.columns:
    Impacted[c]=[i.strip().replace(".","_").replace(" ","_").upper() for i in Impacted[c]]
Impacted['F_J']=Impacted[Impacted.columns[0]]+Impacted[Impacted.columns[1]]
def impact_matching(Impacted,mathing_df,indexes=[0,1]):
    new_jobs_with_impacted=[]
    for idx,row in mathing_df[mathing_df.columns[indexes]].iterrows():
        if len(row[mathing_df.columns[indexes[1]]])<56:
            new_jobs_with_impacted.append(row[mathing_df.columns[indexes[1]]])
        else:
            new_jobs_with_impacted.append(dict(zip(list(Impacted[Impacted.columns[3]]),list(Impacted[Impacted.columns[2]]))).get(row[mathing_df.columns[indexes[0]]]+row[mathing_df.columns[indexes[1]]],""))
    return new_jobs_with_impacted

Wave3_new_df['Impacted Job Name ']=impact_matching(Impacted,Wave3_new_df,indexes=[0,1])
Wave3_new_df['APPLname/Jobname']=Wave3_new_df[Wave3_new_df.columns[3]]+"/"+Wave3_new_df[Wave3_new_df.columns[4]]
Wave3_new_df=Wave3_new_df.rename(columns={Wave3_new_df.columns[3]:"APPL Name"})
#Wave3_new_df.to_excel("Wave3_new_df.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

filal_df = pd.merge(Wave3_new_df, Quantitative_df,on=[Wave3_new_df.columns[5]] ,how="left")


def tostring(df,colum_number):
    return [str(i) for i in df[df.columns[colum_number]]]
def tolist(df,colum_number):
    return [[j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")] for  i in df[df.columns[colum_number]]]
# filal_df[filal_df.columns[2]]=tostring(filal_df,2)
# filal_df[filal_df.columns[8]]=tostring(filal_df,8)
# filal_df=filal_df.drop_duplicates().reset_index().iloc[:,1:]
# filal_df[filal_df.columns[8]]=tolist(filal_df,8)
# filal_df[filal_df.columns[2]]=tolist(filal_df,2)
#filal_df1 = pd.merge(Wave3_new_df, Quantitative_df,on=[Wave3_new_df.columns[5]] ,how="right")
#filal_df1.to_excel("filal_df1 Wave3_new_df, Quantitative_df merged.xlsx", sheet_name='QUANTITATIVE Resource',index=False)
#Wave3_new_df.to_excel("filal_df Wave3_new_df, Quantitative_df merged.xlsx", sheet_name='QUANTITATIVE Resource',index=False)
#    print(" ".join([r[i] for i in range(len(filal_df.columns))]))
final_df_comparing=filal_df[[filal_df.columns[2],filal_df.columns[8]]].fillna("")
matched=[]
extra_in_ctm=[]
extra_in_ESP=[]
for idx,data in final_df_comparing.iterrows():
    matched.append("")
    extra_in_ctm.append("")
    extra_in_ESP.append("")
    ctm=list(sorted(data[filal_df.columns[2]]))
    esp=list(sorted(data[filal_df.columns[8]]))
    if ctm==esp:
        matched[-1]=ctm
    else:
        ctm_resource=[]
        for resource in ctm:
            if resource not in esp:
                ctm_resource.append(resource)
        extra_in_ctm[-1]=ctm_resource
        esp_resource=[]
        for resource in esp:
            if resource not in ctm:
                esp_resource.append(resource)
        extra_in_ESP[-1]=esp_resource
filal_df['Matched']=["YES" if type(i)==list else "NO" for i in matched]
filal_df[filal_df.columns[2]]=[" \n".join(i) if type(i)==list else i for i in filal_df[filal_df.columns[2]]]
filal_df[filal_df.columns[8]]=[" \n".join(i) if type(i)==list else i for i in filal_df[filal_df.columns[8]]]
filal_df['extra_in_ctm']=[" \n".join(i) if type(i)==list else i for i in extra_in_ctm]
filal_df['extra_in_ESP']=[" \n".join(i) if type(i)==list else i for i in extra_in_ESP]
filal_df['lenth of Jobs in CTM']=[len(i) for i in filal_df['Jobs in CTM']]
filal_df['lenth of Jobs in Impacted']=[len(i) for i in filal_df['Impacted Job Name ']]
filal_df=filal_df.drop_duplicates().reset_index().iloc[:,1:]
filal_df.to_excel("Quantitative Resource_Comparison_CTM2ESP.xlsx", sheet_name='QUANTITATIVE Resource',index=False)

print(f"completed in {datetime.now()-start}")