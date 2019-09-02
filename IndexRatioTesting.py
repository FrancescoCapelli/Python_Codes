# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 14:05:45 2019

@author: sartirr
"""

import pandas as pd
import cx_Oracle


bondlist=pd.read_excel(r"C:\Users\sartirr\Desktop\bondlist.xlsx",sheet_name='Sheet2')    
instrument_code_list= list(bondlist['INST_CODE'])


DPS_Collector=[]
for i in range(len(instrument_code_list)):
    sqlCmd = '''select settlementdate,il_uplift 
    from allcobdata_view 
    where inst_code = &instCode 
    order by settlementdate asc'''
    
    strConnection = cx_Oracle.connect('mis', 'mis', 'DPS_LIVE')
    result = pd.read_sql_query(sqlCmd, strConnection,params={'instCode': instrument_code_list[i]})
    strConnection.close()
    
    DPS_Collector.append(result)


IR=pd.read_csv(r"C:\Users\sartirr\Desktop\NewIR1.txt", header=None)
inst_code=[IR.iloc[i,0].split(" ")[0] for i in range(len(IR))]
date=[IR.iloc[i,0].split(" ")[-1] for i in range(len(IR))]
IR['bond']=inst_code
IR['date']=date
data=pd.to_datetime([IR['date'][i][0:6] for i in range(len(IR))] ,format='%m%d%y')   
il_uplift=[float(IR['date'][i][8:]) for i in range(len(IR))]
IR['Dates']=data
IR['IL_UP']=il_uplift
bond_uni = list(dict.fromkeys(inst_code))
df=IR[['bond','Dates','IL_UP']]

dataFrameCollector=[]
for i in range(len(bond_uni)):
    IR17=df[df['bond']==bond_uni[i]]
    dataFrameCollector.append(IR17)


finalResultShort=[]
for i in range(len(dataFrameCollector)):
    C=DPS_Collector[i].merge(dataFrameCollector[i], left_on='SETTLEMENTDATE', right_on='Dates', how ='inner')
    difference=sum(C['IL_UPLIFT']-C['IL_UP'])
    finalResultShort.append(difference)








bondlist=pd.read_excel(r"C:\Users\sartirr\Desktop\bondlist.xlsx",sheet_name='Sheet3')    
instrument_code_list= list(bondlist['INST_CODE'])


DPS_Collector=[]
for i in range(len(instrument_code_list)):
    sqlCmd = '''select settlementdate,il_uplift 
    from allcobdata_view 
    where inst_code = &instCode 
    order by settlementdate asc'''
    
    strConnection = cx_Oracle.connect('mis', 'mis', 'DPS_LIVE')
    result = pd.read_sql_query(sqlCmd, strConnection,params={'instCode': instrument_code_list[i]})
    strConnection.close()
    
    DPS_Collector.append(result)





IR=pd.read_csv(r"C:\Users\sartirr\Desktop\NewIR2.txt", header=None)
inst_code=[IR.iloc[i,0].split(" ")[0] for i in range(len(IR))]
date=[IR.iloc[i,0].split(" ")[-1] for i in range(len(IR))]
IR['bond']=inst_code
IR['date']=date
data=pd.to_datetime([IR['date'][i][0:6] for i in range(len(IR))] ,format='%m%d%y')   
il_uplift=[float(IR['date'][i][8:]) for i in range(len(IR))]
IR['Dates']=data
IR['IL_UP']=il_uplift
bond_uni = list(dict.fromkeys(inst_code))
df=IR[['bond','Dates','IL_UP']]


dataFrameCollector=[]
for i in range(len(bond_uni)):
    IR17=df[df['bond']==bond_uni[i]]
    dataFrameCollector.append(IR17)


finalResultLong=[]
for i in range(len(dataFrameCollector)):
    C=DPS_Collector[i].merge(dataFrameCollector[i], left_on='SETTLEMENTDATE', right_on='Dates', how ='inner')
    difference=sum(C['IL_UPLIFT']-C['IL_UP'])
    finalResultLong.append(difference)
