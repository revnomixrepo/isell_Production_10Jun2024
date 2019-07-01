import os
import re
import sys
import CMAs
import pandas as pd
import numpy as np
import iSell_fun_02
import iSellFormat2 as form2
import beautiMode
import directRecs
import monthlymodule as mnthprice
import seasonalmodule as czonprice
import GRID as grid
import simpleRecs as simp
import csv
import Leaf_Module as leaf


def Flow(masterpth,defaultpath,LRdate,accMan, accpath):
    basepath=defaultpath+'\\'+'InputData'
    masterpath = defaultpath+'\\'+'masters'
    beautipth = masterpth+'\\'+'iSell'
    #-----------------------Glossary sheet-----------------------------
    glossary = pd.read_excel(defaultpath+r'\masters\logo\Glossary.xlsx')
    
    #----------------------Master Input Conditions---------------------      

    inputmaster = pd.ExcelFile(accpath+'\\'+'InputConditionMaster_{}.xlsx'.format(accMan[0]))
    
    format2file = pd.read_excel(masterpath+'\\'+'Format2_iSells.xlsx')
    format2isells = list(format2file['HotelNames'])

    
    
    inputdf2 = pd.read_excel(inputmaster,'Accounts') #Accounts Sheet
    season_range = pd.read_excel(masterpth+'\\'+'season_master.xlsx')
    dow_weight = pd.read_excel(masterpth+'\\'+'dow_weights.xlsx') #dow weights sheet
    
    
    if accMan[0] == 'All':
        inputdf = pd.DataFrame(inputdf2)
        print('############# Preparing iSells for All Account Managers #################')
    else:
        inputdf = pd.DataFrame(inputdf2[inputdf2['AccManager'].isin(accMan)]) 
        print('############# Preparing iSells for {} #################'.format(accMan))
        
    
                           
    monthlyrates = pd.read_excel(inputmaster,'Monthly_MinRates') #Monthly_Rates Sheet
    
    
    monthlyjump = pd.read_excel(inputmaster,'Monthly_Jump')
    monthlymax = pd.read_excel(inputmaster,'Monthly_MaxRates')
    
    #========================================================================================================
    #============================Dow Weight DataFrame [Dow,ClusterNames....]=================================
    cldowlist=['ClusterName','Mon','Tue','Wed','Thu','Fri','Sat','Sun']   
    dow_cluster = pd.DataFrame(dow_weight.loc[:,cldowlist])
    dow_cluster.set_index('ClusterName',inplace=True)
    dow_cluster2 = dow_cluster.T
    dow_cluster2.reset_index(inplace=True)
    dow_cluster2.rename(columns={'index':'Dow'},inplace=True)  

    
    
    
    #============================Monthly==========================================================
    htlmonthlist=['hotelname','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
    #------------------Month MinRate DataFrame[Month,HotelNames...]------------------------------------
    monthMinRate = pd.DataFrame(monthlyrates.loc[:,htlmonthlist])
    monthMinRate.set_index('hotelname',inplace=True)
    monthMinRate2 = monthMinRate.T
    monthMinRate2.reset_index(inplace=True)
    monthMinRate2.rename(columns={'index':'Month'},inplace=True)  
    
    
    #------------------Monthly Jump DataFrame[Month, HotelNames...]---------------------------------------
    monthJump = pd.DataFrame(monthlyjump.loc[:,htlmonthlist])
    monthJump.set_index('hotelname',inplace=True)
    monthJump2 = monthJump.T
    monthJump2.reset_index(inplace=True)
    monthJump2.rename(columns={'index':'Month'},inplace=True)   
    
    
    #------------------Monthly MaxRate DataFrame[Month,HotelNames...]------------------------------------
    monthMaxRate = pd.DataFrame(monthlymax.loc[:,htlmonthlist])
    monthMaxRate.set_index('hotelname',inplace=True)
    monthMaxRate2 = monthMaxRate.T
    monthMaxRate2.reset_index(inplace=True)
    monthMaxRate2.rename(columns={'index':'Month'},inplace=True)   
    
    #==========================Seasonal========================================
    
    #--------------------from Seasonal Range--------------------------------------
    name_s1s=dict(zip(season_range['hotelname'],season_range['season1start date']))
    name_s1e=dict(zip(season_range['hotelname'],season_range['season1end date']))
    name_s2s=dict(zip(season_range['hotelname'],season_range['season2start date']))
    name_s2e=dict(zip(season_range['hotelname'],season_range['season2end date']))
    
    #--------------------seasonal minimum rates----------------------------------
    name_s1min = dict(zip(season_range['hotelname'],season_range['s1_minrate']))
    name_s2min = dict(zip(season_range['hotelname'],season_range['s2_minrate']))
    
    #--------------------seasonal maxrates---------------------------------------
    name_s1max = dict(zip(season_range['hotelname'],season_range['s1_maxrate']))
    name_s2max = dict(zip(season_range['hotelname'],season_range['s2_maxrate']))
    
    #-----------------------seasonal jumps-----------------------------------------
    name_s1jump = dict(zip(monthlyjump['hotelname'],monthlyjump['Season1']))
    name_s2jump = dict(zip(monthlyjump['hotelname'],monthlyjump['Season2']))
    
    #================================================================================================
    #================================================================================================
    
    ezeedates = pd.read_excel(masterpath+'\\'+'ezeedate_format.xlsx')
    jfacts = pd.read_excel(masterpath+r'\zFactors.xlsx')
    dropcol = pd.read_excel(masterpath+'\\'+'DropColumns.xlsx')
    print('All master files read !')


    ##=======================Dictionaries======================================
    #--------------------from Accounts-----------------------------------------
    name_accman = dict(zip(inputdf['hotelname'],inputdf['AccManager']))
    name_cap = dict(zip(inputdf['hotelname'],inputdf['cap']))
    name_maxcap=dict(zip(inputdf['hotelname'],inputdf['otacap']))
    name_msrate = dict(zip(inputdf['hotelname'],inputdf['msrate']))
    name_ftr=dict(zip(inputdf['hotelname'],inputdf['flowthrough']))
    name_rateplan= dict(zip(inputdf['hotelname'],inputdf['rateplan']))
    
    #RateOnCM flag
    name_chman = dict(zip(inputdf['hotelname'],inputdf['ChannelMan']))
    inputdf['RateOnCM'] =  inputdf['RateOnCM'].astype(int)
    name_cmflag = dict(zip(inputdf['hotelname'],inputdf['RateOnCM']))
    
    #phychological factor
    name_psy = dict(zip(inputdf['hotelname'],inputdf['PsychologicalFactor']))   
    
    name_hnf = dict(zip(inputdf['hotelname'],inputdf['HNF']))
    name_curr = dict(zip(inputdf['hotelname'],inputdf['Currency']))
    name_win=dict(zip(inputdf['hotelname'],inputdf['isellwindow']))
    name_win2=dict(zip(inputdf['hotelname'],inputdf['clientwindow(180)']))
    GridType = dict(zip(inputdf['hotelname'],inputdf['GridType']))
    priceType = dict(zip(inputdf['hotelname'],inputdf['PricingType']))
    pricejump = dict(zip(inputdf['hotelname'],inputdf['PriceJump'])) 
    htl_cluster=dict(zip(inputdf['hotelname'],inputdf['ClusterName']))
    
    ##=========================monthly and seasonal useMaxRate flags==========================
    month_useMax = dict(zip(monthlyrates['hotelname'],monthlyrates['use_MaxRate']))
    cson_useMax = dict(zip(season_range['hotelname'],season_range['use_MaxRate']))
    #------------------------useCeiling and useFloor-------------------------------------
    use_ceiling = dict(zip(inputdf['hotelname'],inputdf['use_CeilingRate']))
    use_floor = dict(zip(inputdf['hotelname'],inputdf['use_FloorRate']))
    #--------------------------------useGrid---------------------------------------------------
    use_Grid = dict(zip(inputdf['hotelname'],inputdf['use_Grid']))

    
    
    #-----------------jump types dataframe-------------------------------------
    jumpType = dict(zip(inputdf['hotelname'],inputdf['JumpType'])) 
    

    
    from datetime import datetime
    ddmmyy = datetime.now()
    tdayfold = ddmmyy.strftime("%d_%b_%Y")
    iselldt=ddmmyy.strftime("%d%b%Y")
    os.chdir(basepath+'\{}'.format('OutPut_CSV'))


    try:
        os.mkdir(tdayfold)
    except FileExistsError:
        pass
        

    sysdt=LRdate#str(input("Enter Last iSell Run Date for reading Last Report('mm/dd/yyyy'):"))
    sysdt2=pd.to_datetime(sysdt)
    lastfoldname=sysdt2.strftime('%d_%b_%Y')
    LRdt=sysdt2.strftime("%d%b%Y")
    print('All folders updated !!!')
    print('---------------------------------------------------')

    for sr, names in enumerate(inputdf['hotelname'],start=1):
        #-------------------format 2 name setting(flag)-----------------------------#
        if '_OTA' in names:
            format2flag = 1
        else:
            format2flag = 0
            pass
        
        #-------------------Dynamic Dictionaries-------------------------------------------
        #Hotel Cluster Weights
        clustName=htl_cluster[names]
        htl_dowWt = dict(zip(dow_cluster2['Dow'],dow_cluster2[clustName]))
        
        #----------------------------------------------------------------------------------
        print('{}.Creating {}_iSell ...'.format(sr,names))
        print('\tChannel Manager :{}'.format(name_chman[names]))
        isellrange = int(name_win[names])
        
        if name_chman[names] == 'Staah':
            cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')))
            staahfile = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xlsx')))
            staahfile.dropna(subset=['CheckIn Date','CheckOut Date'],inplace=True)
            pcdata=''
        elif name_chman[names] == 'AxisRooms':
            staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')))
            cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xls')))
            pcdata = pd.read_excel(basepath+'\{}\{}\{}'.format('Price_Calendar',tdayfold,names+str('_PC.xls')))
        elif name_chman[names] == 'BookingHotel':
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
            
        elif name_chman[names] == 'TravelClick':
                     
            #===========================Travel Click OTA Condition===============================
            if '_OTA' in names:
                staahfile2 = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names[:-4] + str('_OTAData.csv')))   
                staahfile2['Subchannel Desc'].fillna(value='blankval',inplace=True)
                staahfile2['Subchannel Desc'] = np.where(staahfile2['Subchannel Desc'] == 'blankval', staahfile2['Channel Name'],staahfile2['Subchannel Desc'])
                staahfile2.drop('Channel Name',axis=1,inplace=True)
                #---------------renamed 'Subchannel Desc' as Channel Name---------------------
                staahfile2.rename(columns={'Subchannel Desc':'Channel Name'},inplace=True)
                #---------------removing ['PMS','Brand.com'] from Channel Name---------------
                staahfile3 = staahfile2[~staahfile2['Channel Name'].isin(['PMS','Brand.com'])]
                staahfile = pd.DataFrame(staahfile3)
                
                cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names[:-4] + str('_CM.xlsx')),
                                   skiprows=[1, 2], quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names[:-4] + str('_PC.xlsx')))
                staahfile['Rooms'] = 1
                
            else:
                staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
                
            
                cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),
                                       skiprows=[1, 2], quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
                staahfile['Rooms'] = 1
                         
        elif name_chman[names] == 'Maximojo':
            staahfile = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xlsx')))
            cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')))
            pcdata=''
        elif name_chman[names] == 'Djubo':
            staahfile = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xlsx')),skiprows=1)
            cmdata=''
            pcdata=''
        elif name_chman[names] == 'eZee':
            checkIn = dict(zip(ezeedates['Hotel'],ezeedates['Checkin']))
            checkOut = dict(zip(ezeedates['Hotel'],ezeedates['Checkout']))
            
            staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')))
            staahfile.dropna(axis=0,subset=['Arrival','Dept'],inplace=True)
            staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'],format=checkIn[names])
            staahfile['Dept'] = pd.to_datetime(staahfile['Dept'],format=checkOut[names])        
            staahfile['Rooms']=1
            
            cmdata = pd.read_csv(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.csv')))
            pcdata=''

        elif name_chman[names] == 'LeafDover':
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            cmData1 = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),
                                    header=[1])
            # hnfData1 = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            # outpath = basepath + '\{}\{}'.format('HNF', tdayfold)

            # leaf.lhd(cmData1, hnfData1, outpath, names)
            # To add Leaf Dover (ota, cm)
            # import Report_Leaf_H as lhd

            # lhd.lhd(inventryStatus, forcast)

            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                    delimiter=",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,
                                    encoding='utf8')
            # cmdata = pd.DataFrame(staahfile)
            cmrates2 = pd.DataFrame(cmdata.loc[:, ['Date', 'CMRate']])
            cmrates2['Date'] = pd.to_datetime(cmrates2['Date'], format="%Y-%m-%d")

        elif name_chman[names] == 'UK':
            pcdata=''
            
            if names == 'Leaf Hotel Dover':
                cmData1 = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')),header=[1])
