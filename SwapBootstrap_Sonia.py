# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 10:48:52 2018

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
 

data_ois=pd.read_excel(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\Pricing templates\BootstrappingSwapCurve_francesco.xlsx",sheet_name='ois')
tableOfParameters=getTablesOfParameters(data_ois)

#########################################################################################################
#plot the spline
#########################################################################################################
datelist_ois = pd.date_range(start = data_ois.loc[0,'date'], end = data_ois.loc[len(data_ois)-1,'date'] ).tolist()

Interpolation=[]
for i in range(len(datelist_ois)):
    interpolatedValue=getSplineValue(datelist_ois[i],tableOfParameters)
    Interpolation.append(interpolatedValue)

A=np.vstack(Interpolation)
#
#
data=pd.read_excel(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\Pricing templates\BootstrappingSwapCurve_francesco.xlsx",sheet_name='ois')
data1=data.set_index('date')
G=pd.DataFrame(datelist_ois)
G['date']=A
G=G.set_index(0)

#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='rate')
#ax = G.plot(legend=False,ax=ax,color='r')
#ax.set_title('OIS Swap Coupon Curve ', horizontalalignment='center', verticalalignment='bottom')  
#############################################################################################################
#setting coupon dates given cobdate
##############################################################################################################
index=[]
for i in range(60):
    n=(i+1)*12
    index.append(n)
date = data.loc[0,'date'] 
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
###### add coupons
############################################################################
CF=pd.DataFrame(columns = AA)
CF.insert(0, "Coupon", data['rate'][4:])
#take difference among years and take fraction
B=pd.DataFrame(pd.to_datetime(AA))
B=B.diff()
C=B[0][1:].dt.total_seconds()/ (24 * 60 * 60)

C=pd.DataFrame(C)
C[1]=C[0]/365
D=list(C[1])
D.insert(0,1)
CF.insert(1,'maturity',data['date'][4:])
maturity = data['date'][4:]
maturity = [str(maturity.iloc[i]).split(' ')[0] for i in range(len(maturity))]
#adding all coupon payments
for i in range(len(D)):

    values=CF['Coupon']*D[i]
    CF[AA[i]]=values/100

#initial payment of 100
CF[AA[0]]=-1    
    
CF1=CF.iloc[:,2:] # only coupons
#setting face values at maturities 
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
#CF1.insert(2,CF[AA[0]])

####################################################################
############ creating year fraction ( distance in terms of yrs from spot date)
####################################################################

b=pd.DataFrame(pd.to_datetime(AA))
c=b[1:]
d=[(c.iloc[i]-b.iloc[0]) for i in range(len(c))]
yearFraction=[float(str(d[i]).split(' ')[3])/365 for i in range(len(d))]
yearFraction.insert(0,1)

#########################################################################
#########################################################################
#generating zc and df for money markets, the first has to be the overnight but the others can be more than 1w, 1m, 6m

cobdate = datelist_ois[0]-1
yearfrac_cobdate = 0.002739 #yearfraction hard coded calculated on the overnight rate
Coupon = data
DFmm1= 1/(1+(Coupon.loc[0,'rate']/100)*yearfrac_cobdate)
ZCmm1 = m.log(DFmm1)/yearfrac_cobdate * -1

diff=[(Coupon.loc[i,'date']- Coupon.loc[0,'date']) for i in range(len(Coupon))]
Coupon.insert(0,'day',diff)
days = [float(str(Coupon.loc[i,'day']).split(' ')[0])/365 for i in range(len(Coupon))]

Coupon.insert(0,'yrs',days)
del Coupon['day']

Coupon['zc']=np.nan
Coupon['df']=np.nan
Coupon.loc[0,'zc']=ZCmm1
Coupon.loc[0,'df']=DFmm1

for i in range(len(Coupon)-1):
    if Coupon.loc[i+1,'yrs'] < 1:
       Coupon.loc[i+1,'df'] = 1/(1+(Coupon.loc[i+1,'rate']/100)*Coupon.loc[i+1,'yrs'])*DFmm1
       Coupon.loc[i+1,'zc'] = m.log(Coupon.loc[i+1,'df'])/(yearfrac_cobdate + Coupon.loc[i+1,'yrs']) * -1

###########################################################################################
############################first swap 2yrs loop###########################################
###########################################################################################
#setting MM dates together with coupon dates       
startingDates = data.loc[0:3,'date'].tolist()
date          =  data.loc[0,'date']

HH=[]
HH.append(date)    
for i in range(len(index)):#46
    matrix=date+relativedelta(months=+index[i])
    HH.append(matrix) 
HH  = startingDates + HH[1:]
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
count = round(Coupon[Coupon['yrs']>=1]['yrs'],1)
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
#for c in range(len(count)):
print(c)       
d = count.iloc[c][0]
swap=CF2.iloc[c,0:d]
swaplist=list(swap)
p=4 # p is imposed 4 because the 4 mm rates are calculated specifically before (over/n, 1w,1m,6m    
if Coupon.loc[p,'yrs']>=1:
   zc=list(Coupon['zc'].iloc[0:p])
   df=list(Coupon['df'].iloc[0:p])
   yf=yearFraction[1] #we have only the 1yr maturity 
   splineDataFrame=pd.DataFrame()
   dates=list(Coupon['date'].iloc[0:p+1])    
   splineDataFrame['date']=dates
   PV=[]
   SwapPV=100
   nextdf=df[-1]   
   for i in range(100):
     print(i)
     print(nextdf)
     
     zc=list(Coupon['zc'].iloc[0:p])
     df=list(Coupon['df'].iloc[0:p])
     dfGuess=nextdf
     zcGuess=-m.log(dfGuess)/yf
     zc.insert(len(zc),zcGuess)
     splineDataFrame['rate']=zc
     tableOfParameters=getTablesOfParameters(splineDataFrame)
     newdf=[1]+[nextdf]
     SwapPV=(sum([swaplist[i]*newdf[i] for i in range(len(newdf))]))
     PV.append(SwapPV)
     nextdf=nextdf+(SwapPV/2)*-1 
#populating in matrix only MM rates
for i in range(len(Coupon)):
    if Coupon['yrs'].loc[i]<1:
        matrix['df'].loc[i]= Coupon['df'].loc[i]
        matrix['zc'].loc[i]= Coupon['zc'].loc[i]

newdf=pd.DataFrame(newdf)
matrix['df'].loc[4]= newdf.loc[1][0]
matrix['zc'].loc[4]= -m.log(newdf.loc[1][0])/yearFraction[1]     
Coupon.loc[p,'df']= newdf.loc[1][0]
Coupon.loc[p,'zc']= -m.log(newdf.loc[1][0])/yearFraction[1]
    
###########################################################################################
############################remaining swap loops###########################################
###########################################################################################       
       
for c in range(1,len(count)):
    print(c)
    #c=2
    d1 = count.iloc[c][0]
    d2 = count.iloc[c-1][0]
    swap=CF2.iloc[c,0:d1]
    swaplist=list(swap)

    zc=[matrix['zc'].iloc[0:d2+3]]
    df=[matrix['df'].iloc[0:d2+3]]
    yf=yearFraction[d2:d1] 
    splineDataFrame=pd.DataFrame()
    #dates=list(pd.to_datetime([matrix[0].iloc[0:d2+2]][0],format='%Y-%m-%d') )
    dates=list([matrix[0].iloc[0:d2+3]][0])
    newdate=pd.to_datetime(swap.index[-1],format='%Y-%m-%d')
    dates.append(newdate)
    splineDataFrame['date']=dates
        
    PV=[]
    SwapPV=100
    nextdf=df[0][len(df[0])-1]
    missingDates_2=list(swap.index[d2:d1]) 
    len_yf=len(yf)
    
    for i in range(100):
               print(i)
               print(nextdf)
    
#while SwapPV!=0:
               zc=[matrix['zc'].iloc[0:d2+3]]
               df=[matrix['df'].iloc[0:d2+3]]
               dfGuess=nextdf
               zcGuess=-m.log(dfGuess)/yf[-1]
               #zc[0].insert(len(zc),zcGuess)
               zc=list(zc[0])
               zc.insert(len(zc),zcGuess)
               splineDataFrame['rate']=zc
               tableOfParameters=getTablesOfParameters(splineDataFrame)
               Interp=[]
               if len(missingDates_2) >1:
                   for j in range(len(missingDates_2)-1):
        
                       evaluationDate=pd.to_datetime(missingDates_2[j],format='%Y-%m-%d')
                       interpolatedValue=getSplineValue(evaluationDate,tableOfParameters)
                       Interp.append(interpolatedValue)
        
                   newdf=[m.exp(-Interp[i].iloc[0]*yf[i]) for i in range(len(Interp))]
                   newdf=[1]+list(df[0][4:])+newdf+[nextdf]
                   SwapPV=(sum([swaplist[i]*newdf[i] for i in range(len(newdf))]))
                   PV.append(SwapPV)
                   nextdf=nextdf+(SwapPV/2)*-1
                
               else: 
                   newdf=[1]+list(df[0][4:])+[nextdf]
                   SwapPV=(sum([swaplist[i]*newdf[i] for i in range(len(newdf))]))
                   PV.append(SwapPV)
                   nextdf=nextdf+(SwapPV/2)*-1 

    newdf=pd.DataFrame(newdf)
    #newdf = newdf[1:]
    for l in range(1,len(newdf)):
        matrix['df'].loc[l+3]= newdf.loc[l][0]
        matrix['zc'].loc[l+3]= -m.log(newdf.loc[l][0])/yearFraction[l] 

    p=c+4       
    Coupon.loc[p,'df']= np.squeeze((newdf[-1:]).values)
    Coupon.loc[p,'zc']= -m.log(np.squeeze((newdf[-1:]).values))/yf[-1]    
    
    

########################################################################################    

       
final_zerocoupon= []
final_zerocoupon= pd.DataFrame(final_zerocoupon)
discountfactor= []  
discountfactor = pd.DataFrame(discountfactor)  

final_zerocoupon['date'] = Coupon['date']
discountfactor['date'] = Coupon['date']
final_zerocoupon['zc'] = Coupon['zc']*100
discountfactor['df'] = Coupon['df']

from datetime import datetime,timedelta
yesterday_cobdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(1)

difference=[(Coupon.loc[i,'date']- yesterday_cobdate) for i in range(len(Coupon))]
Days=[float(str(difference[i]).split(' ')[0])/365 for i in range(len(difference))]
discountfactor.insert(1,'days',Days)
discountfactor = discountfactor.drop(['date'],axis=1) 
new_row = pd.DataFrame({'days':0, 'df':1},index = [0])
discountfactor = pd.concat([new_row, discountfactor]).reset_index(drop = True)
discountfactor.columns = ['Time','DF']

import os

if os.path.exists(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\Pricing templates\PythonCodesandResults\DF_Sonia.xls"):
  os.remove(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\Pricing templates\PythonCodesandResults\DF_Sonia.xls")
else:
  print("The file has never been saved before")
  pass

writer = pd.ExcelWriter(r"\\data01\primissu\ERQA\Analytical Tasks\Syndication\Pricing templates\PythonCodesandResults\DF_Sonia.xls")
discountfactor.to_excel(writer,'Sheet1',index=False)
writer.save() 

#######################################################
#fitting zero coupon curve and other various charts
########################################################

#tableOfParameters=getTablesOfParameters(final_zerocoupon)
#datelist2_ois = pd.date_range(start = final_zerocoupon.loc[0,'date'], end = data.loc[len(final_zerocoupon)-1,'date'] ).tolist()
#Interpolation=[]
#for i in range(len(datelist2_ois)):
#    interpolatedValue2=getSplineValue(datelist2_ois[i],tableOfParameters)
#    Interpolation.append(interpolatedValue2)
#
#F=np.vstack(Interpolation)
#
#del final_zerocoupon['date']
#final_zerocoupon=final_zerocoupon.set_index('date')
#
#results_sonia=pd.DataFrame(datelist2_ois)
#results_sonia['date']=F
#results_sonia=results_sonia.set_index(0)



#bx = final_zerocoupon.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='g')
#bx = results_sonia.plot(legend=False,ax=bx) 
#bx.set_title('OIS Swap Zero Coupon Curve ', horizontalalignment='center', verticalalignment='bottom')  
#
#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
#ax = G.plot(legend=False,ax=ax) 

#import matplotlib.pyplot as plt
#plt.plot(results_sonia,label ='SONIA ZC Curve')
#plt.plot(BB,label ='LIBOR ZC Curve')
#plt.plot(G,label ='Sonia Coupon Curve')
#plt.plot(G1,label ='LIBOR Coupon Curve')
#
##coupon=plt.plot(G)
##plt.title('LIBOR Swap Curve: Coupon vs ZC, cobdate 15-Feb 2018')
#plt.title('Swap Curves, cobdate 15-Feb 2019')
#plt.xlabel('years')
#plt.ylabel('rates(%)')
#plt.legend()
#plt.show()          




#
#import matplotlib.pyplot as plt
#plt.plot(results_sonia,label ='SONIA DF')
#plt.plot(BB,label ='LIBOR DF')
#
##coupon=plt.plot(G)
##plt.title('LIBOR Swap Curve: Coupon vs ZC, cobdate 15-Feb 2018')
#plt.title('Discount Factors, cobdate 15-Feb 2019')
#plt.xlabel('years')
#plt.ylabel('rates(%)')
#plt.legend()
#plt.show()          