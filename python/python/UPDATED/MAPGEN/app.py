from datetime import datetime
import sys
import pandas as pd
pd.options.mode.chained_assignment = None
pd.set_option("display.max_colwidth", 10000)
print("Program executing Please wait!")
start=datetime.now()
mapgen_file,ctm_file=sys.argv[1],sys.argv[2]
class predessors_matching:
    def __init__(self,mapgen_file,ctm_file):
        self.mapgen_file=mapgen_file
        self.ctm_file=ctm_file
    def mapgen(self):
        mapgen_data=pd.read_excel(self.mapgen_file,sheet_name=0,usecols="A,D,E").fillna("")
        mapgen_data["A_j"]=mapgen_data[mapgen_data.columns[0]].str.upper()+mapgen_data[mapgen_data.columns[1]].str.upper()
        return mapgen_data
    def ctm(self):
        CTM_DATA=pd.read_excel(self.ctm_file,sheet_name=1,usecols="B,E,F,G").fillna("")
        CTM_DATA=CTM_DATA[CTM_DATA.TAG=="JOB"].iloc[:,1:]
        CTM_DATA["A_j"]=CTM_DATA[CTM_DATA.columns[1]].str.upper()+CTM_DATA[CTM_DATA.columns[0]].str.upper()
        return CTM_DATA

object=predessors_matching(mapgen_file,ctm_file)
data=pd.merge(object.mapgen(),object.ctm(),on="A_j",how="outer").fillna("")
def matching(mapgen_predessor,ctm_predessor):
    matched=[]
    Matched_Conditions=[]
    Extra_condition_In_ESP=[]
    Extra_condition_In_CTM=[]
    for m,c in zip(mapgen_predessor,ctm_predessor):
        if m.upper()==c:
            matched.append("YES")
            Matched_Conditions.append(m)
            Extra_condition_In_ESP.append("")
            Extra_condition_In_CTM.append("")
        else:
            m=m.upper().split(",")
            c=c.split(",")
            Matched_Conditions_=[]
            Extra_condition_In_ESP_=[]
            Extra_condition_In_CTM_=[]
            for i in m:
                a=1
                for j in c:
                    if i==j:
                        a=0
                        Matched_Conditions_.append(j)
                        break
                if a:
                    Extra_condition_In_ESP_.append(i)
            for j in c:
                a=1
                for i in m:
                    if i==j:
                        a=0
                        Matched_Conditions_.append(j)
                        break
                if a:
                    Extra_condition_In_CTM_.append(j)
            if len(Extra_condition_In_ESP_)==0 and len(Extra_condition_In_CTM_)==0:
                matched.append("YES")
                Matched_Conditions.append(",".join(list(set(Matched_Conditions_))))
                Extra_condition_In_ESP.append("")
                Extra_condition_In_CTM.append("")
            else:
                matched.append("NO")
                Matched_Conditions.append(",".join(list(set(Matched_Conditions_))))
                Extra_condition_In_ESP.append(",".join(Extra_condition_In_ESP_))
                Extra_condition_In_CTM.append(",".join(Extra_condition_In_CTM_))
    return matched,Matched_Conditions,Extra_condition_In_ESP,Extra_condition_In_CTM
compare=matching(list(data[data.columns[2]]),list(data[data.columns[6]]))
data['matched']=compare[0]
data['Matched_Conditions']=compare[1]
data['Extra_condition_In_ESP']=compare[2]
data['Extra_condition_In_CTM']=compare[3]
data=data.rename(columns={'APPL NAME':'APPL NAME(Mapgen)','JOB NAMEUpdated':'JOB NAME Updated(Mapgen)','AFTERUpdated':'AFTER Updated(Mapgen)','APPL_NAME':'APPL_NAME(CTM)','new_jobs_with_Impacted':'new_jobs_with_Impacted(CTM)','new_predessor_with_Impacted':'new_predessor_with_Impacted(CTM)'})
data.to_excel("CTMvsMapgen_Output_Compare"+str(datetime.now().strftime("%H%M%S"))+".xlsx",sheet_name="CTMvsMapgen_Output_Compare",index=False)
#BPHNMRW1	BI_BDFLND_ODS_RAWZ_ODS_MEMBER_0003

print(f"completed in {datetime.now()-start}")