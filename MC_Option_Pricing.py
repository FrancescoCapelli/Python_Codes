import numpy as np
from math import floor
from numpy import sqrt, max
from numpy.random import normal
import matplotlib.pyplot as plt
from scipy.stats import norm

def vol(sigma,n):
    #time-varying volatilities
    s=np.zeros((n,1))
    for i in range(0,n): 
        s[i]=sigma
    return s

def ir(r,n):
    #time-varying interest_rates
    rates=np.zeros((n,1))
    for i in range(0,n): 
        rates[i]=r
    return rates

class ENGINE:
    def __init__(self,S0,sigma,r,K,time_frame,iterations,call):
        self.S0=S0
        if isinstance(time_frame,list):
            time_frame=np.array(time_frame)
        self.time_frame=time_frame.reshape((-1,1)) #making the array 1*1
        n=len(time_frame)
        self.vol=vol(sigma,n)
        self.ir=ir(r,n)
        self.K=K
        self.iterations=iterations
        self.call=call
        
    def montecarlo_path(self):
        t=self.time_frame
        n=len(t)
        dt=np.zeros((n,1))
        dt[0,0]=t[0,0]
        if n==1:
            random =normal(0,1) #random generator with normal distribution
        else:
            for i in range(1,n): 
                dt[i,0]=t[i,0]-t[i-1,0]
            random = normal(0,1,(n,1))
            
        lnS=dt*(self.ir-0.5*self.vol**2)+self.vol*sqrt(dt)*random
        returns =np.cumsum(np.concatenate((np.zeros((1,1)),lnS))).reshape((-1,1)) #all log returns for each simulation
        path=self.S0*np.exp(returns) #all price movements
        
        return path
    
    def Black_Scholes(self):
        t=self.time_frame
        n=len(t)
        dt=np.zeros((n,1))
        dt[0,0]=t[0,0]
        if n>1:
            for i in range(1,n): 
                dt[i,0]=t[i,0]-t[i-1,0]
                
        sigma=sqrt(np.sum(dt*self.vol**2)) #aggregating  all volatilities
        r=self.ir[n-1]
        T=self.time_frame[n-1]

        # Black-Scholes
        d1=(np.log(self.S0/self.K) + (r + 0.5*sigma**2)*T)/sigma #sigma already accounts for time
        d2=d1-sigma
        pv=self.K*np.exp(-r*T)
        price=norm.cdf(d1)*self.S0 - norm.cdf(d2)*pv #price of European call
        if not self.call:
            price=price-self.S0+pv #European put
        
        return price[0]
    
    def show(self):
        print('\n CASE 3')
        print('\nInitial data (dividends are not taken into account):')
        print('stock price S0= {0:6.5f}'.format(self.S0))
        print('strike price K= {0:6.5f}'.format(self.K))
        print('volatility sigma= {0:6.5f}'.format(np.mean(self.vol)))
        print('risk-free rate r= {0:6.5f}'.format(np.mean(self.ir)))
        print('maturity in years:',self.time_frame[-1])
        print('number of silumations for MC:',self.iterations)
        print(' ')

