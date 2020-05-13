# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:43:05 2019

@author: Timothy Tam
"""

#import timeit
#
#code_time="""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import math

#dictionaries for storing information of pv, load, storage
pv={}
load={}
storage={}

def solar_data():
    #Read solar data from csv file
    capacity_factor=[]
    import csv
#    with open('pv_38.csv',newline='') as csvfile:
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
#    with open('pv_0.csv',newline='') as csvfile:
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
    capacity_factor=[]
    import csv
#    with open('pv_10.csv',newline='') as csvfile:
    with open('pv_10_2018.csv',newline='') as csvfile:
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

def car_charging():
    import csv
    car_charging_demand=np.zeros(365*48)
    count=0
    with open('car_charging.csv',newline='') as csvfile:
        raw_car_charging=csv.reader(csvfile,delimiter=',')
        for row in raw_car_charging: #Each row is a day
            for t in row:           #Each t repersent a half hour period demand
                car_charging_demand[count]=float(t)
                count+=1
    car_charging_demand=car_charging_demand/30
    return(car_charging_demand)

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
            buy_price[count]=row[0]
            sell_price[count]=row[1]
            count+=1
    return [buy_price,sell_price]
        
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
    total_load=np.array([0]*len(load[0]),dtype=float)
    for loadid in load:
        total_load+=np.array(load[loadid])
    opt_n=[0,6,7,8,8,12,11,12,9,9,1,0]              #Optimum value of n for each month
    excess=total_output-total_load
    storage_time=0                                  #At time 0, storage has now charge. Storage records the charge avaliable for this time slot
    buy=[]                                          #Power bought from market, negative means sold
    balancing=[]                                    #Record power taken or given by storage to meet excess power, after accounting efficiency
#    print(period)
    for day in period:
#        float_load_est=float_load[48*(day-7):48*(day-5)]
#        max_sell_price=np.amax(sell_price[48*day:48*day+47])
#        max_sell_price_t=np.argmax(sell_price[48*day:48*day+47]) #Find the index of maximum sell price of the day
        max_sell_price_t_list=np.flip(np.argsort(sell_price[48*day:48*day+47]))  #List of times with desecding sell price
#        sunrise=0
#        for sun in total_output[48*(day+1):]:       #Find the sunrise of next day
#            if sun > 0:
#                break
#            sunrise+=1
#        save=max(0,-sum(total_output[day*48+max_sell_price_t:day*48+38])+sum(float_load_est[max_sell_price_t:38])+sum(fix_load[day*48+max_sell_price_t:day*48+38]))            #Maximum price always occur between t=31 and t=38, this sum all estimated load between maximum price and 19:00
#        max_buy_price=np.amax(buy_price[day*48+39:day*48+78])    #Find maximum buy price between 19:00 of today and 16:00 of tomorrow
#        print(max_sell_price-max_buy_price)
        month=int(day/(365/12))
        n=opt_n[month]
        for t in range(48):
            dexcess=excess[day*48+t]
            balancing.append(0)
            for storageid in storage:                   #run through all storage facilities               
                if t in max_sell_price_t_list[0:6]:     #Decide how many time periods will be used for forced export
#                if 31<=t<=38 and dexcess>=0:
#                if max_sell_price_t==t:    #Sell everything when max_sell_price>max_buy_price
#                if sell_price[t]>=max_buy_price and 31<=t<=38:
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

def plot_demand(total_output,total_load,balancing):
    year_output=total_output
    year_load=total_load
    total_energy_production=sum(year_output)
    total_energy_consumption=sum(year_load)
    print('Total energy production is ',total_energy_production,'kWh Total energy consumption is ',total_energy_consumption,'kWh')
#    time_list=list(range(len(balancing)))
    time_list=pd.date_range(start='2018-07-09',end='2018-07-12',periods=len(year_load))
    year_balancing=np.array(balancing)
    labels=['total output','storage operation']
    fig,ax=plt.subplots()
    fmt=mdates.DateFormatter('%H:%M ')
    ax.xaxis.set_major_formatter(fmt)
