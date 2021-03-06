# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 00:40:12 2020

@author: timot
"""
from cvxopt.modeling import op, dot,variable, max, matrix, solvers
import numpy as np
import matplotlib.pyplot as plt
import math
def solar_data():
    #Read solar data from csv file
    capacity_factor=[]
    import csv
    with open('pv_38_2018.csv',newline='') as csvfile:
        raw_solar_data=csv.reader(csvfile,delimiter=',')
        line = 0
        for row in raw_solar_data:
            capacity_factor.append(float(row[2]))
    #Make hourly solar data to half hourly by taking average between two data point
    capacity_factor_half_hour=[0]
    for hour in range(len(capacity_factor)):
        if hour<len(capacity_factor)-1:
            approx=(capacity_factor[hour]+capacity_factor[hour+1])*0.5  #Average of hourly data in front and behind
            capacity_factor_half_hour+=[capacity_factor[hour]*0.5,approx*0.5]   #x0.5 as dt is half hour
    capacity_factor_half_hour.append(capacity_factor[-1])
    return np.array(capacity_factor_half_hour)

def solar_data_flat():
    capacity_factor=[]
    import csv
    with open('pv_0_2018.csv',newline='') as csvfile:
        raw_solar_data=csv.reader(csvfile,delimiter=',')
        line = 0
        for row in raw_solar_data:
            capacity_factor.append(float(row[2]))
    #Make hourly solar data to half hourly by taking average between two data point
    capacity_factor_half_hour=[0]
    for hour in range(len(capacity_factor)):
        if hour<len(capacity_factor)-1:
            approx=(capacity_factor[hour]+capacity_factor[hour+1])*0.5  #Average of hourly data in front and behind
            capacity_factor_half_hour+=[capacity_factor[hour]*0.5,approx*0.5]   #x0.5 as dt is half hour
    capacity_factor_half_hour.append(capacity_factor[-1])
    return np.array(capacity_factor_half_hour)

def solar_data_10():
    import csv
    with open('solar_ouput_2014_europe_10.csv',newline='') as csvfile:
        raw_10=csv.reader(csvfile,delimiter=',')
        for line in raw_10:
           capacity_factor_10=[float(h) for h in line]
    capacity_factor_half_hour_10=[0]
    for hour in range(len(capacity_factor_10)):
        if hour<len(capacity_factor_10)-1:
            approx=(capacity_factor_10[hour]+capacity_factor_10[hour+1])*0.5  #Average of hourly data in front and behind
            capacity_factor_half_hour_10+=[capacity_factor_10[hour]*0.5,approx*0.5]   #x0.5 as dt is half hour
    capacity_factor_half_hour_10.append(capacity_factor_10[-1])
    capacity_factor_half_hour_10=np.tile(capacity_factor_half_hour_10,3)
    return np.array(capacity_factor_half_hour_10)

def residential():
    village_annual_demand=11.88e6
    profile_demand=np.zeros(365*48)
    t=0
    import csv
    with open('residential.csv',newline='') as csvfile:
        raw_residential=csv.reader(csvfile,delimiter=',')
        for row in raw_residential:
            for item in row:
                profile_demand[t]=float(item)
                t+=1
    sum_profile_demand=sum(profile_demand)
    scaled_profile_demand=profile_demand/sum_profile_demand*village_annual_demand
#    plt.plot(list(range(len(scaled_profile_demand))),scaled_profile_demand,'-')
    return(scaled_profile_demand)
            

def load_heat_data():
    #Read degree day data from csv file
    #Use shape of degree day curve, scale to estimated heating demand
    import csv
    degree_day=[]
    village_annual_heat_demand=(88000*3+231600*2)*15
    with open('dd2018.csv',newline='') as csvfile:
        raw_heat_demand_data=csv.reader(csvfile,delimiter=',')
        #Column 3 = HDD 10.5C, Column 4 = HDD 15.5C, Column 5 = HDD 18.5C, starting from line 1
        line=0
        column=3
        for row in raw_heat_demand_data:            
            degree_day.append(float(row[column]))
            line+=1
    #Make daily data to half hourly by linear approximating middle values
    half_hourly_demand=np.array([])
    linear_list=np.array(range(48))/48
    for day in range(len(degree_day)):
        if day<len(degree_day)-1:
            day_linear=degree_day[day]+(degree_day[day+1]-degree_day[day])*linear_list
            half_hourly_demand=np.append(half_hourly_demand,day_linear)
        else:
            half_hourly_demand=np.append(half_hourly_demand,[degree_day[day]]*47)
    half_hourly_demand=np.append(half_hourly_demand,half_hourly_demand[len(half_hourly_demand)-1])
    sum_half_hourly_demand=sum(half_hourly_demand)
    scaled_heat_demand=half_hourly_demand/sum_half_hourly_demand*village_annual_heat_demand
    return(scaled_heat_demand)
    
def load_sciencepark():
    #Read average electricity consumption of CIE science park
    #Average of 2017 and 2018, unit: kWh/30min
    import csv
    CIE_demand=np.zeros(365*48)
    count=0
    science_park_demand=354748*44   #Estimated using ratio of building area
    with open('science_park.csv',newline='') as csvfile:
        raw_sciencepark=csv.reader(csvfile,delimiter=',')
        for row in raw_sciencepark: #Each row is a day
            for t in row:           #Each t repersent a half hour period demand
                CIE_demand[count]=float(t)
                count+=1
    sum_CIE_demand=sum(CIE_demand)
    scaled_science_park_demand=CIE_demand/sum_CIE_demand*science_park_demand
    return(scaled_science_park_demand)

def hot_water():
    import csv
    with open('hot water.csv',newline='') as csvfile:
        raw_hot_water=csv.reader(csvfile,delimiter=',')
        i=1
        for row in raw_hot_water:
            if i==1:
                daily_hot_water=row
            if i==2:
                hourly_hot_water=row
            i+=1
    daily_hot_water=np.array([float(d) for d in daily_hot_water])
    del hourly_hot_water[24:365]
    hourly_hot_water=np.array([float(h) for h in hourly_hot_water])
    half_hour_hot_water=[]
    for h in range(len(hourly_hot_water)-1):
        half_hour_hot_water.append(hourly_hot_water[h])
        half_hour_hot_water.append((hourly_hot_water[h]+hourly_hot_water[h+1])/2)
    half_hour_hot_water.append(hourly_hot_water[-1])
    half_hour_hot_water.append((hourly_hot_water[-1]+hourly_hot_water[0])/2)
    half_hour_hot_water=np.array(half_hour_hot_water)
    year_hot_water=np.array([])
    for d in daily_hot_water:
        year_hot_water=np.append(year_hot_water,d*half_hour_hot_water)
    scaled_year_hot_water=year_hot_water/sum(year_hot_water)*3.528e6
    return scaled_year_hot_water
    
def price():
    buy_price=np.zeros(365*48)
    sell_price=np.zeros(365*48)
    count=0
    import csv
    with open('price.csv',newline='') as csvfile:
        raw_price=csv.reader(csvfile,delimiter=',')
        for row in raw_price:
            buy_price[count]=max(0.00001,float(row[0]))
            sell_price[count]=max(0.00001,float(row[1]))
            count+=1
    return [buy_price,sell_price]

def market(buy,sell_price,buy_price):
    cost=0
    t=0
    for energy in buy:
        if energy <0:
            price=energy*sell_price[t]
        else:
            price=energy*buy_price[t]
        cost+=price
        t+=1
    return cost

def energy_system(pv,load,storage):
    total_output=np.array([0]*len(pv[0]['output']),dtype=float)
    for pvid in pv:
        total_output+=pv[pvid]['output']
    total_load=np.array([0]*len(load[0]),dtype=float)
    for loadid in load:
        total_load+=np.array(load[loadid])
    excess=total_output-total_load                  #Calculate excess power before using storage
    storage_time=0                                  #At time 0, storage has now charge. Storage records the charge avaliable for this time slot
    buy=[]                                          #Power bought from market, negative means sold
    balancing=[]                                    #Record power taken or given by storage to meet excess power, after accounting efficiency
    for dexcess in excess:                          #dexcess is the excess at this time slot
        balancing.append(0)
        for storageid in storage:                   #run through all storage facilities
        #charge power is the amount charged to storage
            if dexcess>=0:                          #pv > load, storage charging
                charge_power=min(dexcess*storage[storageid]['efficiency'],storage[storageid]['capacity']-storage[storageid]['stored'][storage_time],storage[storageid]['power'])    #charge power is the lesser of dexcess or remaining space of storage 
                dexcess-=charge_power/storage[storageid]['efficiency']      #amount of power taken from dexcess, after accounting efficiency
                balancing[storage_time]-=charge_power/storage[storageid]['efficiency']
            else:                                   #pv < load, storage discharging
                charge_power=max(dexcess/storage[storageid]['efficiency'],-storage[storageid]['stored'][storage_time],-storage[storageid]['power'])  #charge power is the less negative of dexcess or remaining charge
                dexcess-=charge_power*storage[storageid]['efficiency']      #amount of power given to dexcess, after accounting efficiency
                balancing[storage_time]-=charge_power*storage[storageid]['efficiency']
            storage[storageid]['stored'].append(storage[storageid]['stored'][storage_time]+charge_power)
        storage_time+=1
        buy.append(-dexcess)
    return [buy,total_output,total_load,balancing]

def energy_system_conditioal(pv,load,storage,buy_price,sell_price,period):      #period indicates which day of year the energy system is run
    total_output=np.array([0]*len(pv[0]['output']),dtype=float)
    for pvid in pv:
        total_output+=pv[pvid]['output']
    fix_load=np.array(load[1]+load[3])        #load which assmued to be accurately predicted, which is heat load
    float_load=np.array(load[0])+np.array(load[2])  #Load which cannot be predicited accurately
    total_load=np.array([0]*len(load[0]),dtype=float)
    for loadid in load:
        total_load+=np.array(load[loadid])
    excess=total_output-fix_load-float_load
    storage_time=0                                  #At time 0, storage has now charge. Storage records the charge avaliable for this time slot
    buy=[]                                          #Power bought from market, negative means sold
    balancing=[]                                    #Record power taken or given by storage to meet excess power, after accounting efficiency
    for day in period:
        float_load_est=float_load[48*(day-7):48*(day-5)]
        max_sell_price=np.amax(sell_price[48*day:48*day+47])
        max_sell_price_t=np.argmax(sell_price[48*day:48*day+47]) #Find the index of maximum sell price of the day
        max_sell_price_t_list=np.flip(np.argsort(sell_price[48*day:48*day+47]))  #List of times with desecding sell price
#        sunrise=0
#        for sun in total_output[48*(day+1):]:       #Find the sunrise of next day
#            if sun > 0:
#                break
#            sunrise+=1
        save=max(0,-sum(total_output[day*48+max_sell_price_t:day*48+38])+sum(float_load_est[max_sell_price_t:38])+sum(fix_load[day*48+max_sell_price_t:day*48+38]))            #Maximum price always occur between t=31 and t=38, this sum all estimated load between maximum price and 19:00
        max_buy_price=np.amax(buy_price[day*48+39:day*48+78])    #Find maximum buy price between 19:00 of today and 16:00 of tomorrow
#        print(max_sell_price-max_buy_price)
        for t in range(48):
            dexcess=excess[day*48+t]
            balancing.append(0)
            for storageid in storage:                   #run through all storage facilities               
                if t in max_sell_price_t_list[0:4]:     #Decide how many time periods will be used for forced export
#                if 31<=t<=38 and dexcess>=0:
#                if max(max_sell_price_t,31)<=t<=38 and dexcess>=0:    #Sell everything when max_sell_price>max_buy_price
#                if sell_price[day*48+t]>=max_buy_price and 31<=t<=38 and dexcess>=0:
                    charge_power=-min(storage[storageid]['power'],storage[storageid]['stored'][storage_time],50000-dexcess)
#                    print(charge_power)
                    dexcess-=charge_power*storage[storageid]['efficiency']      #amount of power taken from dexcess, after accounting efficiency
                    balancing[storage_time]-=charge_power*storage[storageid]['efficiency'] 
                else:
                    if dexcess>=0:                          #pv > load, storage charging
                        charge_power=min(dexcess*storage[storageid]['efficiency'],storage[storageid]['capacity']-storage[storageid]['stored'][storage_time],storage[storageid]['power'])    #charge power is the lesser of dexcess or remaining space of storage 
                        dexcess-=charge_power/storage[storageid]['efficiency']      #amount of power taken from dexcess, after accounting efficiency
                        balancing[storage_time]-=charge_power/storage[storageid]['efficiency']
                    else:                                   #pv < load, storage discharging
                        charge_power=max(dexcess/storage[storageid]['efficiency'],-storage[storageid]['stored'][storage_time],-storage[storageid]['power'])  #charge power is the less negative of dexcess or remaining charge
                        dexcess-=charge_power*storage[storageid]['efficiency']      #amount of power given to dexcess, after accounting efficiency
                        balancing[storage_time]-=charge_power*storage[storageid]['efficiency']
                storage[storageid]['stored'].append(storage[storageid]['stored'][storage_time]+charge_power)
            storage_time+=1
            buy.append(-dexcess)
#    print(max(buy, key=abs))
    return [buy,total_output,total_load,balancing]

def create_pv(pv,capacity,initial_cost,capacity_factor):
    #add new pv assest to pv dictionary
    pvid=len(pv)
    pv[pvid]={}
    pv[pvid]['capacity']=capacity               #in kWh
    pv[pvid]['initial_cost']=initial_cost       #in pounds
    pv[pvid]['output']=np.array(capacity_factor,dtype=float)*capacity #output = capacity x capacity factor, which gives power in kW
    return pv

def create_load(load,power_use):
    #add new load assest to load dictionary
    loadid=len(load)
    load[loadid]=np.array(power_use,dtype=float)
    return load

def create_storage(storage,capacity,power,efficiency,initial_cost):
    #add new storage to storage dictionary
    storageid=len(storage)
    storage[storageid]={}
    storage[storageid]['capacity']=capacity         #capacity of storage in kWh
    storage[storageid]['power']=power               #maximum input or output power of storage, after calculating efficiency
    storage[storageid]['efficiency']=efficiency     #efficiency of storage in both input or output
    storage[storageid]['initial_cost']=initial_cost #in pounds
    storage[storageid]['stored']=[0]                #start with empty storage
    return storage

def cvxopt(storage_size_list):
    cost_list=[]
    for storage_max in storage_size_list:
        storage_max=float(storage_max)
        storage_power=storage_max/4
        [buy_price,sell_price]=price()
        
        pvl=236000*0.9*0.2*0.9*solar_data()+88000*0.9*0.2*0.9*solar_data_flat()
        fix_load=load_heat_data()+hot_water()    #load which assmued to be accurately predicted, which is heat load
        float_load=residential()+load_sciencepark()     #Load which cannot be predicited accurately, so predicted by data of a week ago
        use_load=fix_load+np.roll(float_load,7*48)   #Estimated total load to be used for cvxopt
        '''
        #use_load=load_heat_data()+hot_water()+residential()+load_sciencepark()
        
        eff=math.sqrt(0.85)
        start=200
        end=207
        duration=(end-start)*48
        day_i=list(range(start*48,end*48))
        
        
        cml=([-1.]+[0.]*(duration-1)+[1.])*(duration-1)+[-1.]
        #cml=([-math.sqrt(0.85)]+[0.]*(duration-1)+[math.sqrt(0.85)])*(duration-1)+[-math.sqrt(0.85)]
        #cml=([-0.85]+[0.]*(duration-1)+[0.85])*(duration-1)+[-0.85]
        cm=matrix(cml,(duration,duration))
        
        pv=matrix(pvl[day_i],(duration,1))
        load=matrix(use_load[day_i],(duration,1))
        bp=matrix(buy_price[day_i],(duration,1))
        sp=matrix(sell_price[day_i],(duration,1))
        
        storage_max=100000.
        zero=matrix([0.]*duration,(duration,1))
        emax=matrix([storage_max]*duration,(duration,1))  #maximum storage
        pmax=matrix([50.e3]*duration,(duration,1))  #maximum power to grid
        charge_pmax=matrix([25000.]*duration,(duration,1))
        effm=matrix([eff]*duration,(duration,1))
        ieffm=matrix([1/eff]*duration,(duration,1))
        #discharge_pmax=matrix([-25000.]*duration,(duration,1))
        
        e=variable(duration)  #Stored energy
        c=variable(duration)  #Charging energy 
        d=variable(duration)  #Discharging energy 
        b=variable(duration)  #Buy
        s=variable(duration)  #Sell 
        
        i1=(b>=zero)
        i2=(s>=zero)
        i3=(e>=zero)
        i4=(e<=emax)
        i5=(b<=pmax)
        i6=(s<=pmax)
        i7=(c<=charge_pmax)
        i8=(d<=charge_pmax)
        i9=(c>=zero)
        i10=(d>=zero)
        
        e1=(c/eff-d*eff+load-pv==b-s)
        e2=(e[0]==matrix([0.]))
        e3=(c-d==cm*e)
        
        ob=dot(b,bp)-dot(s,sp)
        
        lp=op(ob,[i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,e1,e2,e3])
        solvers.options['show_progress'] = True
        lp.solve()
        '''
        
        eff=math.sqrt(0.85)
        start=0
        end=365
        duration=(end-start)*48
        day_i=list(range(start*48,end*48))
        cvxopt_balancing=[]
        cvxopt_buy=np.array([])     #Record power traded with grid, positive = import
        cvxopt_storage=np.array([])     #Record amount of stored energy
        day_cost=0
        
        for day in range(start,end):
            time_index=list(range(day*48,day*48+48))
            cml=([-1.]+[0.]*(48-1)+[1.])*(48-1)+[-1.]
            #cml=([-math.sqrt(0.85)]+[0.]*(duration-1)+[math.sqrt(0.85)])*(duration-1)+[-math.sqrt(0.85)]
            #cml=([-0.85]+[0.]*(duration-1)+[0.85])*(duration-1)+[-0.85]
            cm=matrix(cml,(48,48))
            
            pv=matrix(pvl[time_index],(48,1))
            load=matrix(use_load[time_index],(48,1))
            bp=matrix(buy_price[time_index],(48,1))
            sp=matrix(sell_price[time_index],(48,1))
            
            zero=matrix([0.]*48,(48,1))
            emax=matrix([storage_max]*48,(48,1))  #maximum storage
            pmax=matrix([50.e3]*48,(48,1))  #maximum power to grid
            charge_pmax=matrix([storage_power]*48,(48,1))
            #discharge_pmax=matrix([-25000.]*duration,(duration,1))
            
            e=variable(48)  #Stored energy
            c=variable(48)  #Charging energy 
            d=variable(48)  #Discharging energy 
            b=variable(48)  #Buy
            s=variable(48)  #Sell 
            
            i1=(b>=zero)
            i2=(s>=zero)
            i3=(e>=zero)
            i4=(e<=emax)
            i5=(b<=pmax)
            i6=(s<=pmax)
            i7=(c<=charge_pmax)
            i8=(d<=charge_pmax)
            i9=(c>=zero)
            i10=(d>=zero)
            i11=(c[47]-d[47]+e[47]>=matrix([0.]))
            i12=(c[47]-d[47]+e[47]<=matrix([storage_max]))
            
            e1=(c/eff-d*eff+load-pv==b-s)
            if day == start:
                e2=(e[0]==matrix([0.]))
            else:
                next_storage=cvxopt_storage[-1]-cvxopt_balancing[-1]
                e2=(e[0]==matrix(next_storage))
            e3=(c-d==cm*e)
            
            ob=dot(b,bp)-dot(s,sp)
            
            lp=op(ob,[i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,e1,e2,e3])
            solvers.options['show_progress'] = False
            lp.solve()
            day_cost+=lp.objective.value()[0]
        
            for t in range(0,48):
                cvxopt_balancing.append(d.value[t]-c.value[t])
                cvxopt_buy=np.append(cvxopt_buy,b.value[t]-s.value[t])
                cvxopt_storage=np.append(cvxopt_storage,e.value[t])
        #print(b.value[47]-s.value[47])
        #print(c.value[47]*eff-d.value[47]/eff+e.value[47])
        
#        print(day_cost)
        
        buy=[]
        charge_power_l=[]
        balancing_l=[]
        storage=np.array([e.value[0]])     #Initial charge in storage decided by cvxopt
        excess=(pvl-fix_load-float_load)[day_i]
        for t in range(duration):
            if cvxopt_balancing[t]>0:      #Storage discharge
                if cvxopt_balancing[t]>storage[t]:      #CVXOPT wants more discharge than currently stored
        #            balancing=-storage[t]*eff            #Storage discharge all stored
                    charge_power=-storage[t]
        #            print('a')
                else:
        #            balancing=-cvxopt_balancing[t]*eff   #Do as CVXOPT wants
                    charge_power=-cvxopt_balancing[t]
        #            print('b')
            else:                           #Storage charge
                if cvxopt_balancing[t]>storage_max-storage[t]:      #CVXOPT wants to charge more than remaining capacity
        #            balancing=(storage_max-storage[t])/eff             #Charge by remaining capacity
                    charge_power=storage_max-storage[t]
        #            print('c')
                else:
        #            balancing=-cvxopt_balancing[t]/eff   #Do as CVXOPT wants
                    charge_power=-cvxopt_balancing[t]
        #            print('d')
            if charge_power>0:
                balancing=charge_power/eff
            else:
                balancing=charge_power*eff
            buy.append(-excess[t]+balancing)
            balancing_l.append(balancing)
            charge_power_l.append(-charge_power)
            storage=np.append(storage,storage[t]+charge_power)
        #    print(t,excess[t],charge_power,cvxopt_balancing[t])
        #    print(buy[t],cvxopt_buy[t])
        #    print(storage[t],cvxopt_storage[t])
        running_cost=market(buy,sell_price[day_i],buy_price[day_i])
#        print(running_cost)
        cost_list.append(running_cost)
        print(max(max(buy-cvxopt_buy),-min(buy-cvxopt_buy)))
        #print(sell_price[day_i])
        #print(buy_price[day_i])
        
        #fig,ax=plt.subplots()
        #ax.plot(list(range(0,duration)),(fix_load+float_load)[day_i],'-r',label='actual')
        #ax.plot(list(range(0,duration)),use_load[day_i],'-b',label='estimate')
        #ax.step(list(range(0,duration)),buy,'-r',label='actual')
        #ax.step(list(range(0,duration)),cvxopt_buy,'-b',label='estimate')
        #ax.step(list(range(0,duration)),charge_power_l,'-r',label='actual')
        #ax.step(list(range(0,duration)),cvxopt_balancing,'-b',label='estimate')
        #ax.step(list(range(0,duration+1)),storage,'-b',label='estimate')
        #fig.legend()
    return cost_list



storage_size_list=np.array(range(0,11))*10000
cvxopt_cost=cvxopt(storage_size_list)
print(cvxopt_cost)