#                cmData1.to_csv(r'E:\All_In_One_iSell\Testing\cmdata1.csv')
                hnfData1 = pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')))
                outpath = basepath+'\{}\{}'.format('HNF',tdayfold)

                leaf.lhd(cmData1, hnfData1, outpath, names, isellrange)
                # To add Leaf Dover (ota, cm)
                # import Report_Leaf_H as lhd

                # lhd.lhd(inventryStatus, forcast)

                staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.csv')), delimiter =",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,encoding='utf8')
                cmdata = pd.DataFrame(staahfile)            
                cmrates2 = pd.DataFrame(cmdata.loc[:,['Date','CMRate']])
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'],format="%Y-%m-%d")      
                
            elif names == 'Best Western Clifton':
            
                staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.csv')), delimiter =",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,encoding='utf8')
                #staahfile.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\CM_Availability\staahfile.csv')
                
                cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')))        
                
                xls = pd.ExcelFile(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')))
                months = xls.sheet_names
                months2 = months[1:8]
                data=[]
                for m in months2:            
                    cmdf = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')),sheetname=m,skiprows=1)
        #            cmdf.rename(columns={'Unnamed: 0':'Date'},inplace=True)
                    cmdf2 = pd.DataFrame(cmdf.set_index('Unnamed: 0').T).reset_index()
                    
                    data.append(cmdf2)            
                cmrates=pd.concat(data)
        #        cmrates.reset_index(inplace=True)
                cmrates.rename(columns={'index':'Date'},inplace=True)
                        
                cmrates2 = pd.DataFrame(cmrates)
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'],format="%d/%m/%Y")
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'],format="%d-%b-%Y")
            
        
        elif name_chman[names] == 'TravelBook':
            pcdata=''
            staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.csv')), delimiter =",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,encoding='utf8')
            
            cmdata = pd.DataFrame(staahfile)
            
            cmrates2 = pd.DataFrame(cmdata.loc[:,['Date','CMRate']])
            cmrates2['Date'] = pd.to_datetime(cmrates2['Date'],format="%Y-%m-%d")        
        
        
        elif name_chman[names] == 'SiteMinder':
            staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')))
            staahfile['Total Amount'] = staahfile['Total Amount'].str.extract('(\d+)').astype(int)
            staahfile['Rooms']=1
            
            cmdata=''
            pcdata=''
            
        elif name_chman[names] == 'AsiaTech':
            staahfile = pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')), delimiter =",", index_col=False, header=0)
            cmdata=''
            pcdata=''
            
        elif name_chman[names] == 'BookingCentre':
            staahfile2 = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xlsx')),skiprows=9)
            #staahfile2['Cost2']=staahfile2['Cost'].apply(lambda x: x.str.replace(',',''))
            staahfile2['Cost'] = staahfile2['Cost'].str.replace('₨','')
          
            staahfile2['Cost'] = pd.to_numeric(staahfile2['Cost'].apply(lambda x: re.sub(',', '', str(x))))
            #staahfile2.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\OTA_Data\16_Oct_2018\staahfile.csv')
            staahfile2['Rooms']=1
            staahfile2['Status']=staahfile2['Status'].fillna(value=1)
            staahfile =  pd.DataFrame(staahfile2[staahfile2.Status != 1])
            
            cmdata=''
            pcdata=''
            
        elif name_chman[names] == 'ResAvenue':
            staahfile2 = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xls')),skiprows=2)
            staahfile2['Booking Status']=staahfile2['Booking Status'].fillna(value=1)
            staahfile =  pd.DataFrame(staahfile2[staahfile2['Booking Status'] != 1])
            
            cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xls')),skiprows=1)
            pcdata = pd.read_excel(basepath+'\{}\{}\{}'.format('Price_Calendar',tdayfold,names+str('_PC.xls')),skiprows=3)       
            
        elif name_chman[names] == 'RezNext':
            staahfile = pd.read_excel(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.xlsx')))
            cmdata = pd.read_excel(basepath+'\{}\{}\{}'.format('CM_Availability',tdayfold,names+str('_CM.xlsx')))    
        
        
        else:
            print("There is no such Channel Manager Added in Input Conditions !!!")               
            
        #==================================format2 name setting====================================================
        if format2flag == 1:
            rsfile = pd.read_csv(basepath+'\{}\{}\{}'.format('RS_Data',tdayfold,names[:-4]+str('_RSData.csv')),encoding='cp1252')
            dc = pd.read_excel(basepath+'\{}\{}'.format('Demand_Calendar',names[:-4]+str('.xlsx')))
            #---------------------------------LastReport name should have OTA-------------------------------------------
            df_LR = pd.read_csv(basepath+'\{}\{}\{}'.format('OutPut_CSV',lastfoldname,str('iSell_')+names+str('_{}.csv'.format(LRdt))))
            #------------------------------------------------------------------------------------------------------------
            if use_Grid[names] == 1:
                df_PG = pd.read_excel(basepath+'\{}\{}'.format('Pricing_Grid',names[:-4]+str('_PG.xlsx')))
            else:
                pass
            
            rateshopfile = pd.read_csv(basepath + '\{}\{}\{}'.format('RateShop', tdayfold, names[:-4] + str('_RateShop.csv')))
        
        else:       
            rsfile = pd.read_csv(basepath+'\{}\{}\{}'.format('RS_Data',tdayfold,names+str('_RSData.csv')),encoding='cp1252')
            dc = pd.read_excel(basepath+'\{}\{}'.format('Demand_Calendar',names+str('.xlsx')))
            df_LR = pd.read_csv(basepath+'\{}\{}\{}'.format('OutPut_CSV',lastfoldname,str('iSell_')+names+str('_{}.csv'.format(LRdt))))
            
            if use_Grid[names] == 1:
                df_PG = pd.read_excel(basepath+'\{}\{}'.format('Pricing_Grid',names+str('_PG.xlsx')))
            else:
                pass
            
            rateshopfile = pd.read_csv(basepath + '\{}\{}\{}'.format('RateShop', tdayfold, names + str('_RateShop.csv')))
        #================================================================================================================
            
        
        #---------------------------Frame('Date','Dow')-----------------------------------------------
        tday = ddmmyy.strftime("%d-%b-%Y")       
        index=pd.date_range(tday,periods= isellrange)
        frame=pd.DataFrame({'Date':index})
        frame['Dow'] = frame['Date'].apply(lambda x:x.strftime('%a')) 
        
        #---------------------# df_total,df_ota,df_ttlsold #--------------------------------------------
        
        if name_chman[names] in ['UK','TravelBook']:
            pass   
            
            
        else:        
            df_total,df_ota,df_ttlsold=iSell_fun_02.dfconv(defaultpath,staahfile,names,name_chman[names])
            print('\tdfconv done !!!')

            df_ttlsold.fillna(value=0,inplace=True)
            #print(type(df_ttlsold))
            #df_ttlsold.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\ttlsold.csv')

            #df_all
            df_all = iSell_fun_02.occframe(df_total,isellrange)
            df_ota2 = df_ota.pivot(index='occupancydate', columns='Channel',values='No_of_Rooms')
            df_ota2.reset_index(inplace=True)

            #df_all2
            df_all2= pd.merge(df_all,df_ota2,on='occupancydate',how='left')
            df_all2.fillna(value=0,inplace=True)
            df_all3=df_all2.rename(columns={'occupancydate':'Date','No_of_Rooms':'OTA_Sold','RevPD':'OTA Revenue'})
            ddff=df_all3.set_index('Date')
            #df_all3.to_csv(r'E:\iSell_Project\Djubo\df_all3.csv')

            otabreak=pd.DataFrame(ddff.iloc[:,2:])
            otabreak.reset_index(inplace=True)

            otasold =pd.DataFrame(ddff.loc[:,'OTA_Sold'])
            otasold.reset_index(inplace=True)

            otarev = pd.DataFrame(ddff.loc[:,'OTA Revenue'])
            otarev.reset_index(inplace=True)
        
        
    #----------------------# df merging #---------------------------------------------


        #1)---------------# DC #------------------------------------------------------------
        dc2=iSell_fun_02.frame(dc,isellrange)
        dc3_1=dc2.loc[:,['Date','Event']]
        dc3 = pd.merge(frame,dc3_1,on='Date',how='left')
        dc3['Capacity']=name_cap[names]
        print('\tDC attached !')

        #2)---------------# CM_Avail #----------------------------------------------
        
        if name_chman[names] == 'Djubo':
            cap = int(name_cap[names])
            print(cap)
            rmsavail,cmdf = CMAs.CM_Djubo(df_ttlsold,cap,isellrange)
            
        elif name_chman[names] == 'SiteMinder':
            cap = int(name_cap[names])
            print(cap)
            rmsavail,cmdf = CMAs.CM_Djubo(df_ttlsold,cap,isellrange)
            
        elif name_chman[names] == 'BookingCentre':
            cap = int(name_cap[names])
            print(cap)
            rmsavail,cmdf = CMAs.CM_Djubo(df_ttlsold,cap)        
            
        elif name_chman[names] == 'AsiaTech':
            cap = int(name_cap[names])
            print(cap)
            rmsavail,cmdf = CMAs.CM_Djubo(df_ttlsold,cap,isellrange)
        
        elif name_chman[names] == 'UK':
            #attch avail, OTA_Sold and CM_Rate
            if names == 'Leaf Hotel Dover':
                #-------------similar to getfam----------------
                rmsavail,cmdf = CMAs.CM_TB(staahfile,cmrates2)  
            elif names =='Best Western Clifton':
                rmsavail,cmdf = CMAs.CM_UK(staahfile,cmrates2,name_msrate[names],isellrange)

            
        elif name_chman[names] == 'TravelBook':
            rmsavail,cmdf = CMAs.CM_TB(staahfile,cmrates2)           
            
        elif name_chman[names] == 'RezNext':
            #attch avail, OTA_Sold and CM_Rate
            rmsavail,cmdf = CMAs.CM_RezNext(cmdata,name_msrate[names],name_ftr[names],name_rateplan[names],isellrange)
            
        else:
            rmsavail,cmdf = CMAs.CM_Avails(cmdata,name_msrate[names],name_ftr[names],name_chman[names],pcdata,name_rateplan[names],isellrange)
            
         
    #    df_ttlsold.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\ttlsold2.csv')
    #    rmsavail.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\ttlsold3.csv')
    #    
        iSelldf1 = iSell_fun_02.merging(dc3,rmsavail)
        print('\tCM And FTR added !!!')
        if name_chman[names] in ['UK','TravelBook']:
            iSelldf2 = iSelldf1
            print('\tOTA Sold Added')
        else:
            iSelldf2 = iSell_fun_02.merging(iSelldf1,otasold)
            print('\tOTA Sold Added')
            
        #==================== HNF On The FLY =======================================
        if GridType[names] == 'Hybrid':
            flyHNF = pd.DataFrame(iSelldf2.loc[:,['Date','Capacity','Rooms Avail To Sell Online']])
            flyHNF['Sold'] = flyHNF['Capacity'] - flyHNF['Rooms Avail To Sell Online']
            flyHNF['Date'] = flyHNF['Date'].apply(lambda x:x.strftime("%d-%b-%Y"))            
            flyHNF2 = pd.DataFrame(flyHNF.loc[:,['Date','Sold']])
            flyHNF2.to_excel(basepath +'\\'+'HNF\{}\{}_HNF.xlsx'.format(tdayfold,names))
            print("\tHNF On the fly Calculated")
        else:
            pass
        
        

        #3)---------------# Last Report #------------------------------------------
        LRfinal = iSell_fun_02.dfLR(df_LR,name_chman[names])
        LRfinal2 = iSell_fun_02.frame(LRfinal,isellrange)       
        
        #======================# Last SeasonalRate #=====================================
        cmflag = name_cmflag[names]
        if cmflag == 0:
            Last_szrates = pd.DataFrame(df_LR.loc[:,['Date','SeasonalRate_y']])
            Last_szrates.rename(columns={'SeasonalRate_y':'Last_szrate'},inplace=True)      
            #Last_szrates.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\lastszrate1.csv')  
            
            try:
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'],format="%d-%b-%Y")
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'],format='%Y-%m-%d')
            except:
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'])
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'],format='%Y-%m-%d')
                
            
            print('\tRead last Report with seasonal rates !!!')
            #Last_szrates.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\lastszrate2.csv') 
        elif cmflag == 1:
            Last_szrates = 'NotRequired'               
        else:
            print('\tPlease Check RateOnCM column in InputCondition, It should be 1 or 0')
            sys.exit()
            
        #4)========================== Pickup =================================================
        iSelldf2_1 = iSell_fun_02.merging(iSelldf2,LRfinal2)
#        iSelldf2_1.to_csv(r'D:\Hrishikesh\All_In_One_iSell\masters\iSelldf2_1.csv')
        iSelldf2_1['Pickup'] = iSelldf2_1['OTA_Sold']-iSelldf2_1['Last_OTASOLD']
        iSelldf2_1.fillna(value=0,inplace=True)
        
        iSelldf2 = iSelldf2_1.drop(['Last_OTASOLD','LAvg'],axis=1)       
        
        print('\tPickup Added !!!')
        
        #5)---------------# OTA Revenue #------------------------------------------
        
        if name_chman[names] in ['UK','TravelBook']:
            iSelldf4=iSell_fun_02.merging(iSelldf2,cmdf)
            
            print('\tRevenue, ADR, CM Rate Added !!!')
        else:        
            iSelldf3 = iSell_fun_02.merging(iSelldf2,otarev)
            print('\tRevenue Added !!!')
            
            #6)--------------# ADR #--------------------------------------------------
            
            iSelldf3['ADR OTB']=(iSelldf3['OTA Revenue']/iSelldf3['OTA_Sold']).round(0)
            iSelldf3['ADR OTB'].fillna(value=0,inplace=True)
            print('\tADR Added !!!')

            #7)--------------# Rate on CM #---------------------------------------------------
            iSelldf4 = iSell_fun_02.merging(iSelldf3,cmdf)  
            
            print('\tRate on CM Added !!!')
            
        
        print('\t-----Pricing Conditions------')
            
        #8)-------------# Pricing Type #------------------------------------------------------
        #phychological factor        
        psy_fact = name_psy[names]
        
        print('\tGrid Type is :{}'.format(GridType[names]))
        
        if priceType[names] == 'Monthly':
            #--------------Monthly Dynamic Dictionaries----------------------------------------            
            #Hotel Monthly Min Rate
            month_minR = dict(zip(monthMinRate2['Month'],monthMinRate2[names]))            
            #-------(*print monthly min rates*)---------
#            print(month_minR)
            #---------------------------------------
            #Hotel Monthly Jumps
            month_jump = dict(zip(monthJump2['Month'],monthJump2[names]))
            
            if month_useMax[names] == 1:
                #Hotel Monthly Max Rate
                month_maxR = dict(zip(monthMaxRate2['Month'],monthMaxRate2[names]))
            elif use_ceiling[names] ==1:
                month_maxR = dict(zip(monthMaxRate2['Month'],monthMaxRate2[names]))                
            else:
                month_maxR=''          
            
            
            
            print('\tPricing Type is :{}'.format(priceType[names]))
            iSelldf44,isellforgrid=mnthprice.month_minmax(names,iSelldf4,month_minR,htl_dowWt,jfacts,month_jump,htl_cluster,jumpType[names],month_maxR,month_useMax[names],use_ceiling[names])
            
            #-----------------Min, min, Max, max, (4 columns) fetching after Rate on CM
#            iSelldf44.to_csv(r'E:\All_In_One_iSell\Testing\iSelldf44_{}.csv'.format(names))
            #---------------------------------------------------------------------------------
            print('\tMonthly Rates Fetched')
            
            if use_Grid[names] == 1:
                pgdf = pd.DataFrame(df_PG)
            else:
                pgdf=grid.Gridcreator(names,isellforgrid,month_minR,htl_dowWt,clustName,month_jump,jfacts,jumpType[names],psy_fact,priceType[names])     
                if names in format2isells:
                    #-------------dump grid for format2 iSell----------------------------
                    pgdf.to_excel(basepath+'\{}\{}'.format('Pricing_Grid',names+'_PG.xlsx'))
                else:
                    pass
                    
            
            
        elif priceType[names] == 'Seasonal':
            print('\tPricing Type is :{}'.format(priceType[names]))
            #-----------------Seasonal Range, Minimum Rates, MaxRates Jumps------------------------
            s1start = name_s1s[names]
            s1end = name_s1e[names]
            s2start = name_s2s[names]
            s2end =name_s2e[names]
            #czon range
            csonrange = [s1start,s1end,s2start,s2end]
            
            s1min = name_s1min[names]
            s2min = name_s2min[names]
            
            #czonal min rates
            czonminrates=[s1min,s2min]
            czonminratesdict={'S1':czonminrates[0],'S2':czonminrates[1]}
            
            #czonmaxrates
            czonmaxrates=[name_s1max[names],name_s2max[names]]
            
            s1jump=name_s1jump[names]
            s2jump=name_s2jump[names]
            #czonal jumps
            czonjumps=[s1jump,s2jump]
            czonjumpsdict = {'S1':czonjumps[0],'S2':czonjumps[1]} 
            
            
            iSelldf44,isellforgrid=czonprice.czonmin_max(names,iSelldf4,csonrange,czonminrates,htl_dowWt,jfacts,czonjumps,htl_cluster,jumpType[names],czonmaxrates,cson_useMax[names])
            
#            isellforgrid.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\isellforgrid.csv')
            
            print('\tSeasonal Rates Fetched')   
            
            if use_Grid[names] == 1:
                pgdf = pd.DataFrame(df_PG)
            else:
                pgdf=grid.Gridcreator(names,isellforgrid,czonminratesdict,htl_dowWt,clustName,czonjumpsdict,jfacts,jumpType[names],psy_fact,priceType[names])          
            
            
            
        else:
            print('\tPricing Type is not defined')
            sys.exit()
        print("\tAll Grids Generated")
    
        #=============================================================================================
        #--------------------------------PRICING ALGOS------------------------------------------------
        #=============================================================================================
        
        #===========================1) Simple Pricing =================================================
        
        if GridType[names] == 'Simple':
            iSelldf5,szRates = simp.simRecs(names,iSelldf44,int(pricejump[names]),Last_szrates,name_chman[names],name_cmflag[names],name_curr[names],psy_fact,use_ceiling[names],use_floor[names])
            #------getting iSelldf5 and szRates from Simple GridType-----------------------
        else:        
            #=======================2) HNF Based Pricing===================================================
            if name_hnf[names]=='Yes':
                #-----------------------I)UK----------------------------------------------             
                if name_chman[names] == 'UK':
                    try:
                        df_hnf = pd.read_csv(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.csv')), delimiter =",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,encoding='utf8')
                    except FileNotFoundError:
                        print('HNF Not found for UK, It is mandatory for UK')
                        sys.exit()
                        
                    if names == 'Leaf Hotel Dover':
                        htlsold,htlavail = iSell_fun_02.TBhnfconv(df_hnf,name_maxcap[names],isellrange) 
                    else:
                        htlsold,htlavail = iSell_fun_02.UKhnfconv(df_hnf,name_maxcap[names],isellrange)     
                        
#                    htlsold,htlavail = iSell_fun_02.UKhnfconv(df_hnf,name_maxcap[names],isellrange) 
                    
                    iSelldf444_1 = iSell_fun_02.merging(iSelldf44,htlsold)
                    iSelldf444 = iSell_fun_02.merging(iSelldf444_1,htlavail)
                    iSelldf5,szRates=iSell_fun_02.hnf_rcpalgo(iSelldf444,name_ftr[names],name_maxcap[names],name_curr[names],name_chman[names],Last_szrates,psy_fact,name_cmflag[names],use_ceiling[names],use_floor[names])
                    #-----------getting iSelldf5 and szRates from UK---------------------------------
                    print('\tUK Recommendations added as per HNF updated !!!')
                
                #-----------------------I)TB----------------------------------------------          
                        
                elif name_chman[names] =='TravelBook':
                    df_hnf = pd.read_csv(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.csv')), delimiter =",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,encoding='utf8')
                    htlsold,htlavail = iSell_fun_02.TBhnfconv(df_hnf,name_maxcap[names],isellrange) 
                    
                    iSelldf444_1 = iSell_fun_02.merging(iSelldf44,htlsold)
                    iSelldf444 = iSell_fun_02.merging(iSelldf444_1,htlavail)
                    iSelldf5,szRates=iSell_fun_02.hnf_rcpalgo(iSelldf444,name_ftr[names],name_maxcap[names],name_curr[names],name_chman[names],Last_szrates,psy_fact,name_cmflag[names],use_ceiling[names],use_floor[names]) 
                    #-----------getting iSelldf5 and szRates from UK---------------------------------
                    print('\tTB Recommendations added as per HNF updated !!!')
                    
                #-----------------II) HNF based Direct Pricing --------------------------------------    
                else:                 
                    
                    if GridType[names] == 'Direct':
                        cmflag = name_cmflag[names]
                        df_hnf = pd.read_excel(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.xlsx')))
                        print("\tHNF read for {}".format(names))
                        #----------------------calculate hotel sold and availability frames------------------------
                        htlsold,htlavail=iSell_fun_02.hnfconv(df_hnf,name_cap[names],isellrange)
                        
                        iSelldf444_1 = iSell_fun_02.merging(isellforgrid,htlsold)
                        iSelldf444 = iSell_fun_02.merging(iSelldf444_1,htlavail)
                        iSelldf5,szRates = directRecs.dRecs(iSelldf444,pgdf,isellrange,Last_szrates,cmflag,priceType[names],name_hnf[names],name_ftr[names])                
                        print('\tDirect Recommendations added as per HNF updated !!!')
                        #------getting iSelldf5 and szRates from Direct GridType-----------------------
                        
                    #---------------------III) HNF Based Normal Pricing #------------------------------------------    
                    else:
                        try:
                            df_hnf = pd.read_excel(basepath+'\{}\{}\{}'.format('HNF',tdayfold,names+str('_HNF.xlsx')))
                        except FileNotFoundError:
                            print('HNF Not Found please update HNF or set No in HNF column of Input Conditions Master')
                            sys.exit()
                        
                        print("\tHNF read for {}".format(names))
                        htlsold,htlavail=iSell_fun_02.hnfconv(df_hnf,name_cap[names],isellrange)                        
                            
                        iSelldf444_1 = iSell_fun_02.merging(iSelldf44,htlsold)
                        iSelldf444 = iSell_fun_02.merging(iSelldf444_1,htlavail)
                        iSelldf5,szRates=iSell_fun_02.hnf_rcpalgo(iSelldf444,name_ftr[names],name_maxcap[names],name_curr[names],name_chman[names],Last_szrates,psy_fact,name_cmflag[names],use_ceiling[names],use_floor[names])
                        #------getting iSelldf5 and szRates from Normal GridType-----------------------
                        print('\tNormal Recommendations added as per HNF updated !!!')   
                    
            #==========================3) Non HNF Based Pricing=======================================    
            else:
                if GridType[names] == 'Direct':
                    #-----------------I) Direct Recommendations(Non HNF Based) -----------------------------------
                    cmflag = name_cmflag[names]
                    iSelldf5,szRates = directRecs.dRecs(isellforgrid,pgdf,isellrange,Last_szrates,cmflag,priceType[names],name_hnf[names],name_ftr[names])
                    print("\tDirect Recommendations added (Non HNF)")                
                else:                        
                    #-------------------II) Normal Pricing(Non HNF Based) #------------------------------------------------
                    iSelldf5,szRates=iSell_fun_02.nonHNF_rcpalgo(iSelldf44,name_ftr[names],name_maxcap[names],name_curr[names],name_chman[names],Last_szrates,psy_fact,name_cmflag[names],use_ceiling[names],use_floor[names])
                    print('\tNormal Recommendations added (Non HNF)')         
            
            #=========================================================================================            
            
                
        

        print('\t-----------------------------')
        #=================== Merge Current Seasonal rates with iSell for cmflag = 0  ==============================================
        if cmflag == 0:
            iSelldf55 = iSell_fun_02.merging(iSelldf5,szRates)   
            print("\tSeasonal Rates merged with the iSell")            
        elif cmflag == 1:
            iSelldf55 = pd.DataFrame(iSelldf5)
        else:
            print('\tRateOnCM is not set in input conditions, it should be 0 or 1')
            sys.exit()
       
        #=====================================================================================================
                     
        
        #9)---------------------# Rate Shop #--------------------------------------  
        lrate4,rstable2,cavg=iSell_fun_02.RateShop(rsfile,isellrange)
        iSelldf6_1 = iSell_fun_02.merging(iSelldf55,lrate4)
        iSelldf6 = iSell_fun_02.merging(iSelldf6_1,rstable2)
        print('\tRateshop added !!!')
        
        #10)--------------------# Market Trend #-------------------------
        lavg = LRfinal.loc[:,['Date','LAvg']]
        iSelldf7_1 = iSell_fun_02.merging(iSelldf6,lavg)
        iSelldf7 = iSell_fun_02.merging(iSelldf7_1,cavg)
        iSelldf7['Market Trend'] = iSelldf7.loc[:,'CAvg']-iSelldf7.loc[:,'LAvg']
        iSelldf7['Market Trend'] = iSelldf7['Market Trend'].fillna(value=0)	
        iSelldf7.drop(['LAvg', 'CAvg'],axis=1,inplace=True)
        print('\tMarket Trend added !!!')
        
        if name_chman[names] in ['UK','TravelBook']:
            iSelldf7.rename(columns={'OTA Revenue':'Revenue'},inplace=True)
            iSelldf8 = iSelldf7
        else:    
            iSelldf8 = iSell_fun_02.merging(iSelldf7,otabreak)
            print('\tOTA Data added !!!')
        
        if name_cmflag[names] == 0:
            iSelldf8 = iSell_fun_02.merging(iSelldf8,szRates)
        else:
            pass
        
        
        collist=['Season']
        try:
            iSelldf9_1=iSelldf8.drop(collist,axis=1)
        except:
            iSelldf9_1=pd.DataFrame(iSelldf8)
         
#        print('Season deleted')
        iSelldf9 = pd.DataFrame(iSelldf9_1.iloc[:int(isellrange),:])
        iSelldf10 = iSelldf9.round(0)
        iSelldf10['Date'] = iSelldf10['Date'].apply(lambda x:x.strftime("%d-%b-%Y"))
        
        #11)-------------------------# Drop col list #------------------------------
        if name_hnf[names] == 'Yes':
            iSelldf10.drop('Rooms Avail To Sell Online',axis=1,inplace=True)
        else:
            pass         
    
        colname = list(dropcol[name_chman[names]])
        colnames = [n for n in colname if str(n) != 'nan']
#        print(colnames)
        try:
            iSelldf10.drop(colnames,axis=1,inplace=True)
        except:
            pass
        
        #12)--------------------# Adoption #------------------------------------------   
        finaladop = iSell_fun_02.Adopcal(iSelldf10,179,89)
#        print(finaladop)
        print("\tAdoption calculated !!!")          
                       
        
#        #========================reset name again for format2(check flag)=========================
#        if format2flag == 1:
#            names = names+'_OTA'
#        else:
#            pass
        #==============================================================================
        #13)-----------------#Rate on CM check and iSell CSV dump #-------------------------------------
        if name_cmflag[names] ==0:           
            iSelldf10.drop('SeasonalRate_x',axis=1,inplace=True)
            
            try:
                iSelldf10.drop('No',axis=1,inplace=True)
            except:
                pass
                
            iSelldf10.to_csv(basepath+'\\'+'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold,names,iselldt))
            print('----------{}_{}_iSell generated_#{} !!!----------------'.format(sr,names,name_chman[names]))
            beautiMode.isellbeautify(defaultpath, iSelldf10,names,beautipth,name_win2[names],isellrange,glossary,name_ftr[names],pgdf,finaladop,name_accman[names],rateshopfile, name_cap[names])

        
        elif name_cmflag[names] == 1:
                        
            if (iSelldf10['Rate on CM'].sum() == 0) :
                iSelldf10.to_csv(basepath+'\\'+'OutPut_CSV\{}\iSell_{}_{}_BAD.csv'.format(tdayfold,names,iselldt))
                beautiMode.isellbeautify(defaultpath, iSelldf10,names,beautipth,name_win2[names],isellrange,glossary,name_ftr[names],pgdf,finaladop,name_accman[names],rateshopfile, name_cap[names])

            else :
                iSelldf10.to_csv(basepath+'\\'+'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold,names,iselldt))
                beautiMode.isellbeautify(defaultpath, iSelldf10,names,beautipth,name_win2[names],isellrange,glossary,name_ftr[names],pgdf,finaladop,name_accman[names],rateshopfile, name_cap[names])
            
            print('----------{}_{}_iSell Generated _#{} !!!----------------'.format(sr,names,name_chman[names]))
        else:
            print('Please set 0 or 1 to RateOnCM column of Accounts sheet')
            sys.exit()   
        
        #14)===========================Format2 Call==========================================
        if format2flag == 1:
            outcsvpath = basepath+'\\'+'OutPut_CSV\{}'.format(tdayfold)            
            combine_iSell,finaladop = form2.total_ota_merging(names[:-4] ,name_ftr[names], iselldt, outcsvpath)
            combine_iSell.to_csv(basepath+'\\'+'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold,names[:-4]+'_Combine',iselldt))
            print("Combine iSell dumped for {}".format(names[:-4]))
            beautiMode.isellbeautify(defaultpath, combine_iSell, names[:-4]+'_Combine', beautipth, int(name_win2[names]), isellrange, glossary, name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile, name_cap[names])
        else:
            pass
            
            
            
    print("################## ALL iSell Generated for {} , Thanks ! ########################".format(accMan))




    
    
        
    
    
    
    
