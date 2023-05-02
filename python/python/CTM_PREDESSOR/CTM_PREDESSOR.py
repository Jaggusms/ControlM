from datetime import datetime
from itertools import count
import sys
import pandas as pd
import xml.etree.ElementTree as et
pd.options.mode.chained_assignment = None
pd.set_option("display.max_colwidth", 10000)
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
if not (xml_file.lower().endswith("xml")):
    print("Please pass valide params 1. xml_file")
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
data["PARENT_FOLDER"]=data["PARENT_FOLDER"].apply(lambda x:x.upper())
data["JOBNAME"]=data["JOBNAME"].apply(lambda x:x.upper())
data['str_OUTCOND']=[" \n".join(i)  for i in data['OUTCOND'] ]
def find_all_duplicates(l):
    duplacated=list({x for x in l if l.count(x) > 1})
    return "" if len(duplacated)==0 else duplacated
data['duplicated_OUTCOND']=data['OUTCOND'].apply(find_all_duplicates)
data['duplicated_INCOND']=data['INCOND'].apply(find_all_duplicates)
data['OUTCOND']=[[j for j in i if not j.endswith("-")]  for i in data['OUTCOND'] ]
Matched_In_Out_Conditions=[]
Matched_In_Out_Conditions_index=[]
Same_In_Out_in_different_folder=[]
Same_In_Out_in_different_folder_index=[]
Not_exist_OutConditions=[]
Not_exist_OutConditions_index=[]
for i,row in data[data.columns[[0,2,3]]].iterrows():
    predessor1=[]
    predessor2=[]
    if len(row[2])==0:
        Matched_In_Out_Conditions.append(",".join(predessor1))
        Matched_In_Out_Conditions_index.append(i)
    else:
        Not_exist=[]
        a=b=c=0
        for in_cond in row[2]:
            inconditon=in_cond[:in_cond.find(" ")]
            new_data=data[data.str_OUTCOND.str.contains(inconditon)]
            if len(new_data.index)==0:
                a=1
                Not_exist.append(in_cond)
                Not_exist_OutConditions_index.append(i)
            elif len(new_data.index)>1:
                b=1
                #Same_In_Out_.append(inconditon)
                predessor2.append(",".join([i[0]  if i[0]==i[1] else "-".join(i) if row[0]==i[0] else i[1]+"("+i[0]+")"  for i in new_data[['PARENT_FOLDER','JOBNAME']].values.tolist()]))
                #jobs.append(",".join(new_data['JOBNAME'].tolist()))
                #predessor1="\n".join([j for j in  list(new_data['JOBNAME'])])              
                Same_In_Out_in_different_folder_index.append(i)
            else:
                c=1
                #Matched_In_Out_.append(inconditon)
                #predessor1="\n".join([f+"-"+ j for f,j in  zip(list(new_data['PARENT_FOLDER']),list(new_data['JOBNAME']))])
                if new_data['TAG'].tolist()[0]=='JOB':
                    if row[0]==new_data['PARENT_FOLDER'].tolist()[0]:
                        predessor1.append(",".join(new_data['JOBNAME'].tolist()))
                    else:
                        predessor1.append(new_data['JOBNAME'].tolist()[0]+"("+new_data['PARENT_FOLDER'].tolist()[0]+")")
                else:
                    predessor1.append(",".join(new_data['JOBNAME'].tolist()))
                Matched_In_Out_Conditions_index.append(i)
        if a:
            Not_exist_OutConditions.append("\n".join(Not_exist))
        if b:
            #only_jobs.append(",".join(jobs))
            Same_In_Out_in_different_folder.append(",".join(predessor2))
        if c:
            Matched_In_Out_Conditions.append(",".join(list(set(predessor1))))
def convert_to_string(df):
    df=df
    for i in df.columns:
        df[i]=[str(i) for i in df[i]]
    return df

matched_data=data.iloc[list(set(Matched_In_Out_Conditions_index)),[0,1,2,6,7]]
matched_data['predessor']=Matched_In_Out_Conditions
Not_exist=data.iloc[list(set(Not_exist_OutConditions_index)),[0,1,2,6,7]]
Not_exist['not_exist_condition']=Not_exist_OutConditions
Same_In_Out=data.iloc[list(set(Same_In_Out_in_different_folder_index)),[0,1,2,6,7]]
Same_In_Out['predessor']=Same_In_Out_in_different_folder

matched_data=convert_to_string(matched_data).drop_duplicates().reset_index(drop=True)
Not_exist=convert_to_string(Not_exist).drop_duplicates().reset_index(drop=True)
Same_In_Out=convert_to_string(Same_In_Out).drop_duplicates().reset_index(drop=True)
with pd.ExcelWriter("CTM_In-Out_Conditions"+str(datetime.now().strftime("%H%M%S"))+".xlsx") as w:
    #data.to_excel(w, sheet_name='data',index=False)
    matched_data.to_excel(w, sheet_name='matched_data',index=False)
    Same_In_Out.to_excel(w, sheet_name='Same_In_Out',index=False)
    Not_exist.to_excel(w, sheet_name='Not_exist',index=False)
print(f"completed in {datetime.now()-start}")