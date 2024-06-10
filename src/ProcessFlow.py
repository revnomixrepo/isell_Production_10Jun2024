"""
Created on Wed Jan 16 16:48:13 2019
@author: revse

Updated on Thu July 28 2022
@Yadnesh Kolhe
"""

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
import newpatch_functionality as npf
import warnings
warnings.filterwarnings('ignore')
import send_att_mail as mail
import Rm_type as rt
from datetime import date,timedelta
from datetime import datetime
import time
import os.path
from os import path


def Flow(masterpth, defaultpath, LRdate, accMan, accpath, logflag, mstr_flag='No', hnf_flag='No'):
    import logging

    from datetime import datetime
    ddmmyy = datetime.now()
    tdayfold = ddmmyy.strftime("%d_%b_%Y")
    iselldt = ddmmyy.strftime("%d%b%Y")

    cm_room_type_df = pd.DataFrame()
    # ================================Logger Addition===================================
    logpth = defaultpath + '\\' + 'logs'
    # ---------------------------------log flag-----------------------------------------------
    if logflag == 'DEBUG':
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename=logpth + '\\' + 'iSell_{}_Debug_{}.log'.format(iselldt, accMan),
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename=logpth + '\\' + 'iSell_{}_Info_{}.log'.format(iselldt, accMan), level=logging.INFO)

    logging.warning('is when this event was logged by {}.'.format(accMan))
    logging.warning('Logging Mode: {}.'.format(logflag))
    logging.info('=======================================================================')

    logging.debug('------------------------------------------------------------')
    logging.debug('Module:ProcessFlow, SubModule:Flow')
    # =====================================================================================

    basepath = defaultpath + '\\' + 'InputData'
    masterpath = defaultpath + '\\' + 'masters'
    beautipth = masterpth + '\\' + 'iSell'
    # -----------------------Glossary sheet-----------------------------
    glossary = pd.read_excel(defaultpath + r'\masters\logo\Glossary.xlsx')

    # ----------------------Master Input Conditions---------------------

    if mstr_flag == 'Yes':
        inputmaster = pd.ExcelFile(masterpth + '\\' + 'InputConditionMaster.xlsx')
        inputdf2 = pd.read_excel(inputmaster, 'Accounts')  # Accounts Sheet
        if hnf_flag == 'No':
            inputdf2 = inputdf2[inputdf2['HNF'] == 'No']
        elif hnf_flag == 'Yes':
            inputdf2 = inputdf2[inputdf2['HNF'] == 'Yes']
        else:
            print('please select hnf flag')
    else:
        inputmaster = pd.ExcelFile(accpath + '\\' + 'InputConditionMaster_{}.xlsx'.format(accMan[0]))
        inputdf2 = pd.read_excel(inputmaster, 'Accounts')  # Accounts Sheet
    format2file = pd.read_excel(masterpath + '\\' + 'Format2_iSells.xlsx')
    format2isells = list(format2file['HotelNames'])

    inputdf2 = pd.read_excel(inputmaster, 'Accounts')  # Accounts Sheet
    season_range = pd.read_excel(masterpth + '\\' + 'season_master.xlsx')
    dow_weight = pd.read_excel(masterpth + '\\' + 'dow_weights.xlsx')  # dow weights sheet
    cm_colname = pd.read_excel(masterpth + '\\' + 'cm_master.xlsx')  # cm col name


    if accMan[0] == 'All':
        inputdf = pd.DataFrame(inputdf2)
        logging.info('############# Preparing iSells for All Account Managers #################')
    else:
        inputdf = pd.DataFrame(inputdf2[inputdf2['AccManager'].isin(accMan)])
        logging.info('############# Preparing iSells for {} #################'.format(accMan))
        logging.debug('InputConditionMaster_{} File ::'.format(accMan))
        logging.debug(inputdf)

    monthlyrates = pd.read_excel(inputmaster, 'Monthly_MinRates')  # Monthly_Rates Sheet

    monthlyjump = pd.read_excel(inputmaster, 'Monthly_Jump')
    monthlymax = pd.read_excel(inputmaster, 'Monthly_MaxRates')

    # ========================================================================================================
    # ============================Dow Weight DataFrame [Dow,ClusterNames....]=================================
    cldowlist = ['ClusterName', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_cluster = pd.DataFrame(dow_weight.loc[:, cldowlist])
    dow_cluster.set_index('ClusterName', inplace=True)
    dow_cluster2 = dow_cluster.T
    dow_cluster2.reset_index(inplace=True)
    dow_cluster2.rename(columns={'index': 'Dow'}, inplace=True)
    logging.debug('dow_cluster dataframe ::')
    logging.debug(dow_cluster2)

    # ============================Monthly==========================================================
    htlmonthlist = ['hotelname', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # ------------------Month MinRate DataFrame[Month,HotelNames...]------------------------------------
    monthMinRate = pd.DataFrame(monthlyrates.loc[:, htlmonthlist])
    monthMinRate.set_index('hotelname', inplace=True)
    monthMinRate2 = monthMinRate.T
    monthMinRate2.reset_index(inplace=True)
    monthMinRate2.rename(columns={'index': 'Month'}, inplace=True)
    logging.debug('MinRate dataframe ::')
    logging.debug(monthMinRate2)

    # ------------------Monthly Jump DataFrame[Month, HotelNames...]---------------------------------------
    monthJump = pd.DataFrame(monthlyjump.loc[:, htlmonthlist])
    monthJump.set_index('hotelname', inplace=True)
    monthJump2 = monthJump.T
    monthJump2.reset_index(inplace=True)
    monthJump2.rename(columns={'index': 'Month'}, inplace=True)

    logging.debug('Monthlyjump dataframe ::')
    logging.debug(monthJump2)

    # ------------------Monthly MaxRate DataFrame[Month,HotelNames...]------------------------------------
    monthMaxRate = pd.DataFrame(monthlymax.loc[:, htlmonthlist])
    monthMaxRate.set_index('hotelname', inplace=True)
    monthMaxRate2 = monthMaxRate.T
    monthMaxRate2.reset_index(inplace=True)
    monthMaxRate2.rename(columns={'index': 'Month'}, inplace=True)
    logging.debug('MonthlyMax Rate dataframe ::')
    logging.debug(monthMaxRate2)

    # ==========================Seasonal========================================

    # --------------------from Seasonal Range--------------------------------------
    name_s1s = dict(zip(season_range['hotelname'], season_range['season1start date']))
    name_s1e = dict(zip(season_range['hotelname'], season_range['season1end date']))
    name_s2s = dict(zip(season_range['hotelname'], season_range['season2start date']))
    name_s2e = dict(zip(season_range['hotelname'], season_range['season2end date']))

    # --------------------seasonal minimum rates----------------------------------
    name_s1min = dict(zip(season_range['hotelname'], season_range['s1_minrate']))
    name_s2min = dict(zip(season_range['hotelname'], season_range['s2_minrate']))

    # --------------------seasonal maxrates---------------------------------------
    name_s1max = dict(zip(season_range['hotelname'], season_range['s1_maxrate']))
    name_s2max = dict(zip(season_range['hotelname'], season_range['s2_maxrate']))

    # -----------------------seasonal jumps-----------------------------------------
    name_s1jump = dict(zip(monthlyjump['hotelname'], monthlyjump['Season1']))
    name_s2jump = dict(zip(monthlyjump['hotelname'], monthlyjump['Season2']))

    # ================================================================================================
    # ================================================================================================

    ezeedates = pd.read_excel(masterpath + '\\' + 'ezeedate_format.xlsx')
    jfacts = pd.read_excel(masterpath + r'\zFactors.xlsx')
    dropcol = pd.read_excel(masterpath + '\\' + 'DropColumns.xlsx')
    logging.info('All master files read !')

    ##=======================Dictionaries======================================
    # --------------------from Accounts-----------------------------------------
    name_accman = dict(zip(inputdf['hotelname'], inputdf['AccManager']))
    name_cap = dict(zip(inputdf['hotelname'], inputdf['cap']))
    name_maxcap = dict(zip(inputdf['hotelname'], inputdf['otacap']))
    name_msrate = dict(zip(inputdf['hotelname'], inputdf['msrate']))
    name_ftr = dict(zip(inputdf['hotelname'], inputdf['flowthrough']))
    name_rateplan = dict(zip(inputdf['hotelname'], inputdf['rateplan']))

    # RateOnCM flag
    name_chman = dict(zip(inputdf['hotelname'], inputdf['ChannelMan']))
    inputdf['RateOnCM'] = inputdf['RateOnCM'].astype(float).astype(int)
    name_cmflag = dict(zip(inputdf['hotelname'], inputdf['RateOnCM']))

    # phsychological factor
    name_psy = dict(zip(inputdf['hotelname'], inputdf['PsychologicalFactor']))

    name_hnf = dict(zip(inputdf['hotelname'], inputdf['HNF']))
    name_curr = dict(zip(inputdf['hotelname'], inputdf['Currency']))
    name_win = dict(zip(inputdf['hotelname'], inputdf['isellwindow']))
    name_win2 = dict(zip(inputdf['hotelname'], inputdf['clientwindow(180)']))
    GridType = dict(zip(inputdf['hotelname'], inputdf['GridType']))
    priceType = dict(zip(inputdf['hotelname'], inputdf['PricingType']))
    pricejump = dict(zip(inputdf['hotelname'], inputdf['PriceJump']))
    htl_cluster = dict(zip(inputdf['hotelname'], inputdf['ClusterName']))

    ##=========================monthly and seasonal useMaxRate flags==========================
    month_useMax = dict(zip(monthlyrates['hotelname'], monthlyrates['use_MaxRate']))
    cson_useMax = dict(zip(season_range['hotelname'], season_range['use_MaxRate']))
    # ------------------------useCeiling and useFloor-------------------------------------
    use_ceiling = dict(zip(inputdf['hotelname'], inputdf['use_CeilingRate']))
    use_floor = dict(zip(inputdf['hotelname'], inputdf['use_FloorRate']))
    # --------------------------------useGrid and cussion---------------------------------------------------
    use_Grid = dict(zip(inputdf['hotelname'], inputdf['use_Grid']))
    use_cussion = dict(zip(inputdf['hotelname'], inputdf['cussion']))

    # -----------------jump types dataframe-------------------------------------
    jumpType = dict(zip(inputdf['hotelname'], inputdf['JumpType']))

    os.chdir(basepath + '\{}'.format('OutPut_CSV'))
    try:
        os.mkdir(tdayfold)
    except FileExistsError:
        pass

    sysdt = LRdate  # str(input("Enter Last iSell Run Date for reading Last Report('mm/dd/yyyy'):"))
    logging.info("Last Report date provided is :{}".format(LRdate))
    logging.debug(LRdate)
    sysdt2 = pd.to_datetime(sysdt)
    last7foldname1 = sysdt2 - timedelta(days=6)
    lastfoldname = sysdt2.strftime('%d_%b_%Y')
    last7foldname = last7foldname1.strftime('%d_%b_%Y')
    lastfoldname = sysdt2.strftime('%d_%b_%Y')
    # last7foldname=sysdt2-timedelta(days=7)
    # last7foldname=last7foldname.strftime('%d_%b_%Y')

    LRdt = sysdt2.strftime("%d%b%Y")

    logging.info('All folders updated !!!')
    logging.info('---------------------------------------------------')

    for sr, names in enumerate(inputdf['hotelname'], start=1):
        # -------------------format 2 name setting(flag)-----------------------------#
        if '_OTA' in names:
            format2flag = 1
            logging.debug('set format2flag = 1 as _OTA in names for Format2iSell')
        else:
            format2flag = 0
            logging.debug('set format2flag = 0 for NormalFormat')

            # -------------------Dynamic Dictionaries-------------------------------------------
        # Hotel Cluster Weights
        clustName = htl_cluster[names]
        logging.debug('ClusterName:{}'.format(clustName))
        htl_dowWt = dict(zip(dow_cluster2['Dow'], dow_cluster2[clustName]))
        logging.debug('Hotel Day of Week Weights:{}'.format(htl_dowWt))

        # ----------------------------------------------------------------------------------
        print('{}.Creating {}_iSell ...'.format(sr, names))
        logging.info('{}.Creating {}_iSell ...'.format(sr, names))
        logging.info('Channel Manager :{}'.format(name_chman[names]))
        isellrange = int(name_win[names])
        logging.info('isellwindow:{}'.format(isellrange))
        # --------------------------------------------------------------------------------------------------------------

        #----------A.S. 3May2023--------------------------------------------------------------------------------
          #'Ramada by Wyndham Tashkent','The Boma Nairobi BNBO','Boma Inn Nairobi RCH','Boma Inn Eldoret BIE'
        if names in ('Naivasha Kongoni Hotel','Qaribu Inn','Ziwa Beach Resort'):
            df_cc=pd.read_excel(masterpath + '\\' + 'currency_mapping.xlsx')
            cc_value = dict(zip(df_cc['Hotel_name'], df_cc['CC_Factor']))
            cc_name =dict(zip(df_cc['Hotel_name'],df_cc['Currency']))

        else:
            cc_value=1

        #use cc_value[names] where u want to multiply

        #------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if name_chman[names] == 'Staah':
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')))
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))
            staahfile.dropna(subset=['CheckIn Date', 'CheckOut Date'], inplace=True)
            pcdata = ''
            cmdata2 = ''
            # try:
            #     staahfile.dropna(subset=['CheckIn Date', 'CheckOut Date'], inplace=True)
            # except:
            #     staahfile.columns = staahfile.iloc[1]
            #     staahfile = staahfile[3:]
            #     try:
            #         staahfile.dropna(subset=['Arrival Date', 'Departure Date'], inplace=True)
            #     except:
            #         staahfile.dropna(subset=['CheckIn Date', 'CheckOut Date'], inplace=True)
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'StayFlexi':  #Y.K. 06"Dec
            cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
            try:
                staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            except:
                staahfile = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            staahfile['Rooms'] = 1
            staahfile = staahfile.dropna(thresh=5)
            # cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')))
            cmdata2 =''
            pcdata = ''
        # --------------------------------------------------------------------------------------------------------------

        elif name_chman[names] == 'TravelBook_NoCM':  # A.S. 13"Apr2023
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))
            staahfile['Total'] = np.where(staahfile["Rate code"].isin(['DOM HB LM', 'DOM BB']), staahfile['Total']*0.0088,staahfile['Total'])
            staahfile['Rooms'] = 1
            staahfile = staahfile.dropna(thresh=5)
            # cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')))
            cmdata = ''
            pcdata = ''
            cmdata2= ''
        # -----------------------------------------------------------------------------------------------------------

        elif name_chman[names]  == 'AsiaTech1':
            #staahfile = staahfile.dropna(thresh=5)
            cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')),encoding="latin1", index_col= False)
            cmdata2 = ''
            pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))

        # cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
        # staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
        # staahfile['Rooms'] = 1
        # pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
        # cmdata2 = ''

        #-------------------------------A.S. 10May2023--------------------------------------------------------------------

        elif name_chman[names]  == 'Cloudbeds':

            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),skiprows=1, encoding= 'latin1')
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')), encoding= 'latin1')
            #-----------------A.S.Oct23-------
            staahfile['Room Number']=staahfile['Room Number'].astype('str')
            staahfile['Nights']=staahfile['Nights']*staahfile['Room Number'].apply(lambda x:len(x.split(',')))
            staahfile['Nights']=staahfile['Nights'].astype('int')
            #---------------------------------
            cmdata2 = ''
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx'), encoding= 'latin1'))
            staahfile['Rooms'] = 1
            staahfile=staahfile.dropna(subset=['Nights','Room Type'])
       #----------------------------------------A.S. 29May23------------------------------------------------------------

        elif name_chman[names] == 'Q2B':

            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')), encoding= 'latin1',skiprows=1)
            try:
                staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')), encoding= 'latin1')
            except:
                try:
                    import OleFileIO_PL
                    with open(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')), 'rb') as file:
                        corrpted_file = OleFileIO_PL.OleFileIO(file)
                        if corrpted_file.exists('Workbook'):
                            staahfile_ = corrpted_file.openstream('Workbook')
                            staahfile = pd.read_excel(staahfile_, engine='xlrd')
                except:
                    staahfile = pd.read_html(
                        basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')),
                        encoding='latin1') #A.S. 29May23

            staahfile['TotalValue'] = np.where(staahfile["Rev_Group"].isin(['Accommodation Revenue (KES)']),staahfile['TotalValue']*0.00732,staahfile['TotalValue'])

            cmdata2 = ''
            pcdata = ''
            #pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx'), encoding= 'latin1'))
            staahfile['Rooms'] = 1

       # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Synxis':    #Y.K. 06"Dec
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            # cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
            ###  Y.K. 07"Dec added for the last two row remove bcz there are unwanted values.
            staahfile = staahfile.drop(staahfile.index[-2:])
            staahfile['Rooms'] = 1
            cmdata2 = ''
            pcdata = ''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Phobs':
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')),header=1)
            staahfile = staahfile.dropna(how='all', axis=1)
            staahfile['Total'] = staahfile['Total'].str.replace(",", ".").astype(float)
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')),
                                   encoding="latin1", skiprows=13)
            staahfile['Rooms'] = 1
            cmdata2 = ''
            pcdata = ''

        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Staah Max':
            try:
                cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            except:
                cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')),encoding="latin1")

            try:
                otafile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')),header=2)
            except:
                otafile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')),header=2)

            cmdata2=''
            otafile.dropna(subset=['Arrival Date', 'Departure Date'], inplace=True)
            staahfile = pd.DataFrame(otafile)
            staahfile['Arrival Date'] = staahfile['Arrival Date'].str.split(',', expand=True)[0]
            staahfile['Departure Date'] = staahfile['Departure Date'].str.split(',', expand=True)[0]
            pcdata = ''

            # cm_room_type_df = rt.rm_StaahMax(cmdata)

            if names == "Hotel EnglishPoint & Spa":
                staahfile["Total Amount: (All Inclusive)"] = np.where(staahfile['Room Type'].str.contains('KES', regex=True),
                                                               staahfile["Total Amount: (All Inclusive)"] * 0.0088,
                                                               staahfile["Total Amount: (All Inclusive)"])

        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Eglobe':
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            #staahfile['Rooms'] = 1               # Comment this line for room calculation 22"Dec
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
            cmdata2=''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'AxisRooms':
            cm_col = dict(zip( cm_colname['AxisRooms'], cm_colname['stdname']))
            #staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))

            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')))
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xls')))
            cmdata2 =  ''
            staahfile = staahfile.rename(columns=cm_col)

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Louvre':

            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            staahfile.dropna(axis=0, subset=['Arrival', 'Departure'], inplace=True)
            staahfile['Arrival']=staahfile['Arrival'].astype('str')
            staahfile['Departure'] = staahfile['Departure'].astype('str')

            staahfile['Arrival'] = staahfile['Arrival'].apply(lambda x: x[0:10])
            staahfile['Departure'] = staahfile['Departure'].apply(lambda x: x[0:10])
            # staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'], format=checkIn[names])
            # staahfile['Dept'] = pd.to_datetime(staahfile['Dept'], format=checkOut[names])
            staahfile['Rooms'] = 1
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')), skiprows=1, header=0)

            pcdata = pd.read_excel( basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
        # --------------------------------------------------------------------------------------------------------------



        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'AxisRooms1':
            cm_col = dict(zip( cm_colname['AxisRooms1'], cm_colname['stdname']))
            #staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')))
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xls')))
            cmdata2 =  ''
            staahfile = staahfile.rename(columns=cm_col)
        # --------------------------------------------------------------------------------------------------------------
        
        elif name_chman[names] == 'BookingHotel':
            try:
                staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
                #A.S. 21Apr2023

            except:
                staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))

            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx')))
            cmdata2 = ''
        # --------------------------------------------------------------------------------------------------------------
        # elif name_chman[names] == 'TravelClick':
        #
        #     # ===========================Travel Click OTA Condition===============================
        #     if '_OTA' in names:
        #         staahfile2 = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names[:-4] + str('_OTAData.csv')))
        #         staahfile2['Subchannel Desc'].fillna(value='blankval', inplace=True)
        #         staahfile2['Subchannel Desc'] = np.where(staahfile2['Subchannel Desc'] == 'blankval',
        #                                                  staahfile2['Channel Name'], staahfile2['Subchannel Desc'])
        #         staahfile2.drop('Channel Name', axis=1, inplace=True)
        #         # ---------------renamed 'Subchannel Desc' as Channel Name---------------------
        #         staahfile2.rename(columns={'Subchannel Desc': 'Channel Name'}, inplace=True)
        #         # ---------------removing ['PMS','Brand.com'] from Channel Name---------------
        #         staahfile3 = staahfile2[~staahfile2['Channel Name'].isin(['PMS', 'Brand.com', 'CALL-HOTEL'])]
        #
        #         # ------------------remove House Bookings for YO1----------------------------
        #         if names in ["YO1 India's Holistic Wellness Center_OTA"]:
        #             staahfile = pd.DataFrame(staahfile3[staahfile3['Rate Plan'] != 'House'])
        #         else:
        #             staahfile = pd.DataFrame(staahfile3)
        #         # -----------------------------------------------------------------------------
        #
        #         cmdata = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names[:-4] + str('_CM.csv')),
        #             skiprows=[1, 2], quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
        #
        #         cmdata2 = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names[:-4] + str('_CM.csv')),
        #             skiprows=[1, 2], quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
        #
        #
        #         pcdata = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names[:-4] + str('_PC.csv')))
        #         staahfile['Rooms'] = 1
        #         cmdata2=''
        #
        #
        #     else:
        #         staahfile2 = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
        #
        #         # ------------------remove House Bookings for YO1---------------------------------
        #         if names in ["YO1 India's Holistic Wellness Center"]:
        #             staahfile = pd.DataFrame(staahfile2[staahfile2['Rate Plan'] != 'House'])
        #         else:
        #             staahfile = pd.DataFrame(staahfile2)
        #         # ---------------------------------------------------------------------------------
        #
        #         cmdata = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')),
        #             quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
        #         # cmdata2 = pd.read_csv(
        #         #     basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM2.csv')),
        #         #     quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
        #         cmdata2 = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM2.csv')),
        #             error_bad_lines=False, encoding="latin1")
        #         pcdata = pd.read_csv(
        #             basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #         staahfile['Rooms'] = 1
        elif name_chman[names] == 'TravelClick':

            # ===========================Travel Click OTA Condition===============================
            if '_OTA' in names:
                staahfile2 = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names[:-4] + str('_OTAData.csv')))
                staahfile2['Subchannel Desc'].fillna(value='blankval', inplace=True)
                staahfile2['Subchannel Desc'] = np.where(staahfile2['Subchannel Desc'] == 'blankval',
                                                         staahfile2['Channel Name'], staahfile2['Subchannel Desc'])
                staahfile2.drop('Channel Name', axis=1, inplace=True)
                # ---------------renamed 'Subchannel Desc' as Channel Name---------------------
                staahfile2.rename(columns={'Subchannel Desc': 'Channel Name'}, inplace=True)
                # ---------------removing ['PMS','Brand.com'] from Channel Name---------------
                staahfile3 = staahfile2[~staahfile2['Channel Name'].isin(['PMS', 'Brand.com', 'CALL-HOTEL'])]

                # ------------------remove House Bookings for YO1----------------------------
                if names in ["YO1 India's Holistic Wellness Center_OTA"]:
                    staahfile = pd.DataFrame(staahfile3[staahfile3['Rate Plan'] != 'House'])
                else:
                    staahfile = pd.DataFrame(staahfile3)
                # -----------------------------------------------------------------------------

                cmdata = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names[:-4] + str('_CM.csv')),
                    skiprows=[1, 2], quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                pcdata = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names[:-4] + str('_PC.csv')),
                    skiprows = [1, 2], quoting = csv.QUOTE_NONE, error_bad_lines = False, encoding = "latin1")
                try:
                    pcdata['Room'] = pcdata['Room'].apply(lambda x: x.strip("''"))  #23-03-2023 A.S. removed quotation if available in room column
                except:
                    pass

                staahfile['Rooms'] = 1

            else:
                staahfile2 = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))

                # ------------------remove House Bookings for YO1---------------------------------
                if names in ["YO1 India's Holistic Wellness Center"]:
                    staahfile = pd.DataFrame(staahfile2[staahfile2['Rate Plan'] != 'House'])
                else:
                    staahfile = pd.DataFrame(staahfile2)
                # ---------------------------------------------------------------------------------

                cmdata = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')),
                    quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                cmdata2 = pd.read_csv(
                     basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM2.csv')),
                     quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                try:
                    cmdata2['Room'] = cmdata2['Room'].apply(lambda x: x.strip("''"))    #23-03-2023 A.S. removed quotation if available in room column
                except:
                    pass

                # cmdata2 = pd.read_csv(
                #     basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM2.csv')),
                #     error_bad_lines=False, encoding="latin1")
                pcdata = pd.read_csv(
                     basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')),
                    quoting=csv.QUOTE_NONE, error_bad_lines=False, encoding="latin1")
                try:
                    pcdata['Room'] = pcdata['Room'].apply(lambda x: x.strip("''"))  #23-03-2023 A.S. removed quotation if available in room column
                except:
                    pass

                staahfile['Rooms'] = 1
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Maximojo':
            try:
                staahfile = pd.read_excel(
                    basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')))   #A.S 21Apr2023

            except:
                staahfile = pd.read_excel(
                    basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))


            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            pcdata = ''
            cmdata2=''
        # --------------------------------------------------------------------------------------------------------------
        # TB: TravelBook Normal iSell
        elif name_chman[names] in ['TB', 'TB1']:
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')),
                                   skiprows=1)
            staahfile['Rooms'] = 1
            pcdata = ''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Djubo':
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')),
                                      skiprows=1)
            cmdata = ''
            pcdata = ''

        #--------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Bookingjini':
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            cmdata = ''
            pcdata = ''

            # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Rategain':
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            cmdata = ''
            pcdata = ''
            staahfile['Check-in'] = staahfile['Check-in'].astype('str')
            staahfile['Check-out'] = staahfile['Check-out'].astype('str')

            staahfile['Check-in'] = staahfile['Check-in'].apply(lambda x: x[0:10])
            staahfile['Check-out'] = staahfile['Check-out'].apply(lambda x: x[0:10])
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Ease Room':
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            cmdata2 = ''
            pcdata = ''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'Guestline':

            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),
                                  encoding='latin1')
 #            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),
 #                                   encoding='latin1')
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')),
                                      encoding='latin1')
            pcdata = pd.read_excel(
               basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx'), encoding='latin1'))
#             cmdata = pd.read_excel(
#                 basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xlsx'), encoding='latin1'))
            cmdata2 = ''
        # --------------------------------------------------------------------------------------------------------------
        # elif name_chman[names] == 'eZee':
        #     checkIn = dict(zip(ezeedates['Hotel'], ezeedates['Checkin']))
        #     checkOut = dict(zip(ezeedates['Hotel'], ezeedates['Checkout']))
        #
        #     staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
        #     staahfile.dropna(axis=0, subset=['Arrival', 'Dept'], inplace=True)
        #     staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'], format=checkIn[names])
        #     staahfile['Dept'] = pd.to_datetime(staahfile['Dept'], format=checkOut[names])
        #     staahfile['Rooms'] = 1
        #
        #     cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
        #     cmdata2=''
        #     if names == 'Hotel Emerald':
        #         pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #     elif names == 'The Emory Hotel':
        #         pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #     elif names == 'Xanadu Collection All Suite Hotel':
        #         pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #     elif names == 'Kingfisher Casa':
        #         pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #     elif names == 'Leisure Lodge Beach & Golf Resort':
        #         pcdata = pd.read_csv(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))
        #     else:
        #         pcdata = ''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'eZeeNoCM':
            checkIn = dict(zip(ezeedates['Hotel'], ezeedates['Checkin']))
            checkOut = dict(zip(ezeedates['Hotel'], ezeedates['Checkout']))

            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            staahfile.dropna(axis=0, subset=['Arrival', 'Dept'], inplace=True)
            staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'], format=checkIn[names])
            staahfile['Dept'] = pd.to_datetime(staahfile['Dept'], format=checkOut[names])
            staahfile['Rooms'] = 1

            # cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
            cmdata2 = ''

            try:
                pcdata = pd.read_csv(
                    basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))  ##
            except:
                pcdata = ''
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'GuestCentric':  # S.W. 16May2024
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            staahfile = staahfile[staahfile['Check-In'] != '0000-00-00']
            staahfile['Channel'].fillna('Website', inplace=True)
            staahfile['Status'] = staahfile['Status'].apply(lambda x: 1 if x == 'Confirmed' or x == 'New' else 0)

            cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')),
                                 skiprows=1)
            pcdata = cmdata.iloc[:, :2]
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'IDS':
            rows_to_skip=40
            staahfile=pd.read_csv(basepath+'\{}\{}\{}'.format('OTA_Data',tdayfold,names+str('_OTAData.csv')),skiprows=2,skipfooter=rows_to_skip, engine='python')
            pcdata = pd.read_excel(basepath+'\{}\{}\{}'.format('Price_Calendar',tdayfold,names+str('_PCData.xlsx')), skiprows=4)
            pcdata = pcdata.drop(columns=pcdata.columns[0], errors='ignore')
            cmdata2 =''
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'eZee':
            checkIn = dict(zip(ezeedates['Hotel'], ezeedates['Checkin']))
            checkOut = dict(zip(ezeedates['Hotel'], ezeedates['Checkout']))

            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            staahfile.dropna(axis=0, subset=['Arrival', 'Dept'], inplace=True)
            if names in ["Grand Hotel D' Europe","Theory9 Premium Service Apts, Bandra"]:
                staahfile.dropna(axis=0,subset=['Arrival', 'Dept', 'Total'], inplace=True)#A.S.Jun23


            staahfile['Arrival'] = staahfile['Arrival'].apply(lambda x: str(x)[2:12])
            staahfile['Dept'] = staahfile['Dept'].apply(lambda x: str(x)[2:12])


            try:
                staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'], format=checkIn[names])
                staahfile['Dept'] = pd.to_datetime(staahfile['Dept'], format=checkOut[names])
            except:
                try:
                    staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'], dayfirst=True)
                    staahfile['Dept'] = pd.to_datetime(staahfile['Dept'], dayfirst=True)
                except:
                    staahfile['Arrival'] = pd.to_datetime(staahfile['Arrival'])
                    staahfile['Dept'] = pd.to_datetime(staahfile['Dept'])

            staahfile['Rooms'] = 1
            cmdata = pd.read_csv(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.csv')))
            cmdata2 = ''

            pcdata = pd.read_csv(
                basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.csv')))



        #---------------------------------------------------------------------------------------------------------------
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
        # ------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'UK':
            pcdata = ''

            if names == 'Leaf Hotel Dover':
                cmData1 = pd.read_excel(
                    basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')), header=[1])
                hnfData1 = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
                outpath = basepath + '\{}\{}'.format('HNF', tdayfold)

                leaf.lhd(cmData1, hnfData1, outpath, names, isellrange+rng)
                # To add Leaf Dover (ota, cm)
                # import Report_Leaf_H as lhd

                # lhd.lhd(inventryStatus, forcast)

                staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                        delimiter=",", index_col=False, header=0, low_memory=False,
                                        quoting=csv.QUOTE_ALL, encoding='utf8')
                cmdata = pd.DataFrame(staahfile)
                cmrates2 = pd.DataFrame(cmdata.loc[:, ['Date', 'CMRate']])
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'], format="%Y-%m-%d")
        # ------------------------------------------------------------------------------------------------------------
            elif names == 'Best Western Clifton':

                staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                        delimiter=",", index_col=False, header=0, low_memory=False,
                                        quoting=csv.QUOTE_ALL, encoding='utf8')
                # staahfile.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\CM_Availability\staahfile.csv')

                cmdata = pd.read_excel(
                    basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))

                xls = pd.ExcelFile(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))
                months = xls.sheet_names
                months2 = months[1:8]
                data = []
                for m in months2:
                    cmdf = pd.read_excel(
                        basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')),
                        sheet_name=m, skiprows=1)
                    #            cmdf.rename(columns={'Unnamed: 0':'Date'},inplace=True)
                    cmdf2 = pd.DataFrame(cmdf.set_index('Unnamed: 0').T).reset_index()

                    data.append(cmdf2)
                cmrates = pd.concat(data)
                #        cmrates.reset_index(inplace=True)
                cmrates.rename(columns={'index': 'Date'}, inplace=True)
                cmrates2 = pd.DataFrame(cmrates)
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'], format="%d/%m/%Y")
                cmrates2['Date'] = pd.to_datetime(cmrates2['Date'], format="%d-%b-%Y")
                logging.debug('Best Western CMRate(cmrates2) ::')
                logging.debug(cmrates2)

        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] in ['TravelBook', 'BW']:
            pcdata = ''
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                    delimiter=",", index_col=False, header=0, low_memory=False, quoting=csv.QUOTE_ALL,
                                    encoding='utf8')

            cmdata = pd.DataFrame(staahfile)
            cmrates2 = pd.DataFrame(cmdata.loc[:, ['Date', 'CMRate']])
            cmrates2['Date'] = pd.to_datetime(cmrates2['Date'], format="%Y-%m-%d")


        # --------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'SiteMinder':
            staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')))
            #staahfile['Total Amount'] = staahfile['Total Amount'].str.extract('(\d+)').astype(int)
            try:
                staahfile['Total Amount'] = staahfile['Total Amount'].str.split('(', 1).str[0].str.strip().astype(float)
            except:
                staahfile['Total price'] = staahfile['Total price'].str.split(' ', 1).str[1].str.strip().astype(float)

            staahfile['Room']=staahfile['Room'].apply(lambda x: str(x).split(' ')[0])

            staahfile=staahfile.rename(columns={'Room':'Rooms'})
            # staahfile['Rooms'] = 1
            cmdata = ''
            pcdata = ''
        # ------------------------------------------------------------------------------------------------------------
        # elif name_chman[names] in ['Rategain', 'Rategain1']:
        #     staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
        #     cmdata = ''
        #     pcdata = ''
        # ------------------------------------------------------------------------------------------------------------
        # elif name_chman[names] == 'AsiaTech':
        #     staahfile = pd.read_csv(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.csv')),
        #                             delimiter=",", index_col=False, header=0)
        #     cmdata = ''
        #     pcdata = ''
        # ------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'BookingCentre':
            staahfile2 = pd.read_excel(
                basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')), skiprows=9)
            # staahfile2['Cost2']=staahfile2['Cost'].apply(lambda x: x.str.replace(',',''))
            staahfile2['Cost'] = staahfile2['Cost'].str.replace('₨', '')
            staahfile2['Cost'] = pd.to_numeric(staahfile2['Cost'].apply(lambda x: re.sub(',', '', str(x))))
            # staahfile2.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\OTA_Data\16_Oct_2018\staahfile.csv')
            staahfile2['Rooms'] = 1
            staahfile2['Status'] = staahfile2['Status'].fillna(value=1)
            staahfile = pd.DataFrame(staahfile2[staahfile2.Status != 1])

            cmdata = ''
            pcdata = ''
        # ------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'ResAvenue':
            staahfile2 = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xls')),
                                       skiprows=2)
            staahfile2['Booking Status'] = staahfile2['Booking Status'].fillna(value=1)
            staahfile = pd.DataFrame(staahfile2[staahfile2['Booking Status'] != 1])

            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xls')),
                                   skiprows=1)
            pcdata = pd.read_excel(basepath + '\{}\{}\{}'.format('Price_Calendar', tdayfold, names + str('_PC.xls')),
                                   skiprows=3)
        # ------------------------------------------------------------------------------------------------------------
        elif name_chman[names] == 'RezNext':
            staahfile = pd.read_excel(basepath + '\{}\{}\{}'.format('OTA_Data', tdayfold, names + str('_OTAData.xlsx')))
            cmdata = pd.read_excel(basepath + '\{}\{}\{}'.format('CM_Availability', tdayfold, names + str('_CM.xlsx')))

        else:
            logging.info("There is no such Channel Manager Added in Input Conditions !!!")

            # ===============================debug all input data frames=================================================
        logging.debug('----------------------------------------------------------------')
        logging.debug('Input Data Files required for {} to create iSell'.format(name_chman[names]))
        # ------------------------------------------cmdata--------------------------------

        try:
            logging.debug('{}_CM dataframe ::'.format(names))
            logging.debug(cmdata)
        except:
            logging.debug('No cmdata needed')

        # --------------------------------------staahfile(ota data)------------------------
        try:
            logging.debug('{}_OTAData dataframe ::'.format(names))
            logging.debug(staahfile)
        except:
            logging.debug('No OTAData needed')

            # --------------------------------------PC data(price calander)------------------------
        try:
            logging.debug('{}_PC dataframe ::'.format(names))
            logging.debug(pcdata)
        except:
            logging.debug('No pcdata needed')

            # ------------------------------------------------------------------------------------

        # ==================================format2 name setting====================================================
        if format2flag == 1:
            rsfile = pd.read_csv(basepath + '\{}\{}\{}'.format('RS_Data', tdayfold, names[:-4] + str('_RSData.csv')),
                                 encoding='cp1252')
            dc = pd.read_excel(basepath + '\{}\{}'.format('Demand_Calendar', names[:-4] + str('.xlsx')))
            # ---------------------------------LastReport name should have OTA-------------------------------------------
            try:
                df_LR = pd.read_csv(basepath + '\{}\{}\{}'.format('OutPut_CSV', lastfoldname,
                                                              str('iSell_') + names + str('_{}.csv'.format(LRdt))))
            except:
                path_LR = npf.Lrdate_outputCSV(LRdt,basepath,names)
                df_LR = pd.read_csv(path_LR)
            # ------------------------------------------------------------------------------------------------------------
            if use_Grid[names] == 1:
                df_PG = pd.read_excel(basepath + '\{}\{}'.format('Pricing_Grid', names[:-4] + str('_PG.xlsx')))
            else:
                pass

            rateshopfile = pd.read_csv(
                basepath + '\{}\{}\{}'.format('RateShop', tdayfold, names[:-4] + str('_RateShop.csv')))
            #--------------------------A.S. 4May2023--------------------------------------------------------
              #'The Boma Nairobi BNBO', 'Boma Inn Nairobi RCH', 'Boma Inn Eldoret BIE'
            if names in ('Naivasha Kongoni Hotel','Qaribu Inn','Ziwa Beach Resort'):
                rateshopfile['NetRate']= rateshopfile['NetRate']/cc_value[names]
                rateshopfile['NetRate'] = rateshopfile['NetRate'].fillna(0)
                rateshopfile['NetRate'] = rateshopfile['NetRate'].astype('int64')
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate']/cc_value[names]
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate'].fillna(0)
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate'].astype('int64')
            #---------------------------------------------------------------------------------------------



        else:
            rsfile = pd.read_csv(basepath + '\{}\{}\{}'.format('RS_Data', tdayfold, names + str('_RSData.csv')),
                                 encoding='cp1252')
            dc = pd.read_excel(basepath + '\{}\{}'.format('Demand_Calendar', names + str('.xlsx')))
           ##Reading old frame for pickup & markettrend----------------------------------------------------------------------
            try:
                df_LR = pd.read_csv(basepath + '\{}\{}\{}'.format('OutPut_CSV', lastfoldname,
                                                                  str('iSell_') + names + str('_{}.csv'.format(LRdt))))
            except:
                path_LR = npf.Lrdate_outputCSV(LRdt,basepath,names)
                df_LR = pd.read_csv(path_LR)
            ## ------------------------------------------------------------------------------------------------
            # -------------------7DayBefore Report---------------------------------------
            try:
                df_LR7 = pd.read_csv(basepath + '\{}\{}\{}'.format('OutPut_CSV', last7foldname,
                                                                  str('iSell_') + names + str('_{}.csv'.format(last7foldname1.strftime('%d%b%Y')))))
            except:
                path_LR7 = npf.Lrdate_outputCSV(LRdt,basepath,names)
                df_LR7 = pd.read_csv(path_LR7)
            # =================================================================================

            if use_Grid[names] == 1:
                df_PG = pd.read_excel(basepath + '\{}\{}'.format('Pricing_Grid', names + str('_PG.xlsx')))
            else:
                pass

            rateshopfile = pd.read_csv(
                basepath + '\{}\{}\{}'.format('RateShop', tdayfold, names + str('_RateShop.csv')))
            #--------------------------A.S. 4May2023--------------------------------------------------------
               #The Boma Nairobi BNBO', 'Boma Inn Nairobi RCH', 'Boma Inn Eldoret BIE'
            if names in ('Naivasha Kongoni Hotel','Qaribu Inn',"Ziwa Beach Resort"):
                rateshopfile['NetRate']= rateshopfile['NetRate']/cc_value[names]
                rateshopfile['NetRate'] = rateshopfile['NetRate'].fillna(0)
                rateshopfile['NetRate'] = rateshopfile['NetRate'].astype('int64')
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate']/cc_value[names]
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate'].fillna(0)
                rateshopfile['OnsiteRate'] = rateshopfile['OnsiteRate'].astype('int64')

                rateshopfile['Currency']=str(cc_name[names])
            #---------------------------------------------------------------------------------------------
        # ================================================================================================================

        # --------------------------------------(Demand Calendar)---------------------------------
        try:
            logging.debug('{} Demand Calendar dataframe ::'.format(names))
            logging.debug(dc)
        except:
            logging.debug('Demand calendar is needed, not found')
            # -----------------------------------(last isell report)----------------------------------
        try:
            logging.debug('{} Last iSell Report dataframe ::'.format(names))
            logging.debug(df_LR)
        except:
            logging.debug('Last iSell Report is needed, not found')

            # -----------------------------------(RSData Report)----------------------------------
        try:
            logging.debug('{}_RSData Report dataframe ::'.format(names))
            logging.debug(rsfile)
        except:
            logging.debug('RSData Report is needed, not found')

        # -----------------------------------(Rateshop Report)----------------------------------
        try:
            logging.debug('{}_RateShop Report dataframe ::'.format(names))
            logging.debug(rateshopfile)
        except:
            logging.debug('RateShop Report is needed, not found')

        # ------------------------------------Pricing Grid----------------------------------------
        try:
            logging.debug('{}_PG dataframe ((use_Grid=1)::'.format(names))
            logging.debug(df_PG)
        except:
            logging.debug('External Pricing Grid is not found (use_Grid=0)')

        logging.debug('----------------------------------------------------------------')
        # ==============================================================================================

        # ---------------------------Frame('Date','Dow')-----------------------------------------------
        tday=datetime.now() #A.S. Jun23
        # rng = (tday) - (tday.replace(day=1))
        rng = (tday) - (tday-timedelta(days=1))
        rng = rng.days
        tday = tday.strftime("%d-%b-%Y")
        tday = datetime.strptime(tday,"%d-%b-%Y")

        # yday=datetime.now().replace(day=1)
        yday1 = datetime.now()-timedelta(days=1)


        #yday = date.today()+timedelta(days=-1)
        yday=yday1.strftime("%d-%b-%Y")
        yday2=yday1.strftime("%Y-%m-%d")
        index = pd.date_range(yday,periods=isellrange+rng)
        frame = pd.DataFrame({'Date': index})
        frame['Dow'] = frame['Date'].apply(lambda x: x.strftime('%a'))
        logging.debug('Frame with {} days(isellwindow) range'.format(isellrange+rng))
        logging.debug(frame)

        # ---------------------# df_total,df_ota,df_ttlsold #--------------------------------------------

        if name_chman[names] in ['UK', 'TravelBook', 'BW']:
            pass
        else:
            logging.debug('Exploading data ...')
            df_total, df_ota, df_ttlsold = iSell_fun_02.dfconv(defaultpath, staahfile, names, name_chman[names],cc_value,name_accman[names]) #A.S. cc_value added
            logging.info('Occupancy conversion done, returned (df_total,df_ota,df_ttlsold) !!!')

            df_ttlsold.fillna(value=0, inplace=True)

            # df_all
            df_all = iSell_fun_02.occframe(df_total, isellrange+rng)
            logging.debug('Merged df_total with iSell frame')
            df_ota2 = df_ota.pivot(index='occupancydate', columns='Channel', values='No_of_Rooms')
            df_ota2.dropna(axis=0,how='all')#A.S. Jun2023
            df_ota2.reset_index(inplace=True)
            logging.debug('OTA Pivote Table (df_ota2) ::')
            logging.debug(df_ota2)

            # df_all2
            df_all2 = pd.merge(df_all, df_ota2, on='occupancydate', how='left')
            df_all2.fillna(value=0, inplace=True)
            df_all3 = df_all2.rename(
                columns={'occupancydate': 'Date', 'No_of_Rooms': 'OTA_Sold', 'RevPD': 'OTA Revenue'})
            ddff = df_all3.set_index('Date')

            logging.debug('final dataframe (ddff) ::')
            logging.debug(ddff)

            otabreak = pd.DataFrame(ddff.iloc[:, 2:])
            otabreak.reset_index(inplace=True)
            logging.debug('otabreak dataframe ::')
            logging.debug(otabreak)

            otasold = pd.DataFrame(ddff.loc[:, 'OTA_Sold'])
            otasold.reset_index(inplace=True)
            logging.debug('otasold dataframe ::')
            logging.debug(otasold)

            otarev = pd.DataFrame(ddff.loc[:, 'OTA Revenue'])
            otarev.reset_index(inplace=True)
            logging.debug('otarev dataframe ::')
            logging.debug(otarev)

        # ----------------------# df merging #---------------------------------------------

        # 1)---------------# Demand Calendar #------------------------------------------------------------
        dc2 = iSell_fun_02.frame(dc, isellrange+rng)
        dc3_1 = dc2.loc[:, ['Date', 'Event']]
        dc3 = pd.merge(frame, dc3_1, on='Date', how='left')
        dc3['Capacity'] = name_cap[names]

        logging.info('Demand Calendar attached and capacity added ::')
        logging.debug(dc3)

        # 2)---------------# CM_Avail #----------------------------------------------

        if name_chman[names] == 'Djubo':
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)


        elif name_chman[names] in ['GuestCentric']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_GuestCentric(cmdata, name_rateplan[names], pcdata, name_ftr[names],
                                                  isellrange + rng)

        elif name_chman[names] == 'Bookingjini':       #saurabh & suyash
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Bookingjini(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] == "Rategain":               #saurabh & suyash
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Rategain(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] == 'SiteMinder':
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] == 'Guestline':
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Guestline(cmdata,name_rateplan[names],pcdata,name_ftr[names] ,isellrange)


        elif name_chman[names] in ['Louvre']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Louvre(cmdata,name_rateplan[names],pcdata,name_ftr[names],isellrange+rng)

        elif name_chman[names] in ['Ease Room']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_EaseRoom(cmdata, name_ftr[names], isellrange+rng)

        elif name_chman[names] in ['StayFlexi']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] in ['Phobs']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Phobs(cmdata,isellrange+rng)

        elif name_chman[names] in ['eZeeNoCM']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_eZeeNoCM(name_rateplan[names],pcdata,name_ftr[names],isellrange+rng)

        elif name_chman[names] in ['Ease Room']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] in ['TravelBook_NoCM']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)


        elif name_chman[names] in ['Synxis']:
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)

        # elif name_chman[names] in ['Rategain', 'Rategain1']:
        #     cap = int(name_cap[names])
        #     logging.info(cap)
        #     rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange+rng)

        elif name_chman[names] == 'BookingCentre':
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap)

        # elif name_chman[names] == 'Asiatech':
        #     cap = int(name_cap[names])
        #     logging.info(cap)
        #     rmsavail, cmdf = CMAs.CM_Djubo(df_ttlsold, cap, isellrange)

        elif name_chman[names] == 'UK':
            # attch avail, OTA_Sold and CM_Rate
            if names == 'Leaf Hotel Dover':
                # -------------similar to getfam----------------
                rmsavail, cmdf = CMAs.CM_TB(staahfile, cmrates2)
            elif names == 'Best Western Clifton':
                rmsavail, cmdf = CMAs.CM_UK(staahfile, cmrates2, name_msrate[names], isellrange+rng)


        elif name_chman[names] in ['TravelBook', 'BW']:
            rmsavail, cmdf = CMAs.CM_TB(staahfile, cmrates2)

        elif name_chman[names] == 'RezNext':
            # attch avail, OTA_Sold and CM_Rate
            rmsavail, cmdf = CMAs.CM_RezNext(cmdata, name_msrate[names], name_ftr[names], name_rateplan[names],
                                            isellrange+rng)
        elif name_chman[names] =='TravelClick':
            rmsavail, cmdf = CMAs.CM_Avails(cmdata, names, name_msrate[names], name_ftr[names], name_chman[names],
                                            pcdata, name_rateplan[names], isellrange+rng, cmdata2)

        elif name_chman[names] == 'IDS':
            cap = int(name_cap[names])
            logging.info(cap)
            rmsavail, cmdf = CMAs.CM_IDS(name_rateplan[names], pcdata, name_ftr[names], isellrange + rng)
            # rmsavail, cmdf = CMAs.CM_IDS(pcdata, isellrange + rng)

        else:
            rmsavail, cmdf = CMAs.CM_Avails(cmdata, names, name_msrate[names], name_ftr[names], name_chman[names],
                                            pcdata, name_rateplan[names], isellrange+rng, cmdata2)

        # # --------------------------A.S. 4May2023------------------------
        #   #The Boma Nairobi BNBO', 'Boma Inn Nairobi RCH', 'Boma Inn Eldoret BIE
        # if names in (''):
        #     cmdf['Rate on CM']=cmdf['Rate on CM']/cc_value[names]
        #     cmdf['Rate on CM'] = cmdf['Rate on CM'].astype('int64')
        # #-----------------------------------------------------------------



        iSelldf1 = iSell_fun_02.merging(dc3, rmsavail)


        logging.info('Demand calendar and Availability merged ::')
        logging.debug(iSelldf1)

        if name_chman[names] in ['UK', 'TravelBook', 'BW']:
            iSelldf2 = iSelldf1
        else:

            iSelldf2 = iSell_fun_02.merging(iSelldf1, otasold)

        if name_chman[names] == 'IDS':
            iSelldf2['Rooms Avail To Sell Online'] = 0
            pass
        else:

            #------------------------------------------Inventory Open%--------------A.S.23---------------------#

            iSelldf2["Inventory Open%"] = (iSelldf2["Rooms Avail To Sell Online"] / (iSelldf2["Capacity"] - iSelldf2["OTA_Sold"])) * 100
            iSelldf2["Inventory Open%"]=iSelldf2["Inventory Open%"].replace(np.nan,0)
            iSelldf2["Inventory Open%"] = iSelldf2["Inventory Open%"].replace([np.inf,-np.inf], 0)
            iSelldf2["Inventory Open%"] = iSelldf2["Inventory Open%"].astype('int')
            df_inv = iSelldf2.loc[:, ['Date', 'Inventory Open%']]
            # df_inv = df_inv.loc(df_inv['Inventory Open%'] < 30 and (df_inv['Date'] >= yday))

            # --------------------------------------------------------------------------------------
            logging.info('OTA Sold merged ::')
            logging.debug(iSelldf2)

        # ==================== HNF On The FLY =======================================
        logging.debug("Checking for 'Hybrid' Condition in GridType Column...")

        if GridType[names] == 'Hybrid':
            logging.debug('GridType is Hybrid')
            flyHNF = pd.DataFrame(iSelldf2.loc[:, ['Date', 'Capacity', 'Rooms Avail To Sell Online']])
            flyHNF['Sold'] = flyHNF['Capacity'] - flyHNF['Rooms Avail To Sell Online']
            flyHNF['Date'] = flyHNF['Date'].apply(lambda x: x.strftime("%d-%b-%Y"))
            flyHNF2 = pd.DataFrame(flyHNF.loc[:, ['Date', 'Sold']])
            flyHNF2.to_excel(basepath + '\\' + 'HNF\{}\{}_HNF.xlsx'.format(tdayfold, names))
            logging.info("HNF On the fly Calculated and dumped in today's HNF folder")
            logging.debug(flyHNF2)
        else:
            logging.debug('GridType is not Hybrid')
            pass

        # 3)---------------# Last Report #------------------------------------------
        LRfinal_2 = iSell_fun_02.dfLR(df_LR, name_chman[names])
        LRfinal2 = iSell_fun_02.frame(LRfinal_2, isellrange+rng)

        #-------------------7daybefore report---------------------------------------
        if names=="YO1 Health_Resort_OTA":
          pass

        else:
            if names == "YO1 Health Resort":
                names1="YO1 Health Resort_OTA_Combine"
                LRfinal_7 = iSell_fun_02.dfLR7(df_LR7, name_chman[names1])
            else:
                LRfinal_7 = iSell_fun_02.dfLR7(df_LR7, name_chman[names])

            LRfinal7 = iSell_fun_02.frame(LRfinal_7, isellrange+rng)
        #=================================================================================
        cmflag = name_cmflag[names]

        # ======================# Last SeasonalRate #=====================================
        if cmflag == 0:
            Last_szrates = pd.DataFrame(df_LR.loc[:, ['Date', 'SeasonalRate_y']])
            Last_szrates.rename(columns={'SeasonalRate_y': 'Last_szrate'}, inplace=True)
            # Last_szrates.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\lastszrate1.csv')

            try:
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'], format="%d-%b-%Y")
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'], format='%Y-%m-%d')
            except:
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'])
                Last_szrates['Date'] = pd.to_datetime(Last_szrates['Date'], format='%Y-%m-%d')

            logging.info('\tRead last Report with seasonal rates !!!')
            # Last_szrates.to_csv(r'E:\iSell_Project\All_In_One_iSell\InputData\lastszrate2.csv')
        elif cmflag == 1:
            Last_szrates = 'NotRequired'
        else:
            logging.info('\tPlease Check RateOnCM column in InputCondition, It should be 1 or 0')
            sys.exit()


        # 5)---------------# OTA Revenue #------------------------------------------

        if name_chman[names] in ['UK', 'TravelBook', 'BW']:
            iSelldf4 = iSell_fun_02.merging(iSelldf2, cmdf)

            logging.info('\tRevenue, ADR, CM Rate Added !!!')
        else:
            iSelldf3 = iSell_fun_02.merging(iSelldf2, otarev)
            logging.info('\tRevenue Added !!!')

            # 6)--------------# ADR #--------------------------------------------------

            iSelldf3['ADR OTB'] = (iSelldf3['OTA Revenue'] / iSelldf3['OTA_Sold']).round(0)
            iSelldf3['ADR OTB'].fillna(value=0, inplace=True)
            logging.info('ADR Added !!!')

            # 7)--------------# Rate on CM #---------------------------------------------------

            iSelldf4 = iSell_fun_02.merging(iSelldf3, cmdf)
        # 4)========================== Pickup =================================================
        iSelldf2_1 = iSell_fun_02.merging(iSelldf4, LRfinal2)
        iSelldf2_1['Pickup'] = iSelldf2_1['OTA_Sold'] - iSelldf2_1['Last_OTASOLD']
        iSelldf2_1['Revenue Pickup'] = iSelldf2_1['OTA Revenue'] - iSelldf2_1['Last_OTA_Revenue']
        iSelldf2_1['ADR Pickup'] = iSelldf2_1['ADR OTB'] - iSelldf2_1['Last_ADR_OTB']

        iSelldf7_1 = iSell_fun_02.merging(iSelldf2_1, LRfinal7)
        iSelldf7_1['Rooms Last 7 Days Pickup']=iSelldf7_1['OTA_Sold']-iSelldf7_1['Last_OTASOLD7']
        iSelldf7_1['Revenue Last 7 Days Pickup'] = iSelldf7_1['OTA Revenue'] - iSelldf7_1['Last_OTA_Revenue7']
        iSelldf7_1['ADR Last 7 Days Pickup'] = iSelldf7_1['ADR OTB'] - iSelldf7_1['Last_ADR_OTB7']

        iSelldf7_1.fillna(value=0, inplace=True)

        iSelldf4 = iSelldf7_1.drop(['Last_OTASOLD7','Last_OTASOLD', 'LAvg1'], axis=1)

        logging.info('\tPickup Added !!!')

