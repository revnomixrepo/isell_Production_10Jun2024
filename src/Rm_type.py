import pandas as pd
import iSell_fun_02
import numpy  as np
import logging
from datetime import datetime

def rm_StaahMax(cmdata):
    ##A
    dfff = cmdata.copy()
    columns_0_ls = dfff[dfff.columns[0]].to_list()
    data_start_row_index = columns_0_ls.index('Availability')
    data_date_row_index = data_start_row_index + 1

    columns_0_ls_modified = columns_0_ls[data_date_row_index:]
    room_index = columns_0_ls_modified.index(np.nan)

    df_ = dfff.iloc[data_date_row_index: data_date_row_index + room_index]

    df_ = df_.T.reset_index(drop=True)
    df_.columns = df_.iloc[0]
    df_ = df_.rename(columns={df_.columns[0]: 'Date'})
    df = df_[1:].reset_index(drop=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

    melt_avl = df.melt(id_vars=df[["Date"]], var_name='Room Type',
                       value_name='Availability')

    ##Rates
    columns_0_ls = dfff[dfff.columns[0]].to_list()
    data_start_row_index = columns_0_ls.index('Room Rates')
    data_date_row_index = data_start_row_index + 1

    columns_0_ls_modified = columns_0_ls[data_date_row_index:]
    room_index = columns_0_ls_modified.index(np.nan)

    df_ = dfff.iloc[data_date_row_index: data_date_row_index + room_index]

    df_ = df_.T.reset_index(drop=True)
    df_.columns = df_.iloc[0]
    df_ = df_.rename(columns={df_.columns[0]: 'Date'})
    df = df_[1:].reset_index(drop=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

    melt_Rmrates = df.melt(id_vars=df[["Date"]], var_name='Room Type',
                           value_name='Room Rates')

    main_df = melt_avl.merge(melt_Rmrates, on=['Date', 'Room Type'])
    return main_df

def rm_eZee(cmdata):
    df= cmdata.copy()

    df = df[df['Room Type'] != '-'].reset_index(drop=True)
    df = df.drop(columns=['Room Type ID', 'Operation', 'Rate Plan ID', 'Rate Plan'])
    df_melt = df.melt(id_vars=df[['Room Type']], var_name='Date', value_name='Room Rates')

    try:
        df_melt['Date'] = pd.to_datetime(df_melt['Date'], format='@%Y-%m-%d')
    except:
        df_melt['Date'] = pd.to_datetime(df_melt['Date'], format='%Y-%m-%d')

    return df_melt

def rm_axisroom():
    pass



def cmpc_rmType(cmdata,chman,pcdata):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_Avails')

    # if chman == 'Staah':
    #     dfa,dfb = CM_Staah(cmdata,msrate,ftr,isellrange)
    #
    # elif chman == 'StayFlexi':
    #     dfa, dfb = CM_StayFlexi(cmdata, msrate, ftr, isellrange)
    #
    # elif chman == 'Synxis':
    #     dfa, dfb = CM_Synxis(cmdata, msrate, ftr, isellrange)
    #
    # elif chman == 'AsiaTech1':
    #     dfa, dfb = CM_AsiaTech1(cmdata,pcdata,ftr, msrate, ratepl, isellrange)
    #
    # elif chman == 'AxisRooms':
    #     print("AxisRooms - CM Availability and Rate Fetch")
    #     dfa,dfb = CM_AxisRooms(cmdata,pcdata,ftr,isellrange)
    #
    # elif chman == 'Maximojo':
    #     dfa,dfb = CM_Maximojo(cmdata,msrate,ratepl,ftr,isellrange)
    #
    # elif chman == 'eZee':
    #     dfa,dfb = CM_eZee(cmdata,ratepl, pcdata,ftr,isellrange, htlname)
    #
    # elif chman in ['TB','TB1']:
    #     dfa,dfb = CM_TB_Normal(cmdata,ratepl, pcdata,ftr,isellrange)
    #
    # elif chman == 'ResAvenue':
    #     print("ResAvenue - CM Availability and Rate Fetch")
    #     dfa,dfb = CM_ResAvenue(cmdata,pcdata,ftr,isellrange)
    # elif chman == 'BookingHotel':
    #     print("BookingHotel - CM Availability and Rate Fetch")
    #     dfa,dfb = BookingHotel_CM(pcdata, cmdata, ftr, msrate, isellrange)
    # elif chman == 'TravelClick':
    #     print("TravelClick - CM Availability and Rate Fetch")
    #     dfa, dfb = TravelClick(pcdata, cmdata,cmdata2, ftr, msrate, ratepl, isellrange)
    # elif chman == 'Eglobe':
    #     dfa, dfb = CM_Eglobe(cmdata,pcdata,ftr, msrate, ratepl, isellrange)
    # elif chman == 'Staah Max':
    #     dfa, dfb = CM_Staah_Max(cmdata,ftr, msrate, isellrange)
    #
    # logging.debug('availability and rateonCM frames returned to ProcessFlow')
    # return(dfa,dfb)
    return True
