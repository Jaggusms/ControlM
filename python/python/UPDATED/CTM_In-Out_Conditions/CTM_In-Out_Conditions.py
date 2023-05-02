from datetime import datetime
import sys
import pandas as pd
import xml.etree.ElementTree as et
pd.options.mode.chained_assignment = None
# if len(sys.argv)!=5:
#     print("please pass correct params")
#     sys.exit(1)
# xml_file,esp_file,imp_jobs_file,appl_rename_file=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
# if not (xml_file.lower().endswith("xml") or esp_file.lower().endswith("xml") or imp_jobs_file.lower().endswith("xml") or appl_rename_file.lower().endswith("xml")):
#     print("Please pass valide params 1. xml_file 2. esp_file 3. imp_jobs_file 4. appl_rename_file")
#     sys.exit(1)

if len(sys.argv)!=2:
    print("please pass correct params")
    sys.exit(1)
xml_file=sys.argv[1]
if not (xml_file.lower().endswith("xml") ):
    print("Please pass valide params 1. xml_file ")
    sys.exit(1)
print("Program executing Please wait!")
start=datetime.now()




class conditions_Checking:
    def __init__(self,xml_file):
       self.xml_file=xml_file
    def xml(self):
        parsexml=et.parse(self.xml_file)
        root=parsexml.getroot()
        xml=[]
        for r in root:
            parent=[]
            FOLDER=r.attrib.get("PARENT_FOLDER","")
            parent.append(FOLDER)
            parent.append(r.tag)
            parent.append(FOLDER)
            INCOND=r.findall('INCOND')
            parent.append(self.INCOND1(INCOND))
            OUTCOND=r.findall('OUTCOND')
            parent.append(self.OUTCOND1(OUTCOND)) 
            xml.append(parent)
            JOB=r.findall('JOB')
            for j in JOB:
                job_data=[]
                job_data.append(FOLDER)
                job_data.append(j.tag)
                job_data.append(j.attrib.get("JOBNAME",""))
                INCOND=j.findall('INCOND')
                job_data.append(self.INCOND1(INCOND))
                OUTCOND=j.findall('OUTCOND')
                ON=j.findall('ON')
                Variable=j.findall('VARIABLE')
                job_data.append(self.OUTCOND1(OUTCOND)+self.ON1(ON)+self.VARIABLE1(Variable)) 
                xml.append(job_data)
            
        for r1 in root.findall("./SMART_FOLDER/"):
            if r1.tag=="SUB_FOLDER":
                sub_folder=[]
                parent_folder=r1.attrib.get("PARENT_FOLDER","")
                FOLDER=r1.attrib.get("JOBNAME","")
                sub_folder.append(parent_folder)
                sub_folder.append(r1.tag)
                sub_folder.append(FOLDER)
                INCOND=r1.findall('INCOND')
                sub_folder.append(self.INCOND1(INCOND))
                OUTCOND=r1.findall('OUTCOND')
                sub_folder.append(self.OUTCOND1(OUTCOND)) 
                xml.append(sub_folder)
            JOB=r1.findall('JOB')
            for j in JOB:
                job_data=[]
                job_data.append(j.attrib.get("PARENT_FOLDER",""))
                job_data.append(j.tag)
                job_data.append(j.attrib.get("JOBNAME",""))
                INCOND=j.findall('INCOND')
                job_data.append(self.INCOND1(INCOND))
                OUTCOND=j.findall('OUTCOND')
                ON=j.findall('ON')
                Variable=j.findall('VARIABLE')
                job_data.append(self.OUTCOND1(OUTCOND)+self.ON1(ON)+self.VARIABLE1(Variable)) 
                xml.append(job_data)


            # INCOND=r.findall('INCOND')
            # data.append(self.INCOND1(INCOND))
            # OUTCOND=r.findall('OUTCOND')
            # data.append(self.OUTCOND1(OUTCOND))   
        return xml

    def ESP():
        pass

    def IMPACTED():
        pass
    
    def appl_rename():
        pass

    def INCOND1(self,INCOND):
        L_INCOND=[]
        for a in INCOND:
            L_INCOND.append(" ".join(list(a.attrib.values())))
        return L_INCOND	
        
    def OUTCOND1(self,OUTCOND):
        L_OUT=[]
        for a in OUTCOND:
            L_OUT.append(" ".join(list(a.attrib.values())))
        return L_OUT
    def ON1(self,ON):
        L_ON=[]
        for p in ON:
            DOCOND=p.findall('DOCOND')
            for a in DOCOND:
                L_ON.append(" ".join(list(a.attrib.values())))
        return L_ON 
    def VARIABLE1(self,VARIABLE):
        L_VARIABLE=[]
        for B in VARIABLE:
            if B.attrib.get("NAME","")=="%%ADD_CONDITION":
                L_VARIABLE.append(B.attrib.get("VALUE",""))   
        return L_VARIABLE



