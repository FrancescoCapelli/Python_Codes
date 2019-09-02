# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:26:22 2019

@author: capellf
"""

#import pandas as pd

class CoveredRatio:

    def __init__(self, temtab_nobu, grouped_dates):
        
            self.Dates = grouped_dates['Dates'].values
            self.Maturity_1Month = temtab_nobu['Maturity_1Month'].values
            self.Maturity_3Month = temtab_nobu['Maturity_3Month'].values
            self.Maturity_6Month = temtab_nobu['Maturity_6Month'].values    

class SeatDataHolder_SONIA:

    def __init__(self, seat_data, grouped_dates):
        
        self.Dates = grouped_dates['Dates'].values
        self.Auction_Id = seat_data['Auction_Id'].values
        self.Auction_Date = seat_data['Auction_Date'].values
        self.Yield = seat_data['Yield'].values
        self.Amount = seat_data['Amount'].values
        self.Auction_Type_Code = seat_data['Auction_Type_Code'].values
        self.MaturityDate = seat_data['MaturityDate'].values
        self.Instrument_Tenor = seat_data['Instrument_Tenor'].values
        self.Allocated = seat_data['Allocated'].values
        self.Counterparty_Code = seat_data['Counterparty_Code'].values
        self.Bid_Client_Code = seat_data['Bid_Client_Code'].values
        self.Bid_Client_Name = seat_data['Bid_Client_Name'].values
        self.Stock_amount = seat_data['Stock_amount'].values
        self.Cover_Ratio = seat_data['Cover_Ratio'].values
        self.Average_Yield_Accepted = seat_data['Average_Yield_Accepted'].values
        self.Auction_DateNumKey = seat_data['Auction_DateNumKey'].values
        self.MaturityBucket = seat_data['MaturityBucket'].values
        self.Sonia = seat_data['Sonia'].values
        self.Spread_Bid = seat_data['Spread_Bid'].values
        self.Bid_Scaled = seat_data['Bid_Scaled'].values
        self.Spread_Average_Bid_Accepted = seat_data['Spread_Average_Bid_Accepted'].values
        
        
class SeatDataHolder_DBV:

    def __init__(self, seat_data, grouped_dates):
        
        self.Dates = grouped_dates['Dates'].values
        self.Auction_Id = seat_data['Auction_Id'].values
        self.Auction_Date = seat_data['Auction_Date'].values
        self.Yield = seat_data['Yield'].values
        self.Amount = seat_data['Amount'].values
        self.Auction_Type_Code = seat_data['Auction_Type_Code'].values
        self.MaturityDate = seat_data['MaturityDate'].values
        self.Instrument_Tenor = seat_data['Instrument_Tenor'].values
        self.Allocated = seat_data['Allocated'].values
        self.Counterparty_Code = seat_data['Counterparty_Code'].values
        self.Bid_Client_Code = seat_data['Bid_Client_Code'].values
        self.Bid_Client_Name = seat_data['Bid_Client_Name'].values
        self.Stock_amount = seat_data['Stock_amount'].values
        self.Cover_Ratio = seat_data['Cover_Ratio'].values
        self.Average_Yield_Accepted = seat_data['Average_Yield_Accepted'].values
        self.Auction_DateNumKey = seat_data['Auction_DateNumKey'].values
        self.MaturityBucket = seat_data['MaturityBucket'].values
        self.DBV = seat_data['DBV'].values
        self.Spread_Bid = seat_data['Spread_Bid'].values
        self.Bid_Scaled = seat_data['Bid_Scaled'].values
        self.Spread_Average_Bid_Accepted = seat_data['Spread_Average_Bid_Accepted'].values
        
        
class BidAmountAggregated:

    def __init__(self, tem_tab, grouped_dates):
        
            self.Dates = grouped_dates['Dates'].values
            self.b1_1Month = tem_tab['b1_1Month'].values
            self.b2_1Month = tem_tab['b2_1Month'].values
            self.b3_1Month = tem_tab['b3_1Month'].values
            self.b4_1Month = tem_tab['b4_1Month'].values
            self.b5_1Month = tem_tab['b5_1Month'].values
            self.b1_3Month = tem_tab['b1_3Month'].values
            self.b2_3Month = tem_tab['b2_3Month'].values
            self.b3_3Month = tem_tab['b3_3Month'].values
            self.b4_3Month = tem_tab['b4_3Month'].values
            self.b5_3Month = tem_tab['b5_3Month'].values
            self.b1_6Month = tem_tab['b1_6Month'].values
            self.b2_6Month = tem_tab['b2_6Month'].values
            self.b3_6Month = tem_tab['b3_6Month'].values
            self.b4_6Month = tem_tab['b4_6Month'].values
            self.b5_6Month = tem_tab['b5_6Month'].values
            