class Vanilla(ENGINE):
    def __init__(self,S0,sigma,r,K,time_frame,iterations,call):
        ENGINE.__init__(self,S0,sigma,r,K,time_frame,iterations,call)
        
    def payoff(self):   
        n=len(self.time_frame)
        path=ENGINE.montecarlo_path(self)
        c=path[n,0]-self.K
        pay_off=max([c,0]) if self.call else max([-c,0]) 
        
        return pay_off     
    
    def pricing(self,chart=False):
        final_prices=np.zeros((self.iterations,1))
        mov_avg=np.zeros((self.iterations,1))
        for i in range(0,iterations): 
            final_prices[i]=self.payoff()    
        mov_avg[0]=final_prices[0]
        for i in range(1,iterations): 
            mov_avg[i]=mov_avg[i-1]*i/(i+1) + final_prices[i]/(i+1)
        n=len(self.time_frame)
        mov_avg=np.exp(-self.ir[n-1]*self.time_frame[n-1])*mov_avg # discounting the moving average
        price=mov_avg[self.iterations-1] #price chosen as last iteration
        bucket=floor(np.log2(self.iterations)) #bucketing iterations using the integer of log2 of iterations
        mov_avg_bucket=np.zeros((bucket,1))
        for i in range(0,bucket): 
            mov_avg_bucket[i]=mov_avg[int(2**(i+1))]
        
        if chart:
            scale=np.array(range(1,bucket+1))
            fig=plt.figure()    
            ax=fig.add_subplot(1,1,1)  
            y=self.Black_Scholes()*np.ones((scale.shape))
            ax.plot(scale,y,'g--',label='VANILLA BLACK-SCHOLES')
            ax.scatter(scale,mov_avg_bucket,label='VANILLA MONTE CARLO')
            ax.set_xlabel('LOG2 OF NUMBER OF ITERATIONS')
            ax.set_ylabel('OPTION PRICE')
            ax.set_ylim([0.0,8.0])
            ax.set_title('VANILLA OPTIONS: call= {}'.format(self.call))
            ax.legend(loc='best') 
            plt.show()  
        
        return price[0]
      
class Asian(ENGINE):
    def __init__(self,S0,sigma,r,K,time_frame,iterations,call,setting,speed):
        ENGINE.__init__(self,S0,sigma,r,K,time_frame,iterations,call) 
        self.setting = setting
        self.call = call
        self.speed = speed
        print('PRICING ASIAN OPTION WITH:',setting)
        print('CALL = ',call)
        
    def payoff(self):   
        t=self.time_frame
        n=len(t)
        path=ENGINE.montecarlo_path(self)
        if self.speed==False: 
            c=np.mean(path[1:n+1,0])-self.K #taking the mean of all prices simulated up to n included
            pay_off=max([c,0]) if self.call else max([-c,0]) 
        if self.speed==True:
            dt=np.zeros((n,1))
            dt[0,0]=t[0,0]
            if n>1:
                for i in range(1,n): 
                    dt[i,0]=t[i,0]-t[i-1,0]
            sigma=sqrt(np.sum(dt*self.vol**2)) #aggregating  all volatilities
            r=self.ir[n-1]
            T=self.time_frame[n-1]
            if np.mean(path[1:n,0]) - K > 0.0: pay_off_1 =np.mean(path[1:n,0]) - K                           
            else: pay_off_1=0.0
            call=True
            optionSP = Vanilla(path[n,0],sigma,r,K,T/n,iterations,call)
            c = optionSP.Black_Scholes()/n
            
            pay_off_2=max([c,0]) if self.call else max([-c,0])
            pay_off=pay_off_1+pay_off_2
            
        return pay_off      
    
    def pricing(self,chart=False):
        final_prices=np.zeros((self.iterations,1))
        mov_avg=np.zeros((self.iterations,1))
        for i in range(0,iterations): 
            final_prices[i]=self.payoff()
        mov_avg[0]=final_prices[0]
        for i in range(1,iterations): 
            mov_avg[i]=mov_avg[i-1]*i/(i+1) + final_prices[i]/(i+1) 
        n=len(self.time_frame)
        mov_avg=np.exp(-self.ir[n-1]*self.time_frame[n-1])*mov_avg # discounting the moving average
        price=mov_avg[self.iterations-1] #price chosen as last iteration
        bucket=floor(np.log2(self.iterations))
        mov_avg_bucket=np.zeros((bucket,1))
        for i in range(0,bucket): 
            mov_avg_bucket[i]=mov_avg[int(2**(i+1))]
        
        if chart:
            scale=np.array(range(1,bucket+1))
            fig=plt.figure()    
            ax=fig.add_subplot(1,1,1)  
            y=self.Black_Scholes()*np.ones((scale.shape))
            ax.plot(scale,y,'g--',label='Black Scholes Vanilla')
            ax.scatter(scale,mov_avg_bucket,label='Montecarlo Asian')
            ax.set_xlabel('LOG2 OF NUMBER OF ITERATIONS')
            ax.set_ylabel('OPTION PRICE')
            ax.set_ylim([0.0,8.0])
            stl = self.setting + ', speed=' + str(self.speed)
            ax.set_title("ASIAN " +stl)
            ax.legend(loc='best') 
            plt.show()  
        
        return price[0]

    
