# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 15:14:57 2019

@author: revse
"""
import sys
import pandas as pd
import iSell_fun_02 as fun2


#================compound interest=============================================
#minrate, %age increase(jump),times=0 -> 9
def compound_interest(principle, rate, time):  
    # Calculates compound interest
    CI = principle * (pow((1 + rate/100), time))
    return(CI)


def Gridcreator(htl,isell,mnthminrates,wts,htlcluster,mnthjumps,jumpfact,jType,psy,priceType):
    
    if priceType == 'Monthly':
        filtername='Month'
        #------------------extract isell months----------------------------------
        mnthlist = isell[filtername].unique()  
                       
    elif priceType == 'Seasonal':
        filtername='Season'
        mnthlist=['S1','S2']
    else:
        print('Undefined PricingType')
        sys.exit()          
    
    jumpdict = {1:'Base',2:'Short',3:'High',4:'Long'}
    dowlist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    #--------------------------jump factor sheet-------------------------------------
    jumpfactdf = pd.DataFrame(jumpfact) 
    jumpfactdf2 = jumpfactdf.loc[:,['JumpName',jType]] 
    
    #------------------------Jump and Factor dictionary------------------------------
    jfact = dict(zip(jumpfactdf2['JumpName'],jumpfactdf2[jType]))        
    monthdata=[] 
    
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
    
    csondata2 = pd.concat(monthdata)
    #-------------------min rate calculation-----------------------------------
    csondata2['min_rate'] = csondata2['Min_Rate']*csondata2['DowWt']
    
    #-------------------create new column['Dow','min_rate','Jfact']--------------------------------------
    csondata2['new_col'] = list(zip(csondata2.Dow,csondata2.min_rate,csondata2.Jfact))
#    csondata2.to_csv(r'E:\iSell_Project\All_In_One_iSell\gtdc\csondata2.csv')
    
    steps=[0,1,2,3,4,5,6,7,8,9]
    
    finalczongrid=[]
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
        
    
    finalczongrid2= pd.concat(finalczongrid)
    finalczongrid3 = finalczongrid2.loc[:,['Hotel','Cluster','Min_Rate','Jump',filtername,'Occ','Mon','Tue','Wed','Thu','Fri','Sat','Sun']]
#    finalczongrid3.to_csv(r'E:\iSell_Project\All_In_One_iSell\gtdc\kkk_{}.csv'.format(htl))
    return(finalczongrid3)
    
        



