import sys
m=sys.argv[1]
output=m.split(".")[0]+"_details"+'.xlsx'
import xml.etree.ElementTree as et
parsexml=et.parse(m)
root=parsexml.getroot()
def VARIABLE1(VARIABLE,keypoint):
    L_VARIABLE=[]
    if VARIABLE:
        if 'VARIABLE' not in keypoint:
            keypoint.append('VARIABLE')
        
        for B in VARIABLE:
            s=list(B.attrib.values())
            L_VARIABLE.append(" ".join(s))   
        return L_VARIABLE
    else:
        if 'VARIABLE' not in keypoint:
            keypoint.append('VARIABLE')
        return ''
def RBC1(RBC,keypoint):
    L_RBC=[]
    if RBC:
        if 'RBC' not in keypoint:
            keypoint.append('RBC')

        for a in RBC:
            s=list(a.attrib.values())
            L_RBC.append(" ".join(s))
        return L_RBC
    else:
        if 'RBC' not in keypoint:
            keypoint.append('RBC')
        return ''
def CONTROL1(CONTROL,keypoint):
    L_CONTROL=[]
    if CONTROL:
        if 'CONTROL' not in keypoint:
            keypoint.append('CONTROL')

        for a in CONTROL:
            s=list(a.attrib.values())
            L_CONTROL.append(str(s[0])+' '+str(s[1]))
        return L_CONTROL
    else:
        if 'CONTROL' not in keypoint:
            keypoint.append('CONTROL')
        return '' 

def QUANTITATIVE1(QUA,keypoint):
    L_QUA=[]
    if QUA:
        if 'QUANTITATIVE' not in keypoint:
            keypoint.append('QUANTITATIVE')
        for a in QUA:
            s=list(a.attrib.values())
            L_QUA.append(str(s[0])+' '+str(s[1]))
        return L_QUA
    else:
        if 'QUANTITATIVE' not in keypoint:
            keypoint.append('QUANTITATIVE')
        return ''
    
def INCOND1(INCOND,keypoint):
    L_INCOND=[]
    if INCOND:
        if 'INCOND' not in keypoint:
            keypoint.append('INCOND')

        for a in INCOND:
            s=list(a.attrib.values())
            L_INCOND.append(str(s[0])+' '+str(s[1])+" "+str(s[2]))
        return L_INCOND	
    else:
        if 'INCOND' not in keypoint:
            keypoint.append('INCOND')
        return '' 

def OUTCOND1(OUTCOND,keypoint):
    L_OUT=[]
    if OUTCOND:
        if 'OUTCOND' not in keypoint:
            keypoint.append('OUTCOND')
        for a in OUTCOND:
            s=list(a.attrib.values())
            L_OUT.append(str(s[0])+' '+str(s[1])+" "+str(s[2]))
        return L_OUT
    else:
        if 'OUTCOND' not in keypoint:
            keypoint.append('OUTCOND')
        return ''

def ON1(ON,keypoint):
    L_ON=[]
    if ON:
        if 'ON' not in keypoint:
            keypoint.append('ON')
        key=['CODE']
        st=''
        for p in ON:
            k=list(p.attrib.keys())
            v=list(p.attrib.values())
            for q in key:
                if q in k:
                    st +=str(v[k.index(q)])+" "
                DOACTION=p.findall('DOACTION')
                if DOACTION:
                    for aB in DOACTION:
                        l=list(aB.attrib.values())
                        st +=" ".join(l)+" "
                DOCOND=p.findall('DOCOND')
                if DOCOND:
                    for aB in DOCOND:
                        l=list(aB.attrib.values())
                        st +=" ".join(l)+" "
                DOEMAIL=p.findall('DOMAIL')
                if DOEMAIL:
                    for aB in DOEMAIL:
                        l=list(aB.attrib.values())
                        st +=" ".join(l)+" "  
                DOSHOUT=p.findall('DOSHOUT')
                if DOSHOUT:
                    for aB in DOSHOUT:
                        l=list(aB.attrib.values())
                        st +=" ".join(l)+" "  
        L_ON.append(st)
        return L_ON           
    else:
        if 'ON' not in keypoint:
            keypoint.append('ON')
        return ''