class Barrier(ENGINE):
    def __init__(self,S0,sigma,r,K,time_frame,iterations,call,B,trigger,setting,different_barrier_time_frame,speed):
        ENGINE.__init__(self,S0,sigma,r,K,time_frame,iterations,call)  
        self.B=B
        self.trigger=trigger
        self.setting = setting
        self.different_barrier_time_frame = different_barrier_time_frame
        self.speed = speed
        self.call = call
        print('PRICING BARRIER OPTION',trigger,'with',setting)
        print('CALL = ',call)
        
    def payoff(self):   
        t=self.time_frame
        n=len(t)
        path=ENGINE.montecarlo_path(self)
        if self.speed==False:
            c=path[n,0]-self.K
            
            if different_barrier_time_frame == True:
                s = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19] #selecting only 0.05,0.15... up to 0.95
                path2 = path[s,0]
                path1 = path2.reshape((-1,1))
                
            if self.trigger in {'down-and-out','up-and-out'}:
                    pay_off=max([c,0]) if self.call else max([-c,0])
                    
                    if self.different_barrier_time_frame == False:
                       if (self.trigger=='down-and-out' and any(path[1:n,0] < B)) or (self.trigger=='up-and-out' and any(path[1:n,0] > B)):
                           pay_off=0.0                                                   
                    if self.different_barrier_time_frame == True:
                       if (self.trigger=='down-and-out' and any(path1[:,0] < B)) or (self.trigger=='up-and-out' and any(path1[:,0] > B)):
                           pay_off=0.0
                    
            elif self.trigger in {'down-and-in','up-and-in'}:  
                    pay_off=0.0
                    
                    if self.different_barrier_time_frame == False:
                        if (self.trigger=='down-and-in' and any(path[1:n,0] < B)) or (self.trigger=='up-and-in' and any(path[1:n,0] > B)):
                          pay_off=max([c,0]) if self.call else max([-c,0])       
                    if self.different_barrier_time_frame == True:
                        if (self.trigger=='down-and-in' and any(path1[1:n,0] < B)) or (self.trigger=='up-and-in' and any(path1[1:n,0] > B)):
                          pay_off=max([c,0]) if self.call else max([-c,0])       
       
        if self.speed==True:
            dt=np.zeros((n,1))
            dt[0,0]=t[0,0]
            if n>1:
                for i in range(1,n): 
                    dt[i,0]=t[i,0]-t[i-1,0]
            sigma=sqrt(np.sum(dt*self.vol**2)) #aggregating  all volatilities
            r=self.ir[n-1]
            T=self.time_frame[n-1]
            c=path[n-1,0]-self.K
            
            if different_barrier_time_frame == True:
                s = [1, 3, 5, 7, 9, 11, 13, 15, 17] #selecting only 0.05,0.15... up to 0.85 as last time frame will be calculated with BS
                path2 = path[s,0]
                path1 = path2.reshape((-1,1))
            
            if self.trigger in {'down-and-out','up-and-out'}:
                    pay_off_1=max([c,0]) if self.call else max([-c,0])
                    
                    if self.different_barrier_time_frame == False:
                       if (self.trigger=='down-and-out' and any(path[1:n-1,0] < B)) or (self.trigger=='up-and-out' and any(path[1:n-1,0] > B)):
                           pay_off_1=0.0                                                   
                    if self.different_barrier_time_frame == True:
                       if (self.trigger=='down-and-out' and any(path1[:,0] < B)) or (self.trigger=='up-and-out' and any(path1[:,0] > B)):
                        pay_off_1=0.0
                    
            elif self.trigger in {'down-and-in','up-and-in'}:  
                    pay_off_1=0.0
                    
                    if self.different_barrier_time_frame == False:
                        if (self.trigger=='down-and-in' and any(path[1:n-1,0] < B)) or (self.trigger=='up-and-in' and any(path[1:n-1,0] > B)):
                          pay_off_1=max([c,0]) if self.call else max([-c,0])       
                    if self.different_barrier_time_frame == True:
                        if (self.trigger=='down-and-in' and any(path1[1:n,0] < B)) or (self.trigger=='up-and-in' and any(path1[1:n,0] > B)):
                          pay_off_1=max([c,0]) if self.call else max([-c,0])       
            

            if pay_off_1 > 0.0:   
                
                call=True
                optionSP = Vanilla(path[n,0],sigma,r,K,T/n,iterations,call)
                c = optionSP.Black_Scholes()/n
            
                pay_off_2=max([c,0]) if self.call else max([-c,0])
                
            if pay_off_1==0.0:
                pay_off_2=0.0
                
            pay_off=pay_off_1+pay_off_2
        
        
        return pay_off         

    def pricing(self,chart=False):
        final_prices=np.zeros((self.iterations,1))
        mov_avg=np.zeros((self.iterations,1))
        for i in range(0,iterations): final_prices[i]=self.payoff()
        mov_avg[0]=final_prices[0]
        for i in range(1,iterations): mov_avg[i]=mov_avg[i-1]*i/(i+1) + final_prices[i]/(i+1) 
        n=len(self.time_frame)
        mov_avg=np.exp(-self.ir[n-1]*self.time_frame[n-1])*mov_avg # discounting the moving average
        price=mov_avg[self.iterations-1] #price chosen as last iteration
        bucket=floor(np.log2(self.iterations))
        mov_avg_bucket=np.zeros((bucket,1))
        for i in range(0,bucket): mov_avg_bucket[i]=mov_avg[int(2**(i+1))]
        
        if chart:
            scale=np.array(range(1,bucket+1))
            fig=plt.figure()    
            ax=fig.add_subplot(1,1,1)
            y=self.Black_Scholes()*np.ones((scale.shape))
            ax.plot(scale,y,'r--',label='Black Scholes Vanilla')
            ax.scatter(scale,mov_avg_bucket,label='MONTE CARLO BARRIER')
            ax.set_xlabel('LOG2 OF NUMBER OF ITERATIONS')
            ax.set_ylabel('OPTION PRICE/BARRIER PRICE')
            #BB=B*np.ones((scale.shape))
            #ax.plot(scale,BB,'-g',label='BARRIER')
            ax.legend(loc='best')
            stl = self.trigger + ' with ' + self.setting + ', speed=' + str(self.speed)
            ax.set_title("BARRIER " +stl)
            plt.show()  
        
        return price[0]