#    p1=ax.stackplot(time_list,year_output/1000*2,year_balancing/1000*2,labels=labels)
#    p2=ax.plot(time_list,year_load/1000*2,'-k',label='total load')
    p1=ax.step(time_list,total_output/500,'-r',label='PV generation')
    p2=ax.step(time_list,total_load/500,'-k',label='demand')
    p3=ax.fill_between(time_list,0,(total_output+balancing)/500,step='pre',color='y',label='system output')
    ax.set_xlim([time_list[0],time_list[-1]])
    ax.set_ylim([0,55])
    plt.title('Force Discharge during 6 Highest Export Price')
    plt.ylabel('power (MW)')
    plt.xlabel('time')
    fig.legend(loc='upper center', bbox_to_anchor=(0.76, 0.9), ncol=1)
#    plt.grid()
    plt.savefig('conditional 1.png',dpi=1200)

def plot_average(total_output,total_load,balancing):
    fig,ax=plt.subplots()
    t_list=np.array(range(49))/2
    average_output=day_average(total_output)*2/1000
    average_load=day_average(total_load)*2/1000
    average_balancing=day_average(balancing)*2/1000
    p1=ax.step(t_list,average_output,'-r',label='PV generation')
    p2=ax.step(t_list,average_load,'-k',label='demand')
#    labels=['average output','storage operation']
#    p3=ax.stackplot(t_list,average_output,average_balancing,labels=labels,step='pre')
    p3=ax.fill_between(t_list,0,average_output+average_balancing,step='pre',color='y',label='system output')
    ax.set_xlim([0,24])
    ax.set_ylim([0,25])
    plt.xticks(np.array(range(9))*3,['00:00','03:00','06:00','09:00','12:00','15:00','18:00','21:00','00:00'])
    plt.ylabel('power (MW)')
    plt.xlabel('time')
    plt.title('Average Power in Simple System of 2018')
    fig.legend(loc='upper center', bbox_to_anchor=(0.76, 0.9), ncol=1)
#    plt.grid()
    plt.savefig('2018 average energy.png',dpi=600)

def day_average(l):
    average_l=np.zeros(48)
    for day in range(0,365):
        average_l+=l[48*day:48*(day+1)]
    average_l=average_l/365
    average_l=np.append(average_l[0],average_l)
    return average_l

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

def captial_cost(pv,storage):
    cost=0
    for pvid in pv:
        cost+=pv[pvid]['initial_cost']
    for storageid in storage:
        cost+=storage[storageid]['initial_cost']
    return cost

house_pv=231600*0.2
sp_pv=88000*0.2
pandr_pv=11520*0.2


load={}
pv={}
storage={}
pv=create_pv(pv,house_pv,house_pv*56.95,solar_data())
pv=create_pv(pv,sp_pv,sp_pv*56.95,solar_data_flat())
pv=create_pv(pv,pandr_pv,pandr_pv*56.95,solar_data_10())
#Create load by create_load(load,list of load power in time)
load=create_load(load,residential())            #load_id = 0
load=create_load(load,load_heat_data())         #load_id = 1
load=create_load(load,load_sciencepark())       #load_id = 2
load=create_load(load,hot_water())              #load_id = 3
load=create_load(load,car_charging())
[buy_price,sell_price]=price()
storage=create_storage(storage,40000,40000/8,math.sqrt(0.85),40000*14.2)
start=0
end=365
#[buy2,total_output2,total_load2,balancing2]=energy_system(pv,load,storage)
[buy2,total_output2,total_load2,balancing2]=energy_system_conditioal(pv,load,storage,buy_price,sell_price,list(range(start,end)))
running_cost=market(buy2,sell_price,buy_price)
initial_cost=captial_cost(pv,storage)
total_cost=running_cost+initial_cost
#plot_demand(total_output2[start*48:end*48],total_load2[start*48:end*48],balancing2[start*48:end*48])
plot_demand(total_output2[start*48:end*48],total_load2[start*48:end*48],balancing2)
#plot_average(total_output2,total_load2,balancing2)
print('Operating cost is ',running_cost, ', initial cost is ',initial_cost,', total cost is ',total_cost)
#"""
#elapsed_time=timeit.timeit(code_time,number=100)/100
#print(elapsed_time)
