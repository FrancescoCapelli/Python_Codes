# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:47:06 2019

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
 

data=pd.read_excel(r"S:\Francesco\PRICING\presentation\BootstrappingSwapCurve_francesco_cobdate15feb2019.xlsx",sheet_name='Sheet4')
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


data=pd.read_excel(r"S:\Francesco\PRICING\presentation\BootstrappingSwapCurve_francesco_cobdate15feb2019.xlsx",sheet_name='Sheet4')
data1=data.set_index('x')
G=pd.DataFrame(datelist)
G['x']=A
G=G.set_index(0)
#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
#ax = G.plot(legend=False,ax=ax)

import matplotlib.pyplot as plt
ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
ax = G.plot(legend=False,ax=ax)
plt.title('UK ZC-Inflation Swap Curve Cobdate 15-Feb-2019')
plt.xlabel('years')
plt.ylabel('rates(%)')
plt.show() 
#############################################################################################################

    
######################################################################################## 
##############SWAP CHARTS###############################################################    
########################################################################################    

finalzerocoupon = []
finalzerocoupon= pd.DataFrame(finalzerocoupon)
discountfactor= []  
discountfactor = pd.DataFrame(discountfactor)  
finalzerocoupon['x'] = Coupon['x']
finalzerocoupon['y'] = Coupon['zc']*100
tableOfParameters=getTablesOfParameters(finalzerocoupon)
datelist2 = pd.date_range(start = finalzerocoupon.loc[0,'x'], end = data.loc[len(finalzerocoupon)-1,'x'] ).tolist()
Interpolation=[]
for i in range(len(datelist2)):
    interpolatedValue2=getSplineValue(datelist2[i],tableOfParameters)
    Interpolation.append(interpolatedValue2)

B=np.vstack(Interpolation)

del finalzerocoupon['X']
finalzerocoupon=finalzerocoupon.set_index('x')

BB=pd.DataFrame(datelist2)
BB['x']=B
BB=BB.set_index(0)
#bx = finalzerocoupon.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='g')
#bx = BB.plot(legend=False,ax=bx) 
#
#ax = data1.plot(legend=False, figsize=(8, 5), x_compat=True,linestyle='',marker='o',color='r')
#ax = G.plot(legend=False,ax=ax) 

import matplotlib.pyplot as plt
zeroC=plt.plot(BB)
coupon=plt.plot(G)
plt.title('Coupon vs Zero Coupon')
plt.xlabel('yrs')
plt.ylabel('rates(%)')
#plt.legend(loc=2, ncol=2)
plt.show()       
      
#from pandas import ExcelWriter
# 
#writer = ExcelWriter(r"C:\Users\capel\Desktop\Excel\pricing\bootstrapping\outputLIBORswap.xlsx")
#Coupon.to_excel(writer,'Sheet1',index=False)
#BB1.to_excel(writer,'Sheet2',index=False)
#G.to_excel(writer,'Sheet3',index=False)
#writer.save()       

