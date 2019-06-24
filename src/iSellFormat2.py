import pandas as pd
import iSell_fun_02 as ifun
from datetime import datetime


def total_ota_merging(htlname, ftr, iselldt, outcsvpath):        
    print("You are in iSellFormat2, isellTotal and isellOTA merging")
    #===========================1) Read Total df====================================
    df_total = pd.read_csv(outcsvpath+r"\iSell_{}_{}.csv".format(htlname,iselldt))
    print("1.Read iSell_{}_{}.csv".format(htlname,iselldt))
    df_total['Date'] = pd.to_datetime(df_total['Date'],format='%d-%b-%Y')
    
    #----------------------recommendations from total df------------------------------
    total_rec = pd.DataFrame(df_total.loc[:,['Date','Recommended Rate']])
    total_rec['Date'] = pd.to_datetime(total_rec['Date'],format='%Y-%m-%d') 
    
    #--------------------find OTAs from Total df([Date, otas]-------------------------
    get_marketTrend_loc = df_total.columns.get_loc("Market Trend")
    total_otas = pd.concat([pd.DataFrame(df_total.loc[:,['Date']]),pd.DataFrame(df_total.iloc[:,get_marketTrend_loc+1:])],axis=1)
    total_otas['Date'] = pd.to_datetime(total_otas['Date'],format='%Y-%m-%d')
    
    df_total2 = pd.DataFrame(df_total.loc[:,['Date', 'Dow', 'Event', 'Capacity',
           'Hotel Availability', ftr, 'OTA_Sold', 'Pickup',
           'OTA Revenue', 'ADR OTB']])
    
    df_total2['Date'] = pd.to_datetime(df_total2['Date'],format='%Y-%m-%d')
    
    df_total2.rename(columns={'OTA_Sold':'Total Sold', 'Pickup':'Total Pickup',
           'OTA Revenue':'Total Revenue', 'ADR OTB':'Total ADR OTB'},inplace=True)
    
    #============================2) ota df============================================
    df_ota = pd.read_csv(outcsvpath+r"\iSell_{}_OTA_{}.csv".format(htlname,iselldt))
    df_ota['Date'] = pd.to_datetime(df_ota['Date'],format='%d-%b-%Y')
    print("2.Read iSell_{}_OTA_{}.csv ".format(htlname,iselldt))
    
    #---------------keep only required columns in ota df----------------------------------------
    df_ota.drop(['Dow', 'Event', ftr, 'Capacity','Hotel Sold','Hotel Availability'],axis=1,inplace=True)
    df_ota['Date'] = pd.to_datetime(df_ota['Date'],format='%Y-%m-%d')    
    #==================================================================================    
    #=======================Merging total and ota isell data===========================
    format2 = df_total2.merge(df_ota,on='Date',how='left')
    format2.rename(columns={'Pickup':'OTA Pickup'},inplace=True)
    format2['Date'] = pd.to_datetime(format2['Date'],format='%Y-%m-%d')
    
    #-------------------------Merge total df otas with final format-----------------
    format3 = format2.merge(total_otas,on='Date',how='left')
    #-------------------------assign recommendations from total df-------------------
    format3['Recommended Rate'] = total_rec['Recommended Rate']
    format3['Date'] = format3['Date'].apply(lambda x:x.strftime('%d-%b-%Y'))
    
    try:
        format3.drop('Unnamed: 0',axis=1,inplace=True)
    except:
        pass
    

    #==========================================================================
    print('Final Combine iSell and adoption df returned')
    format4 = format3.rename(columns={'Total Pickup':'Pickup'})
    finaladop = ifun.Adopcal(format4,179,89)
    return(format3,finaladop)
