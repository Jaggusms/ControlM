import xml.etree.ElementTree as ET
import pandas as pd
import sys
pd.options.mode.chained_assignment = None
from datetime import datetime
def commands_formating(df):
    commands=[]
    for idx, row in df.iterrows():
        if len(row[-1])>1:
            commands.append(row[-1])
        elif len(row[4])<1:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}{row[1].strip()}" if row[2].strip().endswith("/") else f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}/{row[1].strip()}"
            commands.append(cmd)
        else:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[4].strip()} {row[3].strip()} {row[5].strip()}"
            commands.append(cmd)
    return commands
        #if row[-1]
XML_DATA=pd.read_excel(sys.argv[1],sheet_name=0).fillna('')
XML_DATA.CYCLIC = XML_DATA.CYCLIC.astype(int)
XML_DATA.MAXWAIT = XML_DATA.MAXWAIT.astype(int)
XML_DATA.MAXRERUN = XML_DATA.MAXRERUN.astype(int)
for i in XML_DATA.columns:
    if i=='TIMEFROM':
        XML_DATA[i]=XML_DATA[i].apply(lambda x: str(str(x).strip())[:-2])
    else:
        XML_DATA[i]=XML_DATA[i].apply(lambda x: str(str(x).strip()))
XML_DATA['CMDLINE']=commands_formating(XML_DATA[XML_DATA.columns[23:30]])
FOLDER_COLUMNS=XML_DATA.columns[[0,1,6,8,9,10,11,12,15,16,17,18,19,20,34]]
SUB_FOLDER_COLUMS=XML_DATA.columns[[0,3,8,9,10,11,12,15,16,17,18,19,34,20]]
JOB_COLUMNS=XML_DATA.columns[[0,3,7,9,10,11,12,15,16,17,18,19,20,34,-1]]
full_time=datetime.now()    
date=full_time.strftime("%Y%m%d")
time=full_time.strftime("%H%M%S")
DEFTABLE=ET.Element("DEFTABLE")
first_level='FOLDER|SMART_FOLDER'
second_level='SUB_FOLDER'
Third_level='JOB'
def default_keys():
    QUANTITATIVE_default_keys={"QUANT":"1","ONFAIL":"R","ONOK":"R"}
    job_default_keys={"JOBISN":"1","TASKTYPE":"Command","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","MAXRUNS":"0","TIMETO":">","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","END_FOLDER":"N","CYCLIC_TOLERANCE":"0","CYCLIC_TYPE":"C","VERSION_HOST":"VA10P50185","SYSDB":"0","IND_CYCLIC":"T","RULE_BASED_CALENDAR_RELATIONSHIP":"A"}
    smart_folder_default_keys={"CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"SMART Table","IS_CURRENT_VERSION":"Y","DAYSKEEPINNOTOK":"0","ENFORCE_VALIDATION":"N","USED_BY_CODE":"0","PLATFORM":"UNIX","MODIFIED":"False","TYPE":"2"}
    sub_folder_default_keys={"JOBISN":"2","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"Sub-Table","CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","MAXRUNS":"0","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","USE_INSTREAM_JCL":"N","VERSION_OPCODE":"N","IS_CURRENT_VERSION":"Y","VERSION_SERIAL":"1"}
    return QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys,sub_folder_default_keys
for idx,row in XML_DATA[(XML_DATA.TAG=='FOLDER') |(XML_DATA.TAG=='SMART_FOLDER') ].iterrows():
    FOLDER_row=row
    default=default_keys()
    QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys=default[0],default[1],default[2]
    fist_levl_tag=ET.Element(row[2])
    smd=row[FOLDER_COLUMNS].to_dict()
    smd.update(smart_folder_default_keys)
    for key,value in smd.items():
        if key=='FOLDER_ORDER_METHOD' and value =="":
            pass
        elif key=='FOLDER_NAME':
            fist_levl_tag.set(key,value)
            fist_levl_tag.set('JOBNAME',value)
        else:
            fist_levl_tag.set(key,value)
    SUB_folder_data=XML_DATA[(XML_DATA.PARENT_FOLDER==row[0]) &  (XML_DATA.TAG==second_level)]
    if len(SUB_folder_data)!=0:
        for idx, row in SUB_folder_data.iterrows():
            SUB_ROW=row
            second_level_tag=ET.Element(second_level)
            default=default_keys()
            QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys=default[0],default[1],default[2]
            sud=row[SUB_FOLDER_COLUMS].to_dict()
            sud.update(smart_folder_default_keys)
            for key,value in sud.items():
                second_level_tag.set(key,value)
            JOB_data=XML_DATA[(XML_DATA.PARENT_FOLDER==row[0]+"/"+row[3]) &  (XML_DATA.TAG==Third_level)]
            
            for idx, row in JOB_data.iterrows():
                JOB=ET.Element('JOB')
                job_keys=row[JOB_COLUMNS].to_dict()
                job_keys.update(job_default_keys)
                for key,value in job_keys.items():
                    JOB.set(key,value)
                
                CONTROL_DATA=[(i[:-2], i[-1]) for i in row[21].split("\n")]  if len([i for i in row[21].split("\n") if i !=""])>0 else []
                for data in CONTROL_DATA:
                    CONTROL_DATA_tag=ET.Element('CONTROL')
                    CONTROL_DATA_tag.set('NAME',data[0])
                    CONTROL_DATA_tag.set('TYPE',data[1])
                    CONTROL_DATA_tag.set('ONFAIL','R')
                    JOB.append(CONTROL_DATA_tag)

                QUANTITATIVE_DATA=row[22].split(",")
                for value in QUANTITATIVE_DATA:
                    QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                    QUANTITATIVE_DATA_TAG.set('NAME',value)
                    for key,value in default_keys()[0].items():
                        QUANTITATIVE_DATA_TAG.set(key,value)
                    JOB.append(QUANTITATIVE_DATA_TAG)
                
                INCOND_DATA=[(i[:i.find(':')], i[i.find(':')+1:]) for i in row[4].split("\n")]  if len([i for i in row[4].split("\n") if i !=""])>0 else []
                for data in INCOND_DATA:
                    INCOND_DATA_tag=ET.Element('INCOND')
                    #INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+FOLDER_row[0].replace("/","-").replace(" ","")) required for jobs and subfolder and its jobs
                    INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row[0]+"-"+row[1])
                    INCOND_DATA_tag.set('ODATE',data[1])
                    INCOND_DATA_tag.set('AND_OR','A')
                    OUTCOND_DATA_tag=ET.Element('OUTCOND')
                    OUTCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+row[0]+"-"+row[1])
                    OUTCOND_DATA_tag.set('ODATE',data[1])
                    OUTCOND_DATA_tag.set('SIGN','-')
                    JOB.append(INCOND_DATA_tag)
                    JOB.append(OUTCOND_DATA_tag)  

                OUTCOND_DATA=row[5].split("\n")  if len([i for i in row[5].split("\n") if i !=""])>0 else []
                for data in OUTCOND_DATA:
                    OUTCOND_DATA_tag=ET.Element('OUTCOND')
                    OUTCOND_DATA_tag.set('NAME',row[0]+"-"+row[1]+"-TO-"+data.replace("/","-").replace(" ",""))
                    OUTCOND_DATA_tag.set('ODATE','ODAT')
                    OUTCOND_DATA_tag.set('SIGN','+')
                    JOB.append(OUTCOND_DATA_tag)     

                PRED_ON_data=row[30].split("\n")  if len([i for i in row[30].split("\n") if i !=""])>0 else []
                for cond in PRED_ON_data:
                    PRED_ON_DATA_tag=ET.Element('ON')
                    PRED_ON_DATA_tag.set('STMT','*')
                    PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                    DOACTION_tag=ET.Element('DOACTION')
                    DOACTION_tag.set('ACTION','OK')
                    PRED_ON_DATA_tag.append(DOACTION_tag)
                    JOB.append(PRED_ON_DATA_tag)
                    PRED_ON_DATA_tag=ET.Element('ON')
                    PRED_ON_DATA_tag.set('STMT','*')
                    PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
                    DOCOND_tag=ET.Element('DOCOND')
                    DOCOND_tag.set('NAME',row[1]+"-TO-"+cond.replace("/","-").replace(" ",""))
                    DOCOND_tag.set('ODATE','ODAT')
                    DOCOND_tag.set('SIGN','+')
                    PRED_ON_DATA_tag.append(DOCOND_tag)
                    JOB.append(PRED_ON_DATA_tag)

                EVENT_ON_DATA=row[31]
                if EVENT_ON_DATA.upper()=='YES':
                    EVENT_ON_DATA_tag=ET.Element('ON')
                    EVENT_ON_DATA_tag.set('STMT','*')
                    EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                    DOACTION_tag=ET.Element('DOACTION')
                    DOACTION_tag.set('ACTION','OK')
                    EVENT_ON_DATA_tag.append(DOACTION_tag)
                    JOB.append(EVENT_ON_DATA_tag)
                MAIL_ON_DATA=""

                RBC_data=row[13].split(",")
                for value in RBC_data:
                    RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
                    RULE_BASED_CALENDARS.set('NAME',value)
                    JOB.append(RULE_BASED_CALENDARS)
                second_level_tag.append(JOB)

            CONTROL_DATA=[(i[:-2], i[-1]) for i in SUB_ROW[21].split("\n")]  if len([i for i in SUB_ROW[21].split("\n") if i !=""])>0 else []
            for data in CONTROL_DATA:
                CONTROL_DATA_tag=ET.Element('CONTROL')
                CONTROL_DATA_tag.set('NAME',data[0])
                CONTROL_DATA_tag.set('TYPE',data[1])
                CONTROL_DATA_tag.set('ONFAIL','R')
                second_level_tag.append(CONTROL_DATA_tag)

            QUANTITATIVE_DATA=SUB_ROW[22].split(",")
            for value in QUANTITATIVE_DATA:
                QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                QUANTITATIVE_DATA_TAG.set('NAME',value)
                for key,value in default_keys()[0].items():
                    QUANTITATIVE_DATA_TAG.set(key,value)
                second_level_tag.append(QUANTITATIVE_DATA_TAG)
            
            INCOND_DATA=[(i[:i.find(':')], i[i.find(':')+1:]) for i in SUB_ROW[4].split("\n")]  if len([i for i in SUB_ROW[4].split("\n") if i !=""])>0 else []
            for data in INCOND_DATA:
                INCOND_DATA_tag=ET.Element('INCOND')
                #INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+FOLDER_row[0].replace("/","-").replace(" ","")) required for jobs and subfolder and its jobs
                INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+SUB_ROW[0]+"-"+SUB_ROW[1])
                INCOND_DATA_tag.set('ODATE',data[1])
                INCOND_DATA_tag.set('AND_OR','A')
                OUTCOND_DATA_tag=ET.Element('OUTCOND')
                OUTCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+SUB_ROW[0]+"-"+SUB_ROW[1])
                OUTCOND_DATA_tag.set('ODATE',data[1])
                OUTCOND_DATA_tag.set('SIGN','-')
                second_level_tag.append(INCOND_DATA_tag)
                second_level_tag.append(OUTCOND_DATA_tag)  

            OUTCOND_DATA=SUB_ROW[5].split("\n")  if len([i for i in SUB_ROW[5].split("\n") if i !=""])>0 else []
            for data in OUTCOND_DATA:
                OUTCOND_DATA_tag=ET.Element('OUTCOND')
                OUTCOND_DATA_tag.set('NAME',SUB_ROW[0]+"-"+SUB_ROW[1]+"-TO-"+data.replace("/","-").replace(" ",""))
                OUTCOND_DATA_tag.set('ODATE','ODAT')
                OUTCOND_DATA_tag.set('SIGN','+')
                second_level_tag.append(OUTCOND_DATA_tag)     

            PRED_ON_data=FOLDER_row[30].split("\n")  if len([i for i in FOLDER_row[30].split("\n") if i !=""])>0 else []
            for cond in PRED_ON_data:
                PRED_ON_DATA_tag=ET.Element('ON')
                PRED_ON_DATA_tag.set('STMT','*')
                PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                DOACTION_tag=ET.Element('DOACTION')
                DOACTION_tag.set('ACTION','OK')
                PRED_ON_DATA_tag.append(DOACTION_tag)
                second_level_tag.append(PRED_ON_DATA_tag)
                PRED_ON_DATA_tag=ET.Element('ON')
                PRED_ON_DATA_tag.set('STMT','*')
                PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
                DOCOND_tag=ET.Element('DOCOND')
                DOCOND_tag.set('NAME',FOLDER_row[1]+"-TO-"+cond.replace("/","-").replace(" ",""))
                DOCOND_tag.set('ODATE','ODAT')
                DOCOND_tag.set('SIGN','+')
                PRED_ON_DATA_tag.append(DOCOND_tag)
                second_level_tag.append(PRED_ON_DATA_tag)

            EVENT_ON_DATA=FOLDER_row[31]
            if EVENT_ON_DATA.upper()=='YES':
                EVENT_ON_DATA_tag=ET.Element('ON')
                EVENT_ON_DATA_tag.set('STMT','*')
                EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                DOACTION_tag=ET.Element('DOACTION')
                DOACTION_tag.set('ACTION','OK')
                EVENT_ON_DATA_tag.append(DOACTION_tag)
                second_level_tag.append(EVENT_ON_DATA_tag)
            MAIL_ON_DATA=""
            RBC_data=row[13].split(",")
            for value in RBC_data:
                RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
                RULE_BASED_CALENDARS.set('NAME',value)
                second_level_tag.append(RULE_BASED_CALENDARS)
            
            fist_levl_tag.append(second_level_tag)
    else:
        JOB_data=XML_DATA[(XML_DATA.PARENT_FOLDER.str.contains(row[0])) &  (XML_DATA.TAG==Third_level)]
        for idx, row in JOB_data.iterrows():
            JOB=ET.Element('JOB')
            job_keys=row[JOB_COLUMNS].to_dict()
            job_keys.update(job_default_keys)
            for key,value in job_keys.items():
                JOB.set(key,value)
            fist_levl_tag.append(JOB)
            variable_data=[(i[:i.find(':')], i[i.find(':')+1:]) for i in row[14].split("\n")]  if len([i for i in row[14].split("\n") if i !=""])>0 else []
            #print(row[0],variable_data)
            for data in variable_data:
                variable_data_tag=ET.Element('VARIABLE')
                variable_data_tag.set('NAME',data[0])
                variable_data_tag.set('VALUE',data[1])
                JOB.append(variable_data_tag)
            
            CONTROL_DATA=[(i[:-2], i[-1]) for i in row[21].split("\n")]  if len([i for i in row[21].split("\n") if i !=""])>0 else []
            for data in CONTROL_DATA:
                CONTROL_DATA_tag=ET.Element('CONTROL')
                CONTROL_DATA_tag.set('NAME',data[0])
                CONTROL_DATA_tag.set('TYPE',data[1])
                CONTROL_DATA_tag.set('ONFAIL','R')
                JOB.append(CONTROL_DATA_tag)

            QUANTITATIVE_DATA=row[22].split(",")
            for value in QUANTITATIVE_DATA:
                QUANTITATIVE_DATA_TAG=ET.Element('QUANTITATIVE')
                QUANTITATIVE_DATA_TAG.set('NAME',value)
                for key,value in default_keys()[0].items():
                    QUANTITATIVE_DATA_TAG.set(key,value)
                JOB.append(QUANTITATIVE_DATA_TAG)

            INCOND_DATA=[(i[:i.find(':')], i[i.find(':')+1:]) for i in row[4].split("\n")]  if len([i for i in row[4].split("\n") if i !=""])>0 else []
    
            for data in INCOND_DATA:
                INCOND_DATA_tag=ET.Element('INCOND')
                INCOND_DATA_tag.set('NAME',row[0].replace("/","-").replace(" ","")+"-"+data[0].replace("/","-").replace(" ","")+"-TO-"+row[0].replace("/","-").replace(" ","")+"-"+row[3])
                INCOND_DATA_tag.set('ODATE',data[1])
                INCOND_DATA_tag.set('AND_OR','A')
                OUTCOND_DATA_tag=ET.Element('OUTCOND')
                OUTCOND_DATA_tag.set('NAME',row[0].replace("/","-").replace(" ","")+"-"+data[0].replace("/","-").replace(" ","")+"-TO-"+row[0].replace("/","-").replace(" ","")+"-"+row[3])
                OUTCOND_DATA_tag.set('ODATE',data[1])
                OUTCOND_DATA_tag.set('SIGN','-')
                JOB.append(INCOND_DATA_tag)
                JOB.append(OUTCOND_DATA_tag) 

            OUTCOND_DATA=row[5].split("\n")  if len([i for i in row[5].split("\n") if i !=""])>0 else []
            for data in OUTCOND_DATA:
                OUTCOND_DATA_tag=ET.Element('OUTCOND')
                OUTCOND_DATA_tag.set('NAME',row[0].replace("/","-").replace(" ","")+"-"+row[3]+"-TO-"+row[0].replace("/","-").replace(" ","")+"-"+data.replace("/","-").replace(" ",""))
                OUTCOND_DATA_tag.set('ODATE','ODAT')
                OUTCOND_DATA_tag.set('SIGN','+')
                JOB.append(OUTCOND_DATA_tag)      
            
            PRED_ON_data=row[30].split("\n")  if len([i for i in row[30].split("\n") if i !=""])>0 else []
            for cond in PRED_ON_data:
                PRED_ON_DATA_tag=ET.Element('ON')
                PRED_ON_DATA_tag.set('STMT','*')
                PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                DOACTION_tag=ET.Element('DOACTION')
                DOACTION_tag.set('ACTION','OK')
                PRED_ON_DATA_tag.append(DOACTION_tag)
                JOB.append(PRED_ON_DATA_tag)
                PRED_ON_DATA_tag=ET.Element('ON')
                PRED_ON_DATA_tag.set('STMT','*')
                PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
                DOCOND_tag=ET.Element('DOCOND')
                DOCOND_tag.set('NAME',row[3]+"-TO-"+cond.replace("/","-").replace(" ",""))
                DOCOND_tag.set('ODATE','ODAT')
                DOCOND_tag.set('SIGN','+')
                PRED_ON_DATA_tag.append(DOCOND_tag)
                JOB.append(PRED_ON_DATA_tag)
            
            EVENT_ON_DATA=row[31]
            if EVENT_ON_DATA.upper()=='YES':
                EVENT_ON_DATA_tag=ET.Element('ON')
                EVENT_ON_DATA_tag.set('STMT','*')
                EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
                DOACTION_tag=ET.Element('DOACTION')
                DOACTION_tag.set('ACTION','OK')
                EVENT_ON_DATA_tag.append(DOACTION_tag)
                JOB.append(EVENT_ON_DATA_tag)
            MAIL_ON_DATA=""

            RBC_data=row[13].split(",")
            for value in RBC_data:
                RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
                RULE_BASED_CALENDARS.set('NAME',value)
                JOB.append(RULE_BASED_CALENDARS)
    
    CONTROL_DATA=[(i[:-2], i[-1]) for i in FOLDER_row[21].split("\n")]  if len([i for i in FOLDER_row[21].split("\n") if i !=""])>0 else []
    for data in CONTROL_DATA:
        CONTROL_DATA_tag=ET.Element('CONTROL')
        CONTROL_DATA_tag.set('NAME',data[0])
        CONTROL_DATA_tag.set('TYPE',data[1])
        CONTROL_DATA_tag.set('ONFAIL','R')
        fist_levl_tag.append(CONTROL_DATA_tag)
   
    INCOND_DATA=[(i[:i.find(':')], i[i.find(':')+1:]) for i in FOLDER_row[4].split("\n")]  if len([i for i in FOLDER_row[4].split("\n") if i !=""])>0 else []
    for data in INCOND_DATA:
        INCOND_DATA_tag=ET.Element('INCOND')
        #INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+FOLDER_row[0].replace("/","-").replace(" ","")) required for jobs and subfolder and its jobs
        INCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+FOLDER_row[1])
        INCOND_DATA_tag.set('ODATE',data[1])
        INCOND_DATA_tag.set('AND_OR','A')
        OUTCOND_DATA_tag=ET.Element('OUTCOND')
        OUTCOND_DATA_tag.set('NAME',data[0].replace("/","-").replace(" ","")+"-TO-"+FOLDER_row[1])
        OUTCOND_DATA_tag.set('ODATE',data[1])
        OUTCOND_DATA_tag.set('SIGN','-')
        fist_levl_tag.append(INCOND_DATA_tag)
        fist_levl_tag.append(OUTCOND_DATA_tag)  

    OUTCOND_DATA=FOLDER_row[5].split("\n")  if len([i for i in FOLDER_row[5].split("\n") if i !=""])>0 else []
    for data in OUTCOND_DATA:
        OUTCOND_DATA_tag=ET.Element('OUTCOND')
        OUTCOND_DATA_tag.set('NAME',FOLDER_row[1]+"-TO-"+data.replace("/","-").replace(" ",""))
        OUTCOND_DATA_tag.set('ODATE','ODAT')
        OUTCOND_DATA_tag.set('SIGN','+')
        fist_levl_tag.append(OUTCOND_DATA_tag)     

    PRED_ON_data=FOLDER_row[30].split("\n")  if len([i for i in FOLDER_row[30].split("\n") if i !=""])>0 else []
    for cond in PRED_ON_data:
        PRED_ON_DATA_tag=ET.Element('ON')
        PRED_ON_DATA_tag.set('STMT','*')
        PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
        DOACTION_tag=ET.Element('DOACTION')
        DOACTION_tag.set('ACTION','OK')
        PRED_ON_DATA_tag.append(DOACTION_tag)
        fist_levl_tag.append(PRED_ON_DATA_tag)
        PRED_ON_DATA_tag=ET.Element('ON')
        PRED_ON_DATA_tag.set('STMT','*')
        PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
        DOCOND_tag=ET.Element('DOCOND')
        DOCOND_tag.set('NAME',FOLDER_row[1]+"-TO-"+cond.replace("/","-").replace(" ",""))
        DOCOND_tag.set('ODATE','ODAT')
        DOCOND_tag.set('SIGN','+')
        PRED_ON_DATA_tag.append(DOCOND_tag)
        fist_levl_tag.append(PRED_ON_DATA_tag)

    EVENT_ON_DATA=FOLDER_row[31]
    if EVENT_ON_DATA.upper()=='YES':
        EVENT_ON_DATA_tag=ET.Element('ON')
        EVENT_ON_DATA_tag.set('STMT','*')
        EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
        DOACTION_tag=ET.Element('DOACTION')
        DOACTION_tag.set('ACTION','OK')
        EVENT_ON_DATA_tag.append(DOACTION_tag)
        fist_levl_tag.append(EVENT_ON_DATA_tag)
    MAIL_ON_DATA=""
    MAXWAIT_value=FOLDER_row[19]
    EVERYDAY={'NAME':"EVERYDAY",'MAXWAIT':MAXWAIT_value,'DAYS_AND_OR':"O",'JAN':"1",'FEB':"1",'MAR':"1",'APR':"1",'MAY':"1",'JUN':"1",'JUL':"1",'AUG':"1",'SEP':"1",'OCT':"1",'NOV':"1",'DEC':"1",'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'DAYS':"ALL",'LEVEL':"N"}
    RULE_BASED_CALENDAR=ET.Element('RULE_BASED_CALENDAR')
    for key,value in EVERYDAY.items():
        RULE_BASED_CALENDAR.set(key,value)
    fist_levl_tag.append(RULE_BASED_CALENDAR)
    DEFTABLE.append(fist_levl_tag)
# for idx,row in XML_DATA.iterrows():
#     print(row[2])
#     if row[2] in first_level:
#         print(1)
#         fist_levl_tag=ET.Element(row[2])
#         for key,value in row[FOLDER_COLUMNS].to_dict().items():
#             fist_levl_tag.set(key,value)
#     if row[2] in second_level:
#         print(2)
#         SUB_FOLDER=ET.Element(row[2])
#         SUB_FOLDER.text=""
#         for key,value in row[FOLDER_COLUMNS].to_dict().items():
#             SUB_FOLDER.set(key,value)
#         fist_levl_tag.append(SUB_FOLDER)
#     if row[2] in Third_level:
#         print(3)
#         JOB=ET.Element(row[2])
#         JOB.text=""
#         for key,value in row[JOB_COLUMNS].to_dict().items():
#             JOB.set(key,value)
#         fist_levl_tag.append(JOB)     
#    DEFTABLE.append(fist_levl_tag)
    
# with open("new.xml", "wb") as f:
#     f.write(ET.tostring(Customers,space="\t", level=0))
tree=ET.ElementTree(DEFTABLE)
ET.indent(tree, space="\t", level=0)
tree.write(open(sys.argv[1][:-5]+".xml", "wb"))

 
# for tag in tags:
#                 if tag=='JOB':
#                     data={'JOBISN':"2",'APPLICATION':"EDLR2",'SUB_APPLICATION':"EDWARD LO SUP",'JOBNAME':"BTEQ_CLM_NASCO_CLLK_INS_LD_RIM392699_0001"}
#                     customer1=ET.Element(tag)
#                     customer1.text=""
#                     for key,value in data.items():
#                         customer1.set(key,value)
#                     fist_levl_tag.append(customer1)
#                 else:
#                     customer1=ET.Element(tag)
#                     customer1.text=""
#                     customer1.set('id','1')
#                     fist_levl_tag.append(customer1)

        #    elif tag=='RULE_BASE_CALENDERS':
        #     data={'NAME':"EVERYDAY", 'MAXWAIT':"30"}
        #     customer1=ET.Element(tag)
        #     customer1.text=""
        #     for key,value in data.items():
        #         customer1.set(key,value)
        #     fist_levl_tag.append(customer1)
        # elif tag=='INCOND':
        #     data={'NAME':"EVERYDAY", 'MAXWAIT':"30"}
        #     customer1=ET.Element(tag)
        #     customer1.text=""
        #     for key,value in data.items():
        #         customer1.set(key,value)
        #     fist_levl_tag.append(customer1)


# >>> import xml.etree.ElementTree as xml
# >>> s= '<p>blah <b>bleh</b> blih</p>\n'
# >>> t=xml.fromstring(s)
# >>> "".join( [ t.text ] + [ xml.tostring(e) for e in t.getchildren() ] )
# 'blah <b>bleh</b> blih'