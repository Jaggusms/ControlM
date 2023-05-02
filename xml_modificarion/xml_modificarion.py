import xml.etree.ElementTree as ET
import pandas as pd
import sys
from datetime import datetime
pd.options.mode.chained_assignment = None
XML_DATA=pd.read_excel("TEST1.XLSX").fillna("")
for i in XML_DATA.columns:
    XML_DATA[i]=XML_DATA[i].apply(lambda x: str(x).strip())
def try_to_change_int(x):
    try:
        x=str(round(float(x)))
    except:
        pass
    return x
def try_to_eval(x):
    try:
        x=eval(x)
    except:
        pass
    return x 

def variable_tag_adding(row,memory):
    variable_data=[(i[:i.find(':')], i[i.find(':')+1:]) for i in row.split("\n") if i !=""] 
    #print(row[0],variable_data)
    for data in variable_data:
        variable_data_tag=ET.Element('VARIABLE')
        variable_data_tag.set('NAME',data[0])
        variable_data_tag.set('VALUE',data[1])
        memory.append(variable_data_tag)
def control_tag_adding(row,memory):
    CONTROL_DATA=[(i[:-2], i[-1]) for i in row.split("\n") if i !=""] 
    for data in CONTROL_DATA:
        CONTROL_DATA_tag=ET.Element('CONTROL')
        CONTROL_DATA_tag.set('NAME',data[0])
        CONTROL_DATA_tag.set('TYPE',data[1])
        CONTROL_DATA_tag.set('ONFAIL','R')
        memory.append(CONTROL_DATA_tag)

def INCOND_tag_adding(row1,row2,row3,memory):
    INCOND_DATA=[(i[:i.find(':')], i[i.find(':')+1:]) for i in row3.split("\n") if i!=""]
    for data in INCOND_DATA:
        INCOND_DATA_tag=ET.Element('INCOND')
        if "CTMFW_FOR" in data[0]:
            INCOND_DATA_tag.set('NAME',data[0][data[0].find("CTMFW_"):]+"-TO-"+row1+"-"+row2)
        else:
            if "/" in data[0]:
                if row1==" ":
                    INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row2)
                else:
                    INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row1.replace("/","-").replace(" ","")+"-"+row2)
            else:
                INCOND_DATA_tag.set('NAME',data[0].replace(" ","")+"-TO-"+row2)
        INCOND_DATA_tag.set('ODATE',data[1])
        INCOND_DATA_tag.set('AND_OR','A')
        OUTCOND_DATA_tag=ET.Element('OUTCOND')
        if "CTMFW_FOR" in data[0]:
            OUTCOND_DATA_tag.set('NAME',data[0][data[0].find("CTMFW_"):]+"-TO-"+row1+"-"+row2)
        else:
            if "/" in data[0]:
                if row1==" ":
                    OUTCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row2)
                else:
                    OUTCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row1.replace("/","-").replace(" ","")+"-"+row2)
            else:
                OUTCOND_DATA_tag.set('NAME',data[0].replace(" ","")+"-TO-"+row2)
    
        OUTCOND_DATA_tag.set('ODATE',data[1])
        OUTCOND_DATA_tag.set('SIGN','-')
        memory.append(INCOND_DATA_tag)
        memory.append(OUTCOND_DATA_tag)

def OUTCOND_tag_adding(row1,row2,row3,memory):
    OUTCOND_DATA=[i for i in row3.split("\n") if i !=""]
    for data in OUTCOND_DATA:
        OUTCOND_DATA_tag=ET.Element('OUTCOND')
        if "/" in data:
            if row1==" ":
                OUTCOND_DATA_tag.set('NAME',row2+"-TO-"+data.replace("/","-").replace(" ",""))
            else:
                OUTCOND_DATA_tag.set('NAME',row1.replace("/","-").replace(" ","")+"-"+row2+"-TO-"+data.replace("/","-").replace(" ",""))
        else:
            OUTCOND_DATA_tag.set('NAME',row2+"-TO-"+data.replace(" ",""))
        OUTCOND_DATA_tag.set('ODATE','ODAT')
        OUTCOND_DATA_tag.set('SIGN','+')
        memory.append(OUTCOND_DATA_tag)  

