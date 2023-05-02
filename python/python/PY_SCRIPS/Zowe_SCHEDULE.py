import os
from datetime import datetime
import pandas as pd
import re,sys

Migatrion_file,cros_work_file=sys.argv[1],sys.argv[2]
try:
    cros_work_file=pd.read_csv(cros_work_file).fillna("na")
except:
    print("Cross Work file Not exist")
    sys.exit(1)
zowe_cammands={}
for file in SS_MIG_EDS_ESP:
    if file in SS_MIG_EDS_ESP_AUTHUSERS:
        logger.info("*"*150)
        logger.info(f"{file} exist in {SS_MIG_EDS_ESP_AUTHUSERS_CWD} and going for Validation") 
        for i in cros_work_file.columns:
            cros_work_file[i]=cros_work_file[i].str.strip()
        Migatrion_file=os.path.join(SS_MIG_EDS_ESP_CWD,file)
        try:
            mig_file_data =pd.read_csv(Migatrion_file).fillna("na")
            logger.info(f"{file} read Sucessfull")
        except:
            logger.info(f"{file} read not Sucessfull")
        RITM=mig_file_data[list(mig_file_data.columns)[0]].loc[0].strip()
        validation_sucess=True
        if not RITM.startswith("RITM"):
            logger.info(f"{RITM} not Valid")
            validation_sucess=False
        else:
            logger.info(f"{RITM} is Valid")
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
        if validation_result[0] and validation_sucess:
            logger.info("Validation Sucess going to generate the Zowe Commands")
            for data,row in df2.iterrows():
                if row[2].upper()=="TRANSFER":
                    appl,Promotion,SourcCrosswalk,environment_1=row[0],row[1],row[3],row[4]
                    environment_1=environment_1.split(".")[4]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    commands.append('zowe endevor transfer element {1} --env SUPP --sys {4} --sub {2} --typ APPL --sn 2 --ccid {0} --com "{5}" --toenv SUPP --tosys {4} --tosub {3} --toele {1} --totyp APPL --tosn 2 --sync --pg APPL --bed'.format(RITM,appl,environment,environment_1,application,Promotion))									  
                    
                if row[2].upper()=="UPDATE":
                    appl,SourcCrosswalk=row[0],row[3]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    commands.append('zowe endevor update element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT test file add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
            
                if row[2].upper()=="ADD":
                    appl,SourcCrosswalk=row[0],row[3]
                    environment=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    commands.append('zowe endevor add element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT test file add" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
                
                if row[2].upper()=="MOVE":
                    appl,SourcCrosswalk,Promotion=row[0],row[3],row[1]
                    environment_1=SourcCrosswalk.split(".")[4]
                    application=SourcCrosswalk.split(".")[3]
                    commands.append('zowe endevor move element {1} --env SUPP --sys {2} --sub {3} --typ APPL --sn 2 --ccid {0} --com "{4}" --sync'.format(RITM,appl,application,environment_1,Promotion))     
             
            zowe_cammands[file.split(".csv")[0]+","+str(RITM)]=commands
            logger.info("The Zowe Commands generated")
            shutil.move(os.path.join(SS_MIG_EDS_ESP_CWD,file),os.path.join(str(SS_MIG_EDS_ESP_CWD)+"_PROCESSED",file))
            #shutil.copy2(os.path.join(SS_MIG_EDS_ESP_CWD,file), str(SS_MIG_EDS_ESP_CWD)+"_PROCESSED")
            logger.info(f"{file} Moved to {SS_MIG_EDS_ESP_CWD} ")
        else:
            logger.info("Validation Fail going to send the Mail with Failure Data")
            mail_from,mail_to,mail_cc=emails()
            mail_sub='Re: ESP Endevor Selfservice Fail -'+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S")
            attachments=[]
            body=str("\n".join([ i for i in [file]+["Validation Failure Data as follows"]+validation_result[1]+["Please check your Migration Form"]]))
            send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
            logger.info("Mail Sent sucussfully")
    else:
        logger.info(f"{file} not exist in {SS_MIG_EDS_ESP_AUTHUSERS_CWD}") 

def zowe_LOG_genaration(zowe_cammands):
    for file,zowe_cammand_list in zowe_cammands.items():
        file_name=file.split(",")
        file=file_name[0]
        logger.info("="*150)
        logger.info(f"{file} going to generate Zowe Reports")
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
                text_file = open(log, "a")
                text_file.write(zowe_cmd+"\n"+"*"*130+"\n"+output+"\n\n")
                text_file.close()
                try:
                    code=re.findall("finished with [0-9]+",output)[0].strip("finished with ") 
                except:
                    code=""
                    pass
                if code =='0004' or code =='0000':
                    SUCCESS_count +=1
                    logger.info(f"{zowe_cmd} command sucuss")
                else:
                    logger.info(f"{zowe_cmd} command Fail")
                    break
            if total_count_of_ZOWE_perFile==SUCCESS_count:
                logger.info(f"{file} Zowe Report are going to send Mail")
                mail_from,mail_to,mail_cc=emails()
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/0-FAILED/0-UNATTEMPTED"
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n\n"+output+"\n" for zowcmd,output in report.items()])
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
                logger.info("Mail Sent sucussfully")
                os.remove(log)
            else:
                logger.info(f"{file} Zowe Report are going to send Mail")
                mail_from,mail_to,mail_cc=emails()
                attachments=[log]
                body="".join([f"Please find the below promotion log details for the APPLs given in the {file} "]+["\n"+"*"*130+"\n"+zowcmd+"\n\n"+output+"\n" for zowcmd,output in report.items()])
                mail_sub="ESP Endevor Selfservice - "+RITM+"-"+datetime.now().strftime("%Y%m%d%H%M%S") +"-  "+str(SUCCESS_count)+"-SUCCEEDED/1-FAILED/"+str(total_count_of_ZOWE_perFile-(SUCCESS_count+1))+"-UNATTEMPTED"
                send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
                logger.info("Mail Sent sucussfully")
                os.remove(log)
        else:
            logger.info(f"{file} not having any Zowe Commands")
        print(f'{file} log generated')
logger.info("~"*150)
logger.info(f"Count of Zowe forms after validation of CSV: {len(zowe_cammands.keys())}")
zowe_LOG_genaration(zowe_cammands)
logging.shutdown()

message_log=[file for file in os.listdir(os.getcwd()) if file.endswith(".log") or file.endswith(".log")]
mail_from,mail_to,mail_cc=emails()
attachments=message_log
body=" Please Find the log file for authorization"
mail_sub="ESP Endevor Selfservice log mail"
send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments) 
script_log_moving()