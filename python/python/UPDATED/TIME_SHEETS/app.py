import pandas as pd
import os,sys
from xlsxwriter import Workbook
pd.options.mode.chained_assignment = None
excel_file=sys.argv[1]
Resource_Under_Raghav=pd.read_excel(excel_file,sheet_name=0)
data=pd.read_excel(excel_file,sheet_name=1)
df1_grouped = data.groupby(data.columns[0])
writer = pd.ExcelWriter('Timecard_Analysis_output.xlsx', engine='xlsxwriter')
for group_name, df_group in df1_grouped:
    #Resource_Under_Raghav[group_name]=
    df_group=df_group.iloc[:,[1,2]]
    df_group=df_group.rename(columns={df_group.columns[0]:Resource_Under_Raghav.columns[0]})
    data1=pd.merge(Resource_Under_Raghav,df_group, on=Resource_Under_Raghav.columns[0], how="left").fillna("Not_Filled")
    #print(str(group_name).split(" ")[0],type(str(group_name).split(" ")[0]))
    data1.to_excel(writer,sheet_name=str(group_name).split(" ")[0],index=False)
writer.close()