def SHOUT1(SHOUT,keypoint):
    L_SHOUT=[]
    if SHOUT:
        if 'NOTFY BEFOR(0)/AFTER' not in keypoint:
            keypoint.append('NOTFY BEFOR(0)/AFTER')
        for a in SHOUT:
            s=list(a.attrib.values())
            L_SHOUT.append(" ".join(s))
        return L_SHOUT
    else:
        if 'NOTFY BEFOR(0)/AFTER' not in keypoint:
            keypoint.append('NOTFY BEFOR(0)/AFTER')
        return ''
    
keypoint=['PARENT_FOLDER','FOLDER_NAME','DATACENTER','FOLDER_ORDER_METHOD','RUN_AS','APPLICATION','SUB_APPLICATION','DESCRIPTION','SITE_STANDARD_NAME','TIMEFROM','TIMETO','CYCLIC','INTERVAL','MAXWAIT','MAXRERUN','CONFIRM']
  
vaa=[[ 'PARENT_FOLDER','FOLDER_NAME','DATACENTER',   'FOLDER_ORDER_METHOD', 'RUN_AS', 'APPLICATION', 'SUB_APPLICATION','DESCRIPTION', 'SITE_STANDARD_NAME', 'TIMEFROM', 'TIMETO', 'CYCLIC', 'INTERVAL', 'MAXWAIT', 'MAXRERUN', 'VARIABLE', 'RBC', 'CONTROL', 'INCOND', 'OUTCOND', 'ON', 'NOTFY_BEFOR(0)/AFTER(1)']]   
vaa2=vaa    
for r in root:
    k=list(r.attrib.keys())
    v=list(r.attrib.values())

    va=[]
    for q in keypoint[:15]:
        if q in k:
            va.append(v[k.index(q)])
        else:
            if q=='FOLDER_ORDER_METHOD':
                va.append('None Manuval Order')
            else:
                va.append('')
    VARIABLE=r.findall('VARIABLE')
    va.append(VARIABLE1(VARIABLE,keypoint)) 
    
    RBC=r.findall('RULE_BASED_CALENDAR')
    va.append(RBC1(RBC,keypoint))
    
    CONTROL=r.findall('CONTROL')
    va.append(CONTROL1(CONTROL,keypoint))
    
    INCOND=r.findall('INCOND')
    va.append(INCOND1(INCOND,keypoint))
    
    OUTCOND=r.findall('OUTCOND')
    va.append(OUTCOND1(OUTCOND,keypoint))
    
    ON=r.findall('ON')
    va.append(ON1(ON,keypoint))
    
    SHOUT=r.findall('SHOUT')
    va.append(SHOUT1(SHOUT,keypoint))
    
    if va not in vaa:
        vaa.append(va)
    
keypoint=['PARENT_FOLDER','JOBNAME','DATACENTER','FOLDER_ORDER_METHOD','RUN_AS','APPLICATION','SUB_APPLICATION','DESCRIPTION','SITE_STANDARD_NAME','TIMEFROM','TIMETO','CYCLIC','INTERVAL','MAXWAIT','MAXRERUN','CONFIRM']
for r1 in root:
    subfolder=r1.findall("SUB_FOLDER")
    for r in subfolder:
        k=list(r.attrib.keys())
        v=list(r.attrib.values())
        va=[]
        for q in keypoint[:15]:
            if q in k:
                va.append(v[k.index(q)])
            else:
                if q=='FOLDER_ORDER_METHOD':
                    va.append('None Manuval Order')
                else:
                    va.append('')
        vaa.append(va)
        VARIABLE=r.findall('VARIABLE')
        va.append(VARIABLE1(VARIABLE,keypoint)) 
    
        RBC=r.findall('RULE_BASED_CALENDAR')
        va.append(RBC1(RBC,keypoint))
    
        CONTROL=r.findall('CONTROL')
        va.append(CONTROL1(CONTROL,keypoint))
    
        INCOND=r.findall('INCOND')
        va.append(INCOND1(INCOND,keypoint))
    
        OUTCOND=r.findall('OUTCOND')
        va.append(OUTCOND1(OUTCOND,keypoint))
    
        ON=r.findall('ON')
        va.append(ON1(ON,keypoint))
    
        SHOUT=r.findall('SHOUT')
        va.append(SHOUT1(SHOUT,keypoint))
    
        if va not in vaa:
            vaa.append(va)     



     
