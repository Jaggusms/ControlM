import os
import difflib
from datetime import datetime
import shutil
from sre_constants import SUCCESS
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import subprocess
import re
#https://github.com/zowe/zowe-cli-sample-scripts/tree/master/python
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
            pass
        
    sender=sender_email
    smtpObj = smtplib.SMTP('30.132.52.66')
    smtpObj.sendmail(sender, mail_to+mail_cc, str(msg))
    #print("mail sent successfully")
#send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)

def emails():
    mail_from=["Jagadeesh.Sannna@legato.com"]
    mail_to=['Jagadeesh.Sanniboina@legato.com','Jagadeesh.Sanniboina@legato.com']
    mail_cc=['Jagadeesh.Sanniboina@legato.com',]
    return mail_from,mail_to,mail_cc

def validation(Migatrion_file,cros_work_file):
    validation_success=True
    COLUMN=Migatrion_file.columns
    cros_work_file_data=[]
    failure_data=[]
    for idx,rows in cros_work_file.iterrows():
        cros_work_file_data.append("".join(rows))
    for idx,rows in Migatrion_file.iterrows():
        #print(rows[COLUMN[0]][-3],rows[COLUMN[1]].split(".")[-2],rows[COLUMN[0]][-1],rows[COLUMN[2]].split(".")[-2])
        try:
            if not rows[COLUMN[1]].split(".")[-2].startswith(rows[COLUMN[0]][-3]) or  not rows[COLUMN[2]].split(".")[-2].startswith(rows[COLUMN[0]][-1]):
                failure_data.append(",".join(rows))
                validation_success=False
        except :
            failure_data.append(",".join(rows))
            pass
        #print(rows[0]+rows[1]+rows[2])
        if "".join(rows) not in cros_work_file_data:
            failure_data.append(",".join(rows))
            validation_success=False        
    return validation_success,failure_data