################################
#Inputs and results        
################################
        
#inputs    
iterations=100000
S0=100
K=103
T=1
r=0.05
sigma=0.1
B=80
chart=True

# pricing vanilla MC vs BS for 1yr maturity comparison calls and puts
time_frame_0=[1.0]

option_0=Vanilla(S0,sigma,r,K,time_frame_0,iterations,True)
BlackScholes_call=option_0.Black_Scholes()
MC_call=option_0.pricing(chart)
option_0.show()

option_0=Vanilla(S0,sigma,r,K,time_frame_0,iterations,False)
BlackScholes_put=option_0.Black_Scholes()
MC_put=option_0.pricing(chart)

print('Black-Scholes call= {0:6.5f}'.format(BlackScholes_call))
print('Black-Scholes put= {0:6.5f}\n'.format(BlackScholes_put))
print('Montecarlo Vanilla  call= {0:6.5f}'.format(MC_call))
print('Montecarlo Vanilla  put= {0:6.5f}\n'.format(MC_put))

# pricing Asian options for 1yr maturity under European execution

dates = 12 #monthly setting dates
intervals=dates+1
time_frame=np.linspace(0,1,intervals) #to create sequencies in array
time_frame_1=time_frame[1:intervals]

option_1=Asian(S0,sigma,r,K,time_frame_1,iterations,True, 'monthly setting dates',False)
price_1=option_1.pricing(chart)