#-------------------------------------------------------------------------------------


            # if pcdata != '':#A.S. 30May23
            #     iSelldf4 = iSell_fun_02.merging(iSelldf3, cmdf)
            # else:
            #     iSelldf4 = iSelldf3


        logging.info('Rate on CM Added !!!')

        logging.info('\t-----Pricing Conditions------')

        # 8)-------------# Pricing Type #------------------------------------------------------
        # phychological factor
        psy_fact = name_psy[names]

        logging.info('\tGrid Type is :{}'.format(GridType[names]))

        if priceType[names] == 'Monthly':
            # --------------Monthly Dynamic Dictionaries----------------------------------------
            # Hotel Monthly Min Rate
            month_minR = dict(zip(monthMinRate2['Month'], monthMinRate2[names]))
            # -------(*logging.info monthly min rates*)---------
            #            logging.info(month_minR)
            # ---------------------------------------
            # Hotel Monthly Jumps
            month_jump = dict(zip(monthJump2['Month'], monthJump2[names]))

            if month_useMax[names] == 1:
                # Hotel Monthly Max Rate
                month_maxR = dict(zip(monthMaxRate2['Month'], monthMaxRate2[names]))
            elif use_ceiling[names] == 1:
                month_maxR = dict(zip(monthMaxRate2['Month'], monthMaxRate2[names]))
            else:
                month_maxR = ''

            logging.info('Pricing Type is :{}'.format(priceType[names]))
            iSelldf44, isellforgrid = mnthprice.month_minmax(names, iSelldf4, month_minR, htl_dowWt, jfacts, month_jump,
                                                             htl_cluster, jumpType[names], month_maxR,
                                                             month_useMax[names], use_ceiling[names])
            try:
                iSelldf44['Rate on CM']=iSelldf44['Rate on CM'].astype('float64') #A.S.May23
            except:
                pass

            # -----------------Min, min, Max, max, (4 columns) fetching after Rate on CM
            #            iSelldf44.to_csv(r'E:\All_In_One_iSell\Testing\iSelldf44_{}.csv'.format(names))
            # ---------------------------------------------------------------------------------
            logging.info('Monthly Rates Fetched')

            if use_Grid[names] == 1:
                pgdf = pd.DataFrame(df_PG)
            else:
                pgdf = grid.Gridcreator(names, isellforgrid, month_minR, htl_dowWt, clustName, month_jump, jfacts,
                                        jumpType[names], psy_fact, priceType[names])
                # pgdf = grid.Gridcreator(names, isellforgrid, month_minR, htl_dowWt, clustName, month_jump, jfacts,
                #                         jumpType[names], psy_fact, 'Seasonal')

                if names in format2isells:
                    # -------------dump grid for format2 iSell----------------------------
                    pgdf.to_excel(basepath + '\{}\{}'.format('Pricing_Grid', names + '_Monthly_PG.xlsx'))
                    # pgdf.to_excel(basepath + '\{}\{}'.format('Pricing_Grid', names + '_Seasonal_PG.xlsx'))

                else:
                    pass

        elif priceType[names] == 'Seasonal':
            logging.info('\tPricing Type is :{}'.format(priceType[names]))
            # -----------------Seasonal Range, Minimum Rates, MaxRates Jumps------------------------
            s1start = name_s1s[names]
            s1end = name_s1e[names]
            s2start = name_s2s[names]
            s2end = name_s2e[names]
            # czon range
            csonrange = [s1start, s1end, s2start, s2end]

            s1min = name_s1min[names]
            s2min = name_s2min[names]

            # czonal min rates
            czonminrates = [s1min, s2min]
            czonminratesdict = {'S1': czonminrates[0], 'S2': czonminrates[1]}

            # czonmaxrates
            czonmaxrates = [name_s1max[names], name_s2max[names]]

            s1jump = name_s1jump[names]
            s2jump = name_s2jump[names]
            # czonal jumps
            czonjumps = [s1jump, s2jump]
            czonjumpsdict = {'S1': czonjumps[0], 'S2': czonjumps[1]}

            iSelldf44, isellforgrid = czonprice.czonmin_max(names, iSelldf4, csonrange, czonminrates, htl_dowWt, jfacts,
                                                            czonjumps, htl_cluster, jumpType[names], czonmaxrates,
                                                            cson_useMax[names])

            # isellforgrid.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\isellforgrid.csv')

            logging.info('\tSeasonal Rates Fetched')

            if use_Grid[names] == 1:
                pgdf = pd.DataFrame(df_PG)
            else:
                pgdf = grid.Gridcreator(names, isellforgrid, czonminratesdict, htl_dowWt, clustName, czonjumpsdict,
                                        jfacts, jumpType[names], psy_fact, priceType[names])
                if names in format2isells:
                    # -------------dump grid for format2 iSell----------------------------
                    pgdf.to_excel(basepath + '\{}\{}'.format('Pricing_Grid', names + '_Seasonal_PG.xlsx'))
                else:
                    pass

        else:
            logging.info('\tPricing Type is not defined')
            sys.exit()
        logging.info("\tAll Grids Generated")

        # =============================================================================================
        # --------------------------------PRICING ALGOS------------------------------------------------
        # =============================================================================================

        # ===========================1) Simple Pricing =================================================

        if GridType[names] == 'Simple':
            iSelldf5, szRates = simp.simRecs(names, iSelldf44, int(pricejump[names]), Last_szrates, name_chman[names],
                                             name_cmflag[names], name_curr[names], psy_fact, use_ceiling[names],
                                             use_floor[names])
            # ------getting iSelldf5 and szRates from Simple GridType-----------------------
        else:
            # =======================2) HNF Based Pricing===================================================
            if name_hnf[names] == 'Yes':
                # -----------------------I)UK----------------------------------------------
                if name_chman[names] == 'UK':
                    try:
                        df_hnf = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                             delimiter=",", index_col=False, header=0, low_memory=False,
                                             quoting=csv.QUOTE_ALL, encoding='utf8')
                    except FileNotFoundError:
                        logging.info('HNF Not found for UK, It is mandatory for UK')
                        sys.exit()

                    if names == 'Leaf Hotel Dover':
                        htlsold, htlavail, oooflag = iSell_fun_02.TBhnfconv(df_hnf, name_maxcap[names], isellrange+rng)
                    else:
                        htlsold, htlavail, oooflag = iSell_fun_02.UKhnfconv(df_hnf, name_maxcap[names], isellrange+rng)

                    #                    htlsold,htlavail = iSell_fun_02.UKhnfconv(df_hnf,name_maxcap[names],isellrange+rng)

                    iSelldf444_1 = iSell_fun_02.merging(iSelldf44, htlsold)
                    iSelldf444 = iSell_fun_02.merging(iSelldf444_1, htlavail)
                    iSelldf5, szRates = iSell_fun_02.hnf_rcpalgo(iSelldf444, name_ftr[names], name_maxcap[names],
                                                                 name_curr[names], name_chman[names], Last_szrates,
                                                                 psy_fact, name_cmflag[names], use_ceiling[names],
                                                                 use_floor[names], use_cussion[names])
                    # -----------getting iSelldf5 and szRates from UK---------------------------------
                    logging.info('\tUK Recommendations added as per HNF updated !!!')

                # -----------------------I)TB----------------------------------------------

                elif name_chman[names] in ['TravelBook', 'BW']:
                    df_hnf = pd.read_csv(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.csv')),
                                         delimiter=",", index_col=False, header=0, low_memory=False,
                                         quoting=csv.QUOTE_ALL, encoding='utf8')
                    htlsold, htlavail, oooflag = iSell_fun_02.TBhnfconv(df_hnf, name_maxcap[names], isellrange+rng)

                    iSelldf444_1 = iSell_fun_02.merging(iSelldf44, htlsold)
                    iSelldf444 = iSell_fun_02.merging(iSelldf444_1, htlavail)
                    iSelldf5, szRates = iSell_fun_02.hnf_rcpalgo(iSelldf444, name_ftr[names], name_maxcap[names],
                                                                 name_curr[names], name_chman[names], Last_szrates,
                                                                 psy_fact, name_cmflag[names], use_ceiling[names],
                                                                 use_floor[names], use_cussion[names])
                    # -----------getting iSelldf5 and szRates from UK---------------------------------
                    logging.info('\tTB Recommendations added as per HNF updated !!!')

                # -----------------II) HNF based Direct Pricing --------------------------------------
                else:
                    if GridType[names] == 'Direct':
                        cmflag = name_cmflag[names]
                        df_hnf = pd.read_excel(basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.xlsx')))
                        logging.info("\tHNF read for {}".format(names))
                        # ----------------------calculate hotel sold and availability frames------------------------
                        htlsold, htlavail, oooflag = iSell_fun_02.hnfconv(df_hnf, name_cap[names], isellrange+rng)
                        iSelldf444_1 = iSell_fun_02.merging(isellforgrid, htlsold)
                        iSelldf444 = iSell_fun_02.merging(iSelldf444_1, htlavail)
                        iSelldf5, szRates = directRecs.dRecs(iSelldf444, pgdf, isellrange+rng, Last_szrates, cmflag,
                                                             priceType[names], name_hnf[names], name_ftr[names])
                        logging.info('\tDirect Recommendations added as per HNF updated !!!')
                        # ------getting iSelldf5 and szRates from Direct GridType-----------------------

                    # ---------------------III) HNF Based Normal Pricing #------------------------------------------
                    else:
                        try:
                            df_hnf = pd.read_excel(
                                basepath + '\{}\{}\{}'.format('HNF', tdayfold, names + str('_HNF.xlsx')))
                        except FileNotFoundError:
                            logging.info(
                                'HNF Not Found please update HNF or set No in HNF column of Input Conditions Master')
                            print('HNF Not Found please update HNF or set No in HNF column of Input Conditions Master')
                            sys.exit()

                        logging.info("\tHNF read for {}".format(names))
                        htlsold, htlavail, oooflag = iSell_fun_02.hnfconv(df_hnf, name_cap[names], isellrange+rng)

                        iSelldf444_1 = iSell_fun_02.merging(iSelldf44, htlsold)
                        iSelldf444 = iSell_fun_02.merging(iSelldf444_1, htlavail)
                        iSelldf5, szRates = iSell_fun_02.hnf_rcpalgo(iSelldf444, name_ftr[names], name_maxcap[names],
                                                                     name_curr[names], name_chman[names], Last_szrates,
                                                                     psy_fact, name_cmflag[names], use_ceiling[names],
                                                                     use_floor[names], use_cussion[names])
                        # ------getting iSelldf5 and szRates from Normal GridType-----------------------
                        logging.info('\tNormal Recommendations added as per HNF updated !!!')

                        # ==========================3) Non HNF Based Pricing=======================================
            else:
                if GridType[names] == 'Direct':
                    # -----------------I) Direct Recommendations(Non HNF Based) -----------------------------------
                    cmflag = name_cmflag[names]
                    iSelldf5, szRates = directRecs.dRecs(isellforgrid, pgdf, isellrange+rng, Last_szrates, cmflag,
                                                         priceType[names], name_hnf[names], name_ftr[names])
                    logging.info("\tDirect Recommendations added (Non HNF)")
                else:
                    # -------------------II) Normal Pricing(Non HNF Based) #------------------------------------------------
                    iSelldf5, szRates = iSell_fun_02.nonHNF_rcpalgo(iSelldf44, name_ftr[names], name_maxcap[names],
                                                                    name_curr[names], name_chman[names], Last_szrates,
                                                                    psy_fact, name_cmflag[names], use_ceiling[names],
                                                                    use_floor[names], use_cussion[names])
                    logging.info('\tNormal Recommendations added (Non HNF)')

                    # =========================================================================================

        logging.info('\t-----------------------------')
        # =================== Merge Current Seasonal rates with iSell for cmflag = 0  ==============================================
        if cmflag == 0:
            iSelldf55 = iSell_fun_02.merging(iSelldf5, szRates)
            logging.info("\tSeasonal Rates merged with the iSell")
        elif cmflag == 1:
            iSelldf55 = pd.DataFrame(iSelldf5)
        else:
            logging.info('\tRateOnCM is not set in input conditions, it should be 0 or 1')
            sys.exit()

        # =====================================================================================================

        # 9)---------------------# Rate Shop #--------------------------------------
        lrate4, rstable2, cavg = iSell_fun_02.RateShop(rsfile, isellrange+rng,names,cc_value) #A.S. names,cc_value added 5May2023
        iSelldf6_1 = iSell_fun_02.merging(iSelldf55, lrate4)
        iSelldf6 = iSell_fun_02.merging(iSelldf6_1, rstable2)
        ls = []
       # #  #====================Rateshop Variance A.S. Jun2023================================
       # #
       #  lr=df_LR.columns.get_loc('LowestRate')
       #  mt=df_LR.columns.get_loc('Market Trend')
       #  rstable3=rstable2.iloc[:-1,1:]
       #  range1=range(lr+1,mt,2)
       #  lst=[]
       #  for i in range1:
       #      lst.append(i)
       #
       #  rstable3 = rstable2.iloc[:-1,0:]
       #  # rtvar=df_LR.iloc[:,lr+1:mt]
       #  rtvar = df_LR[df_LR['Date']>=(yday2)]
       #  rtvar = rtvar.iloc[:,lst]
       #  # rtvar=rtvar[rtvar['Date']>=yday]
       #
       #  rstable3.fillna(0,inplace=True)
       #  rstable3=rstable3.astype('object')
       #  rtvar.fillna(0,inplace=True)
       #  rtvar=rtvar.astype('object')
       #  rtvar=rtvar.reset_index()
       #  rtvar = rtvar.iloc[:,1:]
       #
       #
       #  #rstable3.iloc[:, 1]=rstable3.iloc[:, 1].astype('object')
       #
       # # abc_col=rstable3.iloc[:,1].apply(lambda x:str(x).split(' ')[0])
       #
       #  rstable4=pd.DataFrame()
       #
       #
       #  # dfrs = pd.DataFrame(pd.date_range(start=iSelldf6.iat[0,0], end=iSelldf6.iat[-2,0]), columns=['Date'])
       #  # #rstable4=dfrs.merge(rstable3,how='left',on='Date')
       #  #
       #  # rstable4 = pd.concat([dfrs,rstable3],ignore_index=True)
       #  # rstable4.fillna(0, inplace=True)
       #  # rstable4.drop_duplicates(subset=['Date'],inplace=True)
       #  iSelldf6_=iSelldf6.iloc[:-2,:]
       #  ls=[]
       #
       #  for i,y in enumerate(rtvar.columns,start=1):
       #      rstable4[y]=rstable3.loc[:,y].apply(lambda x:int(str(x).split(' ')[0]))-rtvar.loc[:,y].apply(lambda x:int(str(x).split(' ')[0]))
       #      rstable4[y].replace(0,'',inplace=True)
       #      iSelldf6_.insert(i+lr+1,i+lr+1,(rstable4[y].to_list()))
       #      ls.append(i+lr+1)
       #      lr=lr+1
       #
       #
       #
       #
       #

        #==========Data add from 1st date===================================

        # lr = df_LR.columns.get_loc('LowestRate')
        # mt = df_LR.columns.get_loc('Market Trend')
        #
        # if iSelldf6.iat[0,0]==tday:
        #     pass
        # else:
        #     df_LR1=df_LR.iloc[:, lr + 1:mt]
        #     df_LR1=df_LR1[df_LR1['Date']<tday]
        #
        #     pd.merge(iSelldf6,df_LR1,how='left',on='Date')





        #===================================================================
        logging.info('Rateshop added !!!')

        # 10)--------------------# Market Trend #-------------------------
        lavg = LRfinal2.loc[:, ['Date', 'LAvg']]
        #iSelldf7_1 = iSell_fun_02.merging(iSelldf6, lavg)
        iSelldf7_1 = iSell_fun_02.merging(iSelldf6, lavg)
        iSelldf7 = iSell_fun_02.merging(iSelldf7_1, cavg)
        iSelldf7['Market Trend'] = iSelldf7.loc[:, 'CAvg'] - iSelldf7.loc[:, 'LAvg']
        iSelldf7['Market Trend'] = iSelldf7['Market Trend'].fillna(value=0)
        iSelldf7.drop(['LAvg', 'CAvg'], axis=1, inplace=True)
        logging.info('Market Trend added !!!')

        if name_chman[names] in ['UK', 'TravelBook', 'BW']:
            iSelldf7.rename(columns={'OTA Revenue': 'Revenue'}, inplace=True)
            logging.info('UK or TravelBook iSell dataframe ::')
            iSelldf8 = iSelldf7
            logging.debug(iSelldf8)
        else:
            iSelldf8 = iSell_fun_02.merging(iSelldf7, otabreak)
            logging.info('OTA Data added !!!')

        if name_cmflag[names] == 0:
            iSelldf8 = iSell_fun_02.merging(iSelldf8, szRates)
            logging.info('Seasonal Rates merged for comparison')
            logging.debug(iSelldf8)
        else:
            pass

        # ----------------Handling OOO Flag-------------------------------------
        if name_hnf[names] == 'No':
            oooflag = 0
        else:
            pass

        if oooflag != 1:
            #            print("oooflag ::{}",format(oooflag))
            try:
                iSelldf8.drop('OOO', axis=1, inplace=True)
            except KeyError:
                pass
        else:
            pass

        logging.debug('handled oooflag ::')
        logging.debug(iSelldf8)

        # ----------------------------------------------------------------------

        collist = ['Season']
        try:
            iSelldf9_1 = iSelldf8.drop(collist, axis=1)
        except:
            iSelldf9_1 = pd.DataFrame(iSelldf8)

        iSelldf9 = pd.DataFrame(iSelldf9_1.iloc[:int(isellrange+rng), :])
        iSelldf10 = iSelldf9.round(0)
        iSelldf10['Date'] = iSelldf10['Date'].apply(lambda x: x.strftime("%d-%b-%Y"))

        # ------------------------------------Citadel Sarovar Portico Bengaluru------------------------------------------------

        # if names == "Citadel Sarovar Portico Bengaluru":
        #     iSelldf10.drop("Rooms Avail To Sell Online", axis=1, inplace=True)
        #     iSelldf10.drop("No", axis=1, inplace=True)
        #     iSelldf10.drop("Inventory Open%", axis=1, inplace=True)

        # --------------------------------------------------------------------------------------------------------------

        # 11)-------------------------# Drop col list #------------------------------
        if name_hnf[names] == 'Yes':
            # iSelldf10.drop('Rooms Avail To Sell Online',axis=1,inplace=True)
            iSelldf10 = pd.DataFrame(iSelldf10)
        else:
            pass

        colname = list(dropcol[name_chman[names]])
        colnames = [n for n in colname if str(n) != 'nan']

        logging.debug('column names list to drop columns(mapping) which are not required ::')
        logging.debug(colnames)

        try:
            iSelldf10.drop(colnames, axis=1, inplace=True)
        except:
            pass

        logging.debug('column names dropped')
        # 12)--------------------# Adoption #------------------------------------------
        finaladop = iSell_fun_02.Adopcal(iSelldf10, 179, 89)
        logging.info("Adoption calculated ::")
        logging.debug(finaladop)

        #        #========================reset name again for format2(check flag)=========================
        #        if format2flag == 1:
        #            names = names+'_OTA'
        #        else:
        #            pass

        # ------------------------------------------Inventory Open%--------------A.S.23---------------------

        # iSelldf10["Inventory Open %"] = (iSelldf10["Rooms Avail To Sell Online"] / (
        #             iSelldf10["Capacity"] - iSelldf10["OTA_Sold"])) * 100
        # iSelldf10["Inventory Open %"] = iSelldf10["Inventory Open %"].astype('int')
        # df_inv = iSelldf10.loc[:, ['Date', 'Inventory Open%']]
        df_inv_ = iSelldf10.loc[:,['Date','Inventory Open%']]
        df_inv = df_inv_[df_inv_['Inventory Open%']<30]
        df_inv = df_inv.iloc[1:,:]
        # --------------------------------------------------------------------------------------


        # =================================A.S. 23May23==========================================


        sum_positve_pickups = iSelldf10['Pickup'].agg(lambda count: count[count > 0].sum())
        sum_negative_pickups = -(iSelldf10['Pickup'].agg(lambda count: count[count < 0].sum()))

        total = sum_positve_pickups - sum_negative_pickups

        # ---------------------------
        xyz = df_LR[df_LR['Date'] >= yday1.strftime('%Y-%m-%d')]
        revenue_pickup = int(iSelldf10['OTA Revenue'].sum()) - int(xyz.loc[:, 'OTA Revenue'].sum())
        # ---------------------------


        try:
            adr_pickup = int((revenue_pickup)/abs(total))
        except:
            adr_pickup=0

        text1 = "Total Pickup ({}) - Total Wash ({}) = Actual pickup ({}) Vs. Last report - until next 180 days".format(sum_positve_pickups.astype(int), +sum_negative_pickups.astype(int), total.astype(int))
                  
        text2 = "Total Revenue Pickup = {}".format(revenue_pickup)
                  
        text3 = "Total ADR Pickup = {}".format(adr_pickup)

        text=[text1,text2,text3]
        #------------------------------------------------------------------------




        #------------------------------------------------------------------------------------
        if name_cmflag[names] == 0:
            pass

        else:
            iSelldf10['Rate on CM'] = iSelldf10['Rate on CM'].fillna(0)

            iSelldf10['Rate on CM'] = iSelldf10['Rate on CM'].astype('float64').astype('int64')
       #---------------------------------------------------------------------------------------

        iSelldf10['Date']=iSelldf10['Date'].apply(lambda x:datetime.strptime(x,"%d-%b-%Y"))
        iSelldf10['Date'] = iSelldf10['Date'].apply(lambda x:x.date())


        # 13)-----------------#Rate on CM check and iSell CSV dump #-------------------------------------
        if name_cmflag[names] == 0:
            iSelldf10.drop('SeasonalRate_x', axis=1, inplace=True)

            try:
                iSelldf10.drop('No', axis=1, inplace=True)
            except:
                pass




            iSelldf10.to_csv(basepath + '\\' + 'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold, names, iselldt))
            logging.info('{}_{}_iSell generated_#{} !!!----------------'.format(sr, names, name_chman[names]))
            print('{}_iSell generated_#{} !!!----------------'.format(names, name_chman[names]))
            beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange, glossary,
                                     name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
                                     name_cap[names],cm_room_type_df,tday,rng,ls)
            # beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange, glossary,
            #                          name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
            #                          name_cap[names])


        elif name_cmflag[names] == 1:
            if (iSelldf10['Rate on CM'].sum() == 0):
                # logging.info('iSell CSV is dumped in OutPut_CSV with BAD name as the Rate on CM column is Zero')
                # print('iSell CSV is dumped in OutPut_CSV with BAD name as the Rate on CM column is Zero')

                iSelldf10.to_csv(basepath + '\\' + 'OutPut_CSV\{}\iSell_{}_{}_BAD.csv'.format(tdayfold, names, iselldt))
                beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange,
                                         glossary, name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
                                         name_cap[names],cm_room_type_df,tday,rng,ls)
                # beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange,
                #                          glossary, name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
                #                          name_cap[names])

            else:
                logging.info('iSell CSV is dumped in OutPut_CSV folder')
                iSelldf10.to_csv(basepath + '\\' + 'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold, names, iselldt))
                beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange,
                                         glossary, name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
                                         name_cap[names],cm_room_type_df,tday,rng,ls)#A.S. jun23 tday
                # beautiMode.isellbeautify(defaultpath, iSelldf10, names, beautipth, name_win2[names], isellrange,
                #                          glossary, name_ftr[names], pgdf, finaladop, name_accman[names], rateshopfile,
                #                          name_cap[names])


            print('{}_iSell Generated _#{} !!!----------------'.format(names, name_chman[names]))
            logging.info('{}_iSell Generated _#{} !!!----------------'.format(names, name_chman[names]))
        else:
            logging.info('Please set 0 or 1 to RateOnCM column of Accounts sheet')
            sys.exit()

            # 14)===========================Format2 Call==========================================
        if format2flag == 1:
            logging.info('Format2 condition (format2flag ==1) ::')
            outcsvpath = basepath + '\\' + 'OutPut_CSV\{}'.format(tdayfold)
            combine_iSell, finaladop = form2.total_ota_merging(names[:-4], name_ftr[names], iselldt, outcsvpath)
            logging.debug(combine_iSell)
            combine_iSell['Date'] = combine_iSell['Date'].apply(lambda x: datetime.strptime(x, "%d-%b-%Y"))
            combine_iSell['Date'] = combine_iSell['Date'].apply(lambda x: x.date())
            if names=="YO1 Health Resort_OTA":
                names1="YO1 Health Resort_OTA_Combine"
                combine_iSell.to_csv(basepath + '\\' + 'OutPut_CSV\{}\iSell_{}_{}.csv'.format(tdayfold, names1, iselldt))

            beautiMode.isellbeautify(defaultpath, combine_iSell, names[:-4] + '_Combine', beautipth,
                                     int(name_win2[names]), isellrange, glossary, name_ftr[names], pgdf, finaladop,
                                     name_accman[names], rateshopfile, name_cap[names],cm_room_type_df,tday,rng,ls)

        else:
            pass

        #=============================A.S. 16Aug23===========================================

        if names=='YO1 Health Resort':
            names='YO1 Health Resort_Combine'

        spath =defaultpath+'\\InputData\\Demand\\'+f"{names}_DM.xlsx"

        if path.exists(spath):
            fileToSend = beautipth + '\\' + tdayfold + '\\' + name_accman[names]
            to_day = date.today()
            date1 = to_day.strftime('%d%b%Y')
            filename = 'iSell_{}_{}.xlsx'.format(names, date1)
            filename2 = 'iSell_{}_{}-copy.xlsx'.format(names, date1)

            tpath=[fileToSend+'\\'+filename,fileToSend+'\\'+filename2]
            #spath=f"C:\\vinash\\{names}_DM.xlsx"

            def TestCopyWorksheetMacro(tpath,spath):
            # Replace with the actual path

            # target_path=tpath
            # source_path=spath
                iSell_fun_02.CopyWorksheetToTargetWorkbook(tpath, spath)

            for i in tpath:
                TestCopyWorksheetMacro(i,spath)
        else:
            pass

        #=====================================================================================

        # ==============================suyash16may24=======================================================

        # a_name = accMan[0]
        # gtpath = defaultpath + '\\InputData\\Group_Tracker\\' + a_name + '\\' + f"{names}_GT.xlsx"
        gtpath = defaultpath + '\\InputData\\Group_Tracker\\'+ f"{names}_GT.xlsx"

        if path.exists(gtpath):
            fileToSend = beautipth + '\\' + tdayfold + '\\' + name_accman[names]
            to_day = date.today()
            date1 = to_day.strftime('%d%b%Y')
            filename = 'iSell_{}_{}.xlsx'.format(names, date1)
            filename2 = 'iSell_{}_{}-copy.xlsx'.format(names, date1)

            opath = [fileToSend + '\\' + filename, fileToSend + '\\' + filename2]

            def TestCopyWorksheetMacro(opath, gtpath):
                iSell_fun_02.CopyWorksheetToTargetWorkbook1(opath, gtpath)

            for i in opath:
                TestCopyWorksheetMacro(i, gtpath)
        else:
            pass
    #======================================================================================================

        mapping = pd.read_excel(defaultpath + '/masters/ExpMailMapping.xlsx')
        map = mapping[mapping['Hotel Name'] == names]
        status_name = dict(zip(map['Hotel Name'], map['Status']))
        status = status_name[names]

        if status == 'Yes':
            ema_name = dict(zip(map['Hotel Name'], map['Email Id']))
            num_name = dict(zip(map['Hotel Name'], map['Number']))
            email_id = ema_name[names]
            number = num_name[names]
            mail.send_alert_msg(beautipth, names, name_accman[names], email_id, number, iselldt, tdayfold,text) #A.S. May23-text
            # --------------------------mail mapping for inventory----------------------
            mapping1 = pd.read_excel(defaultpath + '/masters/InvMailMapping.xlsx')
            map1 = mapping1[mapping1['Hotel Name'] == names]
            status_name1 = dict(zip(map1['Hotel Name'], map1['Status']))
            status1 = status_name1[names]
            weekday = datetime.now().strftime('%A')
            if (status1 == 'Yes') and (weekday in ['Monday', 'Friday']):
                ema_name1 = dict(zip(map1['Hotel Name'], map1['Email Id']))
                num_name1 = dict(zip(map1['Hotel Name'], map1['Number']))
                email_id1 = ema_name1[names]
                number1 = num_name1[names]
                if df_inv.head(180).empty:
                  pass
                else:
                  mail.inv_open_msg(names, iselldt, email_id1, number1, df_inv.head(180))

        else:
            print('Status is no for this {} hotel'.format(names))
    logging.info("################## ALL iSell Generated for {} , Thanks ! ########################".format(accMan))
    print("###### ALL iSell Generated for {} , Thanks ! #######".format(accMan))
    # end=time.time()
    # print(end-start)











