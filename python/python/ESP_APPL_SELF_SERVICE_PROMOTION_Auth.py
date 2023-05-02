import os,io
from datetime import datetime
import shutil
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import subprocess
import re,sys,logging

log_name="SCRIPT_VALIDATION_"+str(datetime.now().strftime("%Y%m%d%H%M%S%f"))[:-3]+".log"
logging.basicConfig(filename=log_name,
    format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def script_log_moving():
    message_log=[file for file in os.listdir(os.getcwd()) if file.endswith(".log") or file.endswith(".log")]
    for log in message_log:
        shutil.move(os.path.join(os.getcwd(),log),os.path.join(str(SS_MIG_EDS_ESP_CWD)+"_LOGS",log)) 

def ASCII_REMOVAL(s):
    a=list(range(44,124))
    s_new=s
    for i in s:
        if ord(i) not in a:
            s_new=s_new.replace(i," ")
    return s_new

def send_email(sender_email,mail_to,mail_sub,body,mail_cc=[],attachments=[]):
    msg = MIMEMultipart()
    msgText = MIMEText(body)
    msg.attach(msgText)
    msg['Subject'] = mail_sub #need to get this from variable name here
    msg['To'] = ','.join(mail_to)
    msg['Cc'] = ','.join(mail_cc)
    for doc in attachments:
        try:
            part = MIMEApplication(open(doc, 'rb').read(), _subtype='application/x-mobipocket-ebook')
            part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', doc))
            msg.attach(part)
        except:
            print(f"{doc} not available in the directory")
    sender=sender_email
    try:
        smtpObj = smtplib.SMTP('30.132.52.66')
        smtpObj.sendmail(sender, mail_to+mail_cc, str(msg))
        smtpObj.quit()    
    except:
        print("Mail Id's are invalid or Organization VPN is not connected")
        logging.shutdown()
        script_log_moving()
        sys.exit(1)

def emails():
    mail_from=["dl-EDA_ESP_DevOps@anthem.com"]
    mail_to=["dl-EDS_DevOps-Offshore@legato.com","Harita.Petla@carelon.com"]
    mail_cc=['Srikanth.Gadekal@legato.com', 'Jagadeesh.sanniboina@gmail.com']
    return mail_from,mail_to,mail_cc

def validation(Migatrion_file,cros_work_file):
    validation_success=True
    COLUMN=Migatrion_file.columns
    cros_work_file_data=[]
    failure_data=[]
    if Migatrion_file.empty:
        validation_success=False
        print("Appl details not found")
        return validation_success,failure_data
    for idx,rows in cros_work_file.iterrows():
        cros_work_file_data.append("".join(rows))
    for idx,rows in Migatrion_file.iterrows():
        try:
            if not rows[COLUMN[1]].split(".")[-2].startswith(rows[COLUMN[0]][-3]) or  not rows[COLUMN[2]].split(".")[-2].startswith(rows[COLUMN[0]][-1]):
                rows_data=",".join(rows)
                failure_data.append(rows_data)
                print(f"{rows_data} Source and Target environments are not matched with Promition Rule {rows[COLUMN[0]]}")
                validation_success=False
        except:
            rows_data=",".join(rows)
            failure_data.append(rows_data)
            print(f"{rows_data} Source and Target environments are not matched with Promition Rule {rows[COLUMN[0]]}")
            validation_success=False
            pass
        else:
            rows_data=",".join(rows)
            print(f"{rows_data} Source and Target environments are matched with Promition Rules {rows[COLUMN[0]]}")
        if "".join(rows) not in cros_work_file_data:
            rows_data=",".join(rows)
            failure_data.append(rows_data)
            print(f"{rows_data} is not matched with Crosswalk file")
            validation_success=False      
        else:
            rows_data=",".join(rows)
            print(f"{rows_data} is matched with Cross Crosswalk file")
    return validation_success,failure_data

def parameter_validation():
    if len(sys.argv[1:])!=1:
        print("Parameters are not valid")
        sys.exit(1)
    else:
        print("Parameter validations are successfull")
parameter_validation() 

def path_validation(path):
    if not os.path.isdir(path):
        print(f"{path} Path is not valid")
        sys.exit(1)
    else:
        print(f"{path} path Valid")

path=sys.argv[1]
SS_MIG_EDS_ESP=path.split("\\")[-1]
cwd=path[:path.find(SS_MIG_EDS_ESP)]
path_validation(path)
SS_MIG_EDS_ESP_CWD=os.path.join(cwd,str(SS_MIG_EDS_ESP))
SS_MIG_EDS_ESP_AUTHUSERS_CWD=os.path.join(cwd,str(SS_MIG_EDS_ESP)+"_AUTHUSERS")
path_validation(SS_MIG_EDS_ESP_AUTHUSERS_CWD)
SS_MIG_EDS_ESP_LOG_CWD=os.path.join(cwd,str(SS_MIG_EDS_ESP)+"_LOGS")
path_validation(SS_MIG_EDS_ESP_LOG_CWD)
SS_MIG_EDS_ESP_PROCESSED_CWD=os.path.join(cwd,str(SS_MIG_EDS_ESP)+"_PROCESSED")
path_validation(SS_MIG_EDS_ESP_PROCESSED_CWD)

SS_MIG_EDS_ESP=[file for file in os.listdir(SS_MIG_EDS_ESP_CWD) if file.endswith(".csv") or file.endswith(".CSV")]
print(f"file Read Sucessfully from {SS_MIG_EDS_ESP_CWD}")
SS_MIG_EDS_ESP_AUTHUSERS=[file for file in os.listdir(SS_MIG_EDS_ESP_AUTHUSERS_CWD) if file.endswith(".csv") or file.endswith(".CSV")]
print(f"file Read Sucessfully from {SS_MIG_EDS_ESP_AUTHUSERS_CWD}")
SS_MIG_EDS_ESP_log=[file for file in os.listdir(SS_MIG_EDS_ESP_LOG_CWD) if file.endswith(".csv") or file.endswith(".CSV")]
print(f"file Read Sucessfully from {SS_MIG_EDS_ESP_LOG_CWD}")
SS_MIG_EDS_ESP_PROCESSED=[file for file in os.listdir(SS_MIG_EDS_ESP_PROCESSED_CWD) if file.endswith(".csv") or file.endswith(".CSV")]
print(f"file Read Sucessfully from {SS_MIG_EDS_ESP_PROCESSED_CWD}")

try:
    cros_work_file=pd.read_csv('Retrofit_CrossWalk_File.csv').fillna("na")
    print("Cross Work file read Successfully")
except:
    print("Cross Work file Not exist")
    logging.shutdown()
    script_log_moving()
    sys.exit(1)
zowe_cammands={}
if len(SS_MIG_EDS_ESP)==0:
    print(f"Count of csv form is {len(SS_MIG_EDS_ESP)}")
    logging.shutdown()
    script_log_moving()
    sys.exit(1)
print(f"Count of csv form is {len(SS_MIG_EDS_ESP)}")
for file in SS_MIG_EDS_ESP:
    if file in SS_MIG_EDS_ESP_AUTHUSERS:
        print("*"*150)
        print(f"{file} exist in {SS_MIG_EDS_ESP_AUTHUSERS_CWD} and going for Validation") 
        for i in cros_work_file.columns:
            cros_work_file[i]=cros_work_file[i].str.strip()
        Migatrion_file=os.path.join(SS_MIG_EDS_ESP_CWD,file)
        try:
            mig_file_data =pd.read_csv(Migatrion_file).fillna("na")
            print(f"{file} read Sucessfull")
        except:
            print(f"{file} read not Sucessfull")
        RITM=mig_file_data[list(mig_file_data.columns)[0]].loc[0].strip()
        validation_sucess=True
        if not RITM.startswith("RITM"):
            print(f"{RITM} not Valid")
            validation_sucess=False
        else:
            print(f"{RITM} is Valid")
        header_value=1
        for i, value in enumerate(list(mig_file_data[mig_file_data.columns[0]])[:5]):
            if "APPL" in value.upper():
                header_value=i
                break
        col={}
        for key,value in zip(mig_file_data.columns,list(mig_file_data.loc[header_value])):
            col.update({key:value})
        new_df  = mig_file_data.iloc[header_value+1:,:5].rename(columns=col)
        df2=new_df.reset_index().iloc[:,1:]
        for i in df2.columns:
            df2[i]=df2[i].str.strip()
        validation_result=validation(df2.iloc[:,[1,3,4]],cros_work_file)

        commands=[]
        #if validation_result[0] and validation_sucess:
        if validation_sucess:
            print("Validation Sucess going to generate the Zowe Commands")
            for data,row in df2.iterrows():
                if row[2].upper()=="TRANSFER":
                    appl,Promotion,SourcCrosswalk,environment_1=row[0],row[1],row[3],row[4]
                    environment_1=environment_1.split(".")[4]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    s=ASCII_REMOVAL('zowe endevor transfer element {1} --env SUPP --sys {4} --sub {2} --typ APPL --sn 2 --ccid {0} --com "{5}" --toenv SUPP --tosys {4} --tosub {3} --toele {1} --totyp APPL --tosn 2 --sync --pg APPL --bed'.format(RITM,appl,environment,environment_1,application,Promotion))
                    commands.append(s)
                if row[2].upper()=="UPDATE":
                    appl,SourcCrosswalk=row[0],row[3]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    s=ASCII_REMOVAL('zowe endevor update element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2} --fm {1} --os --ccid {0} --com "DEFAULT test�file�add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
                    commands.append(s)
                if row[2].upper()=="ADD":
                    appl,SourcCrosswalk=row[0],row[3]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    s=ASCII_REMOVAL('zowe endevor add element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2} --fm {1} --os --ccid {0} --com "DEFAULT test�file�add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
                    commands.append(s)
                if row[2].upper()=="MOVE":
                    appl,SourcCrosswalk,Promotion=row[0],row[3],row[1]
                    environment_1=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    s=ASCII_REMOVAL('zowe endevor move element {1} --env SUPP --sys {2} --sub {3} --typ APPL --sn 2 --ccid {0} --com "{4}" --sync'.format(RITM,appl,application,environment_1,Promotion))     
                    commands.append(s)
            zowe_cammands[file[:file.find(".")]+","+str(RITM)]=commands
            print("The Zowe Commands generated")
            shutil.move(os.path.join(SS_MIG_EDS_ESP_CWD,file),os.path.join(str(SS_MIG_EDS_ESP_CWD)+"_PROCESSED",file[:file.find(".")]+"_"+datetime.now().strftime("%Y%m%d%H%M%S")+".csv"))
            #shutil.copy2(os.path.join(SS_MIG_EDS_ESP_CWD,file), str(SS_MIG_EDS_ESP_CWD)+"_PROCESSED")
            print(f"{file} Moved to {SS_MIG_EDS_ESP_CWD} ")
        else:
            print("Validation failed and sending an email with failure details")
            mail_from,mail_to,mail_cc=emails()
            mail_sub='Re: ESP Endevor Selfservice Fail -'+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S")
            attachments=[]
            body=str("\n".join([ i for i in [file]+["Please find the below validation failure details"]+validation_result[1]+["Please check your migration form"]]))
            #send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
            print("Mail Sent sucussfully")
    else:
        print(f"{file} not exist in {SS_MIG_EDS_ESP_AUTHUSERS_CWD}") 

def zowe_LOG_genaration(zowe_cammands):
    for file,zowe_cammand_list in zowe_cammands.items():
        file_name=file.split(",")
        file=file_name[0]
        print("="*150)
        print(f"{file} going to generate Zowe Reports")
        RITM=file_name[1]
        log=file+"_"+datetime.now().strftime("%Y%m%d%H%M%S")+"_ENDEVOR_LOG.txt"
        total_count_of_ZOWE_perFile=len(zowe_cammand_list)
        if total_count_of_ZOWE_perFile!=0:
            SUCCESS_count=0
            report={}
            for zowe_cmd in zowe_cammand_list:
                zowe_cmd=zowe_cmd.replace(u'\xa0',' ')
                result=subprocess.run(zowe_cmd,shell=True,stdout=subprocess.PIPE)
                output = result.stdout.decode('utf-8')
                report.update({zowe_cmd:output})
                
                with io.open(log, "a", encoding="utf-8") as f:
                    f.write(zowe_cmd+"\n"+"*"*130+"\n"+output+"\n\n")
                # text_file = open(log, "a")
                # text_file.write(zowe_cmd+"\n"+"*"*130+"\n"+output+"\n\n")
                # text_file.close()
                try:
                    code=re.findall("finished with [0-9]+",output)[0].strip("finished with ") 
                except:
                    code=""
                    pass
                if code =='0004' or code =='0000':
                    SUCCESS_count +=1
                    print(f"{zowe_cmd} command sucuss")
                else:
                    print(f"{zowe_cmd} command Fail")
                    break
            if total_count_of_ZOWE_perFile==SUCCESS_count:
                print(f"{file} Zowe Report are going to send Mail")
                mail_from,mail_to,mail_cc=emails()
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/0-FAILED/0-UNATTEMPTED"
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n\n"+output+"\n" for zowcmd,output in report.items()])
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
                print("Mail Sent sucussfully")
                os.remove(log)
            else:
                print(f"{file} Zowe Report are going to send Mail")
                mail_from,mail_to,mail_cc=emails()
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n\n"+output+"\n" for zowcmd,output in report.items()])
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/1-FAILED/"+str(total_count_of_ZOWE_perFile-(SUCCESS_count+1))+"-UNATTEMPTED"
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
                print("Mail Sent sucussfully")
                os.remove(log)
        else:
            print(f"{file} not having any Zowe Commands")
        print(f'{file} log generated')
print("~"*150)
print(f"Count of Zowe forms after validation of CSV: {len(zowe_cammands.keys())}")
#zowe_LOG_genaration(zowe_cammands)
logging.shutdown()

message_log=[file for file in os.listdir(os.getcwd()) if file.endswith(".log") or file.endswith(".log")]
mail_from,mail_to,mail_cc=emails()
attachments=message_log
body=" Please Find the log file for authorization"
mail_sub="ESP Endevor Selfservice log mail"
#send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments) 
script_log_moving()