import pandas as pd
import beautiMode as bM
import iSell_fun_02 as ifun
from datetime import datetime

std_path = r'E:\iSell_Project\All_In_One_iSell'

#------------------------read format2 list-------------------------------------
isell_format2 = pd.read_excel(std_path+r'\masters\Format2_iSells.xlsx')

tday = datetime.now()
iselldt = tday.strftime("%d%b%Y")
fold_dt = tday.strftime("%d_%b_%Y")
outcsvpath = std_path+r'\InputData\OutPut_CSV\{}'.format(fold_dt)

format2_isells = list(isell_format2['HotelNames'])
masterfile = pd.ExcelFile(std_path+r'\masters\InputConditionMaster.xlsx')
accounts = pd.read_excel(masterfile,sheet_name='Accounts')
filter_accounts = pd.DataFrame(accounts[accounts['hotelname'].isin(format2_isells)])


##=======================Dictionaries======================================
#--------------------from Accounts-----------------------------------------
name_accman = dict(zip(filter_accounts['hotelname'],filter_accounts['AccManager']))
name_cap = dict(zip(filter_accounts['hotelname'],filter_accounts['cap']))
name_ftr=dict(zip(filter_accounts['hotelname'],filter_accounts['flowthrough']))    
name_win=dict(zip(filter_accounts['hotelname'],filter_accounts['isellwindow']))
name_win2=dict(zip(filter_accounts['hotelname'],filter_accounts['clientwindow(180)'])) 


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
    
    #==================combine isell to test===================================
#    format3.to_csv(r'E:\BeautiMode\Inputs\format2.csv')
    #==========================================================================
    print('Final Combine iSell df returned')
    format4 = format3.rename(columns={'Hotel Pickup':'Pickup'})
    finaladop = ifun.Adopcal(format4,179,89)
    return(format3,finaladop)

   
#=================call total_ota_merging and beautimode========================    
for name in isell_format2['HotelNames']:
    isellrange = int(name_win[name])
    combine_iSell,finaladop = total_ota_merging(name, name_ftr[name], iselldt, outcsvpath)    
    #-------------------------------------------------------------------------#
    beautipth = std_path+r'\masters\iSell'
    
    glossary = pd.read_excel(std_path+r'\masters\logo\Glossary.xlsx')
    pgdf = pd.read_excel(std_path+r'\InputData\Pricing_Grid\{}_PG.xlsx'.format(name))
    rateshopfile = pd.read_csv(std_path+r'\InputData\RateShop\{}\{}_RateShop.csv'.format(fold_dt,name))
    #-------------------------------------------------------------------------#    
    bM.isellbeautify(std_path, combine_iSell, name+'_Combine', beautipth, int(name_win2[name]), isellrange, glossary, name_ftr[name], pgdf, finaladop, name_accman[name], rateshopfile, name_cap[name])
            
    


