# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:27:15 2019

@author: Monthly Pricing
"""

import pandas as pd

#------------------------------read master file-------------------------------------------
xldf = pd.ExcelFile(r'E:\iSell_Project\All_In_One_iSell\masters\MonthlyPricing.xlsx')
testisell = iSelldf4
testisell['Date']= pd.to_datetime(testisell['Date'],format='%Y-%m-%d')
testisell['Month'] = testisell['Date'].apply(lambda x:x.strftime('%b'))
 
monthdf = pd.read_excel(xldf,'Month')
dowdf = pd.read_excel(xldf,'Dow_weight')

#=====================fetch monthwise minimum rates================================
monthdf.set_index('Hotel',inplace=True)
monthdf2 = monthdf.T
monthdf2.reset_index(inplace=True)
monthdf2.rename(columns={'index':'Month'},inplace=True)

monthdf3 = pd.DataFrame(monthdf2.loc[:,['Month','Amarpreet Hotel']]) #from input conditions
monthdf3.rename(columns={'Amarpreet Hotel':'Min_Rate'},inplace=True)

#--------------------merge min rate with isell on month----------------------------
monthdf4 = testisell.merge(monthdf3,on='Month',how='left')
#monthdf4.to_csv(r'E:\iSell_Project\All_In_One_iSell\masters\monthdf4.csv')

#==========================Fetch dow weights========================================
dowdf.set_index('Hotel',inplace=True)
dowdf2 = dowdf.T
dowdf2.reset_index(inplace=True)
dowdf2.rename(columns={'index':'Dow'},inplace=True)

dowdf3 = pd.DataFrame(dowdf2.loc[:,['Dow','Amarpreet Hotel']]) #from input conditions
dowdf3.rename(columns={'Amarpreet Hotel':'Dow_wt'},inplace=True)
#---------------------merge dow weights with isell-----------------------------------
monthdow = monthdf4.merge(dowdf3,on='Dow',how='left')
monthdow['Final_MinRate'] = monthdow['Min_Rate']*monthdow['Dow_wt']


#minrate, %age increase(jump),times=9
def compound_interest(principle, rate, time):  
    # Calculates compound interest
    CI = principle * (pow((1 + rate/100), time))
    return(round(CI))


max_rate=[]
for rate in monthdow['Final_MinRate']:
    mrate=compound_interest(rate,5,9)
    max_rate.append(mrate)
    
monthdow['MaxRate']= max_rate



monthdow.to_csv(r'E:\iSell_Project\All_In_One_iSell\masters\monthdow.csv')





isell_mnths = monthdow['Month'].unique()
isell_dow = monthdow['Dow'].unique()


for mnth in isell_mnths:
    monthdow2 = pd.DataFrame(monthdow[monthdow['Month'] == mnth])
    #--------------weighted DOW minimum rates----------------------------------
    dowMinrate = monthdow2.drop_duplicates(subset='Dow')
    dowMinrate_dict = dict(zip(dowMinrate['Dow'],dowMinrate['Final_MinRate']))
    
    #------------- generating dow patterns ------------------------------------
    for mth in dowMinrate_dict:
        dowpattern(mnth,downame,minrate,'Short') # from input conditions   
        
#
#    
    




#----------------------rounding near 10 if currency is INR---------------------
def applyPsychologicalFactor(n,htlcur):
    if htlcur == "INR":
        rval=(int((round(n,-1))/10)*10)-1    
    else:        
        rval= int(n)
    return rval

#==================================grid calculation============================

def dowpattern(mnthname,downame,minrate,jfact):        
    minrate=2539
    jfact = 1.05
    downame='Mon'    
    
    dowgrid =[]
    
    for i in range(10):
        if i == 0:
            dowgrid.append(minrate)
        else:
            dowgrid.append(round(dowgrid[i-1]*jfact))
    
    
    dowgrid2 = dowgrid[::-1] #reversing the list
      
    dowgrid3 = []
    gridframe=pd.DataFrame({})
    
    for i in dowgrid2:
        #----------rounding near 10 if currency is INR-------------------------
        dowgrid3.append(applyPsychologicalFactor(i,'INR'))
        
    gridframe[downame] = dowgrid3
    return(gridframe)
#    gridframe.to_csv(r'E:\iSell_Project\All_In_One_iSell\masters\gridframe.csv') 
    
    
    
















