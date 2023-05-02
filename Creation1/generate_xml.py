print("Please Wait Program Running!")
import xml.etree.ElementTree as ET
import pandas as pd
import sys
pd.options.mode.chained_assignment = None
from datetime import datetime

def commands_generate(df):
    commands=[]
    for idx, row in df.iterrows():
        if len(row[-1])>0:
            commands.append(row[-1])
        elif len(row[4])<1:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}{row[1].strip()}" if row[2].strip().endswith("/") else f"/usr/bin/ksh {row[0].strip()} {row[2].strip()}/{row[1].strip()}"
            commands.append(cmd)
        else:
            cmd=f"/usr/bin/ksh {row[0].strip()} {row[4].strip()} {row[3].strip()} {row[5].strip()}"
            commands.append(cmd)
    return commands
        
XML_DATA=pd.read_excel(sys.argv[1],sheet_name=0).fillna('')
def try_to_change_int(x):
    try:
        x=str(round(float(x)))
    except:
        x=""
    return x if x!="" else 0

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
XML_DATA.MAXWAIT = XML_DATA.MAXWAIT.astype(int)
for i in XML_DATA.columns:
    if i=='TIMEFROM':
        XML_DATA[i]=XML_DATA[i].apply(lambda x:"0"*(4-len(str(x).strip()[:-2]))+str(x).strip()[:-2] if len(str(x).strip()[:-2])!=4 and str(x)!="" else str(x).strip()[:-2])
    elif i=="INTERVAL":
        XML_DATA[i]=XML_DATA[i].apply(lambda x: "00001M" if x=="" else str(x))
    else:
        XML_DATA[i]=XML_DATA[i].apply(lambda x: str(x).strip())

