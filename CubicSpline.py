# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 15:47:58 2018

@author: sartirr
"""

import pandas as pd
import numpy as np 
#import math as m

#from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import (
    AbstractHolidayCalendar, DateOffset, EasterMonday,
    GoodFriday, Holiday, MO,
    next_monday, next_monday_or_tuesday)
class EnglandAndWalesHolidayCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Years Day', month=1, day=1, observance=next_monday),
        GoodFriday,
        EasterMonday,
        Holiday('Early May bank holiday',
                month=5, day=1, offset=DateOffset(weekday=MO(1))),
        Holiday('Spring bank holiday',
                month=5, day=31, offset=DateOffset(weekday=MO(-1))),
        Holiday('Summer bank holiday',
                month=8, day=31, offset=DateOffset(weekday=MO(-1))),
        Holiday('Christmas Day', month=12, day=25, observance=next_monday),
        Holiday('Boxing Day',
                month=12, day=26, observance=next_monday_or_tuesday)
    ]
    
    
from pandas.tseries.offsets import CDay
business = CDay(calendar=EnglandAndWalesHolidayCalendar())



def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def getCubicSplineParameters(data):
    #TDM=pd.read_excel(r"C:\Users\sartirr\Desktop\CubicSpline1.xlsx",sheet_name='BootStrap',header=None)
    A=data.values
    W=[]
    W.append(A[0,:])
    for i in range(len(A)-1):
        factor=A[i,:][2]/A[i+1,:][1]
        newRow=factor*A[i+1,:]
        AA=A[i,:]
        B=np.array([AA[0],AA[2],AA[3]])
        B=np.append(B,0)
        finalRow=B-newRow
        W.append(finalRow)
        A[i+1,:]=finalRow
    W1=np.vstack(W)
    W2=W1[:,1:]
    H=np.eye(len(W2))
    a=np.zeros(len(W2))
    a=a.reshape(len(W2),1)
    H=np.hstack((H, a))
    H=np.hstack((H, a))
    for i in range(len(W2)):
        H[i][i:i+3]=W2[i]
        
    systemOfEquation=H[:,1:-1]
    X=np.linalg.solve(systemOfEquation,W1[:,0])
    
    return X




def getSplineValue(evaluationDate,tableOfParameters):
    #lowerBound=tableOfParameters['Periods'][0]
    #UpperBound=tableOfParameters['Periods'][1]
    
    #evaluationDate=pd.to_datetime('17/11/2018',format='%d/%m/%Y')
    
    if (tableOfParameters['Periods']==evaluationDate).any():
        polynomial=tableOfParameters[tableOfParameters['Periods']==evaluationDate]['d']
    else:
        diffDates=tableOfParameters['Periods']-evaluationDate
        diffDates=diffDates.dt.total_seconds()/ (24 * 60 * 60)
        index=np.where(diffDates<0)[0][-1]
        
        evaluationPoint=evaluationDate-tableOfParameters['Periods'][index]
        evaluationPoint=evaluationPoint.total_seconds()/ (24 * 60 * 60)
        
        setOfParameters=tableOfParameters[tableOfParameters['Periods']==tableOfParameters['Periods'][index]][['a','b','c','d']]
        polynomial=evaluationPoint**3*setOfParameters['a']+evaluationPoint**2*setOfParameters['b']+evaluationPoint*setOfParameters['c']+setOfParameters['d']
        
    return polynomial



def getTablesOfParameters(data):
    #data=pd.read_excel(r"C:\Users\sartirr\Desktop\swapcurve (Autosaved).xlsx",sheet_name='Sheet2')
    Dates=data['date']
    DatesDiff=Dates.diff()
    data['X']=DatesDiff
    
    
    dataForSpline=pd.DataFrame()
    
    A=data['X'][1:-1].dt.total_seconds()/ (24 * 60 * 60)
    reIndex=A.reset_index()
    dataForSpline['X_0']=reIndex['X']
    B=data['X'][2:].dt.total_seconds()/ (24 * 60 * 60)
    C=B.reset_index()
    dataForSpline['X_1']=   C['X']
    dataForSpline['2(X_0 + X_1)']=2*(dataForSpline['X_0']+dataForSpline['X_1'])
    A=list(data['rate'].diff()[1:])
    A=[-3*(A[i]/dataForSpline['X_0'][i]-A[i+1]/dataForSpline['X_1'][i]) for i in range(len(dataForSpline))]
    dataForSpline['d']=A
    
    dataForSpline=dataForSpline[['d','X_0','2(X_0 + X_1)','X_1']]
    X=getCubicSplineParameters(dataForSpline)
    X=np.insert(X,0,0)
    X=np.append(X,0)
    tableOfParameters=pd.DataFrame()
    tableOfParameters['Periods']=data['date']
    
    tableOfParameters['b']=X
    
    A=list(data['X'][1:].dt.total_seconds()/ (24 * 60 * 60))
    a=[(tableOfParameters['b'][i+1]-tableOfParameters['b'][i])/(3*A[i]) for i in range(len(A))]
    a.append(0)
    tableOfParameters['a']=a
    
    c=[-A[i]*(tableOfParameters['b'][i+1]+2*tableOfParameters['b'][i])/3+(data['rate'][i+1]-data['rate'][i])/A[i] for i in range(len(A))]
    c.append(0)
    tableOfParameters['c']=c
    
    tableOfParameters['d']=data['rate']
    tableOfParameters=tableOfParameters[['Periods','a','b','c','d']]
    
    return tableOfParameters
