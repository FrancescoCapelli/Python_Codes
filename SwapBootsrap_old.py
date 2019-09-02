# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 16:36:47 2018

@author: capellf
"""
import pandas as pd
import numpy as np 
import math as m

from dateutil.relativedelta import relativedelta
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


from CubicSpline  import getTablesOfParameters,getSplineValue,remove_duplicates 
 

data=pd.read_excel(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\0AIL2041 Syndication 09 July 2019\BootstrappingSwapCurve_francesco.xlsx",sheet_name='libor')
tableOfParameters=getTablesOfParameters(data)

#########################################################################################################
#plot the spline
#########################################################################################################
datelist = pd.date_range(start = data.loc[0,'x'], end = data.loc[len(data)-1,'x'] ).tolist()

Interpolation=[]
for i in range(len(datelist)):
    interpolatedValue=getSplineValue(datelist[i],tableOfParameters)
    Interpolation.append(interpolatedValue)

A=np.vstack(Interpolation)


data=pd.read_excel(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\0AIL2041 Syndication 09 July 2019\BootstrappingSwapCurve_francesco.xlsx",sheet_name='libor')
data1=data.set_index('x')
G1=pd.DataFrame(datelist)
G1['x']=A
G1=G1.set_index(0)
#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
#ax = G.plot(legend=False,ax=ax)
  
#############################################################################################################
#setting coupon dates given cobdate
##############################################################################################################
index=[]
for i in range(120):
    n=(i+1)*6
    index.append(n)
date = data.loc[0,'x']    
H=[]
H.append(date)    
for i in range(len(index)):#46
    QQ=date+relativedelta(months=+index[i])
    H.append(QQ)
#only business days
W=[]
for i in range(len(H)):
    if H[i].weekday()<5:
        W.append(H[i])
    else:
        
        W.append(H[i]+business)
W.sort()
QQ=remove_duplicates(W)
AA=[str(QQ[i]).split(' ')[0] for i in range(len(QQ))]

############################################################################
#######add coupons
############################################################################
CF=pd.DataFrame(columns = AA)
CF.insert(0, "Coupon", data['y'][4:])

#take difference among years and take fraction
B=pd.DataFrame(pd.to_datetime(AA))
B=B.diff()
C=B[0][1:].dt.total_seconds()/ (24 * 60 * 60)

C=pd.DataFrame(C)
C[1]=C[0]/365
D=list(C[1])
D.insert(0,1)
#maturity=['2017-09-28','2018-09-28','2019-09-30','2020-09-28','2021-09-28','2022-09-28','2023-09-28','2024-09-30','2025-09-29','2026-09-28','2036-09-29','2046-09-28']
CF.insert(1,'maturity',data['x'][4:])
maturity = data['x'][4:]
maturity = [str(maturity.iloc[i]).split(' ')[0] for i in range(len(maturity))]
#adding all coupon payments
for i in range(len(D)):

    values=CF['Coupon']*D[i]
    CF[AA[i]]=values/100
#initial payment of 100
CF[AA[0]]=-1    
    
CF1=CF.iloc[:,3:] # only coupons

#datelist = pd.date_range(start = data.loc[0,'x'], end = data.loc[len(data)-1,'x'] ).tolist()

for i in range(len(CF1.columns)):
    for j in range(len(maturity)):
        if CF1.columns[i]==maturity[j]:
           values=CF1.iloc[j,i]+1
           CF1.iloc[j,i]=values
        elif CF1.columns[i]>maturity[j]:
            CF1.iloc[j,i]=0
        else:
           values=CF1.iloc[j,i]
           CF1.iloc[j,i]=values 
CF1.insert(0,'Coupon',CF['Coupon'])
CF1.insert(1,'maturity',maturity)
CF1.insert(2,'initial payment date on spot',CF[AA[0]])
###################################################################
####################################################################
b=pd.DataFrame(pd.to_datetime(AA))
c=b[1:]
d=[(c.iloc[i]-b.iloc[0]) for i in range(len(c))]
yearFraction=[float(str(d[i]).split(' ')[3])/365 for i in range(len(d))]
yearFraction.insert(0,1)
#########################################################################
#########################################################################

#generating zc and df for money markets
cobdate = datelist[0]-1
yearfrac_cobdate = 0.002739
Coupon = data

DFmm1= 1/(1+(Coupon.loc[0,'y']/100)*yearfrac_cobdate)
ZCmm1 = m.log(DFmm1)/yearfrac_cobdate * -1

diff=[(Coupon.loc[i,'x']- Coupon.loc[0,'x']) for i in range(len(Coupon))]
z=[str(diff[i]).split(' ')[0] for i in range(len(diff))]
z=pd.DataFrame
Coupon.insert(0,'day',diff)
days = [float(str(Coupon.loc[i,'day']).split(' ')[0])/365 for i in range(len(Coupon))]

Coupon.insert(0,'days',days)
del Coupon['day']

Coupon['zc']=np.nan
Coupon['df']=np.nan
Coupon.loc[0,'zc']=ZCmm1
Coupon.loc[0,'df']=DFmm1

for i in range(len(Coupon)-1):
    if Coupon.loc[i+1,'days'] < 1:
       Coupon.loc[i+1,'df'] = 1/(1+(Coupon.loc[i+1,'y']/100)*Coupon.loc[i+1,'days'])*DFmm1
       Coupon.loc[i+1,'zc'] = m.log(Coupon.loc[i+1,'df'])/(yearfrac_cobdate + Coupon.loc[i+1,'days']) * -1

###########################################################################################
############################first swap 2yrs loop###########################################
###########################################################################################
#setting MM dates together with coupon dates
startingDates = data.loc[0:2,'x'].tolist()
date          =  data.loc[3,'x']

HH=[]
HH.append(date)    
for i in range(len(index)-1):#46
    matrix=date+relativedelta(months=+index[i])
    HH.append(matrix)
#HH is created for the final two loops at the end including MM dates    
HH       = startingDates + HH
#only business days
WW=[]
for i in range(len(HH)):
    if HH[i].weekday()<5:
        WW.append(HH[i])
    else:
        
        WW.append(HH[i]+business)
WW.sort()
matrix=remove_duplicates(WW) 
matrix = pd.DataFrame(matrix)
matrix['df']=np.nan
matrix['zc']=np.nan

#setting count for the coming loops       
count = round(Coupon[Coupon['days']>1]['days'],1)
count = count*2
count = count.reset_index(drop=True)
count = [int(count[i]) for i in range(len(count))]
count=pd.DataFrame(count)
CF2 = CF1
CF2 = CF2.reset_index(drop=True)
del CF2['Coupon']
del CF2['maturity']
count= count+1


#initial loop for first cash flow swap is populated
c=0
print(c)
   
d = count.iloc[c][0]
swap=CF2.iloc[c,0:d]
swaplist=list(swap)
    
p=4
if Coupon.loc[p,'days']>1:
   zc=list(Coupon['zc'].iloc[0:p])
   df=list(Coupon['df'].iloc[0:p])
   yf=yearFraction[2:p+1] 
   splineDataFrame=pd.DataFrame()
   dates=list(Coupon['x'].iloc[0:p+1])    
   splineDataFrame['x']=dates
   PV=[]
   SwapPV=100
   nextdf=df[-1] 
   missingDates_2=list(swap.index[2:p]) #only dates to be interpolated before maturities
   len_yf=len(yf)
   
   for i in range(100):
     print(i)
     print(nextdf)
    
#while SwapPV!=0:
     zc=list(Coupon['zc'].iloc[0:p])
     df=list(Coupon['df'].iloc[0:p])
     dfGuess=nextdf
     zcGuess=-m.log(dfGuess)/yf[len_yf-1]
     zc.insert(len(zc),zcGuess)
     splineDataFrame['y']=zc
     tableOfParameters=getTablesOfParameters(splineDataFrame)
     Interp=[]
     for j in range(len(missingDates_2)):
        
        evaluationDate=pd.to_datetime(missingDates_2[j],format='%Y-%m-%d')
        interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
        Interp.append(interpolatedValue)
        
     #newdf1=([m.exp(-Interp[i].iloc[0]*yf[i]),m.exp(-Interp[i].iloc[0]*yf[i])] for i in range(len(missingDates_2)))
     newdf=[m.exp(-Interp[i].iloc[0]*yf[i]) for i in range(len(Interp))]
     newdf=[1]+df[3:]+newdf+[nextdf]
     SwapPV=(sum([swaplist[i]*newdf[i] for i in range(len(newdf))]))
     PV.append(SwapPV)
     nextdf=nextdf+(SwapPV/2)*-1 

for i in range(len(Coupon)):
    if Coupon['days'].loc[i]<1:
        matrix['df'].loc[i]= Coupon['df'].loc[i]
        matrix['zc'].loc[i]= Coupon['zc'].loc[i]

newdf=pd.DataFrame(newdf)
newdf = newdf[2:]
for l in range(2,len(newdf)+2):
    matrix['df'].loc[l+2]= newdf.loc[l][0]
    matrix['zc'].loc[l+2]= -m.log(newdf.loc[l][0])/yearFraction[l] 

l=4    
Coupon.loc[p,'df']= newdf.loc[l][0]
Coupon.loc[p,'zc']= -m.log(newdf.loc[l][0])/yearFraction[l] 
    
###########################################################################################
############################remaining swap loops###########################################
###########################################################################################    
    
for c in range(1,len(count)):
    print(c)
   
    d1 = count.iloc[c][0]
    d2 = count.iloc[c-1][0]
    swap=CF2.iloc[c,0:d1]
    swaplist=list(swap)

    zc=[matrix['zc'].iloc[0:d2+2]]
    df=[matrix['df'].iloc[0:d2+2]]
    yf=yearFraction[d2:d1] 
    splineDataFrame=pd.DataFrame()
    #dates=list(pd.to_datetime([matrix[0].iloc[0:d2+2]][0],format='%Y-%m-%d') )
    dates=list([matrix[0].iloc[0:d2+2]][0])
    newdate=pd.to_datetime(swap.index[-1],format='%Y-%m-%d')
    dates.append(newdate)
    splineDataFrame['x']=dates
        
    PV=[]
    SwapPV=100
    nextdf=df[0][len(df[0])-1]
    missingDates_2=list(swap.index[d2:d1]) 
    len_yf=len(yf)
   
    for i in range(100):
               print(i)
               print(nextdf)
    
#while SwapPV!=0:
               zc=[matrix['zc'].iloc[0:d2+2]]
               df=[matrix['df'].iloc[0:d2+2]]
               dfGuess=nextdf
               zcGuess=-m.log(dfGuess)/yf[-1]
               #zc[0].insert(len(zc),zcGuess)
               zc=list(zc[0])
               zc.insert(len(zc),zcGuess)
               splineDataFrame['y']=zc
               tableOfParameters=getTablesOfParameters(splineDataFrame)
               Interp=[]
               for j in range(len(missingDates_2)-1):
        
                   evaluationDate=pd.to_datetime(missingDates_2[j],format='%Y-%m-%d')
                   interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
                   Interp.append(interpolatedValue)
        
               newdf=[m.exp(-Interp[i].iloc[0]*yf[i]) for i in range(len(Interp))]
               
               newdf=[1]+list(df[0][3:])+newdf+[nextdf]
               #del newdf[5]
               SwapPV=(sum([swaplist[i]*newdf[i] for i in range(len(newdf))]))
               PV.append(SwapPV)
               nextdf=nextdf+(SwapPV/2)*-1 

    newdf=pd.DataFrame(newdf)
    #newdf = newdf[1:]
    for l in range(1,len(newdf)):
        matrix['df'].loc[l+2]= newdf.loc[l][0]
        matrix['zc'].loc[l+2]= -m.log(newdf.loc[l][0])/yearFraction[l] 

    p=c+4       
    Coupon.loc[p,'df']= np.squeeze((newdf[-1:]).values)
    Coupon.loc[p,'zc']= -m.log(np.squeeze((newdf[-1:]).values))/yf[-1]    
    
    
######################################################################################## 
##############SWAP CHARTS###############################################################    
########################################################################################    

finalzerocoupon1= []
finalzerocoupon1= pd.DataFrame(finalzerocoupon1)
discountfactor= []  
discountfactor = pd.DataFrame(discountfactor)  
finalzerocoupon1['x'] = Coupon['x']
#finalzerocoupon1['y'] = Coupon['zc']*100
finalzerocoupon1['y'] = Coupon['df']
tableOfParameters=getTablesOfParameters(finalzerocoupon1)
datelist2 = pd.date_range(start = finalzerocoupon1.loc[0,'x'], end = data.loc[len(finalzerocoupon1)-1,'x'] ).tolist()
Interpolation=[]
for i in range(len(datelist2)):
    interpolatedValue2=getSplineValue(datelist2[i],tableOfParameters)
    Interpolation.append(interpolatedValue2)

B=np.vstack(Interpolation)

del finalzerocoupon1['X']
finalzerocoupon1=finalzerocoupon1.set_index('x')

results_libor=pd.DataFrame(datelist2)
results_libor['x']=B
results_libor=results_libor.set_index(0)



from datetime import date, timedelta, datetime
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
yesterday_date = datetime.strptime(yesterday, '%Y-%m-%d')

discount_factor_libor = pd.DataFrame(columns = ['Time','DF','Time_delta'])
discount_factor_libor['DF'] = results_libor['x']
discount_factor_libor['Time'] = results_libor.index
discount_factor_libor = discount_factor_libor.reset_index()
discount_factor_libor = discount_factor_libor.drop(0, axis=1)

for i in range(0,len(discount_factor_libor)):
    discount_factor_libor ['Time_delta'][i] = (float(str(discount_factor_libor['Time'][i] - yesterday_date)[0])/365)
    print(discount_factor_libor ['Time_delta'][i])
    





#bx = finalzerocoupon1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='g')
#bx = results_libor.plot(legend=False,ax=bx) 
#
#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
#ax = G1.plot(legend=False,ax=ax) 

#import matplotlib.pyplot as plt
#zeroC=plt.plot(results_libor)
##coupon=plt.plot(G1)
##plt.title('LIBOR Swap Curve: Coupon vs ZC, cobdate 15-Feb 2018')
#plt.title('LIBOR DF, cobdate 15-Feb 2018')
#plt.xlabel('years')
#plt.ylabel('rates(%)')
##plt.legend(loc=2, ncol=2)
#plt.show()       

#
      
#from pandas import ExcelWriter
# 
#writer = ExcelWriter(r"C:\Users\capel\Desktop\Excel\pricing\bootstrapping\outputLIBORswap.xlsx")
#Coupon.to_excel(writer,'Sheet1',index=False)
#results_libor1.to_excel(writer,'Sheet2',index=False)
#G.to_excel(writer,'Sheet3',index=False)
#writer.save()       

