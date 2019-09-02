# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 16:17:20 2019

@author: capellf
"""
import pandas as pd
import numpy as np
import pyodbc #microsoft SQL
import copy
from collections import Counter #to count the repetitions of dates
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tbillreport_billstock import getSQLquery,generateTbillstock
from tbillreport_bids import getDataframeBids
import win32com.client as win32 #to write on existing excel worksheets without changing format
from timeit import default_timer as timer
from data_processing_classes import SeatDataHolder_DBV, BidAmountAggregated, CoveredRatio



start = timer()


#read query fromVDBSQL01
str_connection = pyodbc.connect('DSN=DBV; UID=mis;PWD=mis')
SQL1 = "SELECT Histo.datestock, Value.ric, Histo.c1 FROM DSM.dbo.Histo Histo, DSM.dbo.Value Value WHERE Histo.id = Value.id AND Histo.datestock>='14-Feb-2013' AND Value.ric IN ('SYNREPORATE1M=DMO', 'SYNREPORATE3M=DMO', 'SYNREPORATE6M=DMO') ORDER BY Histo.datestock asc"
query1   = pd.read_sql_query(SQL1, str_connection)
str_connection.close()

#put in order the query
DBVrates= Counter(query1['datestock'])
DBVrates = pd.DataFrame.from_dict(DBVrates, orient='index').reset_index()
DBVrates.columns = ['DBV_Date','30']
DBVrates['30'] = np.nan
DBVrates['90'] = np.nan
DBVrates['181'] = np.nan
DBVrates.columns = ['DBV_Date','30', '90', '181']

for i in range(len(DBVrates)):
    DBVrates['30'][i] = query1['c1'][(query1['datestock'] == DBVrates['DBV_Date'][i]) & (query1['ric'] == 'SYNREPORATE1M=DMO')]
    DBVrates['90'][i] = query1['c1'][(query1['datestock'] == DBVrates['DBV_Date'][i]) & (query1['ric'] == 'SYNREPORATE3M=DMO')]
    DBVrates['181'][i] = query1['c1'][(query1['datestock'] == DBVrates['DBV_Date'][i]) & (query1['ric'] == 'SYNREPORATE6M=DMO')]

#connection to seat production
str_connection = pyodbc.connect('DSN=SEAT_LIVE; UID=mis;PWD=mis')
sql = "SELECT TAS_WF_CPTY_MarketOperationResults.Auction_Id,	TAS_WF_CPTY_MarketOperationResults.Auction_Date, TAS_WF_CPTY_MarketOperationResults.Yield,	TAS_WF_CPTY_MarketOperationResults.Amount,	TAS_WF_CPTY_MarketOperationResults.Auction_Type_Code,	TAS_WF_CPTY_MarketOperationResults.MaturityDate,	TAS_WF_CPTY_MarketOperationResults.Instrument_Tenor,	TAS_WF_CPTY_MarketOperationResults.Allocated,	TAS_WF_CPTY_MarketOperationResults.Counterparty_Code,	TAS_WF_CPTY_MarketOperationResults.Bid_Client_Code,	TAS_WF_CPTY_MarketOperationResults.Bid_Client_Name,	TAS_WF_CPTY_MarketOperationResults.Stock_amount,	TAS_WF_CPTY_MarketOperationResults.Cover_Ratio,	TAS_WF_CPTY_MarketOperationResults.Average_Yield_Accepted FROM 	SeatProd.dbo.TAS_WF_CPTY_MarketOperationResults WHERE TAS_WF_CPTY_MarketOperationResults.Auction_Type_Code = 'TBD'"
seatData   = pd.read_sql_query(sql, str_connection)
str_connection.close()

soniaBuckets = np.array([[-1000,-0.05],[-0.05,0],[0,0.1],[0.1,0.2],[0.2,1000]])

#Matching dates, bucketing and calculating spreads
seatData['Auction_DateNumKey']=seatData['Auction_Date']

#remove hours, minutes and seconds from dates

date_DBV_str= np.empty(0, dtype=str)
date_DBV_date = np.empty(0, dtype=str)

for index, row in DBVrates.iterrows():
    date_DBV_str = np.append(date_DBV_str, row['DBV_Date'].strftime('%d-%b-%Y'))

DBVrates['DBV_Date'] = date_DBV_str    

for index, row in DBVrates.iterrows():

    date_DBV_date = np.append(date_DBV_date,datetime.strptime(row['DBV_Date'], '%d-%b-%Y'))

DBVrates['Auction_DateNumKey'] = date_DBV_date

#DBVrates['DBV_Date']=[DBVrates['DBV_Date'][i].strftime('%d-%b-%Y') for i in range(len(DBVrates))]
#
#DBVrates['Auction_DateNumKey'] = [datetime.strptime(DBVrates['DBV_Date'][i], '%d-%b-%Y') for i in range(len(DBVrates))]

DBVrates_noduplicates = DBVrates.drop_duplicates(subset=['Auction_DateNumKey'], keep=False)
DBVrates = copy.deepcopy(DBVrates_noduplicates)


seatData = seatData.sort_values(by = ['Auction_DateNumKey'])
seatData = seatData.reset_index(drop = True)
DBVrates = DBVrates.sort_values(by = ['Auction_DateNumKey'])
DBVrates = DBVrates.reset_index(drop = True)
DBVrates.columns = ['DBV_date','x30','x90','x181','Auction_DateNumKey']

seatD = copy.deepcopy(seatData)
seatD['MaturityBucket'] = np.nan
seatD['DBV'] = np.nan

for i in seatD.index:
    if seatD.loc[i,'Instrument_Tenor']<=31:
        seatD.set_value(i,'MaturityBucket',1)
        
    elif seatD.loc[i,'Instrument_Tenor']>31 and seatD.loc[i,'Instrument_Tenor']<= 100:
        seatD.set_value(i,'MaturityBucket',2)  
       
    elif seatD.loc[i,'Instrument_Tenor']>100:
        seatD.set_value(i,'MaturityBucket',3) 


#drop duplicates and keep only the first one for each day             
seatDates=seatD['Auction_DateNumKey'].drop_duplicates().reset_index(drop = True)
startdate=seatDates[seatDates == DBVrates['Auction_DateNumKey'][1]].index[0]

#add DBV rates where the date in DBV matches the date in seat. if in DBV the date is missing, we take the previous date of DBV
seatDates=seatDates[startdate:].reset_index(drop = True)

W=[]
for i in range(len(seatDates)):
    A=pd.DataFrame()
    date = seatDates[i]
    dateFixed = seatDates[i]
    while A.empty == True:
        A=DBVrates[DBVrates['Auction_DateNumKey'] == date]
        if A.empty:
            date=date-relativedelta(days=+1)
            A=DBVrates[DBVrates['Auction_DateNumKey'] == date]
    
    
    A['Auction_DateNumKey'] = dateFixed
    W.append(A)

WW=pd.concat((W))
C=pd.merge(seatD, WW, on='Auction_DateNumKey', how='left')

seatD = copy.deepcopy(C)

del seatD['DBV_date']

seatD['DBV'] = seatD['x30'][(seatD['MaturityBucket'] == 1)]
seatD['DBV'][(seatD['MaturityBucket'] == 2)]= seatD['x90'][(seatD['MaturityBucket'] == 2)]
seatD['DBV'][(seatD['MaturityBucket'] == 3)] = seatD['x181'][(seatD['MaturityBucket'] == 3)]

del seatD['x30']
del seatD['x90']
del seatD['x181']

seatD['Stock_amount'] = seatD['Stock_amount']/np.power(10,6)
seatD['Spread_Bid'] = seatD['Yield'] - seatD['DBV']
seatD['Bid_Scaled'] = seatD['Amount']/seatD['Stock_amount']
seatD['Spread_Average_Bid_Accepted'] = seatD['Average_Yield_Accepted'] - seatD['DBV']

##Reporting

groupedDates= Counter(seatD['Auction_DateNumKey'])
groupedDates = pd.DataFrame.from_dict(groupedDates, orient='index').reset_index()
groupedDates.columns = ['Dates','Observations']
#groupedDates['Dates']=[groupedDates['Dates'][i].strftime('%d-%b-%Y') for i in range(len(groupedDates))]

temTab = []
temTabNoBu= [] 
initValues = []
tMonths=['_1Month','_3Month','_6Month']

dict_data1 = {}
dict_data2 = {}
data_ = np.zeros(len(groupedDates))
data1_ = list(data_)
data2_ = list(data_)
for i in range(len(tMonths)):
    for j in range(1,len(soniaBuckets)+1):
        temTab = "{0}{1}{2}".format('b', j , tMonths[i])
        dict_data1[temTab] = data1_
        df1 = pd.DataFrame(dict_data1)
        #print (temTab) 
    temTabNoBu = "{0}{1}".format('Maturity', tMonths[i])
    dict_data2[temTabNoBu] = data2_
    df2 = pd.DataFrame(dict_data2)
    
temTab = df1
temTabNoBu = df2

#populate the classes
tabCoveredRatio = CoveredRatio(temTabNoBu, groupedDates)
tabBidAmountAggregated_class = BidAmountAggregated(temTab, groupedDates)
tabScaledBidAmountAggregated_class = copy.deepcopy(tabBidAmountAggregated_class)

tabSpreadAAP = copy.deepcopy(tabCoveredRatio)
tabStockAmount_class = copy.deepcopy(tabCoveredRatio)
sdata = SeatDataHolder_DBV(seatD, groupedDates)

end1 = timer()
print(" time took to run before the big loop", (end1 - start)/60) 

#generating numpy arrays before triple loop to reduce time consumption
Auction_DateNumKey= np.empty(len(seatD), dtype=str)
Spread_Bid = np.empty(len(seatD), dtype=str)
MaturityBucket = np.empty(len(seatD), dtype=str)

Auction_DateNumKey = sdata.Auction_DateNumKey
Spread_Bid = seatD['Spread_Bid']
MaturityBucket = seatD['MaturityBucket']
dates = groupedDates['Dates'].values


end1 = timer()
print(" time took to run before the big loop", (end1 - start)/60) 

for i, _date in enumerate(dates):
    for k in range(1, 4):
        for j in range(0, len(soniaBuckets)):
            ind = np.where(
                (sdata.Auction_DateNumKey == _date) & (sdata.Spread_Bid > soniaBuckets[j, 0]) & (
                            sdata.Spread_Bid <= soniaBuckets[j, 1]) & (sdata.MaturityBucket == k))[0]
            tabScaledBidAmountAggregated_class.__dict__['b'+str(j + 1)+tMonths[k - 1]][i] = sum(sdata.Bid_Scaled[ind])
            tabBidAmountAggregated_class.__dict__['b' + str(j + 1) + tMonths[k - 1]][i] = sum(sdata.Amount[ind])

        index = np.where((sdata.Auction_DateNumKey == _date) & (sdata.MaturityBucket == k))[0] #[0] because it's a tuple
        if len(index) > 0:
            tabCoveredRatio.__dict__['Maturity' + tMonths[k-1]][i] = sdata.Cover_Ratio[index][-1]
            tabSpreadAAP.__dict__['Maturity' + tMonths[k-1]][i] = sdata.Spread_Average_Bid_Accepted[index][-1]
            tabStockAmount_class.__dict__['Maturity' + tMonths[k-1]][i] = sdata.Stock_amount[index][-1]

end2 = timer()
print(" time took to run the big loop", (end2 - end1)/60)


#recomposing dataframes from classes

#recomposing tabBidAmountAggregated
tabBidAmountAggregated = []
tabBidAmountAggregated = pd.DataFrame()
tabBidAmountAggregated['GroupDates'] = tabBidAmountAggregated_class.Dates
tabBidAmountAggregated['b1_1Month'] = tabBidAmountAggregated_class.b1_1Month
tabBidAmountAggregated['b2_1Month'] = tabBidAmountAggregated_class.b2_1Month
tabBidAmountAggregated['b3_1Month'] = tabBidAmountAggregated_class.b3_1Month
tabBidAmountAggregated['b4_1Month'] = tabBidAmountAggregated_class.b4_1Month
tabBidAmountAggregated['b5_1Month'] = tabBidAmountAggregated_class.b5_1Month
tabBidAmountAggregated['b1_3Month'] = tabBidAmountAggregated_class.b1_3Month
tabBidAmountAggregated['b2_3Month'] = tabBidAmountAggregated_class.b2_3Month
tabBidAmountAggregated['b3_3Month'] = tabBidAmountAggregated_class.b3_3Month
tabBidAmountAggregated['b4_3Month'] = tabBidAmountAggregated_class.b4_3Month
tabBidAmountAggregated['b5_3Month'] = tabBidAmountAggregated_class.b5_3Month
tabBidAmountAggregated['b1_6Month'] = tabBidAmountAggregated_class.b1_6Month
tabBidAmountAggregated['b2_6Month'] = tabBidAmountAggregated_class.b2_6Month
tabBidAmountAggregated['b3_6Month'] = tabBidAmountAggregated_class.b3_6Month
tabBidAmountAggregated['b4_6Month'] = tabBidAmountAggregated_class.b4_6Month
tabBidAmountAggregated['b5_6Month'] = tabBidAmountAggregated_class.b5_6Month
          
#recomposing tabScaledBidAmountAggregated
tabScaledBidAmountAggregated = []
tabScaledBidAmountAggregated = pd.DataFrame()
tabScaledBidAmountAggregated['GroupDates'] = tabScaledBidAmountAggregated_class.Dates
tabScaledBidAmountAggregated['b1_1Month'] = tabScaledBidAmountAggregated_class.b1_1Month
tabScaledBidAmountAggregated['b2_1Month'] = tabScaledBidAmountAggregated_class.b2_1Month
tabScaledBidAmountAggregated['b3_1Month'] = tabScaledBidAmountAggregated_class.b3_1Month
tabScaledBidAmountAggregated['b4_1Month'] = tabScaledBidAmountAggregated_class.b4_1Month
tabScaledBidAmountAggregated['b5_1Month'] = tabScaledBidAmountAggregated_class.b5_1Month
tabScaledBidAmountAggregated['b1_3Month'] = tabScaledBidAmountAggregated_class.b1_3Month
tabScaledBidAmountAggregated['b2_3Month'] = tabScaledBidAmountAggregated_class.b2_3Month
tabScaledBidAmountAggregated['b3_3Month'] = tabScaledBidAmountAggregated_class.b3_3Month
tabScaledBidAmountAggregated['b4_3Month'] = tabScaledBidAmountAggregated_class.b4_3Month
tabScaledBidAmountAggregated['b5_3Month'] = tabScaledBidAmountAggregated_class.b5_3Month
tabScaledBidAmountAggregated['b1_6Month'] = tabScaledBidAmountAggregated_class.b1_6Month
tabScaledBidAmountAggregated['b2_6Month'] = tabScaledBidAmountAggregated_class.b2_6Month
tabScaledBidAmountAggregated['b3_6Month'] = tabScaledBidAmountAggregated_class.b3_6Month
tabScaledBidAmountAggregated['b4_6Month'] = tabScaledBidAmountAggregated_class.b4_6Month
tabScaledBidAmountAggregated['b5_6Month'] = tabScaledBidAmountAggregated_class.b5_6Month
            
#recomposing tabStockAmount

tabStockAmount = []
tabStockAmount = pd.DataFrame()
tabStockAmount['GroupDates'] = tabStockAmount_class.Dates
tabStockAmount['Maturity_1Month'] = tabStockAmount_class.Maturity_1Month
tabStockAmount['Maturity_3Month'] = tabStockAmount_class.Maturity_3Month
tabStockAmount['Maturity_6Month'] = tabStockAmount_class.Maturity_6Month

#update date and provide credentials for DPS oracle access
date            = (datetime.today() - timedelta(days = 1)).strftime('%d-%b-%Y')
queryParameters = {'cobDate': date}
databaseDetails = ['mis', 'mis', 'DPS_LIVE']

#functions to generate tbill_stock
query1, query2 = getSQLquery(queryParameters,databaseDetails)
dataframe_tbillstock=generateTbillstock(query1, query2)

#READING BASE FILE FOR T-BILL TRAFFICLIGHT CHARTS
filepath2 =r'I:\ERQA\Analytical Tasks\TBill_Report\Reports\TBill Bidding Report_20181005_pythoninput_forDBV.xlsx'
dataframe_1m = pd.read_excel(filepath2, 'Data for Chart - 1m', skiprows= [0,1,3])
dataframe_3m = pd.read_excel(filepath2, 'Data for chart - 3m', skiprows=[0,1,3])
dataframe_6m = pd.read_excel(filepath2, 'Data for chart - 6m', skiprows=[0,1,3])
del dataframe_1m['Unnamed: 0']
del dataframe_3m['Unnamed: 0']  
del dataframe_6m['Unnamed: 0']

#functions to generate all tables
table1M, table3M, table6M = getDataframeBids(tabBidAmountAggregated,tabScaledBidAmountAggregated,tabStockAmount,dataframe_1m,dataframe_3m,dataframe_6m,dataframe_tbillstock)

#WRITING ON EXCEL WORKSHEETS:T-BILL TRAFFICLIGHT CHARTS
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb1 = excel.Workbooks.Open(r'I:\ERQA\Analytical Tasks\TBill_Report\Reports\TBill Bidding Report_20181005_pythoninput_forDBV.xlsx')


def createListOfLists(inputList):
    """
    pywin takes lists of lists as an input we create a list of lists here
    """
    outputList = [[ele] for ele in inputList]
    
    return outputList 

def generateExcelfile(wb1,table1M, table3M, table6M):
    ws1 = wb1.Worksheets(3)
    ws2 = wb1.Worksheets(4)
    ws3 = wb1.Worksheets(5)
    #lenghts are currently all the same but it might be that in the futures not all maturities are issued; length1,length2,length3 should be kept.
    length1 = len(table1M) + 4#first four lines are titles 
    length3 = len(table3M) + 4 
    length6 = len(table6M) + 4
    ###### TAB 1 MONTH ####################
    ws1.Range("B5:B"+str(length1)).Value = createListOfLists(table1M['GroupDates'].dt.strftime('%d/%b/%Y').tolist())
    ws1.Range("C5:C"+str(length1)).Value = createListOfLists(table1M['b1_1Month - ScaledBidAmountAggregated'].values.tolist())
    ws1.Range("D5:D"+str(length1)).Value = createListOfLists(table1M['b2_1Month - ScaledBidAmountAggregated'].values.tolist())
    ws1.Range("E5:E"+str(length1)).Value = createListOfLists(table1M['b3_1Month - ScaledBidAmountAggregated'].values.tolist())
    ws1.Range("F5:F"+str(length1)).Value = createListOfLists(table1M['b4_1Month - ScaledBidAmountAggregated'].values.tolist())
    ws1.Range("G5:G"+str(length1)).Value = createListOfLists(table1M['b5_1Month - ScaledBidAmountAggregated'].values.tolist())
    ws1.Range("H5:H"+str(length1)).Value = createListOfLists(table1M['b1_1Month - BidAmountAggregated'].values.tolist())
    ws1.Range("I5:I"+str(length1)).Value = createListOfLists(table1M['b2_1Month - BidAmountAggregated'].values.tolist())
    ws1.Range("J5:J"+str(length1)).Value = createListOfLists(table1M['b3_1Month - BidAmountAggregated'].values.tolist())
    ws1.Range("K5:K"+str(length1)).Value = createListOfLists(table1M['b4_1Month - BidAmountAggregated'].values.tolist())
    ws1.Range("L5:L"+str(length1)).Value = createListOfLists(table1M['b5_1Month - BidAmountAggregated'].values.tolist())
    ws1.Range("M5:M"+str(length1)).Value = createListOfLists(table1M['1M Tender size ml = StockAmount'].values.tolist())
    ws1.Range("N5:N"+str(length1)).Value = createListOfLists(table1M['1-m Tbill Stock'].values.tolist())
    ws1.Range("O5:O"+str(length1)).Value = createListOfLists(table1M['Stock overall'].values.tolist())
    
    ###### TAB 3 MONTHS ####################
    ws2.Range("B5:B"+str(length3)).Value = createListOfLists(table3M['GroupDates'].dt.strftime('%d/%b/%Y').tolist())
    ws2.Range("C5:C"+str(length3)).Value = createListOfLists(table3M['b1_3Month - ScaledBidAmountAggregated'].values.tolist()) 
    ws2.Range("D5:D"+str(length3)).Value = createListOfLists(table3M['b2_3Month - ScaledBidAmountAggregated'].values.tolist())
    ws2.Range("E5:E"+str(length3)).Value = createListOfLists(table3M['b3_3Month - ScaledBidAmountAggregated'].values.tolist())
    ws2.Range("F5:F"+str(length3)).Value = createListOfLists(table3M['b4_3Month - ScaledBidAmountAggregated'].values.tolist())
    ws2.Range("G5:G"+str(length3)).Value = createListOfLists(table3M['b5_3Month - ScaledBidAmountAggregated'].values.tolist())
    ws2.Range("H5:H"+str(length3)).Value = createListOfLists(table3M['b1_3Month - BidAmountAggregated'].values.tolist())
    ws2.Range("I5:I"+str(length3)).Value = createListOfLists(table3M['b2_3Month - BidAmountAggregated'].values.tolist())
    ws2.Range("J5:J"+str(length3)).Value = createListOfLists(table3M['b3_3Month - BidAmountAggregated'].values.tolist())
    ws2.Range("K5:K"+str(length3)).Value = createListOfLists(table3M['b4_3Month - BidAmountAggregated'].values.tolist())
    ws2.Range("L5:L"+str(length3)).Value = createListOfLists(table3M['b5_3Month - BidAmountAggregated'].values.tolist())
    ws2.Range("M5:M"+str(length3)).Value = createListOfLists(table3M['3M Tender size ml = StockAmount'].values.tolist())
    ws2.Range("N5:N"+str(length3)).Value = createListOfLists(table3M['3-m Tbill Stock'].values.tolist())
    ws2.Range("O5:O"+str(length3)).Value = createListOfLists(table3M['Stock overall'].values.tolist())
    
    ###### TAB 6 MONTHS ####################
    ws3.Range("B5:B"+str(length6)).Value = createListOfLists(table6M['GroupDates'].dt.strftime('%d/%b/%Y').tolist())
    ws3.Range("C5:C"+str(length6)).Value = createListOfLists(table6M['b1_6Month - ScaledBidAmountAggregated'].values.tolist())
    ws3.Range("D5:D"+str(length6)).Value = createListOfLists(table6M['b2_6Month - ScaledBidAmountAggregated'].values.tolist())
    ws3.Range("E5:E"+str(length6)).Value = createListOfLists(table6M['b3_6Month - ScaledBidAmountAggregated'].values.tolist())
    ws3.Range("F5:F"+str(length6)).Value = createListOfLists(table6M['b4_6Month - ScaledBidAmountAggregated'].values.tolist())
    ws3.Range("G5:G"+str(length6)).Value = createListOfLists(table6M['b5_6Month - ScaledBidAmountAggregated'].values.tolist())
    ws3.Range("H5:H"+str(length6)).Value = createListOfLists(table6M['b1_6Month - BidAmountAggregated'].values.tolist())
    ws3.Range("I5:I"+str(length6)).Value = createListOfLists(table6M['b2_6Month - BidAmountAggregated'].values.tolist())
    ws3.Range("J5:J"+str(length6)).Value = createListOfLists(table6M['b3_6Month - BidAmountAggregated'].values.tolist())
    ws3.Range("K5:K"+str(length6)).Value = createListOfLists(table6M['b4_6Month - BidAmountAggregated'].values.tolist())
    ws3.Range("L5:L"+str(length6)).Value = createListOfLists(table6M['b5_6Month - BidAmountAggregated'].values.tolist())
    ws3.Range("M5:M"+str(length6)).Value = createListOfLists(table6M['6M Tender size ml = StockAmount'].values.tolist())
    ws3.Range("N5:N"+str(length6)).Value = createListOfLists(table6M['6-m Tbill Stock'].values.tolist())
    ws3.Range("O5:O"+str(length6)).Value = createListOfLists(table6M['Stock overall'].values.tolist())
    
    return wb1


excel.DisplayAlerts = False
generateExcelfile(wb1,table1M, table3M, table6M).SaveAs(r'I:\ERQA\Analytical Tasks\TBill_Report\Reports\TBill Bidding Report_lastupdate_pythonoutput_DBV.xlsx')
excel.Application.Quit()

end3 = timer()
print(" time took to run after the big loop", (end3 - end2)/60)
end = timer()
print(" time took to run in total", (end - start)/60)
