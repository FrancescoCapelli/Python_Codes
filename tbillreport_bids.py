# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 10:45:21 2018

@author: capellf
"""
def getDataframeBids(dataframe_agg,dataframe_scl,dataframe_sto,dataframe_1m,dataframe_3m,dataframe_6m,dataframe_tbillstock):

    old_lendataframe_1m=len(dataframe_1m)
    lastdate_oldreport = dataframe_1m.loc[len(dataframe_1m)-1,'GroupDates']
    lastDate_resultseat = dataframe_agg.loc[len(dataframe_agg)-1,'GroupDates']
    
    
    #adding dates to dataframe_1m,3m,6m
    for ii in range (len (dataframe_agg)):
        if (lastdate_oldreport<lastDate_resultseat) and (dataframe_agg.loc[ii,'GroupDates']> lastdate_oldreport):
            dataframe_1m.loc[len(dataframe_1m),'GroupDates']= (dataframe_agg.loc[ii,'GroupDates'])#> lastdate_oldreport)
            dataframe_3m.loc[len(dataframe_3m),'GroupDates']= (dataframe_agg.loc[ii,'GroupDates'])
            dataframe_6m.loc[len(dataframe_6m),'GroupDates']= (dataframe_agg.loc[ii,'GroupDates'])

    diff_leng = len(dataframe_1m) - old_lendataframe_1m
    
    #populating dataframe_1m,dataframe_3m and dataframe_6m with the following columns: BID AMOUNT AGGREGATED xM,SCALED BID AMOUNT AGGREGATED xM, xM Tender size ml = 'StockAmount
    for rr in range(diff_leng):
             #BID AMOUNT AGGREGATED 1M
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b1_1Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b1_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b2_1Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b2_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b3_1Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b3_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b4_1Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b4_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b5_1Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b5_1Month']
             #SCALED BID AMOUNT AGGREGATED 1M
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b1_1Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b1_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b2_1Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b2_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b3_1Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b3_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b4_1Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b4_1Month']
             dataframe_1m.loc[old_lendataframe_1m + rr ,'b5_1Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b5_1Month']
             #1M Tender size ml = 'StockAmount'
             dataframe_1m.loc[old_lendataframe_1m + rr ,'1M Tender size ml = StockAmount'] = dataframe_sto.loc[len(dataframe_sto)- diff_leng + rr,'Maturity_1Month']
            
             #BID AMOUNT AGGREGATED 3M
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b1_3Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b1_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b2_3Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b2_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b3_3Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b3_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b4_3Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b4_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b5_3Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b5_3Month']
             #SCALED BID AMOUNT AGGREGATED 3M
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b1_3Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b1_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b2_3Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b2_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b3_3Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b3_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b4_3Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b4_3Month']
             dataframe_3m.loc[old_lendataframe_1m + rr ,'b5_3Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b5_3Month']
             #3M Tender size ml = 'StockAmount'
             dataframe_3m.loc[old_lendataframe_1m + rr ,'3M Tender size ml = StockAmount'] = dataframe_sto.loc[len(dataframe_sto)- diff_leng + rr,'Maturity_3Month']
             
    
             #BID AMOUNT AGGREGATED 6M
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b1_6Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b1_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b2_6Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b2_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b3_6Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b3_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b4_6Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b4_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b5_6Month - BidAmountAggregated'] = dataframe_agg.loc[len(dataframe_agg)- diff_leng + rr,'b5_6Month']
             #SCALED BID AMOUNT AGGREGATED 6M
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b1_6Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b1_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b2_6Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b2_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b3_6Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b3_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b4_6Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b4_6Month']
             dataframe_6m.loc[old_lendataframe_1m + rr ,'b5_6Month - ScaledBidAmountAggregated'] = dataframe_scl.loc[len(dataframe_scl)- diff_leng + rr,'b5_6Month']
             #6M Tender size ml = 'StockAmount'
             dataframe_6m.loc[old_lendataframe_1m + rr ,'6M Tender size ml = StockAmount'] = dataframe_sto.loc[len(dataframe_sto)- diff_leng + rr,'Maturity_6Month']
         
         
        
    #populating dataframe_1m,dataframe_3m and dataframe_6m with the following columns:x-m Tbill Stock and STOCK OVERALL          
    for zz in range (len(dataframe_tbillstock)):
             for xx in range (len(dataframe_1m)):
                if dataframe_tbillstock.loc[zz,'COB_DATE'] == dataframe_1m.loc[xx,'GroupDates']:
                   dataframe_1m.loc[xx,'1-m Tbill Stock'] = dataframe_tbillstock.loc[zz,'TBILL_1m']
                   dataframe_3m.loc[xx,'3-m Tbill Stock'] = dataframe_tbillstock.loc[zz,'TBILL_3m']
                   dataframe_6m.loc[xx,'6-m Tbill Stock'] = dataframe_tbillstock.loc[zz,'TBILL_6m']
                   
    for pp in range (len(dataframe_1m)):
                dataframe_1m.loc[pp, 'Stock overall']= dataframe_1m.loc[pp, '1-m Tbill Stock']+ dataframe_3m.loc[pp, '3-m Tbill Stock'] + dataframe_6m.loc[pp, '6-m Tbill Stock']
                dataframe_3m.loc[pp, 'Stock overall']= dataframe_1m.loc[pp, '1-m Tbill Stock']+ dataframe_3m.loc[pp, '3-m Tbill Stock'] + dataframe_6m.loc[pp, '6-m Tbill Stock']
                dataframe_6m.loc[pp, 'Stock overall']= dataframe_1m.loc[pp, '1-m Tbill Stock']+ dataframe_3m.loc[pp, '3-m Tbill Stock'] + dataframe_6m.loc[pp, '6-m Tbill Stock']

    return dataframe_1m,dataframe_3m,dataframe_6m

#table1M, table3M, table6M = getDataframeBids(dataframe_agg,dataframe_scl,dataframe_sto,dataframe_1m,dataframe_3m,dataframe_6m)
         
         
         
         
      