print('ANSWER 1: price = {0:6.5f}'.format(price_1))
print(' ')

optionSPEED1=Asian(S0,sigma,r,K,time_frame_1,iterations,True, 'monthly setting dates',True)
priceSPEED1=optionSPEED1.pricing(chart)
print('ANSWER 1 SPEED: price = {0:6.5f}'.format(priceSPEED1))
print(' ')


dates = 4 #quarterly setting dates
intervals=dates+1
time_frame=np.linspace(0,1,intervals)
time_frame_2=time_frame[1:intervals]

option_2=Asian(S0,sigma,r,K,time_frame_2,iterations,True, 'quarterly setting dates',False)
price_2=option_2.pricing(chart)
print('ANSWER 2: price= {0:6.5f}\n'.format(price_2))
print(' ')

optionSPEED2=Asian(S0,sigma,r,K,time_frame_2,iterations,True, 'quarterly setting dates',True)
priceSPEED2=optionSPEED2.pricing(chart)
print('ANSWER 2 SPEED: price = {0:6.5f}'.format(priceSPEED2))
print(' ')

dates = 52
intervals=dates+1
time_frame=np.linspace(0,1,intervals);
time_frame_3=time_frame[1:intervals]

option_3=Asian(S0,sigma,r,K,time_frame_3,iterations,True, 'weekly setting dates',False)
price_3=option_3.pricing(chart)
print('ANSWER 3: price= {0:6.5f}\n'.format(price_3))
print(' ')

optionSPEED3=Asian(S0,sigma,r,K,time_frame_3,iterations,True, 'weekly setting dates',True)
priceSPEED3=optionSPEED3.pricing(chart)
print('ANSWER 3 SPEED: price = {0:6.5f}'.format(priceSPEED3))
print(' ')


print('CONSIDERATIONS ASIANS:')
print('(Dividends were not taken into account)')
print('All Asian options are cheaper than Vanillas: BS and MC')
print('Asian option prices decrease as frequency of setting dates increases.')
print('Increasing the frequency of setting dates, the variance of payoffs reduces and convergence speeds up.')
print('Regarding SPEED (question on speeding up the convergence), for the Asian call option with strike K, I considered ')
print('a contract with monthly setting where the mean of the underline is computed up to the penultimate month (i.e. second last). At this date  ')
print('the option becomes a vanilla option or is zero.')
print('Accordig to the book: THE CONCEPTS AND PRACTICE OF MATHEMATICAL FINANCE of of M. S. JOSHI, the option pay-off can be written as')     
print('                   1/n max (Stn - (n*K - Stn-1),0)')      
print('in such a way that the Asian call option  has become a vanilla call with strike = (nK - Stn-1). ')
print('This means that there is no need to simulate the final step, and the payoff at time t, can be replaced with the Black-Scholes')
print('value of the option at time tn-1, for the relevant strike. From my speed results with this method ')
print('asian calls and asian speed call prices become very close as the frequency of setting dates increases together with the rise in simulations from 100K to 500K.') 
print(' ')

# pricing Barrier options for 1yr maturity

different_barrier_time_frame = False

option_4=Barrier(S0,sigma,r,K,time_frame_1,iterations,True,B,'down-and-out', 'monthly setting dates', different_barrier_time_frame,False)
price_4=option_4.pricing(chart)
print('ANSWER 4: price= {0:6.5f}'.format(price_4))
print('Black Scholes Vanilla  Call = ',BlackScholes_call)
print(' ')