def MAIL_tag_adding(row,memory):
    d=try_to_eval(row)
    if isinstance(d,dict):
        d1=dict()
        d1["1"]=d if d.get("1",0)==0 else d.get("1")
        MAILS=d1.values() if d.get("2",0)==0 else d.values()
        for mail in MAILS:
            MAIL_ON_DATA_tag=ET.Element('ON')
            MAIL_ON_DATA_tag.set('STMT','*')
            if mail.get("STATUS","").upper()=="1":
                MAIL_ON_DATA_tag.set('CODE','OK')
            else:
                MAIL_ON_DATA_tag.set('CODE','NOTOK')
            DOMAIL_tag=ET.Element('DOMAIL')
            DOMAIL_tag.set('URGENCY','R')
            DOMAIL_tag.set('DEST',mail.get("TO",""))
            DOMAIL_tag.set('CC_DEST',mail.get("CC",""))
            DOMAIL_tag.set('SUBJECT',mail.get("SUBJECT",""))
            DOMAIL_tag.set('MESSAGE',"0011"+mail.get("MESSAGE",""))
            DOMAIL_tag.set('ATTACH_SYSOUT',mail.get("ATTACH_OUTPUT",""))
            MAIL_ON_DATA_tag.append(DOMAIL_tag)
            memory.append(MAIL_ON_DATA_tag)

def QUANTITATIVE_tag_adding(row,memory):
    QUANTITATIVE_DATA=[i for i in row.replace(" ","").split(",") if i!=""]
    for value in QUANTITATIVE_DATA:
        QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
        QUANTITATIVE_DATA_TAG.set('NAME',value)
        for key,value in default_keys()[0].items():
            QUANTITATIVE_DATA_TAG.set(key,value)
        memory.append(QUANTITATIVE_DATA_TAG)

def EVENT_on_tag_adding(row,memory):
    EVENT_ON_DATA=row
    if EVENT_ON_DATA.upper()=='YES':
        EVENT_ON_DATA_tag=ET.Element('ON')
        EVENT_ON_DATA_tag.set('STMT','*')
        EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
        DOACTION_tag=ET.Element('DOACTION')
        DOACTION_tag.set('ACTION','OK')
        EVENT_ON_DATA_tag.append(DOACTION_tag)
        memory.append(EVENT_ON_DATA_tag)

def PRED_ON_tag_adding(row,row3,memory):
    PRED_ON_data=[i for i in row.split("\n") if i !=""]
    for cond in PRED_ON_data:
        PRED_ON_DATA_tag=ET.Element('ON')
        PRED_ON_DATA_tag.set('STMT','*')
        PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
        DOACTION_tag=ET.Element('DOACTION')
        DOACTION_tag.set('ACTION','OK')
        PRED_ON_DATA_tag.append(DOACTION_tag)
        memory.append(PRED_ON_DATA_tag)
        PRED_ON_DATA_tag=ET.Element('ON')
        PRED_ON_DATA_tag.set('STMT','*')
        PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
        DOCOND_tag=ET.Element('DOCOND')
        DOCOND_tag.set('NAME',row3+"-TO-"+cond.replace("/","-").replace(" ",""))
        DOCOND_tag.set('ODATE','ODAT')
        DOCOND_tag.set('SIGN','+')
        PRED_ON_DATA_tag.append(DOCOND_tag)
        memory.append(PRED_ON_DATA_tag)

def RBC_TAG_Adding(row,memory):
    RBC_data=[i for i in row.split("\n") if i !=""]
    if len(RBC_data)==0:
        RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
        RULE_BASED_CALENDARS.set('NAME','EVERYDAY')
        memory.append(RULE_BASED_CALENDARS)
    for calender in RBC_data:
        calender_details=try_to_eval(calender)
        if isinstance(calender_details,dict):
            RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
            RULE_BASED_CALENDARS.set('NAME',calender_details.get("NAME").upper())
            memory.append(RULE_BASED_CALENDARS)
        else: 
            RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
            RULE_BASED_CALENDARS.set('NAME',calender)
            memory.append(RULE_BASED_CALENDARS)


for i in ['CYCLIC','MAXWAIT','MAXRERUN','CONFIRM']:
    XML_DATA[i]=XML_DATA[i].apply(try_to_change_int)
with open('TEST.xml', 'r') as f:
    data = f.read() 
