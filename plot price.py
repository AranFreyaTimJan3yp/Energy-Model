# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 20:02:32 2020

@author: timot
"""
import numpy as np
import matplotlib.pyplot as plt

buy=[]
sell=[]
import csv
with open('price.csv',newline='') as csvfile:
    raw_price=csv.reader(csvfile,delimiter=',')
    for row in raw_price:
        buy.append(float(row[0]))
        sell.append(float(row[1]))
m_buy=np.zeros(48)
m_sell=np.zeros(48)
for t in range(17520):
    m_buy[t%48]+=buy[t]
    m_sell[t%48]+=sell[t]
m_buy=m_buy/365
m_sell=m_sell/365
m_buy=np.append(m_buy[0],m_buy)
m_sell=np.append(m_buy[0],m_sell)
fig,ax=plt.subplots()
ax.step(np.array(range(49))/2,m_sell*100,label='export')
ax.step(np.array(range(49))/2,m_buy*100,label='import')
ax.set_xlim([0,24])
ax.set_ylim([0,30])
ax.set_ylabel('price (p/kWh)')
ax.set_xlabel('time of day')
plt.xticks([0,6,12,18,24])
ax.set_title('Averaged Energy Prices of 2018')
fig.legend(loc='upper center', bbox_to_anchor=(0.48, 0.7), ncol=1)
plt.grid()