XML_DATA['CMDLINE']=commands_generate(XML_DATA[XML_DATA.columns[24:30]])
FOLDER_COLUMNS=XML_DATA.columns[[0,1,6,7]+list(range(9,19))]
SUB_FOLDER_COLUMS=XML_DATA.columns[[0,1]+list(range(9,19))]
JOB_COLUMNS=XML_DATA.columns[[0,3,8,-1]+list(range(9,19))]
full_time=datetime.now()    
date=full_time.strftime("%Y%m%d")
time=full_time.strftime("%H%M%S")
DEFTABLE=ET.Element("DEFTABLE")
first_level='FOLDER|SMART_FOLDER'
second_level='SUB_FOLDER'
Third_level='JOB'
def default_keys():
    QUANTITATIVE_default_keys={"QUANT":"1","ONFAIL":"R","ONOK":"R"}
    job_default_keys={"JOBISN":"1","APPL_TYPE":"OS","TASKTYPE":"Command","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","TIMETO":">","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","END_FOLDER":"N","CYCLIC_TOLERANCE":"0","CYCLIC_TYPE":"C","VERSION_HOST":"VA10P50185","SYSDB":"0","IND_CYCLIC":"T","RULE_BASED_CALENDAR_RELATIONSHIP":"A"}
    smart_folder_default_keys={"CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"SMART Table","IS_CURRENT_VERSION":"Y","DAYSKEEPINNOTOK":"0","ENFORCE_VALIDATION":"N","USED_BY_CODE":"0","PLATFORM":"UNIX","MODIFIED":"False","TYPE":"2"}
    sub_folder_default_keys={"JOBISN":"2","CREATED_BY":"EDS_DEVOPS","CHANGE_USERID":"EDS_DEVOPS","CHANGE_DATE":date,"CHANGE_TIME":time,"CREATION_DATE":date,"CREATION_TIME":time,"TIMETO":">","TASKTYPE":"Sub-Table","CRITICAL":"0","RETRO":"0","AUTOARCH":"1","MAXDAYS":"0","DAYS":"ALL","JAN":"1","FEB":"1","MAR":"1","APR":"1","MAY":"1","JUN":"1","JUL":"1","AUG":"1","SEP":"1","OCT":"1","NOV":"1","DEC":"1","DAYS_AND_OR":"O", "SHIFT":"Ignore Job","SYSDB":"0","IND_CYCLIC":"S","CREATION_USER":"eda_devops","USE_INSTREAM_JCL":"N","VERSION_OPCODE":"N","IS_CURRENT_VERSION":"Y","VERSION_SERIAL":"1"}
    
    RBC_SCDULE={'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'LEVEL':"N"}
        
    return QUANTITATIVE_default_keys,job_default_keys,smart_folder_default_keys,sub_folder_default_keys,RBC_SCDULE
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
    JOB_data=XML_DATA[(XML_DATA.PARENT_FOLDER.str.contains(row[0])) &  (XML_DATA.TAG==Third_level)]
    MAXWAIT_value=max(list(JOB_data['MAXWAIT']))
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
                variable_tag_adding(row[20],JOB)
                control_tag_adding(row[21],JOB)
                QUANTITATIVE_tag_adding(row[22],JOB)
                INCOND_tag_adding(row[0],row[3],row[4],second_level_tag) 
                OUTCOND_tag_adding(row[0],row[3],row[5],JOB)
                PRED_ON_tag_adding(row[30],row[3],JOB)
                EVENT_on_tag_adding(row[31],JOB)
                MAIL_tag_adding(row[32],JOB)
                RBC_TAG_Adding(FOLDER_row[19],JOB)
                second_level_tag.append(JOB)

            control_tag_adding(SUB_ROW[21],second_level_tag)
            INCOND_tag_adding(SUB_ROW[0],SUB_ROW[1],SUB_ROW[4],second_level_tag)
            OUTCOND_tag_adding(SUB_ROW[0],SUB_ROW[1],SUB_ROW[5],JOB) 
            RBC_TAG_Adding(FOLDER_row[19],second_level_tag)
            fist_levl_tag.append(second_level_tag)
    else:
        for idx, row in JOB_data.iterrows():
            JOB=ET.Element('JOB')
            job_keys=row[JOB_COLUMNS].to_dict()
            job_keys.update(job_default_keys)
            for key,value in job_keys.items():
                JOB.set(key,value)
            variable_tag_adding(row[20],JOB)
            control_tag_adding(row[21],JOB)
            QUANTITATIVE_tag_adding(row[22],JOB)
            INCOND_tag_adding(row[0],row[3],row[4],JOB)
            OUTCOND_tag_adding(row[0],row[3],row[5],JOB)
            PRED_ON_tag_adding(row[30],row[3],JOB)
            EVENT_on_tag_adding(row[31],JOB)
            MAIL_tag_adding(row[32],JOB)
            RBC_TAG_Adding(FOLDER_row[19],JOB)
            fist_levl_tag.append(JOB)
    
    control_tag_adding(FOLDER_row[21],fist_levl_tag) 
    INCOND_tag_adding(" ",FOLDER_row[1],FOLDER_row[4],fist_levl_tag)
    OUTCOND_tag_adding(" ",FOLDER_row[1],FOLDER_row[5],fist_levl_tag)
    RBC_data=[i for i in FOLDER_row[19].split("\n") if i !=""]
    MAX_WAIT='0'+str(MAXWAIT_value) if len(str(MAXWAIT_value))!=2 else str(MAXWAIT_value)
    EVERYDAY={'NAME':"EVERYDAY",'MAXWAIT':MAX_WAIT,'DAYS_AND_OR':"O",'JAN':"1",'FEB':"1",'MAR':"1",'APR':"1",'MAY':"1",'JUN':"1",'JUL':"1",'AUG':"1",'SEP':"1",'OCT':"1",'NOV':"1",'DEC':"1",'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'DAYS':"ALL",'LEVEL':"N"}
    RULE_BASED_CALENDAR=ET.Element('RULE_BASED_CALENDAR')
    for key,value in EVERYDAY.items():
        RULE_BASED_CALENDAR.set(key,value)
    fist_levl_tag.append(RULE_BASED_CALENDAR)   
    for calender in RBC_data:
        calender_details=try_to_eval(calender)
        rbc_attrib=default_keys()[4]
        if isinstance(calender_details,dict):
            rbc_attrib.update({"MAXWAIT":MAX_WAIT,'NAME':calender_details.get("NAME").upper()})
            months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
            if calender_details.get("MONTH").upper()!='ALL':
                month_values=list(calender_details.get("MONTH"))
                rbc_attrib.update(dict(zip(months,month_values)))
            else:
                rbc_attrib.update(dict(zip(months,list("111111111111"))))
            if calender_details.get("DAYS").upper()!='ALL' and calender_details.get("WEEKDAYS").upper()!='ALL':
                rbc_attrib.update({"WEEKDAYS":calender_details.get("WEEKDAYS"),"DAYS":calender_details.get("DAYS"),"DAYS_AND_OR":"A"})
            else:
                if calender_details.get("WEEKDAYS").upper()=='ALL':
                    rbc_attrib.update({"DAYS":calender_details.get("DAYS"),"DAYS_AND_OR":"O"})
                else:
                    rbc_attrib.update({"WEEKDAYS":",".join(list(calender_details.get("WEEKDAYS"))),"DAYS_AND_OR":"O"})   
            RULE_BASED_CALENDAR=ET.Element('RULE_BASED_CALENDAR')
            for key,value in rbc_attrib.items():
                RULE_BASED_CALENDAR.set(key,value)
            fist_levl_tag.append(RULE_BASED_CALENDAR)
        else:
            if calender_details.upper()=="EOM":
                rbc_attrib={'NAME':calender,'MAXWAIT':MAX_WAIT,'DAYS':'L1','DAYS_AND_OR':"O",'JAN':"1",'FEB':"1",'MAR':"1",'APR':"1",'MAY':"1",'JUN':"1",'JUL':"1",'AUG':"1",'SEP':"1",'OCT':"1",'NOV':"1",'DEC':"1",'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'LEVEL':"N"}
                RULE_BASED_CALENDAR=ET.Element('RULE_BASED_CALENDAR')
                for key,value in rbc_attrib.items():
                    RULE_BASED_CALENDAR.set(key,value)
                fist_levl_tag.append(RULE_BASED_CALENDAR)
            else:   
                rbc_attrib={'NAME':calender,'MAXWAIT':MAX_WAIT,'DAYSCAL':calender,'DAYS_AND_OR':"O",'JAN':"1",'FEB':"1",'MAR':"1",'APR':"1",'MAY':"1",'JUN':"1",'JUL':"1",'AUG':"1",'SEP':"1",'OCT':"1",'NOV':"1",'DEC':"1",'SHIFT':"Ignore Job",'SHIFTNUM':"+00",'RETRO':"0",'LEVEL':"N"}
                #print(rbc_attrib)
                RULE_BASED_CALENDAR=ET.Element('RULE_BASED_CALENDAR')
                for key,value in rbc_attrib.items():
                    RULE_BASED_CALENDAR.set(key,value)
                fist_levl_tag.append(RULE_BASED_CALENDAR)

    DEFTABLE.append(fist_levl_tag)
tree=ET.ElementTree(DEFTABLE)
ET.indent(tree, space="\t", level=0)
tree.write(open(sys.argv[1][:-5]+".xml", "wb"))




   # PRED_ON_data=FOLDER_row[30].split("\n")  if len([i for i in FOLDER_row[30].split("\n") if i !=""])>0 else []
    # for cond in PRED_ON_data:
    #     PRED_ON_DATA_tag=ET.Element('ON')
    #     PRED_ON_DATA_tag.set('STMT','*')
    #     PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
    #     DOACTION_tag=ET.Element('DOACTION')
    #     DOACTION_tag.set('ACTION','OK')
    #     PRED_ON_DATA_tag.append(DOACTION_tag)
    #     fist_levl_tag.append(PRED_ON_DATA_tag)
    #     PRED_ON_DATA_tag=ET.Element('ON')
    #     PRED_ON_DATA_tag.set('STMT','*')
    #     PRED_ON_DATA_tag.set('CODE','COMPSTAT EQ 0')
    #     DOCOND_tag=ET.Element('DOCOND')
    #     DOCOND_tag.set('NAME',FOLDER_row[1]+"-TO-"+cond.replace("/","-").replace(" ",""))
    #     DOCOND_tag.set('ODATE','ODAT')
    #     DOCOND_tag.set('SIGN','+')
    #     PRED_ON_DATA_tag.append(DOCOND_tag)
    #     fist_levl_tag.append(PRED_ON_DATA_tag)

    # EVENT_ON_DATA=FOLDER_row[31]
    # if EVENT_ON_DATA.upper()=='YES':
    #     EVENT_ON_DATA_tag=ET.Element('ON')
    #     EVENT_ON_DATA_tag.set('STMT','*')
    #     EVENT_ON_DATA_tag.set('CODE','COMPSTAT EQ 7')
    #     DOACTION_tag=ET.Element('DOACTION')
    #     DOACTION_tag.set('ACTION','OK')
    #     EVENT_ON_DATA_tag.append(DOACTION_tag)
    #     fist_levl_tag.append(EVENT_ON_DATA_tag)

        #print(rbc_attrib)
            # print(str(MAXWAIT_value))
            # for key,value in EVERYDAY.items():
            #     RULE_BASED_CALENDAR.set(key,value)
    
    # if len(RBC_data)==0:
    #     RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
    #     RULE_BASED_CALENDARS.set('NAME','EVERYDAY')
    #     JOB.append(RULE_BASED_CALENDARS)
    # for calender in RBC_data:
    #     calender_details=try_to_eval(calender)
        
    #     if isinstance(calender_details,dict):
    #         RULE_BASED_CALENDARS=ET.Element('RULE_BASED_CALENDARS')
    #         RULE_BASED_CALENDARS.set('NAME',calender_details.get("NAME").upper())
    #         JOB.append(RULE_BASED_CALENDARS)
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