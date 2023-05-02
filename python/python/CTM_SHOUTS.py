from datetime import datetime
import sys
import pandas as pd
import xml.etree.ElementTree as et

from pyparsing import col
pd.options.mode.chained_assignment = None
pd.set_option("display.max_colwidth", 10000)
print("Program executing Please wait!")
start=datetime.now()
ctm_file=sys.argv[1]
class CTM_SHOUT_DETAILS:
    def __init__(self,ctm_file):
        self.ctm_file=ctm_file
    def ctm_details(self):
        parsexml=et.parse(self.ctm_file)
        root=parsexml.getroot()
        xml=[]
        for r in root:
            Folder_name,Parent_folder,appl,sub_appl=r.attrib.get('FOLDER_NAME',""),r.attrib.get('PARENT_FOLDER',""),r.attrib.get('APPLICATION',""),r.attrib.get('SUB_APPLICATION',"")
            shouts=r.findall('SHOUT')
            for shout in shouts:
                xml.append([Folder_name,Parent_folder,'',appl,sub_appl]+self.SHOUT1(shout))
            JOB=r.findall('JOB')
            for j in JOB:
                var=j.attrib
                PARENT_FOLDER,JOBNAME,appl,sub_appl=var.get('PARENT_FOLDER',""),var.get("JOBNAME",""),var.get('APPLICATION',""),var.get('SUB_APPLICATION',"")
                shouts=j.findall('SHOUT')
                for shout in shouts:
                    xml.append(['',PARENT_FOLDER,JOBNAME,appl,sub_appl]+self.SHOUT1(shout))
            for r1 in r.findall("./"):  
                if r1.tag in ['FOLDER','SMART_FOLDER','SUB_FOLDER']:
                    Folder_name,Parent_folder,appl,sub_appl=r1.attrib.get('JOBNAME',""),r1.attrib.get('PARENT_FOLDER',""),r1.attrib.get('APPLICATION',""),r1.attrib.get('SUB_APPLICATION',"")
                    shouts=r.findall('SHOUT')
                    for shout in shouts:
                        xml.append([Folder_name,Parent_folder,'',appl,sub_appl]+self.SHOUT1(shout))
                JOB=r1.findall('JOB')
                for j in JOB:
                    var=j.attrib
                    PARENT_FOLDER,JOBNAME,appl,sub_appl=var.get('PARENT_FOLDER',""),var.get("JOBNAME",""),var.get('APPLICATION',""),var.get('SUB_APPLICATION',"")
                    shouts=j.findall('SHOUT')
                    for shout in shouts:
                        xml.append(['',PARENT_FOLDER,JOBNAME,appl,sub_appl]+self.SHOUT1(shout))
                for r2 in r1.findall("./"):
                    if r2.tag in ['FOLDER','SMART_FOLDER','SUB_FOLDER']:
                        Folder_name,Parent_folder,appl,sub_appl=r2.attrib.get('JOBNAME',""),r2.attrib.get('PARENT_FOLDER',""),r2.attrib.get('APPLICATION',""),r2.attrib.get('SUB_APPLICATION',"")
                        shouts=r.findall('SHOUT')
                        for shout in shouts:
                            xml.append([Folder_name,Parent_folder,'',appl,sub_appl]+self.SHOUT1(shout))
                    JOB=r2.findall('JOB')
                    for j in JOB:
                        var=j.attrib
                        PARENT_FOLDER,JOBNAME,appl,sub_appl=var.get('PARENT_FOLDER',""),var.get("JOBNAME",""),var.get('APPLICATION',""),var.get('SUB_APPLICATION',"")
                        shouts=j.findall('SHOUT')
                        for shout in shouts:
                            xml.append(['',PARENT_FOLDER,JOBNAME,appl,sub_appl]+self.SHOUT1(shout))
            
        return xml
    def SHOUT1(self,SHOUT):
        L_SHOUT=[""]*6
        v=SHOUT.attrib
        L_SHOUT[0],L_SHOUT[1],L_SHOUT[2],L_SHOUT[3],L_SHOUT[4],L_SHOUT[5]=v.get("WHEN",""),v.get("TIME",""),v.get("DEST",""),v.get("MESSAGE",""),v.get("URGENCY",""),v.get("DAYSOFFSET","")
        return L_SHOUT
ctm=CTM_SHOUT_DETAILS(ctm_file)
#ctm.ctm_details()
pd.DataFrame(ctm.ctm_details(),columns=['FOLDER_NAME','PARENT_FOLDER','JOBS','APPLICATION','SUB_APPLICATION','When Condition','Shout Time','To','Message','Urgency','Days Offset']).to_excel("CTM_SHOUT_DETAILS_"+str(datetime.now().strftime("%H%M%S"))+".xlsx",sheet_name="CTM_SHOUTS",index=False)
print(f"completed in {datetime.now()-start}")