# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:30:16 2019

@author: Monthly Pricing
"""
import pandas as pd
import sys
#import GRID as grd


def ciRate(minR,maxR,t):
    #------calculate compund interest rate---------------------
    jumfact = (float(maxR)/float(minR))**(1/t)-1 
    jumfact2 = jumfact*100
    jumfact3 = round(jumfact2)
    return(jumfact3)    



#minrate, %age increase(jump),times=0 -> 9
def compound_interest(principle, rate, time):  
    # Calculates compound interest
    CI = principle * (pow((1 + rate/100), time))
    return(CI)



               
def czonmin_max(htl,iSelldf4,csonrange,czonminrates,wtdict,jump_fact,czonjumps,htl_cluster,jType,maxratelist,maxRflag):    
    #------------------------------read Seasonal Rates from list-------------------------
    s1min_rate=czonminrates[0]
    s2min_rate=czonminrates[1]
    
    s1s=pd.to_datetime(csonrange[0],format='%d-%b-%Y')
    s1e=pd.to_datetime(csonrange[1],format='%d-%b-%Y')
    
    s2s=pd.to_datetime(csonrange[2],format='%d-%b-%Y')
    s2e=pd.to_datetime(csonrange[3],format='%d-%b-%Y')
    
    #--------------------date range S1 S2 frames with min rates & Jumps--------------------------
    s1df=pd.DataFrame({})
    s1frame = list(pd.date_range(start=s1s, end=s1e))
    s1df['Date'] = s1frame
    s1df['Date'] = pd.to_datetime(s1df['Date'],format='%Y-%m-%d')
    s1df['Season'] = 'S1'
    s1df['Min_Rate'] = s1min_rate
    s1df['Jump'] = czonjumps[0]
    
    maxratedict = {'S1':maxratelist[0],'S2':maxratelist[1]}
    
    
    s2df=pd.DataFrame({})
    s2frame = list(pd.date_range(start=s2s, end=s2e))
    s2df['Date'] = s2frame
    s2df['Date'] = pd.to_datetime(s2df['Date'],format='%Y-%m-%d')
    s2df['Season'] = 'S2'
    s2df['Min_Rate'] = s2min_rate 
    s2df['Jump'] = czonjumps[1]
        
    sesonalframe = pd.concat([s1df,s2df])
    
    #--------------------------merge Season, Min_Rate and Jump with iSell Frame--------
    iSelldf4['Date'] = pd.to_datetime(iSelldf4['Date'],format='%Y-%m-%d')
    seasonaldf = iSelldf4.merge(sesonalframe,on='Date',how='left')   

    #--------------------------jump factor sheet---------------------------------------
    jumpfactdf = pd.DataFrame(jump_fact)  
    jumpfactdf2 = pd.DataFrame(jumpfactdf.loc[:,['JumpName',jType]])   
    #------------------------Jump and Factor dictionary------------------------------
    jfact = dict(zip(jumpfactdf2['JumpName'],jumpfactdf2[jType]))    
    
    jumpdict = {1:'Base',2:'Short',3:'High',4:'Long'}
    
    #----------------------map jump names from values------------------------------
    seasonaldf['Jump'] = seasonaldf['Jump'].map(jumpdict)   
    #----------------------map dow weights with isell-----------------------------
    seasonaldf['Dow_wt'] = seasonaldf['Dow'].map(wtdict)
    
    seasonaldf['min_rate'] = seasonaldf['Min_Rate']*seasonaldf['Dow_wt']
    seasonaldf['min_rate'] = seasonaldf['min_rate'].astype(float,errors='ignore')
    
    #---------------------monthly jump merge with isell---------------------------------
    monthdow11= pd.DataFrame(seasonaldf)
    #======================map jump factor to Jump ==================================
    monthdow11['Jfact'] = monthdow11['Jump'].map(jfact)
    monthdow11['Jfact'] = monthdow11['Jfact'].astype(int,errors='ignore')
    
    #====================check use max rate condition==============================
    if maxRflag == 0:  
        #=========create list column containing Jfact and min rate============
        monthdow11['new_col'] = list(zip(monthdow11.min_rate, monthdow11.Jfact))     
        max_rate=[]
        #max rate calculation using compound interest
        for rate_jfact in monthdow11['new_col']:
            mrate=compound_interest(rate_jfact[0],rate_jfact[1],9)
            max_rate.append(mrate)
            
        monthdow11['max_rate']= max_rate  
        monthdow2=monthdow11.drop(['Season','Min_Rate','Dow_wt','Jump','Jfact','new_col'],axis=1)
              
    elif maxRflag == 1:
        monthdow11['max_rate'] = monthdow11['Season'].map(maxratedict)
        #Jump Calculation using min,max and time         
        monthdow11.drop(['Jfact','Jump'],axis=1,inplace=True)
        #Create list of min_rate,max_rate and time ->9
        monthdow11['new_col'] = list(zip(monthdow11.Min_Rate, monthdow11.max_rate)) 
        jumprate=[]
        
        for val in monthdow11['new_col']:
            #---------compound interest rate calculator----------------
            jval=ciRate(val[0],val[1],9)
            jumprate.append(jval)
            
            
        monthdow11['Jump'] = jumprate
        monthdow11['Jump'] = monthdow11['Jump'].map(jumpdict)   
        monthdow11['Jfact'] =  monthdow11['Jump'].map(jfact)   
        
        monthdow2 = monthdow11.drop(['Season','Min_Rate','Dow_wt','Jump','Jfact','new_col'],axis=1)
        
    else:
        print('Please define seasonal use_MaxRate 0 or 1')
        sys.exit()
              
    print("\tMonthly values fetched")   
    
    monthdow11.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\{}_month11.csv'.format(htl))
    return(monthdow2,monthdow11)

    