for r1 in root:
    subfolder=r1.findall("SUB_FOLDER")
    for j in subfolder:
        subfolder=j.findall("SUB_FOLDER")
        for r in subfolder:
            k=list(r.attrib.keys())
            v=list(r.attrib.values())
            va=[]
            for q in keypoint[:15]:
                if q in k:
                    va.append(v[k.index(q)])
                else:
                    if q=='FOLDER_ORDER_METHOD':
                        va.append('None Manuval Order')
                    else:
                        va.append('')
            vaa.append(va)
            VARIABLE=r.findall('VARIABLE')
            va.append(VARIABLE1(VARIABLE,keypoint)) 
        
            RBC=r.findall('RULE_BASED_CALENDAR')
            va.append(RBC1(RBC,keypoint))
        
            CONTROL=r.findall('CONTROL')
            va.append(CONTROL1(CONTROL,keypoint))
        
            INCOND=r.findall('INCOND')
            va.append(INCOND1(INCOND,keypoint))
        
            OUTCOND=r.findall('OUTCOND')
            va.append(OUTCOND1(OUTCOND,keypoint))
        
            ON=r.findall('ON')
            va.append(ON1(ON,keypoint))
        
            SHOUT=r.findall('SHOUT')
            va.append(SHOUT1(SHOUT,keypoint))
        
            if va not in vaa:
                vaa.append(va)

          
            

keypoint1=['JOBNAME','PARENT_FOLDER','APPL_TYPE','DESCRIPTION','TASKTYPE','CMDLINE','NODEID','RUN_AS','APPLICATION','SUB_APPLICATION','PRIORITY','CONFIRM','RETRO','DAYS','TIMEFROM','TIMETO','CYCLIC','MAXRERUN','INTERVAL','MAXWAIT']
vaa1=[['JOBNAME', 'PARENT_FOLDER', 'APPL_TYPE', 'DESCRIPTION', 'TASKTYPE', 'CMDLINE', 'NODEID', 'RUN_AS', 'APPLICATION', 'SUB_APPLICATION', 'PRIORITY', 'CONFIRM', 'RETRO', 'DAYS', 'TIMEFROM', 'TIMETO', 'CYCLIC', 'MAXRERUN', 'INTERVAL', 'MAXWAIT', 'VARIABLE', 'RBC', 'CONTROL', 'QUANTITATIVE', 'INCOND', 'OUTCOND', 'ON', 'NOTFY_BEFOR(0)/AFTER']]# data of the headers
vaa3=vaa1

for r in root.findall("./SMART_FOLDER/SUB_FOLDER/"):
    JOB=r.findall('JOB')
    #finding the all attribuets of job
    for j in JOB:
        k=list(j.attrib.keys())       
        v=list(j.attrib.values())
        va=[]
        for q in keypoint1[:20]:  #30 is length of header as for the first
            if q in k:
                va.append(v[k.index(q)])
            else:
                va.append('')
        VARIABLE=j.findall('VARIABLE')
        va.append(VARIABLE1(VARIABLE,keypoint1)) 
            
        RBC=j.findall('RULE_BASED_CALENDARS')
        va.append(RBC1(RBC,keypoint1))
    
        CONTROL=j.findall('CONTROL')
        va.append(CONTROL1(CONTROL,keypoint1))
        
        QUA=j.findall('QUANTITATIVE')
        va.append(QUANTITATIVE1(QUA,keypoint1))
            
        INCOND=j.findall('INCOND')
        va.append(INCOND1(INCOND,keypoint1))
            
        OUTCOND=j.findall('OUTCOND')
        va.append(OUTCOND1(OUTCOND,keypoint1))
            
        ON=j.findall('ON')
        va.append(ON1(ON,keypoint1))
            
        SHOUT=j.findall('SHOUT')
        va.append(SHOUT1(SHOUT,keypoint1))
        if va not in vaa:
            vaa1.append(va)

