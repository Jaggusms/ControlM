from ast import Str
from datetime import datetime
from re import S
import sys
import pandas as pd
import xml.etree.ElementTree as et
ESP,xml_file,Appl_rename=sys.argv[1],sys.argv[2],sys.argv[3]
print("Program executing Please wait!")
start=datetime.now()
def out(x):
    wait=""
    for line in x:
        if "WAIT" in line:
            wait="WAITS" 
    return wait
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
df=dfe[dfe.Lines.str.contains('  WAIT|ADD    NAME')]
df=df[df.Lines.str.contains('\/\*')==False].replace('\n','', regex= True)
#df.to_excel("SELF_DEPENDENCY.xlsx", sheet_name='SELF_DEPENDENCY',index=False)
original=list(df.Lines)
l=list([str(line)[str(line).find("=")+1:] for  line in original if 'NAME=' in str(line)]) 
SELF_DEPENDENCY=[]
def data(l):
    for name in l:
        APPL_=APPL_DETAILS(original,name)
        if APPL_=="":
            SELF_DEPENDENCY.append([name,"NO_WAIT"])
        else:
            SELF_DEPENDENCY.append([name,APPL_])
data(l)
WAIT_ESP = pd.DataFrame(SELF_DEPENDENCY,columns = ['APPL_Name_in_ESP', "WAIT_Exist_or_Not"]).fillna("NO_WAIT")
WAIT_ESP[WAIT_ESP.columns[0]]=WAIT_ESP[WAIT_ESP.columns[0]].apply(lambda x:x.upper())
def INCOND1(INCOND):
    L_INCOND=[]
    if INCOND:
        for a in INCOND:
            s=list(a.attrib.values())
            L_INCOND.append(" ".join(s[:3]))
        return L_INCOND	

def OUTCOND1(OUTCOND):
    L_OUT=[]
    if OUTCOND:
        for a in OUTCOND:
            s=list(a.attrib.values())
            L_OUT.append(" ".join(s[:3]))
        return L_OUT
parsexml=et.parse(xml_file)
root=parsexml.getroot()
xml=[]
for r in root:
    data=[]
    FOLDER=r.attrib.get("PARENT_FOLDER","")
    data.append(FOLDER)
    INCOND=r.findall('INCOND')
    data.append(INCOND1(INCOND))
    OUTCOND=r.findall('OUTCOND')
    data.append(OUTCOND1(OUTCOND))
    xml.append(data)
xls = pd.ExcelFile(Appl_rename)
sheets = xls.sheet_names
Appl_rename_sheet=pd.read_excel(Appl_rename,sheet_name=sheets[0],usecols="H,K")
for i in Appl_rename_sheet.columns:
    Appl_rename_sheet[i]=[i.strip().replace(".","_").replace(" ","_").upper() for i in Appl_rename_sheet[i]]
xml_df = pd.DataFrame(xml,columns = [Appl_rename_sheet.columns[0], "INCOND","OUTCOND"])
xml_df[xml_df.columns[0]]=[i.replace(".","_").replace(" ","_").upper() for i in xml_df[xml_df.columns[0]]]
xml_df[xml_df.columns[1]]=[str(i).upper() for i in xml_df[xml_df.columns[1]]]
xml_df[xml_df.columns[2]]=[str(i).upper() for i in xml_df[xml_df.columns[2]]]
xml_df=xml_df.drop_duplicates().reset_index(drop=True)
#xml_df.to_excel("SELF_DEPENDENCY_XML.xlsx", sheet_name='SELF_DEPENDENCY_XML',index=False)
xml_esp=pd.merge(xml_df,Appl_rename_sheet, on=Appl_rename_sheet.columns[0],how="left").fillna("")
xml_esp=xml_esp.rename(columns={'APPL Name ( Max 8 Characters)':'APPL_Name_in_ESP'})
#xml_esp.to_excel("xml_esp.xlsx", sheet_name='xml_esp',index=False)
xml_esp_prev=xml_esp[xml_esp[xml_esp.columns[1]].str.contains('\*|PREV')]
#xml_esp_prev.to_excel("xml_esp_with_prev.xlsx", sheet_name='xml_esp',index=False)
xml_esp_out_prev=xml_esp[xml_esp[xml_esp.columns[1]].str.contains('\*|PREV')==False]
xml_esp_out_prev["SELF_PRIOR_EXIST_OR_NOT"]=list(str("NO "*len(xml_esp_out_prev)).strip().split())
#xml_esp_out_prev.to_excel("xml_esp_out_prev.xlsx", sheet_name='xml_esp',index=False)
self_prior_xml=[]
for idx,rows in xml_esp_prev.iterrows():
    folder_name=rows[0].upper()
    if folder_name+"-TO-"+folder_name in rows[1]:
        self_prior_xml.append("YES")
    else:
        self_prior_xml.append("NO")
xml_esp_prev["SELF_PRIOR_EXIST_OR_NOT"]=[i for i in self_prior_xml]
#xml_esp_prev.to_excel("xml_esp_prev.xlsx", sheet_name='xml_esp',index=False)
xml_full=xml_esp_prev.append(xml_esp_out_prev, ignore_index=True).fillna("")
xml_esp_combined=pd.merge(xml_full,WAIT_ESP, on=WAIT_ESP.columns[0],how="outer").fillna("")
xml_esp_combined=xml_esp_combined.drop_duplicates(keep="first").reset_index().iloc[:,1:]
xml_esp_combined[xml_esp_combined.columns[-2]]=["Appl might not exist in ESP or Appl Sheet" if i=="" else i for i in xml_esp_combined[xml_esp_combined.columns[-2]]]
xml_esp_combined[xml_esp_combined.columns[-1]]=["Appl might not exist in ESP or Appl Sheet" if i=="" else i for i in xml_esp_combined[xml_esp_combined.columns[-1]]]
#xml_esp_combined.to_excel("final.xlsx", sheet_name='xml_esp',index=False)
xml_esp_combined["Matched"]=[ "YES" if "YESWAITS"==i else "YES" if "NONO_WAIT"==i  else "NO" for i in xml_esp_combined[xml_esp_combined.columns[-2]]+xml_esp_combined[xml_esp_combined.columns[-1]] ]
xml_esp_combined[xml_esp_combined.columns[1]]=["\n".join([j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")]) for  i in xml_esp_combined[xml_esp_combined.columns[1]]]
xml_esp_combined[xml_esp_combined.columns[2]]=["\n".join([j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")]) for  i in xml_esp_combined[xml_esp_combined.columns[2]]]
xml_esp_combined.to_excel("ESP_XML_SELF_PROIR.xlsx", sheet_name='ESP_XML_SELF_PROIR',index=False)
print(f"completed in {datetime.now()-start}")