tree = ET.ElementTree(ET.fromstring(data))
root=tree.getroot()
FOLDER_COLUMNS=XML_DATA.columns[[6,8]+list(range(9,19))]
SUB_FOLDER_COLUMS=XML_DATA.columns[[8]+list(range(9,19))]
JOB_COLUMNS=XML_DATA.columns[[7,9]+list(range(9,19))]
def commands_formating(l,command):
    cmd=""
    if l[-1]!="":
        cmd=l[-1]
    elif l[3]!="" or l[4]!="" or l[5]!="" :
        command_list=[i for i in command.split(" ") if i!=""]
        command_list[1]=l[0] if l[0]!="" else command_list[1]
        command_list[2]=l[4] if l[4]!="" else command_list[2]
        command_list[3]=l[0] if l[3]!="" else command_list[3]
        command_list[4]=l[0] if l[5]!="" else command_list[4]
        als='/usr/bin/ksh wrapperscript foldername infaworkflow paramfile'
        cmd=" ".join(command_list) 
    elif l[1]!="" or l[2]!="" :
        als='/usr/bin/ksh wrapperscript path/listfilename'
        listfilename=command.split("/")[-1]
        #print(listfilename)
        cd=[i for i in command.split(" ") if i!=""]
        wrapperscript=cd[1]
        #print(wrapperscript)
        s_path=cd[2]
        path=s_path[:s_path.find(listfilename)-2]
        #print(path)
        command1=command.replace(wrapperscript,l[0]) if l[0]!="" else command
        command1=command1.replace(listfilename,l[1]) if l[1]!="" else command1
        command1=command1.replace(path,l[2]) if l[2]!="" else command1
        cmd=command1
    else:
        cmd=command    
    return cmd,cmd==command
    
def commands_generate(df):
    commands=[]
    for idx, row in df.iterrows():
        if len(row[-1])>0:
            commands.append(row[-1])
        elif len(row[1])>0:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}{row[1].strip()}" if row[2].strip().endswith("/") else f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}/{row[1].strip()}"
            commands.append(cmd)
        elif len(row[4])>0:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[4].strip()} {row[3].strip()} {row[5].strip()}"
            commands.append(cmd)
        else:
            commands.append("")
    return commands
