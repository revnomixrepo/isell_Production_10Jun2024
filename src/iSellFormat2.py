import pandas as pd
#import beautiMode as bM

ftr = 'Lakeview King'
htlname = "YO1 India's Holistic Wellness Center"
iselldt = '15Jun2019'
outcsvpath = r"E:\iSell_Project\All_In_One_iSell\InputData\OutPut_CSV\15_Jun_2019"

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
           'Hotel Availability', 'Lakeview King', 'OTA_Sold', 'Pickup',
           'OTA Revenue', 'ADR OTB']])
    
    df_total2['Date'] = pd.to_datetime(df_total2['Date'],format='%Y-%m-%d')
    
    df_total2.rename(columns={'OTA_Sold':'Hotel Sold', 'Pickup':'Hotel Pickup',
           'OTA Revenue':'Hotel Revenue', 'ADR OTB':'Hotel ADR OTB'},inplace=True)
    
    #============================2) ota df============================================
    df_ota = pd.read_csv(outcsvpath+r"\iSell_{}_OTA_{}.csv".format(htlname,iselldt))
    df_ota['Date'] = pd.to_datetime(df_ota['Date'],format='%d-%b-%Y')
    print("2.Read iSell_{}_OTA_{}.csv ".format(htlname,iselldt))
    
    #---------------keep only required columns in ota df----------------------------------------
    df_ota.drop(['Dow', 'Event', ftr, 'Capacity','Hotel Sold','Hotel Availability'],axis=1,inplace=True)
    df_ota['Date'] = pd.to_datetime(df_ota['Date'],format='%Y-%m-%d')    
    #=========================================================================================    
    #=======================Merging total and ota isell data==================================
    format2 = df_total2.merge(df_ota,on='Date',how='left')
    format2.rename(columns={'Pickup':'OTA Pickup'},inplace=True)
    format2['Date'] = pd.to_datetime(format2['Date'],format='%Y-%m-%d')
    
    #-------------------------Merge total df otas with final format-----------------
    format3 = format2.merge(total_otas,on='Date',how='left')
    #-------------------------assign recommendations from total df-------------------
    format3['Recommended Rate'] = total_rec['Recommended Rate']
    format3['Date'] = pd.to_datetime(format3['Date'],format='%d-%b-%Y')
    format3.to_csv(r'E:\BeautiMode\Inputs\format2.csv')
    print('Final Combine iSell df returned')
#    return(format3)

total_ota_merging(htlname, ftr, iselldt, outcsvpath)