option4SPEED=Barrier(S0,sigma,r,K,time_frame_1,iterations,True,B,'down-and-out', 'monthly setting dates', different_barrier_time_frame,True)
price4SPEED=option4SPEED.pricing(chart)
print('ANSWER 4 SPEED: price= {0:6.5f}\n'.format(price4SPEED))
print(' ')

option_5=Barrier(S0,sigma,r,K,time_frame_1,iterations,True,B,'down-and-in', 'monthly setting dates', different_barrier_time_frame,False)
price_5=option_5.pricing(chart)
print('ANSWER 5: price= {0:6.5f}'.format(price_5))
print('Black Scholes Vanilla  Call = ',BlackScholes_call)
print(' ')

option5SPEED=Barrier(S0,sigma,r,K,time_frame_1,iterations,True,B,'down-and-in', 'monthly setting dates', different_barrier_time_frame,True)
price5SPEED=option5SPEED.pricing(chart)
print('ANSWER 5 SPEED: price= {0:6.5f}\n'.format(price5SPEED))
print(' ')


call=False
option_6=Barrier(S0,sigma,r,K,time_frame_1,iterations,call,B,'down-and-out', 'monthly setting dates',different_barrier_time_frame,False)
price_6=option_6.pricing(chart)
print('ANSWER 6: price= {0:6.5f}'.format(price_6))
print('Black Scholes Vanilla  put = ',BlackScholes_put)
print(' ')

option6SPEED=Barrier(S0,sigma,r,K,time_frame_1,iterations,call,B,'down-and-out', 'monthly setting dates', different_barrier_time_frame,True)
price6SPEED=option6SPEED.pricing(chart)
print('ANSWER 6 SPEED: price= {0:6.5f}\n'.format(price6SPEED))
print(' ')


different_barrier_time_frame = True
B=120
dates=20
intervals=dates+1
time_frame=np.linspace(0,1,intervals);
time_frame_4=time_frame[1:intervals]

option_7=Barrier(S0,sigma,r,K,time_frame_4,iterations,call,B,'down-and-out', '10 different barrier time_frame', different_barrier_time_frame,False)
price_7=option_7.pricing(chart)
print('ANSWER 7: price= {0:6.5f}'.format(price_7))
print('Black Scholes Vanilla  put = ',BlackScholes_put)
print(' ')

option7SPEED=Barrier(S0,sigma,r,K,time_frame_4,iterations,call,B,'down-and-out','10 different barrier time_frame', different_barrier_time_frame,True)
price7SPEED=option7SPEED.pricing(chart)
print('ANSWER 7 SPEED: price= {0:6.5f}\n'.format(price7SPEED))
print(' ')

print('CONSIDERATIONS BARRIERS:')
print('answer 4: Barrier Call price down-and-out is lower or equal than Vanilla call (if large number of simulations implemented)')
print('answer 5: Barrier Call price down-and-in is zero as the probability of S to decrease by 20 units and go back up by 23 is approx zero (if large numb of simulations implemented)')
print('answer 6: Barrier Put price down-and-out is lower or equal than Vanilla put (if large numb of simulations implemented)')
print('answer 7: with B=120, the Barrier Put price down-and-out is always zero as S is always below 120.')
print('Convergence is faster when incresing the frequency of setting dates. ')
print('Regarding SPEED (speeding up the convergence), For the discrete barrier option, at the last barrier date either the option') 
print('has knocked out, in which case the option is valueless, or it cannot any longer knock out in which case it has become a vanilla call option,') 
print('and we can substitute the Black-Scholes value for the final pay-off. From my speed results, Barrier speed prices are on average higher than Barrier')
print('option prices and lower than BS prices.') 
print('Overall time taken to run is approx 2.8 mins with 100K simulations and approx 13.7 mins with 500k sims.')
print('Speed pricing method didnt really improve in computational time respect to standard pricing of Asians and Barriers.') 
print(' ')
