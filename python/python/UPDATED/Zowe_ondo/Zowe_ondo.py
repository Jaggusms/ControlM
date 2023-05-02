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
for i in cros_work_file.columns:
    cros_work_file[i]=cros_work_file[i].str.strip()
try:
    mig_file_data=pd.read_csv(Migatrion_file).fillna("na")
except:
    print(f"{Migatrion_file} read not Sucessfull")
RITM=mig_file_data[list(mig_file_data.columns)[0]].loc[0].strip()
header_value=1
for i, value in enumerate(list(mig_file_data[mig_file_data.columns[0]])[:5]):
    if "APPL" in value.upper():
        header_value=i
        break
col={}
for key,value in zip(mig_file_data.columns,list(mig_file_data.loc[header_value])):
    col.update({key:value})
new_df  = mig_file_data.iloc[header_value+1:,:6].rename(columns=col)
df2=new_df.reset_index().iloc[:,1:]
for i in df2.columns:
    df2[i]=df2[i].str.strip()
commands=[]
for data,row in df2.iterrows():
    if row[2].upper()=="TRANSFER":
        appl,Promotion,SourcCrosswalk,environment_1,SCHEDULE=row[0],row[1],row[3],row[4],row[5]
        environment_1=environment_1.split(".")[4]
        environment=SourcCrosswalk.split(".")[4]
        application=SourcCrosswalk.split(".")[3]
        if SCHEDULE.upper()=="AUTO":
            commands.append('zowe endevor transfer element {1} --env SUPP --sys {4} --sub {2} --typ APPL --sn 2 --ccid {0} --com "{5} AUTO" --toenv SUPP --tosys {4} --tosub {3} --toele {1} --totyp APPL --tosn 2 --sync --pg APPL --bed'.format(RITM,appl,environment,environment_1,application,Promotion))									  
        if SCHEDULE.upper()=="ONDEMAND":
            commands.append('zowe endevor transfer element {1} --env SUPP --sys {4} --sub {2} --typ APPL --sn 2 --ccid {0} --com "{5} OND" --toenv SUPP --tosys {4} --tosub {3} --toele {1} --totyp APPL --tosn 2 --sync --pg APPL --bed'.format(RITM,appl,environment,environment_1,application,Promotion))									  
        else:
            pass
    if row[2].upper()=="UPDATE":
        appl,SourcCrosswalk,SCHEDULE=row[0],row[3],row[5]
        environment=SourcCrosswalk.split(".")[4]
        application=SourcCrosswalk.split(".")[3]
        if SCHEDULE.upper()=="AUTO":
            commands.append('zowe endevor update element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT AUTO" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
        if SCHEDULE.upper()=="ONDEMAND":
            commands.append('zowe endevor update element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT OND" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
        else:
            pass

    if row[2].upper()=="ADD":
        appl,SourcCrosswalk,SCHEDULE=row[0],row[3],row[5]
        environment=SourcCrosswalk.split(".")[4]
        application=SourcCrosswalk.split(".")[3]
        if SCHEDULE.upper()=="AUTO":
            commands.append('zowe endevor add element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT AUTO" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
        if SCHEDULE.upper()=="ONDEMAND":
            commands.append('zowe endevor add element {1} --env SUPP --sys {3} --sub {4} --typ APPL --fd {2}  --fm {1} --os --ccid {0} --com "DEFAULT OND" --g'.format(RITM,appl,SourcCrosswalk,application,environment))
        else:
            pass

    if row[2].upper()=="MOVE":
        appl,SourcCrosswalk,Promotion,SCHEDULE=row[0],row[3],row[1],row[5]
        environment_1=SourcCrosswalk.split(".")[4]
        application=SourcCrosswalk.split(".")[3]
        if SCHEDULE.upper()=="AUTO":
            commands.append('zowe endevor move element {1} --env SUPP --sys {2} --sub {3} --typ APPL --sn 2 --ccid {0} --com "{4} AUTO" --sync'.format(RITM,appl,application,environment_1,Promotion))     
        if SCHEDULE.upper()=="ONDEMAND":
            commands.append('zowe endevor move element {1} --env SUPP --sys {2} --sub {3} --typ APPL --sn 2 --ccid {0} --com "{4} OND" --sync'.format(RITM,appl,application,environment_1,Promotion))     
        else:
            pass
        
for i in commands:
    print(i)