# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:30:16 2019

@author: Monthly Pricing
"""
import pandas as pd
import logging
import sys


#minrate, %age increase(jump),times=0 -> 9
def compound_interest(principle, rate, time):  
    # Calculates compound interest
    CI = principle * (pow((1 + rate/100), time))
    return(CI)



def ciRate(minR,maxR,t):
    #------calculate compund interest rate---------------------
    jumfact = (float(maxR)/float(minR))**(1/t)-1 
    jumfact2 = jumfact*100
    jumfact3 = round(jumfact2)
    return(jumfact3)    

   
def month_minmax(htl,iSelldf4,minRdict,htl_dowWt,jumpfact,mnthJumpdict,htl_cluster,jType,maxRdict,flag_mRate,ceilingRate): 
#    print(maxRdict)
    #--------------------------jump factor sheet---------------------------------------
    jumpfactdf = pd.DataFrame(jumpfact) 
    jumpfactdf2 = pd.DataFrame(jumpfactdf.loc[:,['JumpName',jType]])  
    
    #------------------------Jump and Factor dictionary------------------------------
    jfact = dict(zip(jumpfactdf2['JumpName'],jumpfactdf2[jType]))    
    
    
    #----------------attach min max rates to isell ----------------------------------
    
    testisell = pd.DataFrame(iSelldf4)
    testisell['Date']= pd.to_datetime(testisell['Date'],format='%Y-%m-%d')
    testisell['Month'] = testisell['Date'].apply(lambda x:x.strftime('%b'))     
    
    #-----------------map monthly minimum rate with isell-------------------------
    testisell['Min_Rate'] = testisell['Month'].map(minRdict)
    
    #-------------------map dow weights to iSell---------------------------------
    testisell['Dow_wt'] = testisell['Dow'].map(htl_dowWt)    
    
    #-----------------map monthly jump number with isell--------------------------
    jumpdict = {1:'Base',2:'Short',3:'High',4:'Long'}
    
    testisell['JumpNum'] = testisell['Month'].map(mnthJumpdict)
    #-----------------map jump names from numbers with isell----------------------
    testisell['Jump'] = testisell['JumpNum'].map(jumpdict)
    #-----------------map jump factors from names with iSell for mRateflag=0----------------------
    testisell['Jfact'] = testisell['Jump'].map(jfact)
    
   
#    testisell.to_csv(r'E:\iSell_Project\All_In_One_iSell\testisell_{}.csv'.format(htl))
    testisell['min_rate'] = testisell['Min_Rate']*testisell['Dow_wt']
    testisell['min_rate'] = testisell['min_rate'].astype(float,errors='ignore')
    
    logging.info('\tChecking MaxRate Flag')
    #---------------------USE MAX Rate Flag Condition-----------------------------------
    if flag_mRate == 0:
        #--------------------ceiling rate condition----------------------------------------
        if ceilingRate == 1:
            testisell['Max_Rate'] = testisell['Month'].map(maxRdict)
        else:
            pass
            
        #---------------------drop the max rate column---------------------------------
        monthdow11= pd.DataFrame(testisell)
        monthdow11['new_col'] = list(zip(monthdow11.min_rate, monthdow11.Jfact))           
        
        #--------------------pass min_rate and jfact to calculate max_rate------------
        max_rate=[]
        #max rate calculation using compound interest
        for rate_jfact in monthdow11['new_col']:
            mrate=compound_interest(rate_jfact[0],rate_jfact[1],9)
            max_rate.append(mrate)
            
        monthdow11['max_rate']= max_rate
        monthdow2 = monthdow11.drop(['Month','Dow_wt','JumpNum','Jump','Jfact','new_col'],axis=1)
                  
    elif flag_mRate == 1:
        #Jump Calculation using min,max and time         
         #-----------------map monthly max rates for mRateflag = 1 --------------------------------------    
        testisell['Max_Rate'] = testisell['Month'].map(maxRdict)
        
        monthdow22= testisell.drop(['Jfact','Jump'],axis=1)
        #Create list of Min_Rate,Max_Rate and time ->9
        monthdow22['new_col2'] = list(zip(monthdow22.Min_Rate, monthdow22.Max_Rate)) 
        
        #--------------------------Calculation of Jump and Jfact--------------------
        jumprate=[]
        for val in monthdow22['new_col2']:
            #---------compound interest rate calculator----------------
            jval=ciRate(val[0],val[1],9)
            jumprate.append(jval)            
        #---------------------------------------------------------------------------   
        
        monthdow22['JumpNum'] = jumprate        
                  
        monthdow22['Jump'] = monthdow22['JumpNum'].map(jumpdict)   
        monthdow22['Jfact'] =  monthdow22['Jump'].map(jfact)  
        
        monthdow22['new_col'] = list(zip(monthdow22.min_rate, monthdow22.Jfact)) 
        
        #--------------------pass min_rate and jfact to calculate max_rate------------        
        max_rate=[]
        #max rate calculation using compound interest
        for rate_jfact in monthdow22['new_col']:
            mrate=compound_interest(rate_jfact[0],rate_jfact[1],9)
            max_rate.append(mrate)
            
        monthdow22['max_rate']= max_rate
        
        
        monthdow11 = pd.DataFrame(monthdow22)
#        monthdow11.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\{}monthdow11.csv'.format(htl))
        monthdow2 = monthdow11.drop(['Month','Dow_wt','JumpNum','Jump','Jfact','new_col','new_col2'],axis=1)
        
    else:
        print("Please set 'use_MaxRate' column 1 or 0")
        sys.exit()                   
        
              
    #dataframe to crosscheck containing all monthly values
#    monthdow11.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\{}monthdow11.csv'.format(htl))
    
    logging.info("\tMonthly values fetched")   
    
    
    return(monthdow2,monthdow11)

    
