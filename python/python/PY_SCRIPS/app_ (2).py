from csv import excel
from datetime import datetime
import re
import sys
import pandas as pd
print("Program executing Please wait!")
start=datetime.now()
data=[]
original=[]
text_file=sys.argv[1]
xml_file=sys.argv[2]
excel_file=sys.argv[3]
with open(text_file,'r') as f:
    original=f.readlines()
    pass
count=[]
for i,line in enumerate(original):
    if "/*" not in line and i in count:
        continue
    else:
        s=""
        rows=["","",""]
        c=0
        for j,line1 in enumerate(original[i:i+25]):
            if "/*" in line1:
                break
            s +=line1.strip("\n")+';'
            if c==0:
                sub_string=s.split(".")[1]
                rows[0]=sub_string[:sub_string.index(")")]
                c +=1
            count.append(i+j)
        appl=re.findall("\(([A-Za-z0-9@#%.]+)\)",s)
        rows[1]=appl[1] if len(appl)>1 else ""
        rows[2]="Yes" if "CALENDAR SYSTEM" in s  else "No" 
        data.append(rows)
        s=""
df=pd.DataFrame(data,columns=['EVENT Name in ESP','Member Name in ESP','Ordermethod in ESP(Yes or No)'])
df1=df.drop_duplicates(keep="first").reset_index().iloc[1:,1:]
df2=pd.read_excel(excel_file,sheet_name="CTM002-FINAL",header=2,usecols="O,K,H").fillna("").rename(columns={"EVENT Name(APPL Name + 8 charatcers)":"EVENT Name in ESP"}).iloc[:,::-1]
df3=pd.merge(df1, df2, how="left", on=["EVENT Name in ESP"]).fillna("")
import xml.etree.ElementTree as et
parsexml=et.parse(xml_file)
root=parsexml.getroot()
xml=[]
for r in root:
    d=r.attrib
    FOLDER_NAME=d['FOLDER_NAME']
    try:
        order_method=d['FOLDER_ORDER_METHOD']
        order_method= 'Yes' if order_method=='SYSTEM' else "No"
    except:
        order_method="No"
    xml.append([FOLDER_NAME,order_method])
xml_df=pd.DataFrame(xml,columns=['Folder Path','Ordermethod in CTM'])
xml_df=xml_df.drop_duplicates(keep="first")
df4=pd.merge(df3,xml_df , how="left", on=["Folder Path"]).fillna("").rename(columns={"Folder Path":"Folder Name in Rename Sheet","APPL Name ( Max 8 Characters)":"APPL Name in Rename sheet"})
df4['Member name = APPL name']=(df4['Member Name in ESP']==df4['APPL Name in Rename sheet'])
df4['Ordermethod in ESP = Ordermentiond in CTM']=(df4['Ordermethod in ESP(Yes or No)']==df4['Ordermethod in CTM'])
one=list(df4.iloc[:,0])
four=list(df4.iloc[:,3])
df4['APPL Name check in Event name']=[one[i][:len(four[i])]==four[i] if len(four[i])>2 else False for i in range(len(one))]
df4.to_excel("ESP_CTM_Ordermethod_Validations.xlsx",sheet_name="ESP-CTM Details",index=False)
print(f"completed in {datetime.now()-start}")
