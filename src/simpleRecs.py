# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:45:55 2019
@author: simple rates recommendations
"""
import numpy as np
import pandas as pd
import iSell_fun_02 as fun2

def simRecs(htl,otbdf,jump,szrates,chman,cmflag,htlcur,psy,useceiling,usefloor):
    
    otbdf['OTA_Sold'] = otbdf['OTA_Sold'].fillna(value=0)
    otbdf['OTA_Sold'] = otbdf['OTA_Sold'].astype(int,errors='ignore')
    otbdf['Recommended Rate'] = otbdf['OTA_Sold'] * jump + otbdf['min_rate']
    
    #---------------------------psy factor-----------------------------------------
    otbdf['Recommended Rate'] = otbdf['Recommended Rate'].apply(lambda row: fun2.applyPsychologicalFactor(row,psy))
    otbdf.drop(['min_rate','max_rate'],axis=1,inplace=True)    
    
    
    if cmflag==0:
        #merging last recommendations with current isell
        otbdf = otbdf.merge(szrates,on='Date',how='left')
        szratedf = pd.DataFrame(otbdf.loc[:,['Date','Recommended Rate']])
        szratedf.rename(columns={'Recommended Rate':'SeasonalRate'},inplace=True)
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] > otbdf['Max_Rate'],otbdf['Max_Rate'],otbdf['Recommended Rate'])
        else:
            pass
         #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] < otbdf['Min_Rate'],otbdf['Min_Rate'],otbdf['Recommended Rate'])
        else:
            pass              
        #---------------------------------------------------------------------------------------        
        
        otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] == otbdf['Last_szrate'],np.nan,otbdf['Recommended Rate'])
        otbdf.drop(['Last_szrate','Min_Rate','Max_Rate'],axis=1,inplace=True)
        
    elif cmflag==1:  
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] > otbdf['Max_Rate'],otbdf['Max_Rate'],otbdf['Recommended Rate'])
        else:
            pass
         #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] < otbdf['Min_Rate'],otbdf['Min_Rate'],otbdf['Recommended Rate'])
        else:
            pass              
        #--------------------------------------------------------------------------------------
        
        
        otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] == otbdf['Rate on CM'],np.nan,otbdf['Recommended Rate'])
        try:
            otbdf.drop(['Min_Rate','Max_Rate'],axis=1,inplace=True)
        except:
            pass
        szratedf = 'NotApplied'      
        
    print("\tSimple Recommendations Returned")
    
    try:
        otbdf.drop('Min_Rate',axis=1,inplace=True)
    except:
        pass    
       
    try:
        otbdf.drop('JumpNum',axis=1,inplace=True)
    except:
        pass    
    return(otbdf,szratedf)