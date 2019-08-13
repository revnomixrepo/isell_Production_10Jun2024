# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 15:14:57 2019

@author: revse
"""
import sys
import pandas as pd
import logging
import iSell_fun_02 as fun2


#================compound interest=============================================
#minrate, %age increase(jump),times=0 -> 9
def compound_interest(principle, rate, time):  
    # Calculates compound interest
    CI = principle * (pow((1 + rate/100), time))
    return(CI)


def Gridcreator(htl,isell,mnthminrates,wts,htlcluster,mnthjumps,jumpfact,jType,psy,priceType):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:GRID, SubModule:Gridcreator')    
    
    if priceType == 'Monthly':
        filtername='Month'
        #------------------extract isell months----------------------------------
        logging.debug('Extracting isell months (mnthlist) ::')        
        mnthlist = isell[filtername].unique()  
        logging.debug(mnthlist)
                       
    elif priceType == 'Seasonal':
        filtername='Season'
        mnthlist=['S1','S2']
    else:
        logging.info('Undefined PricingType, It should be (Monthly/Seasonal)')
        sys.exit()          
    
    jumpdict = {1:'Base',2:'Short',3:'High',4:'Long'}
    logging.debug('Jump Dictionary ::')
    logging.debug(jumpdict)
    
    dowlist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    #--------------------------jump factor sheet-------------------------------------
    logging.debug('Jump value from input condition (jType) :{}'.format(jType))
    jumpfactdf = pd.DataFrame(jumpfact) 
    jumpfactdf2 = jumpfactdf.loc[:,['JumpName',jType]] 
    
    #------------------------Jump and Factor dictionary------------------------------
    jfact = dict(zip(jumpfactdf2['JumpName'],jumpfactdf2[jType])) 
    logging.debug('Jump and Factor dictionary (jfact)::')
    logging.debug(jfact)    
          
    monthdata=[] 
    
    #----------------appending monthdata list---------------------------------
    for cson in mnthlist:
        dff = pd.DataFrame({})        
        dff['Dow'] = dowlist
        dff['Hotel'] = htl
        dff[filtername] = cson
        dff['Min_Rate'] = dff[filtername].map(mnthminrates)
        dff['Cluster'] = htlcluster
        dff['DowWt'] = dff['Dow'].map(wts)
        dff['JumpNum'] = dff[filtername].map(mnthjumps) 
        dff['JumpName'] = dff['JumpNum'].map(jumpdict)
        dff['Jfact'] = dff['JumpName'].map(jfact)
        monthdata.append(dff)
    #--------------------------------------------------------------------------
    logging.debug('Appended monthdata list with dataframes (csondata2) ::')
    csondata2 = pd.concat(monthdata)
    logging.debug(csondata2)
    
    #-------------------min rate calculation-----------------------------------
    logging.debug("Applied dow_weights and 'min_rate' column calculated for recommendation ::")
    csondata2['min_rate'] = csondata2['Min_Rate']*csondata2['DowWt']
    logging.debug(csondata2)
    
    #-------------------create new column['Dow','min_rate','Jfact']--------------------------------------    
    csondata2['new_col'] = list(zip(csondata2.Dow,csondata2.min_rate,csondata2.Jfact))
    logging.debug("new_col added which contains ['Dow','min_rate','Jfact'] values ::")
    logging.debug(csondata2)
    
    steps=[0,1,2,3,4,5,6,7,8,9]
    
    finalczongrid=[]
    
    #-------------appending finalczongrid list with the dataframes----------------------
    for csons in mnthlist:
        csondata3 = csondata2[csondata2[filtername] == csons]
        
        dowpattern=[]
        for dowpat in csondata3['new_col']:
            #passing steps
            patterns=[]
            kk=pd.DataFrame({})
            for t in steps:
                ci = compound_interest(dowpat[1], dowpat[2], t) 
                #-------------pyschlogical factor--------------------------
                ci2=fun2.applyPsychologicalFactor(ci,psy)    
                #----------------------------------------------------------
                patterns.append(ci2)                  
                
            kk[dowpat[0]] = patterns[::-1]
            dowpattern.append(kk)
            
        griddd= pd.concat(dowpattern,axis=1)
        griddd[filtername] = csons
        #mapping
        griddd['Hotel'] = htl
        griddd['Cluster'] = htlcluster
        griddd['JumpNum'] = griddd[filtername].map(mnthjumps)
        griddd['Jump'] = griddd['JumpNum'].map(jumpdict)
        griddd['Min_Rate'] = griddd[filtername].map(mnthminrates)
        griddd['Occ'] = steps[::-1]
        
        finalczongrid.append(griddd)
    #--------------------------------------------------------------------------------    
        
    logging.debug('Rates calculated using compound interest formula, using(min_rate,Jfact,steps) ::')
    finalczongrid2= pd.concat(finalczongrid)
    logging.debug(finalczongrid2)
    
    finalczongrid3 = finalczongrid2.loc[:,['Hotel','Cluster','Min_Rate','Jump',filtername,'Occ','Mon','Tue','Wed','Thu','Fri','Sat','Sun']]
    logging.debug('Final Grid for {} ::'.format(htl))    
    logging.debug(finalczongrid3)    
    return(finalczongrid3)
    
        



