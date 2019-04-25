import pandas as pd
import numpy  as np
import iSell_fun_02

def dRecs(iSelldf4,pgdf,isellrange,lastszrates,cmflag,priceType,hnf,ftr):
    
    iSelldf6 = pd.DataFrame(iSelldf4)
    
    if hnf == 'Yes':
        iSelldf6['availablty']= iSelldf6['Hotel Availability']/iSelldf6['Capacity']
        
    else:
        iSelldf6['availablty']= iSelldf6['Rooms Avail To Sell Online']/iSelldf6['Capacity']
        
    iSelldf6['availablty']= iSelldf6['availablty'].round(decimals=1)
    iSelldf6['line']=iSelldf6['availablty']*10 - 1    
    
    iSelldf6['line']=np.where(iSelldf6['line']<0,0,iSelldf6['line'])
    iSelldf6['line']=np.where(iSelldf6['line']>9,9,iSelldf6['line'])   
    
    iSelldf6['line'] = iSelldf6['line'].astype(int,errors='ignore')
    
#    iSelldf6.to_csv(r'E:\iSell_Project\All_In_One_iSell\iselldf6.csv')
    #---------------------Seasonal or Monthly priceType-------------------------------   
    if priceType == 'Seasonal':
        iSelldf6['params'] = list(zip(iSelldf6['Season'],iSelldf6['Dow'],iSelldf6['line']))
    elif priceType == 'Monthly':
        iSelldf6['params'] = list(zip(iSelldf6['Month'],iSelldf6['Dow'],iSelldf6['line']))  
        
#    iSelldf6.to_csv(r'E:\iSell_Project\All_In_One_iSell\gtdc\iSelldf6.csv')
    
    #----------------recommendations passing parameters to Grid------------------------    
    rec1=[]
    for parlist in iSelldf6['params']:
        s=str(parlist[0])
        d = str(parlist[1])
        l = int(parlist[2])
        
        #-------- pass priceType to recvalue---------------------------        
        rec1.append(iSell_fun_02.recvalue(pgdf,s,l,d,priceType))
    #---------------------------------------------------------------------------------        
    iSelldf6['Recommended Rate'] = rec1            
    #----------------------------isell with all conditions  -----------------------
#    iSelldf6.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\linedf3.csv')
    #--------------------------------DropColumns---------------------------------------------
    if priceType == 'Seasonal':
        iSelldf6.drop(['Season','Min_Rate','Jump','Dow_wt','min_rate','Jfact','new_col','max_rate','availablty','line','params'],axis=1,inplace=True)
    elif priceType == 'Monthly':
        iSelldf6.drop(['Month','Min_Rate','Dow_wt','min_rate','Jump','Jfact','new_col','max_rate','availablty','line','params'],axis=1,inplace=True)
    
    
    #--------------------------------Compare with RateOnCM / LastSeasonalRates----------------
    if cmflag == 1:
        iSelldf6['Recommended Rate'] = np.where(iSelldf6['Rate on CM'] == iSelldf6['Recommended Rate'],np.nan,iSelldf6['Recommended Rate'])
        iSelldf7 = pd.DataFrame(iSelldf6)
        szrate ='Not Required'
        try:
            iSelldf7 = pd.DataFrame(iSelldf7.loc[:,['Date','Dow','Event','Capacity','Hotel Sold','Hotel Availability','Rooms Avail To Sell Online',ftr,'OTA_Sold','Pickup','OTA Revenue','ADR OTB','Rate on CM','Recommended Rate']])
        except:
            pass
        
    elif cmflag == 0:
        #merging last recommendations with current isell
        iSelldf6['Date'] = pd.to_datetime(iSelldf6['Date'],format='%Y-%m-%d')
        lastszrates['Date'] = pd.to_datetime(lastszrates['Date'],format='%Y-%m-%d')
        
        iSelldf7 = iSelldf6.merge(lastszrates,on='Date',how='left')
        
        
        #-----------calculating current seasonal rates-------------------------
        szrate = pd.DataFrame(iSelldf7.loc[:,['Date','Recommended Rate']])
        szrate['Date'] = pd.to_datetime(szrate['Date'],format='%Y-%m-%d')
        szrate.rename(columns={'Recommended Rate':'SeasonalRate'},inplace=True)       
        
        iSelldf7['Recommended Rate'] = np.where(iSelldf7['Recommended Rate'] == iSelldf7['Last_szrate'],np.nan,iSelldf7['Recommended Rate'])
        iSelldf7.drop(['Last_szrate','JumpNum'],axis=1,inplace=True)
        
        if hnf == 'Yes':
            iSelldf7 = pd.DataFrame(iSelldf7.loc[:,['Date','Dow','Event','Capacity','Hotel Sold','Hotel Availability','Rooms Avail To Sell Online',ftr,'OTA_Sold','Pickup','OTA Revenue','ADR OTB','Rate on CM','Recommended Rate']])
        else:
            iSelldf7 = pd.DataFrame(iSelldf7.loc[:,['Date','Dow','Event','Capacity','Rooms Avail To Sell Online',ftr,'OTA_Sold','Pickup','OTA Revenue','ADR OTB','Rate on CM','Recommended Rate']])
            
        
#        iSelldf7.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\linedf7_{}.csv')
        
    return(iSelldf7,szrate)
    