cwd=os.getcwd()
active=os.path.join(cwd,'ACTIVE')
ACTIVE_CSV=[file.upper() for file in os.listdir(active) if file.endswith(".csv") or file.endswith(".CSV")]
APPROVALS=os.path.join(cwd,'APPROVALS')
ACTIVE_MSG=[file.upper() for file in os.listdir(APPROVALS) if file.endswith(".msg") or file.endswith(".MSG")]
PROCESSED=[]
ZOWE=[]
zowe_cammands={}
for file in ACTIVE_CSV:
    approval_string=file[:file.find(".CSV")]+"_PRC_LEAD_APPROVAL.MSG"
    #print(difflib.get_close_matches(approval_string, ACTIVE_MSG, cutoff=0.7))
    if difflib.get_close_matches(approval_string, ACTIVE_MSG, cutoff=0.7):
        cros_work_file=pd.read_csv(os.path.join(cwd,'Retrofit_CrossWalk_File.csv')).fillna("na")
        for i in cros_work_file.columns:
            cros_work_file[i]=cros_work_file[i].str.strip()
        Migatrion_file=os.path.join(active,file)
        df2 = pd.read_csv(Migatrion_file, header=2).fillna("na")
        for i in df2.columns:
            df2[i]=df2[i].str.strip()
        validation_result=validation(df2.iloc[:,[1,3,4]],cros_work_file)

        RITM_Data =pd.read_csv(Migatrion_file, nrows=4).fillna("na_")
        RITM=RITM_Data[list(RITM_Data.columns)[0]].loc[0].strip()
        commands=[]
        if validation_result[0]:
            #print(RITM)
            columns=df2.columns
            d=df2.iloc[df2[df2[columns[2]].str.contains('Move',case=False)].index.tolist(),:]  
            df3=d.reset_index().iloc[:,1:]
            #print(df3)
            for data,row in df2.iterrows():
                appl=df3[columns[0]].loc[0]
                SourcCrosswalk=df3[columns[3]].loc[0]
                environment_1=SourcCrosswalk.split(".")[4]
                application=SourcCrosswalk.split(".")[3]
                Promotion=df3[columns[1]].loc[0]
                commands.append('zowe endevor move element {1} --env SUPP --sys {2} --sub {3} --typ APPL --sn 1 --ccid {0} --com "{4}" --sync'.format(RITM,appl,application,environment_1,Promotion))     
            
            d=df2.iloc[df2[df2[columns[2]].str.contains('Transfer',case=False)].index.tolist(),:]   
            df3=d.reset_index().iloc[:,1:]
            for data,row in df3.iterrows():
                appl=df3[columns[0]].loc[0]
                SourcCrosswalk=df3[columns[3]].loc[0]
                environment_1=df3[columns[4]].loc[0]
                environment_1=environment_1.split(".")[4]
                environment=SourcCrosswalk.split(".")[4]
                application=SourcCrosswalk.split(".")[3]
                Promotion=df3[columns[1]].loc[0]
                commands.append('zowe endevor transfer element {1} --env SUPP --sys {4} --sub {2} --typ APPL --sn 1 --ccid {0} --com "{5}" --toenv SUPP --tosys {4} --tosub {3} --toele {1} --totyp APPL --tosn 1 --sync'.format(RITM,appl,environment,environment_1,application,Promotion))									  
            d=df2.iloc[df2[df2[columns[2]].str.contains('Add',case=False)].index.tolist(),:]   
            df3=d.reset_index().iloc[:,1:]
            for data,row in df3.iterrows():
                appl=df3[columns[0]].loc[0]
                SourcCrosswalk=df3[columns[3]].loc[0]
                environment=SourcCrosswalk.split(".")[4]
                application=SourcCrosswalk.split(".")[3]
                commands.append('zowe endevor add element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULTtest file add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
            
            d=df2.iloc[df2[df2[columns[2]].str.contains('Update',case=False)].index.tolist(),:]   
            df3=d.reset_index().iloc[:,1:]
            for data,row in df3.iterrows():
                appl=df3[columns[0]].loc[0]
                SourcCrosswalk=df3[columns[3]].loc[0]
                environment=SourcCrosswalk.split(".")[4]
                application=SourcCrosswalk.split(".")[3]
                commands.append('zowe endevor update element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULTtest file add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
            
            zowe_cammands[file.split(".CSV")[0]+","+str(RITM)]=commands
            #shutil.move(os.path.join(active,file),os.path.join(cwd,"PROCESSED1",file))
            shutil.copy2(os.path.join(active,file), 'PROCESSED1')
        else:
            zowe_cammands[file.split(".CSV")[0]+","+str(RITM)]=commands
            mail_from,mail_to,mail_cc=emails()
            mail_sub='Re: ESP Endevor Selfservice Fail -'+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S")
            attachments=[]
            body=str("\n".join([ i for i in [file]+["Validation Failure Data as follows"]+validation_result[1]+["Please check your Migration Form"]]))
            send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)


 
def zowe_log_genaration(zowe_cammands):
    for file,zowe_cammand_list in zowe_cammands.items():
        file_name=file.split(",")
        file=file_name[0]
        RITM=file_name[1]
        log=file+datetime.now().strftime("%Y%m%d%H%M%S")+"_LOG.txt"
        total_count_of_ZOWE_perFile=len(zowe_cammand_list)
        if total_count_of_ZOWE_perFile!=0:
            SUCCESS_count=0
            report={}
            for zowe_cmd in zowe_cammand_list:
                result=subprocess.run(zowe_cmd,shell=True,stdout=subprocess.PIPE)
                output = result.stdout.decode('utf-8')
                report.update({zowe_cmd:output})
                text_file = open(log, "a")
                text_file.write(zowe_cmd+"\n"+"*"*130+"\n"+output+"\n\n")
                text_file.close()
                try:
                    code=re.findall("finished with [0-9]+",output)[0].strip("finished with ") 
                except :
                    code=""
                    pass
                if code =='0004' or code =='0000':
                    SUCCESS_count +=1
                else:
                    break
            if total_count_of_ZOWE_perFile==SUCCESS_count:
                mail_from,mail_to,mail_cc=emails()
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/0-FAILED/0-UNATTEMPTED"
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n"+output+"\n" for zowcmd,output in report.items()])
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
            else:
                mail_from,mail_to,mail_cc=emails()
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n"+output+"\n" for zowcmd,output in report.items()])
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/1-FAILED/"+str(total_count_of_ZOWE_perFile-(SUCCESS_count+1))+"-UNATTEMPTED"
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
        print(f'{file} log generated')
#zowe_log_genaration(zowe_cammands)