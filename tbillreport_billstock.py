# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 09:56:55 2018

@author: capellf
"""
import pandas as pd
import cx_Oracle
import numpy as np

def getSQLquery(queryParameters,databaseDetails):
    strConnection = cx_Oracle.connect(databaseDetails[0], databaseDetails[1], databaseDetails[2])
    sqlQuery1 =  """
                select A.COB_DATE, A.FIRST_ISSUE_DATE, A.INST_CODE, A.AMOUNT_OUTSTANDING, A.MATURITY_DATE, A.INST_TYPE 
                from ALLCOBDATA_VIEW A
                where A.INST_TYPE='TBT' AND (A.COB_DATE>'04-Jan-2016' AND A.COB_DATE <= &cobdate )
                ORDER BY COB_DATE
                """
    sqlQuery2 = """
                select DISTINCT A.COB_DATE
                from ALLCOBDATA_VIEW A
                where A.INST_TYPE='TBT' AND (A.COB_DATE>'04-Jan-2016' AND A.COB_DATE <= &cobdate )
                ORDER BY COB_DATE
                """            
            
    queryOutput1   = pd.read_sql_query(sqlQuery1, strConnection, params = queryParameters)
    queryOutput2   = pd.read_sql_query(sqlQuery2, strConnection, params = queryParameters)
    strConnection.close()
    return queryOutput1,queryOutput2

def generateTbillstock(queryOutput1,queryOutput2):

    queryOutput1['REMAINED_MATURITY'] = queryOutput1['MATURITY_DATE']-queryOutput1['COB_DATE']
    queryOutput1['TBILL_TYPE']=np.nan
    queryOutput2['TBILL_1m']=np.nan
    queryOutput2['TBILL_3m']=np.nan
    queryOutput2['TBILL_6m']=np.nan
    queryOutput2['TBILL_9m']=np.nan

    for ii in range(len(queryOutput1)):
    
        if queryOutput1.loc[ii,'REMAINED_MATURITY'].days <=29:
           queryOutput1.loc[ii,'TBILL_TYPE'] = 1
       
        elif queryOutput1.loc[ii,'REMAINED_MATURITY'].days >=30 and queryOutput1.loc[ii,'REMAINED_MATURITY'].days<= 93:
             queryOutput1.loc[ii,'TBILL_TYPE'] = 3  
       
        elif queryOutput1.loc[ii,'REMAINED_MATURITY'].days >=94 and queryOutput1.loc[ii,'REMAINED_MATURITY'].days<= 184:
             queryOutput1.loc[ii,'TBILL_TYPE'] = 6
    
        elif queryOutput1.loc[ii,'REMAINED_MATURITY'].days >=185:
             queryOutput1.loc[ii,'TBILL_TYPE'] = 9
        
    for ii in range(len(queryOutput2)):
        selecDay = queryOutput2.loc[ii,'COB_DATE']
        rawTable = queryOutput1[queryOutput1['COB_DATE']==selecDay]
        values1M= rawTable[rawTable['TBILL_TYPE'] == 1]
        values3M= rawTable[rawTable['TBILL_TYPE'] == 3]
        values6M= rawTable[rawTable['TBILL_TYPE'] == 6]
        values9M= rawTable[rawTable['TBILL_TYPE'] == 9]  
        queryOutput2.loc[ii,'TBILL_1m']=values1M['AMOUNT_OUTSTANDING'].sum()
        queryOutput2.loc[ii,'TBILL_3m']=values3M['AMOUNT_OUTSTANDING'].sum()
        queryOutput2.loc[ii,'TBILL_6m']=values6M['AMOUNT_OUTSTANDING'].sum()
        queryOutput2.loc[ii,'TBILL_9m']=values9M['AMOUNT_OUTSTANDING'].sum()
    
    return queryOutput2

#query1, query2 = getSQLquery(queryParameters,databaseDetails)
#dataframe_tbillstock=generateTbillstock(query1, query2)


