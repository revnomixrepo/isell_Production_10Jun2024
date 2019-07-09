# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:45:55 2019
@author: simple rates recommendations
"""
import numpy as np
import pandas as pd
import logging
import iSell_fun_02 as fun2


def simRecs(htl,otbdf,jump,szrates,chman,cmflag,htlcur,psy,useceiling,usefloor):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:simpleRecs, SubModule:simRecs')    
    
    logging.info('Recommendations calculating as per the Simple GridType')
    otbdf['OTA_Sold'] = otbdf['OTA_Sold'].fillna(value=0)
    otbdf['OTA_Sold'] = otbdf['OTA_Sold'].astype(int,errors='ignore')
    
    logging.debug('calculating Recommended Rate column with OTA_Sold*min_rate condition')
    otbdf['Recommended Rate'] = otbdf['OTA_Sold'] * jump + otbdf['min_rate']    
    #---------------------------psy factor-----------------------------------------
    otbdf['Recommended Rate'] = otbdf['Recommended Rate'].apply(lambda row: fun2.applyPsychologicalFactor(row,psy))
    otbdf.drop(['min_rate','max_rate'],axis=1,inplace=True)    
    logging.debug('dataframe otbdf ::')
    logging.debug(otbdf.to_string())
    
    
    if cmflag==0:
        logging.debug('Rate on CM check (cmflag = 0) : No Rate on CM Column')        
        otbdf = otbdf.merge(szrates,on='Date',how='left')
        szratedf = pd.DataFrame(otbdf.loc[:,['Date','Recommended Rate']])
        szratedf.rename(columns={'Recommended Rate':'SeasonalRate'},inplace=True)
        logging.debug('So merging last recommendations with current isell, rename last recommendations : Seasonal Rates')
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            logging.debug('set Ceiling Rate condition is ON: (useceiling == 1)')
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] > otbdf['Max_Rate'],otbdf['Max_Rate'],otbdf['Recommended Rate'])
            logging.debug('Recommendations Higher than Max_Rate are replaced with Max Rate ::')
            logging.debug(otbdf.to_string())
        else:
            pass
        #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            logging.debug('set Floor Rate condition is ON: (usefloor == 1)')
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] < otbdf['Min_Rate'],otbdf['Min_Rate'],otbdf['Recommended Rate'])
            logging.debug('Recommendations less than Minimum Rate are replaced with Minimum Rate ::')
            logging.debug(otbdf.to_string())
        else:
            pass              
        #---------------------------------------------------------------------------------------        
        
        otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] == otbdf['Last_szrate'],np.nan,otbdf['Recommended Rate'])
        otbdf.drop(['Last_szrate','Min_Rate','Max_Rate'],axis=1,inplace=True)
        
    elif cmflag==1:
        logging.debug('Rate on CM check (cmflag = 1) : Rate on CM Column Present')      
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            logging.debug('set Ceiling Rate condition is ON: (useceiling == 1)')
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] > otbdf['Max_Rate'],otbdf['Max_Rate'],otbdf['Recommended Rate'])
            logging.debug('Recommendations Higher than Max_Rate are replaced with Max Rate ::')
            logging.debug(otbdf.to_string())
        else:
            pass
         #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            logging.debug('set Floor Rate condition is ON: (usefloor == 1)')
            otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] < otbdf['Min_Rate'],otbdf['Min_Rate'],otbdf['Recommended Rate'])
            logging.debug('Recommendations less than Minimum Rate are replaced with Minimum Rate ::')
            logging.debug(otbdf.to_string())
        else:
            pass              
        #--------------------------------------------------------------------------------------
        
        logging.debug('Recommendations same with Rate on CM replace with blanks')
        otbdf['Recommended Rate'] = np.where(otbdf['Recommended Rate'] == otbdf['Rate on CM'],np.nan,otbdf['Recommended Rate'])
        
        #---------------------------drop unrequired columns---------------------
        try:
            otbdf.drop(['Min_Rate','Max_Rate'],axis=1,inplace=True)
        except:
            pass        
        #-----------------------------------------------------------------------
        
        logging.debug('Rate On CM column present, so no need of Seasonal Rates')
        szratedf = 'NotApplied'      
        
    logging.info("Simple Recommendations Returned")
    
    #----------------------drop unrequired columns------------------------------
    try:
        otbdf.drop('Min_Rate',axis=1,inplace=True)
    except:
        pass    
       
    try:
        otbdf.drop('JumpNum',axis=1,inplace=True)
    except:
        pass  
    #---------------------------------------------------------------------------
    
    logging.debug('Recommendations and SeasonalRate DataFrames returned ::')
    logging.debug('Recommendations dataframe ::')
    logging.debug(otbdf.to_string())
    logging.debug('SeasonalRate dataframe ::')
    logging.debug(szratedf)    
    return(otbdf,szratedf)