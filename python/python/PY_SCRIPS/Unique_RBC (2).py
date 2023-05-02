import sys
m=sys.argv[1]
output=m.split(".")[0]+'_Unique_RBC.xlsx'
import xml.etree.ElementTree as et
parsexml=et.parse(m)
root=parsexml.getroot()
data=[[ 'FOLDER_NAME','Rule based calendar Name','Defintion','MAXWAIT','ACTIVE_FROM','ACTIVE_TILL']]    
for r in root:
    k=list(r.attrib.keys()).index('FOLDER_NAME')
    #k=r.attrib.get('FOLDER_NAME',"")
    v=list(r.attrib.values())[k]
    RBC=r.findall('RULE_BASED_CALENDAR')
    for a in RBC:
        key=list(a.attrib.keys())
        value=list(a.attrib.values())
        if "ACTIVE_FROM" in key and "ACTIVE_TILL" in key:
            s=['{0}="{1}"'.format(key[i],value[i]) for i in range(1,len(key))]
            data.append([v,value[0]," ".join(s[1:-3]),s[0],s[-3],s[-2]])  
        if "ACTIVE_FROM" in key and "ACTIVE_TILL"  not in key:
            s=['{0}="{1}"'.format(key[i],value[i]) for i in range(1,len(key))]
            data.append([v,value[0]," ".join(s[1:-2]),s[0],s[-2],''])
        if "ACTIVE_FROM" not in key and "ACTIVE_TILL" in key:
            s=['{0}="{1}"'.format(key[i],value[i]) for i in range(1,len(key))]
            data.append([v,value[0]," ".join(s[1:-2]),s[0],'',s[-2]])
        if "ACTIVE_FROM" not in key and "ACTIVE_TILL" not in key:
            s=['{0}="{1}"'.format(key[i],value[i]) for i in range(1,len(key))]
            data.append([v,value[0]," ".join(s[1:-1]),s[0],'',''])  
import pandas as pd
df1 = pd.DataFrame(columns=data[0], data=data[1:])
df2=df1.iloc[:,1:3]
df3=df1.iloc[:,2]
df4=df1.iloc[:,0:3:2]
df3=df3.drop_duplicates().reset_index().iloc[:,1:]
df2=df2.drop_duplicates().reset_index().iloc[:,1:]
df4=df4.drop_duplicates(subset='Defintion').reset_index().iloc[:,1:]
with pd.ExcelWriter(output) as writer:
    df1.to_excel(writer, sheet_name='output',index=False)
    df2.to_excel(writer, sheet_name='unique_RBC_Definition',index=False)
    df3.to_excel(writer, sheet_name='unique_Definition',index=False)
    df4.to_excel(writer, sheet_name='unique_Definition_their_Folder',index=False)
print("success") 