for r in root.findall("./SMART_FOLDER/"):
    JOB=r.findall('JOB')
    #finding the all attribuets of job
    for j in JOB:
        k=list(j.attrib.keys())       
        v=list(j.attrib.values())
        va=[]
        for q in keypoint1[:20]:  #30 is length of header as for the first
            if q in k:
                va.append(v[k.index(q)])
            else:
                va.append('')
        VARIABLE=j.findall('VARIABLE')
        va.append(VARIABLE1(VARIABLE,keypoint1)) 
            
        RBC=j.findall('RULE_BASED_CALENDARS')
        va.append(RBC1(RBC,keypoint1))
    
        CONTROL=j.findall('CONTROL')
        va.append(CONTROL1(CONTROL,keypoint1))
        
        QUA=j.findall('QUANTITATIVE')
        va.append(QUANTITATIVE1(QUA,keypoint1))
            
        INCOND=j.findall('INCOND')
        va.append(INCOND1(INCOND,keypoint1))
            
        OUTCOND=j.findall('OUTCOND')
        va.append(OUTCOND1(OUTCOND,keypoint1))
            
        ON=j.findall('ON')
        va.append(ON1(ON,keypoint1))
            
        SHOUT=j.findall('SHOUT')
        va.append(SHOUT1(SHOUT,keypoint1))
        if va not in vaa:
            vaa1.append(va)

for r in root:
    JOB=r.findall('JOB')
    #finding the all attribuets of job
    for j in JOB:
        k=list(j.attrib.keys())       
        v=list(j.attrib.values())
    
        va=[]
        for q in keypoint1[:20]:  #30 is length of header as for the first
            if q in k:
                va.append(v[k.index(q)])
            else:
                va.append('')
      # variable keyword details appending in the data
        VARIABLE=j.findall('VARIABLE')
        va.append(VARIABLE1(VARIABLE,keypoint1)) 
            
        RBC=j.findall('RULE_BASED_CALENDARS')
        va.append(RBC1(RBC,keypoint1))
    
        CONTROL=j.findall('CONTROL')
        va.append(CONTROL1(CONTROL,keypoint1))
        
        QUA=j.findall('QUANTITATIVE')
        va.append(QUANTITATIVE1(QUA,keypoint1))
            
        INCOND=j.findall('INCOND')
        va.append(INCOND1(INCOND,keypoint1))
            
        OUTCOND=j.findall('OUTCOND')
        va.append(OUTCOND1(OUTCOND,keypoint1))
            
        ON=j.findall('ON')
        va.append(ON1(ON,keypoint1))
            
        SHOUT=j.findall('SHOUT')
        va.append(SHOUT1(SHOUT,keypoint1))
        if va not in vaa:
            vaa1.append(va)


            
data=vaa2
import pandas as pd
df1 = pd.DataFrame(columns=vaa2[0], data=data[1:])
df2 = pd.DataFrame(columns=vaa3[0], data=vaa3[1:])
df1['RBC']=["\n".join(i) for i in df1['RBC']]
df1['INCOND']=["\n".join(i) for i in df1['INCOND']]
df1['OUTCOND']=["\n".join(i) for i in df1['OUTCOND']]
df1['ON']=["\n".join(i) for i in df1['ON']]
df1['NOTFY_BEFOR(0)/AFTER(1)']=["\n".join(i) for i in df1['NOTFY_BEFOR(0)/AFTER(1)']]
df2['INCOND']=["\n".join(i) for i in df2['INCOND']]
df2['OUTCOND']=["\n".join(i) for i in df2['OUTCOND']]
df2['ON']=["\n".join(i) for i in df2['ON']]
df2['NOTFY_BEFOR(0)/AFTER']=["\n".join(i) for i in df2['NOTFY_BEFOR(0)/AFTER']]
with pd.ExcelWriter(output) as writer:
    df1.to_excel(writer, sheet_name='FOLDER',index=False)
    df2.to_excel(writer, sheet_name='JOB',index=False)
print("success")  

