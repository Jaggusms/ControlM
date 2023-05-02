import sys,re
from datetime import datetime
from time import time
import xml.etree.ElementTree as et
from matplotlib.pyplot import axis
import pandas as pd
import numpy as np
print("Program executing Please wait!")
start=datetime.now()
esp_file,xml_file=sys.argv[1],sys.argv[2:]
def CONTROL1(CONTROL):
    L_CONTROL=[]
    if CONTROL:
        for a in CONTROL:
            L_CONTROL.append(a.attrib['NAME'])
        return L_CONTROL
    else:
        return L_CONTROL

def QUANTITATIVE1(QUA):
    L_QUA=[]
    if QUA:
        for a in QUA:
            L_QUA.append(a.attrib['NAME'])
        return L_QUA
    else:
        return L_QUA
def xml_parse(xml_file):   
    parsexml=et.parse(xml_file)
    root=parsexml.getroot()
    xml_quantitative=[]
    xml_control=[]
    for r in root:
        Datacenter=r.attrib.get('DATACENTER',"")
        CONTROL=r.findall('CONTROL')
        for i in CONTROL1(CONTROL):
            xml_control.append([Datacenter,i])
        for r1 in r.findall("./SMART_FOLDER/SUB_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                QUANTITATIVE=j.findall('QUANTITATIVE')
                for i in QUANTITATIVE1(QUANTITATIVE):
                    xml_quantitative.append([Datacenter,i])
        for r1 in r.findall("./SMART_FOLDER/"):
            JOB=r1.findall('JOB')
            for j in JOB:
                QUANTITATIVE=j.findall('QUANTITATIVE')
                for i in QUANTITATIVE1(QUANTITATIVE):
                    xml_quantitative.append([Datacenter,i])
        JOB=r.findall('JOB')
        for j in JOB:
            QUANTITATIVE=j.findall('QUANTITATIVE')
            for i in QUANTITATIVE1(QUANTITATIVE):
                xml_quantitative.append([Datacenter,i])
    return xml_quantitative,xml_control
xml_quantitative=[]
xml_control=[]
xml_file=[i for i in xml_file if xml_file.endswith(".xml")]
xml_file_filter=[i for i in xml_file if not xml_file.endswith(".xml")]
if len(xml_file_filter)!=0:
    print(*xml_file_filter,end=" ")
    print(" are not taken")
for files in xml_file:
    data=xml_parse(files)
    xml_quantitative +=data[0]
    xml_control +=data[1]
quantitative_resouce_dataframe=pd.DataFrame(xml_quantitative,columns=["CTM_SERVER","QUANTITATIVE_RESORCE_NAME"])
control_resouce_dataframe=pd.DataFrame(xml_control,columns=["CTM_SERVER","CONTROL_RESORCE_NAME"])
quantitative_resouce_dataframe=quantitative_resouce_dataframe.drop_duplicates().reset_index().iloc[:,1:].sort_values(by=[quantitative_resouce_dataframe.columns[1]])
control_resouce_dataframe=control_resouce_dataframe.drop_duplicates().reset_index().iloc[:,1:].sort_values(by=[control_resouce_dataframe.columns[1]])


ESP_ORIGINAL_DATA=[]
with open(esp_file, 'r') as fp:
    ESP_ORIGINAL_DATA=fp.readlines()
ESP_REPORT_datafrmae= pd.DataFrame(ESP_ORIGINAL_DATA, columns= ['Lines']).fillna("")
Resource_lines=ESP_REPORT_datafrmae[ESP_REPORT_datafrmae.Lines.str.contains('Resource',flags=re.IGNORECASE, regex=True,na=False)]
Resource_lines=pd.DataFrame(Resource_lines.Lines.apply(lambda x: " ".join([i for i in x.split(" ") if i!=""] )))
Resource_lines=Resource_lines.Lines.str.split(" ",expand=True)
Resource_lines=Resource_lines.drop([0,2],axis=1).rename({1: 'Resource_Name', 3: 'Resource_Type'}, axis=1).drop_duplicates().reset_index().iloc[:,1:]

MAX_Avail_lines=ESP_REPORT_datafrmae[ESP_REPORT_datafrmae.Lines.str.contains(' Max=| Avail=',flags=re.IGNORECASE, regex=True,na=False)]
random_df = pd.DataFrame([''], columns=MAX_Avail_lines.columns)
MAX_Avail_lines=pd.concat([random_df, MAX_Avail_lines]).reset_index(drop=True)
MAX_Avail_lines=pd.DataFrame(MAX_Avail_lines[MAX_Avail_lines.columns[0]].apply(lambda x:x.replace("*","")).apply(lambda x:x[:-1].replace(" ","")))
#MAX_Avail_lines.index=MAX_Avail_lines.index+1

Resource_lines["Quantity"]=[df.to_string(index = False,header = False,na_rep = '').replace(" ","") for df in np.array_split(MAX_Avail_lines, int(len(MAX_Avail_lines.index)/3))]
Resource_lines["Quantity"].loc[0]=Resource_lines["Quantity"].loc[0][1:]
#Resource_lines.insert(0, "Quantity",Resource_lines["Quantity"].loc[0][1:])
Resource_lines1=Resource_lines["Quantity"].str.split("\n",expand=True)
#Resource_lines["Quantity"]=Resource_lines["Quantity"].apply(lambda x: list(zip(re.findall("[a-zA-Z]+",x),re.findall("[0-9]+",x)))).app
Resource_lines1_new=pd.DataFrame([[""]]*len(Resource_lines.index),columns=['0'])
for i in Resource_lines1.columns:
    data=[["max"+str(i),"avail"+str(i)]]
    for i in Resource_lines1[i]:
        values=re.findall("[0-9]+",i)
        if len(values)==2:
            data.append([values[0],values[1]])
        else:
            data.append(["",values[0]])
    data=pd.DataFrame(data[1:],columns=data[0])
    Resource_lines1_new=pd.concat([Resource_lines1_new,data],axis=1)
Resource_lines1_new=Resource_lines1_new.drop(['0'],axis=1)

def matching(Resource_lines1_new,index):
    matching_list=[]
    for idx,value in Resource_lines1_new.iloc[:,index].iterrows():
        if str(value[0])==str(value[1]):
            matching_list.append("")
        else:
             matching_list.append(value[1])
    return matching_list

#print( ["" if i==True else "no" for i in list(Resource_lines1_new[Resource_lines1_new.columns[2]]==Resource_lines1_new[Resource_lines1_new.columns[0]])])
for i in range(2,len(Resource_lines1_new.columns)):
    if i%2==0:
        Resource_lines1_new[Resource_lines1_new.columns[i]]=matching(Resource_lines1_new,[0,i])
    else:
        Resource_lines1_new[Resource_lines1_new.columns[i]]=matching(Resource_lines1_new,[1,i])

Resource_lines=pd.concat([Resource_lines.iloc[:,:-1],Resource_lines1_new],axis=1)
resources_inesp=list(Resource_lines[Resource_lines.columns[0]])
quantitative_resouce_dataframe["Match_RC_CTMvsESP"]=["Yes" if i in resources_inesp else "No" for i in quantitative_resouce_dataframe[quantitative_resouce_dataframe.columns[1]]]



with pd.ExcelWriter("CTMvsESP_QR_CR_"+str(datetime.now().strftime("%m%d%Y%H%M%S"))+".xlsx") as f:
    control_resouce_dataframe.to_excel(f,sheet_name="CONTROL_RESOURCE",index=False)  
    Resource_lines.to_excel(f,sheet_name="ESP_QR_CR_NAME",index=False) 
    quantitative_resouce_dataframe.to_excel(f,sheet_name="QUANTITATIVE_RESOURCE",index=False) 
print(f"completed in {datetime.now()-start}")