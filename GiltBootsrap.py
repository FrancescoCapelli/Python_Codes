# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 15:46:01 2018

@author: capellf
"""

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import math as m
from CubicSpline import getTablesOfParameters,getSplineValue
import copy




def getCashFlowSchedule(Coupon,NextCouponDate,MatDate):
    NextCouponDate=pd.to_datetime(NextCouponDate,format='%d/%m/%Y')
    MatDate=pd.to_datetime(MatDate,format='%d/%m/%Y')
    setOfCoupon=[]
    setOfDates=[]
    setOfCoupon.append(Coupon)
    setOfDates.append(NextCouponDate)
    
    FutureCouponDate=NextCouponDate
    while FutureCouponDate!=MatDate:
        FutureCouponDate=FutureCouponDate+relativedelta(months=6)
        
        if FutureCouponDate==MatDate:
            setOfCoupon.append(Coupon+1)
            setOfDates.append(FutureCouponDate)
        elif FutureCouponDate<MatDate:
            setOfCoupon.append(Coupon)
            setOfDates.append(FutureCouponDate)
        else:
            break
    bond=pd.DataFrame()
    bond['Coupon']=setOfCoupon
    bond['setOfDates']=setOfDates
    
        
    return bond

def getDailySpline():
    data=pd.read_excel(r"S:\Francesco\PRICING\Copy of BootstrappingSwapCurve_francesco.xlsx",sheet_name='Sheet4')
    data['x']=pd.to_datetime(data['x'])
    tableOfParameters=getTablesOfParameters(data)
    #evaluationDate=pd.to_datetime('15/11/2018',format='%d/%m/%Y')
    #interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
    
    
    #plot the spline
    datelist = pd.date_range(start = data.loc[0,'x'], end = data.loc[len(data)-1,'x'] ).tolist()
    
    Interpolation=[]
    for i in range(len(datelist)):
        interpolatedValue=getSplineValue(datelist[i],tableOfParameters)
        Interpolation.append(interpolatedValue)
    
    A=np.vstack(Interpolation)
    
    
    data=pd.read_excel(r"S:\Francesco\PRICING\Copy of BootstrappingSwapCurve_francesco.xlsx",sheet_name='Sheet4')
    data['x']=pd.to_datetime(data['x'])
    data1=data.set_index('x')
    dailySpline=pd.DataFrame(datelist)
    dailySpline['x']=A
    dailySpline=dailySpline.set_index(0)
    ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
    ax = dailySpline.plot(legend=False,ax=ax)
    
    return dailySpline


def getCashFlowTable(Input,GiltDates,cobDate):
    giltList=[
    'CTGBP1Y Govt',
    'CTGBP2Y Govt',
    'CTGBP3Y Govt',
    'CTGBP4Y Govt',
    'CTGBP5Y Govt',
    'CTGBP6Y Govt',
    'CTGBP7Y Govt',
    'CTGBP8Y Govt',
    'CTGBP9Y Govt',
    'CTGBP10Y Govt',
    'CTGBP12Y Govt',
    'CTGBP15Y Govt',
    'CTGBP20Y Govt',
    'CTGBP25Y Govt',
    'CTGBP30Y Govt',
    'CTGBP40Y Govt',
    'CTGBP50Y Govt'
    ]
    
    #GiltDates=pd.read_excel(r"C:\Users\sartirr\Desktop\coupondates.xlsx")
    
    collectionOfDate=[]
    for i in range(len(giltList)):
    
        dates=GiltDates[giltList]
        singleSetOfDates=dates[giltList[i]].dropna()
        
        collectionOfDate.append(singleSetOfDates)
        
        
        
    collectionOfDate=pd.DataFrame(np.hstack(collectionOfDate))
    collectionOfDate=collectionOfDate.drop_duplicates()
    collectionOfDate=collectionOfDate.sort_values(by=[0])
        
    
    columns=[str(collectionOfDate.iloc[i]).split(' ')[3].split('\n')[0]for i in range(len(collectionOfDate))]
    CF=pd.DataFrame(columns =  columns)
    CF.columns = pd.to_datetime(CF.columns)
    
    #Input=pd.read_excel(r"C:\Users\sartirr\Desktop\coupondates.xlsx",sheet_name='input')
    
    
    CF.insert(0, '2018-11-16', Input['DirtyPrice'] )
    CF.insert(1, 'Maturity', pd.to_datetime((Input['MATURITY'])))   
    

    
    setOfCashFlows=[]
    for i in range(len(Input)):
        singleBond=getCashFlowSchedule(Input['years'].iloc[i],Input['NextCopon'].iloc[i],Input['MATURITY'].iloc[i])
        setOfCashFlows.append(singleBond)
           
            
        
    CF1=CF.iloc[:,2:]
    
    X=[]
    for l in range(len(CF)):
        B=CF1.iloc[l,:]
        A=setOfCashFlows[l]
        for i in range(len(A)):
            date=A['setOfDates'].iloc[i]
            Coupon=A['Coupon'].iloc[i]
            for j in range(len(B)):
                
                if B.index[j]==date:
                    B.iloc[j]=Coupon
        X.append(B)
    
        
    X1=[X[i].values for i in range(len(X))]
    FinalTable=pd.DataFrame(np.vstack(X1))
    FinalTable.columns=CF1.columns
    FinalTable.insert(0, pd.to_datetime(cobDate,format='%d/%m/%Y'), Input['DirtyPrice'] )
    FinalTable=FinalTable.fillna(0)
    
    return FinalTable




def getZCandDFCurve(AA,yearFrac,startingSet):
    
    YF=pd.DataFrame(yearFrac)
    AAA=list(AA.columns)
    YF=YF.set_index([AAA])
    
    
    
    zc=list(startingSet.iloc[0,:])
    df=list(startingSet.iloc[1,:])
    A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
    splineDataFrame=pd.DataFrame()
    
    
    
    
    
    row1=AA.iloc[0,:]
    row1=row1[row1!=0]
    nextdf=df[-1]
    #BondPV=100
    
    
    A.append(row1.index[-1])
    splineDataFrame['x']=A
    numberMissing=list(row1[1:-1].index)
    #while BondPV!=0:
    for l  in range(100):
    
        zc=list(startingSet.iloc[0,:])
        df=list(startingSet.iloc[1,:])
    
        dfGuess=nextdf
        
        zcGuess=-m.log(dfGuess)/float(YF[YF.index==row1.index[-1]].values)
        zc.insert(len(zc),zcGuess)
        
        splineDataFrame['y']=zc
        tableOfParameters=getTablesOfParameters(splineDataFrame)
        Interp=[]
        newdf=[]
        #newzc=[]
        for j in range(len(numberMissing)):
            evaluationDate=row1.index[-2-j]
            if evaluationDate<pd.to_datetime(startingSet.columns[0],format='%d/%m/%Y'):
                interpolatedValue=startingSet.iloc[0,0]
                Interp.append(pd.Series(interpolatedValue))
            else:
                
                interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
                Interp.append(interpolatedValue)
            newdf.append(m.exp(-Interp[j].iloc[0]*float(YF[YF.index==evaluationDate].values)))
        
        
        newdf.reverse()   
        #newdf=m.exp(-Interp[0].iloc[0]*yearFrac[3])
        Interp.reverse()
        newzc=[Interp[i].iloc[0] for i in range(len(Interp))]+[zcGuess]
       
        
        df=[1]+newdf+[dfGuess]
        BondPV=(sum([row1.iloc[i]*df[i] for i in range(len(df))]))
        nextdf=df[-1]+BondPV/2*-1
        
    
    df=list(startingSet.iloc[1,:])+df[1:]
    zc=list(startingSet.iloc[0,:])+newzc
    A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
    B=list(row1.index[1:])
    A=A+B
    
    
    splineDataFrame=pd.DataFrame()
      
    

    
    if len(AA)==1:
        pass
    else:
        for i in range(1,len(AA)):
            #
            row1=AA.iloc[i,:]
            row1=row1[row1!=0]
            nextdf=df[-1]
            #BondPV=100
            previuoszc=zc
            previuosdf=df
            
            A.append(row1.index[-1])
            splineDataFrame['x']=A
            numberMissing = int(np.where(AA.loc[i,:]>1)[0] - np.where(AA.loc[i-1,:]>1)[0] - 1)
            
            if numberMissing==0:
                row1=AA.iloc[i,:]
                row1=row1[row1!=0]
                nextdf=df[-1]
                
                previuoszc=zc
                previuosdf=df
                
                
                numberMissing = int(np.where(AA.loc[i,:]>1)[0] - np.where(AA.loc[i-1,:]>1)[0] - 1)
                for l  in range(100):
                    newdf=[1]+df[3:]+[nextdf]
                    BondPV=(sum([row1.iloc[i]*newdf[i] for i in range(len(newdf))]))
                    nextdf=newdf[-1]+BondPV/2*-1
                
                df=list(startingSet.iloc[1,:])+newdf[1:]
                zc=zc+[-m.log(newdf[-1])/float(YF[YF.index==row1.index[-1]].values)]
                A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
                B=list(row1.index[1:])
                A=A+B
                
                splineDataFrame=pd.DataFrame()
                
            else:
                
                #while BondPV!=0:
                for l  in range(100):
            
                    zc=copy.copy(previuoszc)
                    df=copy.copy(previuosdf)
            
                    dfGuess=nextdf
                    
                    zcGuess=-m.log(dfGuess)/float(YF[YF.index==row1.index[-1]].values)
                    zc.insert(len(zc),zcGuess)
                    
                    splineDataFrame['y']=zc
                    
                    
                    tableOfParameters=getTablesOfParameters(splineDataFrame)
                    Interp=[]
                    newdf=[]
                    #newzc=[]
                    for j in range(numberMissing):
                        evaluationDate=row1.index[-2-j]
                        interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
                        Interp.append(interpolatedValue)
                        newdf.append(m.exp(-Interp[j].iloc[0]*float(YF[YF.index==evaluationDate].values)))
                        
                        
                        
                        
                    newdf.reverse()   
                    #newdf=m.exp(-Interp[0].iloc[0]*yearFrac[3])
                    Interp.reverse()
                    newzc=[Interp[i].iloc[0] for i in range(len(Interp))]+[zcGuess]
                    #newzc=[Interp[0].iloc[0],zcGuess]
                    df=[1]+previuosdf[3:]+newdf+[dfGuess]
                    BondPV=(sum([row1.iloc[i]*df[i] for i in range(len(df))]))
                    nextdf=df[-1]+BondPV/2*-1
                    
                
                df=list(startingSet.iloc[1,:])+df[1:]
                zc=previuoszc+newzc
                A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
                B=list(row1.index[1:])
                A=A+B
                
                
                splineDataFrame=pd.DataFrame()
        
        
        
    dataFrameDF=pd.DataFrame()
    dataFrameDF['df']=df
    dataFrameDF=dataFrameDF.set_index([A])
    
    dataFrameZC=pd.DataFrame()
    dataFrameZC['ZC']=zc
    dataFrameZC=dataFrameZC.set_index([A])
    
    return dataFrameDF,dataFrameZC

Input=pd.read_excel(r"S:\Francesco\PRICING\Copy of BootstrappingSwapCurve_francesco.xlsx",sheet_name='input')
GiltDates=pd.read_excel(r"S:\Francesco\PRICING\Copy of BootstrappingSwapCurve_francesco.xlsx",sheet_name='coupondates')
cobDate='16/11/2018'
FinalTable=getCashFlowTable(Input,GiltDates,cobDate)




startingSet=pd.read_excel(r"S:\Francesco\PRICING\Copy of BootstrappingSwapCurve_francesco.xlsx",sheet_name='giltdates')





###############################################################################
#Francesco set
############################################################################### 
#
#def f(suggestedSpline):
#    #create data for spline
#    splineDataFrame=pd.DataFrame()
#    A=list(pd.to_datetime(startingSet.iloc[2,:]))
#    A.append(pd.to_datetime(Input['MATURITY'][0]))
#    splineDataFrame['x']=A
#    B=list(startingSet.iloc[0,:])
#    B.append(suggestedSpline)
#    splineDataFrame['y']=B
#    
#    #perform spline
#    #suggestedSpline=float(dailySpline[dailySpline.index==pd.to_datetime('22/07/2019',format='%d/%m/%Y')].values)
#
#    tableOfParameters=getTablesOfParameters(splineDataFrame)
#    evaluationDate=pd.to_datetime('22/01/2019',format='%d/%m/%Y')
#    interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
#    del splineDataFrame['X']
#    
#    #workout zc and df
#    zc=[]
#    
#    zc.append(float(interpolatedValue.values))
#    zc.append(suggestedSpline)
#    df=[]
#    df.append(1)
#    df.append(m.exp(-zc[0]*yf1))
#    df.append(m.exp(-zc[1]*yf2))
#    
#    #grab first bond
#    row1=FinalTable.iloc[0,:]
#    row1=list(row1[row1!=0])
#    
#    
#    
#    #workout the present value of the the bond
#    PV=(sum([row1[i]*df[i] for i in range(len(df))]))
#    
#    return PV
#
#
#
#import scipy.optimize 
#x = scipy.optimize.broyden1(f,0.00707, f_tol=0)




###############################################################################
#Michael set
############################################################################### 



NextCouponDates=list(pd.to_datetime(Input['NextCopon'].drop_duplicates()))
Results=[]
for i in range(len(NextCouponDates)):
    print(i)

    FinalTable=getCashFlowTable(Input,GiltDates,cobDate)
    A=pd.to_datetime(Input['NextCopon'])
    FinalTable.insert(0, 'NextCouponDate', A)
    filteredDataFrame=FinalTable[FinalTable['NextCouponDate']==NextCouponDates[i]]
    AA=filteredDataFrame.loc[:, (filteredDataFrame != 0).any(axis=0)]
    AA=AA.iloc[:,1:]
    AA=AA.reset_index(drop=True)
    
    
    A=list(AA.columns)
    yearFrac=[((A[i]-pd.to_datetime(cobDate,format='%d/%m/%Y')).days)/365 for i in range(len(A))]
    
    
    #FinalTable=getCashFlowTable(Input,GiltDates,cobDate)
    singleResult=getZCandDFCurve(AA,yearFrac,startingSet)
    
    Results.append(singleResult)





Mat=pd.to_datetime(list(Input[Input['NextCopon']=='22/01/2019']['MATURITY']),format='%d/%m/%Y')
A=Results[0][1]
maturities=[]
for i in range(len(Mat)):
    a=A[A.index==Mat[i]]
    maturities.append(a)


maturities=np.vstack(maturities)
dataframe1=pd.DataFrame()
dataframe1['mat']=Mat
dataframe1['zc']=maturities
dataframe1.set_index('mat')



Mat=pd.to_datetime(list(Input[Input['NextCopon']=='07/03/2019']['MATURITY']),format='%d/%m/%Y')
A=Results[1][1]
maturities=[]
for i in range(len(Mat)):
    a=A[A.index==Mat[i]]
    maturities.append(a)


maturities=np.vstack(maturities)
dataframe2=pd.DataFrame()
dataframe2['mat']=Mat
dataframe2['zc']=maturities



Mat=pd.to_datetime(list(Input[Input['NextCopon']=='22/04/2019']['MATURITY']),format='%d/%m/%Y')
A=Results[2][1]
maturities=[]
for i in range(len(Mat)):
    a=A[A.index==Mat[i]]
    maturities.append(a)


maturities=np.vstack(maturities)
dataframe3=pd.DataFrame()
dataframe3['mat']=Mat
dataframe3['zc']=maturities



Mat=pd.to_datetime(list(Input[Input['NextCopon']=='07/12/2018']['MATURITY']),format='%d/%m/%Y')
A=Results[3][1]
maturities=[]
for i in range(len(Mat)):
    a=A[A.index==Mat[i]]
    maturities.append(a)


maturities=np.vstack(maturities)
dataframe4=pd.DataFrame()
dataframe4['mat']=Mat
dataframe4['zc']=maturities



#s=[
#
#0.00707,
#0.00696,
#0.00701,
#0.00796,
#0.00919,
#0.00985,
#0.01058,
#0.01149,
#0.01265,
#0.01367,
#0.01478,
#0.01605,
#0.01856,
#0.01911,
#0.01925,
#0.01869,
#0.01858
#]

s=pd.DataFrame(Input['Coupon'])

s=pd.DataFrame(s)

dates=pd.to_datetime(list(Input['MATURITY']),format='%d/%m/%Y')


res = Results[0][1]*100
resdf = Results[0][0]
resdf = resdf.reset_index()

#introducing par yield curve
#resparyield = []
#resparyield = pd.DataFrame(resparyield)
#resparyield= resdf
#resparyield['paryield']=np.nan
#for i in range(len(resdf)):
#    
#
#
#
#resparyield = []
#resparyield = pd.DataFrame(resparyield)
#resparyield[0,'df'] = 1
#resparyield[0,'paryield'] = 0
#
#resdf = resdf.set_index(0)
#
#
#

s=s.set_index(dates)
#
bx = s.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='-',marker='o',color='y')
bx = res.plot(legend=False,ax=bx,linestyle='-',color='g')

spline=getDailySpline()
ax = s.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='-',marker='o',color='b')
ax = (spline*100).plot(legend=False,ax=ax,linestyle='-',color='r')

from pandas import ExcelWriter
 
writer = ExcelWriter(r"S:\Francesco\PRICING\Bootstrapping_gilt_results.xls")
res.to_excel(writer,'Sheet1',index=False)
resdf.to_excel(writer,'Sheet2',index=False)
writer.save()   

###############################################################################
#Alternative
#zc=list(startingSet.iloc[0,:])
#df=list(startingSet.iloc[1,:])
#A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#splineDataFrame=pd.DataFrame()
#
#
#
#
#
#row1=AA.iloc[0,:]
#row1=row1[row1!=0]
#nextdf=df[-1]
##BondPV=100
#
#
#A.append(row1.index[-1])
#splineDataFrame['x']=A
#numberMissing=row1[1:-1].index
##while BondPV!=0:
#for l  in range(100):
#
#    zc=list(startingSet.iloc[0,:])
#    df=list(startingSet.iloc[1,:])
#
#    dfGuess=nextdf
#    
#    zcGuess=-m.log(dfGuess)/float(YF[YF.index==row1.index[-1]].values)
#    zc.insert(len(zc),zcGuess)
#    
#    splineDataFrame['y']=zc
#    tableOfParameters=getTablesOfParameters(splineDataFrame)
#    Interp=[]
#    newdf=[]
#    #newzc=[]
#    for j in range(len(numberMissing)):
#        evaluationDate=numberMissing[j]
#        interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
#        Interp.append(interpolatedValue)
#        newdf.append(m.exp(-Interp[j].iloc[0]*float(YF[YF.index==evaluationDate].values)))
#    
#    
#    newdf.reverse()   
#    #newdf=m.exp(-Interp[0].iloc[0]*yearFrac[3])
#    Interp.reverse()
#    newzc=[Interp[i].iloc[0] for i in range(len(Interp))]+[zcGuess]
#   
#    
#    df=[1]+newdf+[dfGuess]
#    BondPV=(sum([row1.iloc[i]*df[i] for i in range(len(df))]))
#    nextdf=df[-1]+BondPV/2*-1
#    
#
#df=list(startingSet.iloc[1,:])+df[1:]
#zc=list(startingSet.iloc[0,:])+newzc
#A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#B=list(row1.index[1:])
#A=A+B
#
#
#splineDataFrame=pd.DataFrame()
#    



###############################################################################
#previuosVersion
#    zc=list(startingSet.iloc[0,:])
#    df=list(startingSet.iloc[1,:])
#    A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#    splineDataFrame=pd.DataFrame()
#    
#    
#    
#    
#
#    row1=AA.iloc[0,:]
#    row1=row1[row1!=0]
#    nextdf=df[-1]
#    #BondPV=100
#    
#    
#    A.append(row1.index[-1])
#    splineDataFrame['x']=A
#    
#    #while BondPV!=0:
#    for l  in range(100):
#
#        zc=list(startingSet.iloc[0,:])
#        df=list(startingSet.iloc[1,:])
#
#        dfGuess=nextdf
#        
#        zcGuess=-m.log(dfGuess)/float(YF[YF.index==row1.index[-1]].values)
#        zc.insert(len(zc),zcGuess)
#        
#        splineDataFrame['y']=zc
#        
#        
#        tableOfParameters=getTablesOfParameters(splineDataFrame)
#        evaluationDate=row1.index[-2]
#        interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
#        newdf=m.exp(-interpolatedValue*yearFrac[1])
#        newzc=[interpolatedValue.iloc[0],zcGuess]
#        df=[1]+[newdf]+[dfGuess]
#        BondPV=(sum([row1.iloc[i]*df[i] for i in range(len(df))]))
#        nextdf=df[-1]+BondPV/2*-1
#        
#    
#    df=list(startingSet.iloc[1,:])+df[1:]
#    zc=list(startingSet.iloc[0,:])+newzc
#    A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#    B=list(row1.index[1:])
#    A=A+B
#    
#    
#    splineDataFrame=pd.DataFrame()



#
#
#
#
#s=[
#
#0.00707,
#0.00696,
#0.00701,
#0.00796,
#0.00919,
#0.00985,
#0.01058,
#0.01149,
#0.01265,
#0.01367,
#0.01478,
#0.01605,
#0.01856,
#0.01911,
#0.01925,
#0.01869,
#0.01858
#]
#
#A['mm']=s
#
#A['mm']-A['zc']
#
#
#
#dates=pd.to_datetime([
#'22/07/2019',
#'22/07/2020',
#'22/01/2021',
#'22/07/2022',
#'22/07/2023',
#'07/09/2024',
#'07/09/2025',
#'22/07/2026',
#'22/07/2027',
#'22/10/2028',
#'07/12/2030',
#'07/06/2032',
#'07/09/2037',
#'07/12/2042',
#'22/07/2047',
#'22/07/2057',
#'22/07/2068'
#],format='%d/%m/%Y')
#
#
#FinalTable=getCashFlowTable(Input,GiltDates,cobDate)
#A=pd.to_datetime(Input['NextCopon'])
#FinalTable.insert(0, 'NextCouponDate', A)
#filteredDataFrame=FinalTable[FinalTable['NextCouponDate']==NextCouponDates[1]]
#AA=filteredDataFrame.loc[:, (filteredDataFrame != 0).any(axis=0)]
#AA=AA.iloc[:,1:]
#AA=AA.reset_index(drop=True)
#
#
#A=list(AA.columns)
#yearFrac=[((A[i]-pd.to_datetime(cobDate,format='%d/%m/%Y')).days)/365 for i in range(len(A))]
#
#        
#
#
#YF=pd.DataFrame(yearFrac)
#AAA=list(AA.columns)
#YF=YF.set_index([AAA])
#
#
#
#zc=list(startingSet.iloc[0,:])
#df=list(startingSet.iloc[1,:])
#A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#splineDataFrame=pd.DataFrame()
#
#
#
#
#
#row1=AA.iloc[0,:]
#row1=row1[row1!=0]
#nextdf=df[-1]
##BondPV=100
#
#
#A.append(row1.index[-1])
#splineDataFrame['x']=A
#numberMissing=list(row1[1:-1].index)
##while BondPV!=0:
#for l  in range(100):
#
#    zc=list(startingSet.iloc[0,:])
#    df=list(startingSet.iloc[1,:])
#
#    dfGuess=nextdf
#    
#    zcGuess=-m.log(dfGuess)/float(YF[YF.index==row1.index[-1]].values)
#    zc.insert(len(zc),zcGuess)
#    
#    splineDataFrame['y']=zc
#    tableOfParameters=getTablesOfParameters(splineDataFrame)
#    Interp=[]
#    newdf=[]
#    #newzc=[]
#    for j in range(len(numberMissing)):
#        evaluationDate=row1.index[-2-j]
#        if evaluationDate<pd.to_datetime(startingSet.columns[0],format='%d/%m/%Y'):
#            interpolatedValue=startingSet.iloc[0,0]
#            Interp.append(pd.Series(interpolatedValue))
#        else:
#            
#            interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
#            Interp.append(interpolatedValue)
#        newdf.append(m.exp(-Interp[j].iloc[0]*float(YF[YF.index==evaluationDate].values)))
#    
#    
#    newdf.reverse()   
#    #newdf=m.exp(-Interp[0].iloc[0]*yearFrac[3])
#    #Interp.reverse()
#    newzc=[Interp[i].iloc[0] for i in range(len(Interp))]+[zcGuess]
#   
#    
#    df=[1]+newdf+[dfGuess]
#    BondPV=(sum([row1.iloc[i]*df[i] for i in range(len(df))]))
#    nextdf=df[-1]+BondPV/2*-1
#    
#
#df=list(startingSet.iloc[1,:])+df[1:]
#zc=list(startingSet.iloc[0,:])+newzc
#A=list(pd.to_datetime(list(startingSet.columns),format='%d/%m/%Y'))
#B=list(row1.index[1:])
#A=A+B
#
#
#splineDataFrame=pd.DataFrame()
#
#
#
#
#
#