object=conditions_Checking(xml_file)
data=pd.DataFrame(object.xml(),columns=['PARENT_FOLDER','TAG',"JOBNAME","INCOND","OUTCOND"])
#data['OUTCOND']=[i  for i in data['OUTCOND'] ]
data['OUTCOND']=[[j for j in i if not j.endswith("-")]  for i in data['OUTCOND'] ]
data['str_OUTCOND']=[" \n".join(i)  for i in data['OUTCOND'] ]

def find_all_duplicates(l):
    NOT_duplacated=[]
    duplacated=[]
    for i in l:
        if i not in NOT_duplacated:
            NOT_duplacated.append(i)
        else:
            duplacated.append(i)
    return "" if len(duplacated)==0 else duplacated
data['duplicated_OUTCOND']=data['OUTCOND'].apply(find_all_duplicates)

Matched_In_Out_Conditions=[]
Matched_In_Out_Conditions_index=[]
Same_In_Out_in_different_folder=[]
Same_In_Out_in_different_folder_index=[]
Not_exist_OutConditions=[]
Not_exist_OutConditions_index=[]
predessor=[]
for i,v in enumerate(data['INCOND']):
    Not_exist=[]
    Same_In_Out_=[]
    Matched_In_Out_=[]
    predessor1=""
    if len(v)==0:
        Not_exist_OutConditions.append(Not_exist)
        Same_In_Out_in_different_folder.append(Same_In_Out_)
        Matched_In_Out_Conditions.append(Matched_In_Out_)
        predessor.append(predessor1)
        Matched_In_Out_Conditions_index.append(i)
    else:
        for in_cond in v:
            inconditon=in_cond[:in_cond.find(" ")]
            new_data=data[data.str_OUTCOND.str.contains(inconditon)]
            if len(new_data.index)==0:
                Not_exist.append(in_cond)
                Not_exist_OutConditions_index.append(i)
            elif len(new_data.index)>1:
                Same_In_Out_.append(inconditon)
                predessor1=" \n".join([f+"-"+ j for f,j in  zip(list(new_data['PARENT_FOLDER']),list(new_data['JOBNAME']))])
                #predessor1="\n".join([j for j in  list(new_data['JOBNAME'])])
                
                Same_In_Out_in_different_folder_index.append(i)
            else:
                Matched_In_Out_.append(inconditon)
                #predessor1="\n".join([f+"-"+ j for f,j in  zip(list(new_data['PARENT_FOLDER']),list(new_data['JOBNAME']))])
                predessor1=" \n".join([j for j in  list(new_data['JOBNAME'])])
                Matched_In_Out_Conditions_index.append(i)
        Not_exist_OutConditions.append(Not_exist)
        Same_In_Out_in_different_folder.append(Same_In_Out_)
        Matched_In_Out_Conditions.append(Matched_In_Out_)
        predessor.append(predessor1)
data['predessor']=predessor
data["matched"]=Matched_In_Out_Conditions
data["not_exit"]=Not_exist_OutConditions
data["Same_In_Out_in_different_folder_jobs"]=Same_In_Out_in_different_folder

matched_data=data.iloc[Matched_In_Out_Conditions_index,[0,1,2,6,7,8]]
Not_exist=data.iloc[Not_exist_OutConditions_index,[0,1,2,6,7,9]]
Same_In_Out=data.iloc[Same_In_Out_in_different_folder_index,[0,1,2,6,7,10]]