full_time=datetime.now()    
date=full_time.strftime("%Y%m%d")
time=full_time.strftime("%H%M%S")
def default_keys():
    QUANTITATIVE_default_keys={"QUANT":"1","ONFAIL":"R","ONOK":"R"}
    job_default_keys={"JOBISN":"1","APPL_TYPE":"OS","TASKTYPE":"Command","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","TIMETO":">","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","END_FOLDER":"N","CYCLIC_TOLERANCE":"0","CYCLIC_TYPE":"C","VERSION_HOST":"VA10P50185","SYSDB":"0","IND_CYCLIC":"T","RULE_BASED_CALENDAR_RELATIONSHIP":"A"}
    smart_folder_default_keys={"CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"SMART Table","IS_CURRENT_VERSION":"Y","DAYSKEEPINNOTOK":"0","ENFORCE_VALIDATION":"N","USED_BY_CODE":"0","PLATFORM":"UNIX","MODIFIED":"False","TYPE":"2"}
    sub_folder_default_keys={"JOBISN":"2","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"Sub-Table","CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","USE_INSTREAM_JCL":"N","VERSION_OPCODE":"N","IS_CURRENT_VERSION":"Y","VERSION_SERIAL":"1"}
    RBC_SCDULE={'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'LEVEL':"N"}  
    return QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys,sub_folder_default_keys,RBC_SCDULE
for idx,row in XML_DATA.iterrows():
    default=default_keys()
    QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys=default[0],default[1],default[2]
    if row[2]=='SMART_FOLDER':
        for idx,smart_folder in enumerate(root.findall("SMART_FOLDER[@FOLDER_NAME='"+row[1]+"']")):
            smd=row[FOLDER_COLUMNS].to_dict()
            for key,value in smd.items():
                if key=='FOLDER_ORDER_METHOD' and value =="":
                    pass
                if value!="":
                    smart_folder.set(key,value)
            old_CONTROL=set(CONTROL.get("NAME").upper()+":"+CONTROL.get("TYPE").upper() for CONTROL in smart_folder.findall("CONTROL"))
            need_modified_CONTROL=set([i.upper() for i in row[22].split("\n") if i!=""])
            new_addition_CONTROL=need_modified_CONTROL-old_CONTROL
            need_to_delete_CONTROL=need_modified_CONTROL-new_addition_CONTROL
            #print(new_addition_CONTROL,need_to_delete_CONTROL)
            for CONTROL in need_to_delete_CONTROL:
                CONTROL_tag=smart_folder.find("CONTROL[@NAME='"+CONTROL[:CONTROL.find(":")]+"']")
                smart_folder.remove(CONTROL_tag)
            for CONTROL in new_addition_CONTROL:
                CONTROL_DATA_tag=ET.Element('CONTROL')
                CONTROL_DATA_tag.set('NAME',CONTROL[:CONTROL.find(":")])
                CONTROL_DATA_tag.set('TYPE',CONTROL[-1])
                CONTROL_DATA_tag.set('ONFAIL','R')
                smart_folder.append(CONTROL_DATA_tag)  

            old_OUTCONDS=set(OUTCOND.get("NAME").upper() for OUTCOND in smart_folder.findall("OUTCOND"))
            need_modified_OUTCONDS=set([row[1].upper()+"-TO-"+i.upper() for i in row[5].split("\n") if i!=""])
            new_addition_OUTCONDS=need_modified_OUTCONDS-old_OUTCONDS
            need_to_delete_OUTCONDS=need_modified_OUTCONDS-new_addition_OUTCONDS
            # print(new_addition_OUTCONDS)
            # print(need_to_delete_OUTCONDS)
            for outcond in need_to_delete_OUTCONDS:
                outcond_tag=smart_folder.find("OUTCOND[@NAME='"+outcond+"']")
                #print(qua_tag.attrib)
                smart_folder.remove(outcond_tag)
            for outcond in new_addition_OUTCONDS:
                QUANTITATIVE_DATA_TAG=ET.Element('OUTCOND')
                QUANTITATIVE_DATA_TAG.set('NAME',outcond)
                QUANTITATIVE_DATA_TAG.set('ODATE','ODAT')
                QUANTITATIVE_DATA_TAG.set('SIGN','+')
                # print(QUANTITATIVE_DATA_TAG.attrib)
                smart_folder.append(QUANTITATIVE_DATA_TAG)

    elif row[2]=='SUB_FOLFER':
        pass
    elif row[2]=='JOB':
        job_name=[i for i in row[3].split("\n") if i!=""]
        #print(job_name)
        if len(job_name)==1:
            which_job_needTo_Match=job_name[0]
        else:
            which_job_needTo_Match=[i for i in job_name if i.upper()[-1]=="D"][0]
        # print(which_job_needTo_Match)
        # continue
        #print(which_job_needTo_Match)
        if len(root.findall("SMART_FOLDER/JOB[@JOBNAME='"+which_job_needTo_Match[:-2]+"']"))!=0:
            for idx,JOB in enumerate(root.findall("SMART_FOLDER/JOB[@JOBNAME='"+which_job_needTo_Match[:-2]+"']")):
                if row[0]==JOB.attrib.get("PARENT_FOLDER"):
                    
                    if which_job_needTo_Match[-1].upper()=="D" and len(job_name)==1 :
                        root.find("SMART_FOLDER[@FOLDER_NAME='"+row[0]+"']").remove(JOB)
                        # print(which_job_needTo_Match)
                    
                    if  which_job_needTo_Match[-1].upper()=="C" or len(job_name)==2 :
                        # print(which_job_needTo_Match)
                        smd=row[JOB_COLUMNS].to_dict()
                        if len(job_name)==2:
                            updated_job=[i for i in job_name if i.upper()[-1]=="A"][0]
                            smd.update({"JOBNAME": updated_job[:updated_job.find(":")]})
                        cmd=commands_formating(row[range(23,30)].to_list(),JOB.get("CMDLINE"))
                        if not cmd[1]:
                            smd.update({"CMDLINE":cmd[0]})
                        for key,value in smd.items():
                            if value!="":
                                JOB.set(key,value)
                        
                        old_VARIABLE=set(VARIABLE.get("NAME")+":"+VARIABLE.get("VALUE") for VARIABLE in JOB.findall("VARIABLE"))
                        need_modified_VARIABLE=set([i for i in row[20].split("\n") if i!=""])
                        new_addition_VARIABLE=need_modified_VARIABLE-old_VARIABLE
                        need_to_delete_VARIABLE=need_modified_VARIABLE-new_addition_VARIABLE
                        # print(new_addition_VARIABLE,need_to_delete_VARIABLE)
                        for VARIABLE in need_to_delete_VARIABLE:
                            VARIABLE_tag=JOB.find("VARIABLE[@NAME='"+VARIABLE[:VARIABLE.find(":")]+"']")
                            JOB.remove(VARIABLE_tag)
                        for VARIABLE in new_addition_VARIABLE:
                            VARIABLE_DATA_tag=ET.Element('VARIABLE')
                            VARIABLE_DATA_tag.set('NAME',VARIABLE[:VARIABLE.find(":")])
                            VARIABLE_DATA_tag.set('VALUE',VARIABLE[VARIABLE.find(":")+1:])
                            JOB.append(VARIABLE_DATA_tag)  

                        
                        old_qua_memory={qua.get("NAME").upper():qua for qua in JOB.findall("QUANTITATIVE")}
                        old_qua=set(old_qua_memory.keys())
                        need_modified_qua=set([i.upper() for i in row[22].split(",") if i!=""])
                        new_addition_qua=need_modified_qua-old_qua
                        need_to_delete_qua=need_modified_qua-new_addition_qua
                        # print(need_to_delete_qua)
                        # print(new_addition)
                        for qua in need_to_delete_qua:
                            #qua_tag=JOB.find("QUANTITATIVE[@NAME='"+qua+"']")
                            #print(qua_tag.attrib)
                            JOB.remove(old_qua_memory.get(qua))
                        for qua in new_addition_qua:
                            QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                            QUANTITATIVE_DATA_TAG.set('NAME',qua)
                            for key,value in default_keys()[0].items():
                                QUANTITATIVE_DATA_TAG.set(key,value)
                            # print(QUANTITATIVE_DATA_TAG.attrib)
                            JOB.append(QUANTITATIVE_DATA_TAG)


                        old_INCOND=set(INCOND.get("NAME").upper()+":"+INCOND.get("ODATE").upper() for INCOND in JOB.findall("INCOND"))
                        need_modified_INCOND=set([i.upper() for i in row[4].split("\n") if i!=""])
                        need_modified_INCOND=set([i[:i.find(":")]+"-TO-"+row[3][:row[3].find(":")]+":"+i[i.find(":")+1:] if "/" not in i else i[:i.find(":")].replace("/","-").replace(" ","")+"-TO-"+row[0]+"-"+row[3][:row[3].find(":")]+":"+i[i.find(":")+1:]  for i in need_modified_INCOND])
                        #print(old_INCOND,need_modified_INCOND)
                        new_addition_INCOND=need_modified_INCOND-old_INCOND
                        need_to_delete_INCOND=need_modified_INCOND-new_addition_INCOND
                        #print(new_addition_INCOND,need_to_delete_INCOND)
                        for INCOND in need_to_delete_INCOND:
                            INCOND_tag=JOB.findall("INCOND[@NAME='"+INCOND[:INCOND.find(":")]+"']")
                            for i in INCOND_tag:
                                if i.attrib.get("ODATE") ==INCOND[INCOND.find(":")+1:]:
                                    JOB.remove(i)
                            OUTCOND_tag=JOB.findall("OUTCOND[@NAME='"+INCOND[:INCOND.find(":")]+"']")
                            for i in OUTCOND_tag:
                                if i.attrib.get("ODATE") ==INCOND[INCOND.find(":")+1:]:
                                    JOB.remove(i)
                        for data in new_addition_INCOND:
                            INCOND_DATA_tag=ET.Element('INCOND')
                            INCOND_DATA_tag.set('NAME',data[:data.find(":")])
                            INCOND_DATA_tag.set('ODATE',data[data.find(":")+1:])
                            INCOND_DATA_tag.set('AND_OR','A')

                            OUTCOND_DATA_tag=ET.Element('OUTCOND')
                            OUTCOND_DATA_tag.set('NAME',data[:data.find(":")])
                            OUTCOND_DATA_tag.set('ODATE',data[data.find(":")+1:])
                            OUTCOND_DATA_tag.set('SIGN','-')
                            JOB.append(INCOND_DATA_tag)
                            JOB.append(OUTCOND_DATA_tag) 

                        
                        #old_OUTCONDS=set(OUTCOND.get("NAME").upper(): for OUTCOND in JOB.findall("OUTCOND"))
                        old_OUTCONDS_memory={OUTCOND.get("NAME").upper():OUTCOND for OUTCOND in JOB.findall("OUTCOND")}
                        old_OUTCONDS=set(old_OUTCONDS_memory.keys())
                        need_modified_OUTCONDS=set([which_job_needTo_Match[:-2].upper()+"-TO-"+i.upper() for i in row[5].split("\n") if i!=""])
                        new_addition_OUTCONDS=need_modified_OUTCONDS-old_OUTCONDS
                        need_to_delete_OUTCONDS=need_modified_OUTCONDS-new_addition_OUTCONDS
                        # print(new_addition_OUTCONDS,need_to_delete_OUTCONDS)
                        for outcond in need_to_delete_OUTCONDS:
                            #outcond_tag=smart_folder.find("OUTCOND[@NAME='"+outcond+"']")
                            #print(qua_tag.attrib)
                            JOB.remove(old_OUTCONDS_memory.get(outcond))
                        for outcond in new_addition_OUTCONDS:
                            QUANTITATIVE_DATA_TAG=ET.Element('OUTCOND')
                            QUANTITATIVE_DATA_TAG.set('NAME',outcond)
                            QUANTITATIVE_DATA_TAG.set('ODATE','ODAT')
                            QUANTITATIVE_DATA_TAG.set('SIGN','+')
                            # print(QUANTITATIVE_DATA_TAG.attrib)
                            smart_folder.append(QUANTITATIVE_DATA_TAG)

                        # old_RBC_memory={RBC.get("NAME").upper():RBC for RBC in JOB.findall("RULE_BASED_CALENDARS")}
                        # old_RBC=set(old_RBC_memory.keys())
                        # need_modified_RBC=set([i.upper() for i in row[20].split(",") if i!=""])
                        # new_addition_RBC=need_modified_RBC-old_RBC
                        # need_to_delete_RBC=need_modified_RBC-new_addition_RBC
                        # #print(new_addition_RBC,need_to_delete_RBC)
                        # for RBC in need_to_delete_RBC:
                        #     #RBC_tag=JOB.find("RULE_BASED_CALENDARS[@NAME='"+RBC+"']")
                        #     #print(qua_tag.attrib)
                        #     JOB.remove(old_RBC_memory.get(RBC))
                        # for RBC in new_addition_RBC:
                        #     RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
                        #     RULE_BASED_CALENDARS.set('NAME',RBC)
                        #     JOB.append(RULE_BASED_CALENDARS)
                else:
                    if ":" not in which_job_needTo_Match.upper() and len(job_name)==1:
                        smart_folder=root.find("SMART_FOLDER[@FOLDER_NAME='"+row[0]+"']")
                        oneOfJob_details=smart_folder.find("JOB")
                        #print(oneOfJob_details.attrib)
                        JOB=ET.Element('JOB')
                        job_keys=row[XML_DATA.columns[[0,3,7,9]+list(range(10,19))]].to_dict()
                        #print(job_keys)
                        for key,value in oneOfJob_details.attrib.items():
                            if job_keys.get(key,"")!="":
                                JOB.set(key,job_keys.get(key))
                            else:
                                JOB.set(key,value)
                        
                        cmd=commands_generate(pd.DataFrame([list(row[23:30])],columns=list(XML_DATA.columns[23:30])))   
                        if cmd[0]!="":
                            JOB.set("CMDLINE",cmd[0])
                        #print(JOB.attrib)
                        old_VARIABLE=set(VARIABLE.get("NAME")+":"+VARIABLE.get("VALUE") for VARIABLE in oneOfJob_details.findall("VARIABLE"))
                        need_modified_VARIABLE=set([i for i in row[20].split("\n") if i!=""])
                        new_addition_VARIABLE=old_VARIABLE-need_modified_VARIABLE
                        for VARIABLE in new_addition_VARIABLE:
                            VARIABLE_DATA_tag=ET.Element('VARIABLE')
                            VARIABLE_DATA_tag.set('NAME',VARIABLE[:VARIABLE.find(":")])
                            VARIABLE_DATA_tag.set('VALUE',VARIABLE[VARIABLE.find(":")+1:])
                            JOB.append(VARIABLE_DATA_tag)

                        control_tag_adding(row[21],JOB)
                
                        old_qua_memory={qua.get("NAME").upper():qua for qua in oneOfJob_details.findall("QUANTITATIVE")}
                        old_qua=set(old_qua_memory.keys())
                        need_modified_qua=set([i.upper() for i in row[22].replace(" ","").split(",") if i!=""])
                        new_addition_qua=old_qua-need_modified_qua
                        for qua in new_addition_qua:
                            QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                            QUANTITATIVE_DATA_TAG.set('NAME',qua)
                            for key,value in default_keys()[0].items():
                                QUANTITATIVE_DATA_TAG.set(key,value)
                            # print(QUANTITATIVE_DATA_TAG.attrib)
                            JOB.append(QUANTITATIVE_DATA_TAG)

                        INCOND_tag_adding(row[0],row[3],row[4],JOB)
                        OUTCOND_tag_adding(row[0],row[3],row[5],JOB)
                        
                        PRED_ON_tag_adding(row[30],row[3],JOB)
                        EVENT_on_tag_adding(row[31],JOB)
                        MAIL_tag_adding(row[32],JOB)
                        rbc=[]
                        if len(smart_folder.findall("RULE_BASED_CALENDAR"))==1:
                            if smart_folder.get("NAME")=="EVERYDAY":
                                rbc.append("EVERYDAY")
                        else:
                            for i in smart_folder.findall("RULE_BASED_CALENDAR"):
                                if i.get("NAME")!="EVERYDAY":
                                    rbc.append(i.get("NAME"))
                        RBC_TAG_Adding("\n".join(rbc),JOB)
                        smart_folder.append(JOB)    
        else:
            if ":" not in which_job_needTo_Match.upper() and len(job_name)==1:
                smart_folder=root.find("SMART_FOLDER[@FOLDER_NAME='"+row[0]+"']")
                oneOfJob_details=smart_folder.find("JOB")
                #print(oneOfJob_details.attrib)
                JOB=ET.Element('JOB')
                job_keys=row[XML_DATA.columns[[0,3,7,9]+list(range(10,19))]].to_dict()
                #print(job_keys)
                for key,value in oneOfJob_details.attrib.items():
                    if job_keys.get(key,"")!="":
                        JOB.set(key,job_keys.get(key))
                    else:
                        JOB.set(key,value)
                
                cmd=commands_generate(pd.DataFrame([list(row[23:30])],columns=list(XML_DATA.columns[23:30])))   
                if cmd[0]!="":
                    JOB.set("CMDLINE",cmd[0])
                #print(JOB.attrib)
                old_VARIABLE=set(VARIABLE.get("NAME")+":"+VARIABLE.get("VALUE") for VARIABLE in oneOfJob_details.findall("VARIABLE"))
                need_modified_VARIABLE=set([i for i in row[20].split("\n") if i!=""])
                new_addition_VARIABLE=old_VARIABLE-need_modified_VARIABLE
                for VARIABLE in new_addition_VARIABLE:
                    VARIABLE_DATA_tag=ET.Element('VARIABLE')
                    VARIABLE_DATA_tag.set('NAME',VARIABLE[:VARIABLE.find(":")])
                    VARIABLE_DATA_tag.set('VALUE',VARIABLE[VARIABLE.find(":")+1:])
                    JOB.append(VARIABLE_DATA_tag)

                control_tag_adding(row[21],JOB)
        
                old_qua_memory={qua.get("NAME").upper():qua for qua in oneOfJob_details.findall("QUANTITATIVE")}
                old_qua=set(old_qua_memory.keys())
                need_modified_qua=set([i.upper() for i in row[22].replace(" ","").split(",") if i!=""])
                new_addition_qua=old_qua-need_modified_qua
                for qua in new_addition_qua:
                    QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                    QUANTITATIVE_DATA_TAG.set('NAME',qua)
                    for key,value in default_keys()[0].items():
                        QUANTITATIVE_DATA_TAG.set(key,value)
                    # print(QUANTITATIVE_DATA_TAG.attrib)
                    JOB.append(QUANTITATIVE_DATA_TAG)

                INCOND_tag_adding(row[0],row[3],row[4],JOB)
                OUTCOND_tag_adding(row[0],row[3],row[5],JOB)
                
                PRED_ON_tag_adding(row[30],row[3],JOB)
                EVENT_on_tag_adding(row[31],JOB)
                MAIL_tag_adding(row[32],JOB)
                rbc=[]
                if len(smart_folder.findall("RULE_BASED_CALENDAR"))==1:
                    if smart_folder.get("NAME")=="EVERYDAY":
                        rbc.append("EVERYDAY")
                else:
                    for i in smart_folder.findall("RULE_BASED_CALENDAR"):
                        if i.get("NAME")!="EVERYDAY":
                            rbc.append(i.get("NAME"))
                RBC_TAG_Adding("\n".join(rbc),JOB)
                smart_folder.append(JOB) 

    else:
        pass

# folders=['EDLR2_HDP_PROD_MBR_MTM_ACCRCY_ACES_INCR_JS1' ,'EDLR2_HDP_PROD_MBR_MTM_ACCRCY_CHIPS_INCR_JS1' ]
# for idx,i in enumerate(root.findall("SMART_FOLDER")):
#     print(i.attrib.get("JOBNAME"),i.attrib.get("JOBNAME") in folders)
#     if i.attrib.get("JOBNAME") in folders:
#         #root.remove(root[idx])
#         i.set("JOBNAME","1234")
#     for j in i.findall("INCOND"):
#         if j.attrib.get("NAME")=='EDLR2_HDP_PROD_MBR_MTM_ACCRCY_ACES_INCR_JS2-TO-EDLR2_HDP_PROD_MBR_MTM_ACCRCY_ACES_INCR_JS1':
#             j.set("NAME","abc")
#     for job in i.findall("JOB"):
#         if job.attrib.get("JOBNAME")=="MTM_ENRLMNT_ACCRCY_ACES_SRC2FF_UNIX_FILE_VLDTN_0001":
#             job.set("JOBNAME","bcd")
#         for outcond in job.findall("OUTCOND"):
#             if outcond.attrib.get("NAME")=="MTM_ENRLMNT_ACCRCY_ACES_LLK_INS_0002-TO-MTM_ENRLMNT_ACCRCY_ACES_FF2HIVELZ_BDM_LD_0003":
#                 outcond.set("NAME","djbsfnk,")
# for i in range(len(root)-3):
#     root.remove(root[3])
# for smart_folder in range(len(root)):
    
#     if c>2:
#         myroot.remove(myroot[2])
#     c +=1
# foos = tree.findall("entityNo")
# for foo in foos:
#   bars = foo.find("1111111111")
#   for bar in bars:
#     foo.remove(bar)

# countrydata='''
# <data>
#     <country name="Liechtenstein">
#         <rank>1</rank>
#         <year>2008</year>
#         <gdppc>141100</gdppc>
#         <neighbor name="Austria" direction="E"/>
#         <neighbor name="Switzerland" direction="W"/>
#     </country>
#     <country name="Singapore">
#         <rank>4</rank>
#         <year name="1">2011</year>
#         <gdppc>59900</gdppc>
#         <neighbor name="Malaysia" direction="N"/>
#     </country>
#     <country name="Panama">
#         <rank>68</rank>
#         <year>2011</year>
#         <gdppc>13600</gdppc>
#         <neighbor name="Costa Rica" direction="W"/>
#         <neighbor name="Colombia" direction="E"/>
#     </country>
# </data>
# '''
# root = ET.fromstring(countrydata)

# # Top-level elements
# for i in root.findall("."):
#     print(i.tag)

# # All 'neighbor' grand-children of 'country' children of the top-level
# # elements
# for i in root.findall("./country/neighbor"):
#     print(i.tag)

# # # Nodes with name='Singapore' that have a 'year' child
# for i in root.findall(".//year/.[@name='Singapore']"):
#     print(i.attrib)

# # # 'year' nodes that are children of nodes with name='Singapore'
# for i in root.findall("*[@name='Singapore']/year"):
#     print(i.attrib)

# # # All 'neighbor' nodes that are the second child of their parent
# for i in root.findall(".//neighbor[2]"):
#     print(i.attrib)
ET.indent(tree, space="\t", level=0)
tree.write(open("NEW1.xml", "wb"))