with pd.ExcelWriter("new"+str(datetime.now().strftime("%H%M%S"))+".xlsx") as w:
    data.to_excel(w, sheet_name='data',index=False)
    matched_data.to_excel(w, sheet_name='matched_data',index=False)
    Same_In_Out.to_excel(w, sheet_name='Same_In_Out',index=False)
    Not_exist.to_excel(w, sheet_name='Not_exist',index=False)
    
# def out(x):
#     wait=""
#     for line in x:
#         if "WAIT" in line:
#             wait="WAITS" 
#     return wait
# def APPL_DETAILS(original,name,dictonary_with):
#     appl,line_number=[],-1
#     line_number=dictonary_with.get("./ ADD    NAME="+name)
#     appl=list(dictonary_with.values())
#     if appl[-1]==line_number and line_number>0:
#         return out(original[line_number+1:])   
#     if appl[-1]!=line_number and line_number>=0:
#         next_index=appl[appl.index(line_number)+1]
#         return out(original[line_number:next_index])
# original1=[]
# with open(ESP, 'r') as fp:
#     original1=fp.readlines()
# dfe= pd.DataFrame(original1, columns= ['Lines'])
# df=dfe[dfe.Lines.str.contains('  WAIT|ADD    NAME')]
# df=df[df.Lines.str.contains('\/\*')==False].replace('\n','', regex= True)
# #df.to_excel("SELF_DEPENDENCY.xlsx", sheet_name='SELF_DEPENDENCY',index=False)
# original=list(df.Lines)
# appls_df=df[df.Lines.str.contains("./ ADD    NAME=")]
# appl_names=list(appls_df.Lines)
# appl_index=list(appls_df.index)
# dictonary_with=dict(zip(appl_names,appl_index))
# l=list([str(line)[str(line).find("=")+1:] for line in appl_names]) 

# SELF_DEPENDENCY=[]
# def data(l,original,dictonary_with):
#     for name in l:
#         APPL_=APPL_DETAILS(original,name,dictonary_with)
#         if APPL_=="":
#             SELF_DEPENDENCY.append([name,"NO_WAIT"])
#         else:
#             SELF_DEPENDENCY.append([name,APPL_])
# data(l,original,dictonary_with)
# WAIT_ESP = pd.DataFrame(SELF_DEPENDENCY,columns = ['APPL_Name_in_ESP', "WAIT_Exist_or_Not"]).fillna("NO_WAIT")
# WAIT_ESP[WAIT_ESP.columns[0]]=WAIT_ESP[WAIT_ESP.columns[0]].apply(lambda x:x.upper())
# def INCOND1(INCOND):
#     L_INCOND=[]
#     if INCOND:
#         for a in INCOND:
#             s=list(a.attrib.values())
#             L_INCOND.append(" ".join(s[:3]))
#         return L_INCOND	

# def OUTCOND1(OUTCOND):
#     L_OUT=[]
#     if OUTCOND:
#         for a in OUTCOND:
#             s=list(a.attrib.values())
#             L_OUT.append(" ".join(s[:3]))
#         return L_OUT
# parsexml=et.parse(xml_file)
# root=parsexml.getroot()
# xml=[]
# for r in root:
#     data=[]
#     FOLDER=r.attrib.get("PARENT_FOLDER","")
#     data.append(FOLDER)
#     INCOND=r.findall('INCOND')
#     data.append(INCOND1(INCOND))
#     OUTCOND=r.findall('OUTCOND')
#     data.append(OUTCOND1(OUTCOND))
#     xml.append(data)


# xml.to_excel("xml.xlsx", sheet_name='xml',index=False)
# Appl_rename_sheet=pd.read_excel(Appl_rename,sheet_name=sheets[0],usecols="H,K")
# for i in Appl_rename_sheet.columns:
#     Appl_rename_sheet[i]=[i.strip().replace(".","_").replace(" ","_").upper() for i in Appl_rename_sheet[i]]
# xml_df = pd.DataFrame(xml,columns = [Appl_rename_sheet.columns[0], "INCOND","OUTCOND"])
# xml_df[xml_df.columns[0]]=[i.replace(".","_").replace(" ","_").upper() for i in xml_df[xml_df.columns[0]]]
# xml_df[xml_df.columns[1]]=[str(i).upper() for i in xml_df[xml_df.columns[1]]]
# xml_df[xml_df.columns[2]]=[str(i).upper() for i in xml_df[xml_df.columns[2]]]
# xml_df=xml_df.drop_duplicates().reset_index(drop=True)
# #xml_df.to_excel("SELF_DEPENDENCY_XML.xlsx", sheet_name='SELF_DEPENDENCY_XML',index=False)
# xml_esp=pd.merge(xml_df,Appl_rename_sheet, on=Appl_rename_sheet.columns[0],how="left").fillna("")
# xml_esp=xml_esp.rename(columns={'APPL Name ( Max 8 Characters)':'APPL_Name_in_ESP'})
# #xml_esp.to_excel("xml_esp.xlsx", sheet_name='xml_esp',index=False)
# xml_esp_prev=xml_esp[xml_esp[xml_esp.columns[1]].str.contains('\*|PREV')]
# #xml_esp_prev.to_excel("xml_esp_with_prev.xlsx", sheet_name='xml_esp',index=False)
# xml_esp_out_prev=xml_esp[xml_esp[xml_esp.columns[1]].str.contains('\*|PREV')==False]
# xml_esp_out_prev["SELF_PRIOR_EXIST_OR_NOT"]=list(str("NO "*len(xml_esp_out_prev)).strip().split())
# #xml_esp_out_prev.to_excel("xml_esp_out_prev.xlsx", sheet_name='xml_esp',index=False)
# self_prior_xml=[]
# for idx,rows in xml_esp_prev.iterrows():
#     folder_name=rows[0].upper()
#     if folder_name+"-TO-"+folder_name in rows[1]:
#         self_prior_xml.append("YES")
#     else:
#         self_prior_xml.append("NO")
# xml_esp_prev["SELF_PRIOR_EXIST_OR_NOT"]=[i for i in self_prior_xml]
# #xml_esp_prev.to_excel("xml_esp_prev.xlsx", sheet_name='xml_esp',index=False)
# xml_full=xml_esp_prev.append(xml_esp_out_prev, ignore_index=True).fillna("")
# xml_esp_combined=pd.merge(xml_full,WAIT_ESP, on=WAIT_ESP.columns[0],how="outer").fillna("")
# xml_esp_combined=xml_esp_combined.drop_duplicates(keep="first").reset_index().iloc[:,1:]
# xml_esp_combined[xml_esp_combined.columns[-2]]=["_" if i=="" else i for i in xml_esp_combined[xml_esp_combined.columns[-2]]]
# xml_esp_combined[xml_esp_combined.columns[-1]]=["_" if i=="" else i for i in xml_esp_combined[xml_esp_combined.columns[-1]]]
# #xml_esp_combined.to_excel("final.xlsx", sheet_name='xml_esp',index=False)
# xml_esp_combined["Matched"]=[ "YES" if "YESWAITS"==i else "YES" if "NONO_WAIT"==i  else "NO" for i in xml_esp_combined[xml_esp_combined.columns[-2]]+xml_esp_combined[xml_esp_combined.columns[-1]] ]
# xml_esp_combined[xml_esp_combined.columns[1]]=["\n".join([j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")]) for  i in xml_esp_combined[xml_esp_combined.columns[1]]]
# xml_esp_combined[xml_esp_combined.columns[2]]=["\n".join([j.replace("'","").strip().upper() for j in  i.strip("[]").split(",")]) for  i in xml_esp_combined[xml_esp_combined.columns[2]]]
# xml_esp_combined=xml_esp_combined[xml_esp_combined[xml_esp_combined.columns[4]]!="_"]
# xml_esp_combined.to_excel("ESP_XML_SELF_PROIR_OUTPUT.xlsx", sheet_name='ESP_XML_SELF_PROIR',index=False)
print(f"completed in {datetime.now()-start}")