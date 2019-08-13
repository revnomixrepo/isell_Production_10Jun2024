import iSell_fun_02
import pandas as pd
import numpy  as np
import logging
from datetime import datetime

def ezee_new_pc_data(file, ratepaln):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:ezee_new_pc_data')

    df_file = file.drop(columns=['Room Type ID', 'Room Type', 'Rate Plan ID'])
    df_file = df_file[df_file['Operation'] == 'Rates']
    df_file = df_file.drop(columns=['Operation'])
    # df_file = df_file.drop(0, axis=0)
    df_file = df_file.T.reset_index()
    new_header = df_file.iloc[0]
    df_file.columns = new_header
    df_file = df_file.iloc[1:, :]
    df_file.rename(columns={'Rate Plan': 'date'}, inplace=True)
    df_file['Date'] = pd.to_datetime(df_file['date'], format='@%Y-%m-%d')
    df_file = pd.DataFrame(df_file)
    df_file['Date'] = pd.to_datetime(df_file['Date'], format='%Y-%m-%d')
    df_rate = df_file[['Date', ratepaln]]
    df_rate = pd.DataFrame(df_rate)
    df_rate[ratepaln] = df_rate[ratepaln].astype(int)
    df_rate.rename(columns={ratepaln: 'Rate on CM'}, inplace=True)

    #------------returning only rateonCM from new eZee Extranet------------------
    logging.debug('RateonCM Frame (new eZee Extranet) ::')
    logging.debug(df_rate) 
    
    return df_rate


def TravelClick(rfile, ifile, ftr, msrate, rateplan, isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:TravelClick')
    tdate = datetime.today().date()
    year = tdate.year
    month = tdate.month

    # READ RATE FILE
    raw_rdf = pd.DataFrame(rfile)
    raw_rdf = raw_rdf[raw_rdf['Ratetype'] == msrate]

    raw_rdf = raw_rdf[raw_rdf['Roomtype'] == ftr]
    rt_df = raw_rdf[['Date', rateplan]]
    rt_df = pd.DataFrame(rt_df)
    rt_df = rt_df.rename(columns={rateplan: 'Rate on CM'})
    rt_df.Date = pd.to_datetime(rt_df.Date, format='%Y-%m-%d')

    # READ INVENTORY FILE
    i_df = pd.DataFrame(ifile)
    i_df = i_df.rename(columns={'Room': 'Raw_Date'})

    def date_conv(s):
        s.strip()
        i = s.split("/")
        mm = str(i[0])
        if int(mm) < month:
            n_year = year + 1
        else:
            n_year = year
        s = str(n_year) + str(s)
        return s

    i_df['Date'] = i_df['Raw_Date'].apply(lambda x: date_conv(str(x)))

    i_df['Date'].astype('datetime64[ns]')
    i_df['Date'] = pd.to_datetime(i_df['Date'])
    i_df[[0, 1]] = i_df['Property level'].str.split('/', expand=True)
    i_df[0] = i_df[0].astype(int)
    i_df = i_df.rename(columns={0: 'Rooms Avail To Sell Online'})
    inv_df = i_df[['Date', 'Rooms Avail To Sell Online']]

    flt_df = i_df[['Date', ' ' + ftr + ' ']]
    flt_df = pd.DataFrame(flt_df)
    flt_df[[0, 1]] = pd.DataFrame(flt_df[' ' + ftr + ' '].str.split('/', expand=True))
    flt_df[0] = flt_df[0].astype(int)
    flt_df = flt_df.rename(columns={0: ftr})
    flt_df = flt_df[['Date', ftr]]
    rt_df = iSell_fun_02.frame(rt_df, isellrange)
    inv_df = iSell_fun_02.frame(inv_df, isellrange)
    flt_df = iSell_fun_02.frame(flt_df, isellrange)
    cm_df = iSell_fun_02.merging(flt_df, rt_df)
    
    logging.debug('Availability Frame ::')
    logging.debug(inv_df)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cm_df) 
    
    return (inv_df, cm_df)



def BookingHotel_CM(rfile, ifile, ftr,msrate,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:BookingHotel_CM')

    def exsplit(df, column):
        numb_df = df[column].str.split('_', expand=True)
        return numb_df[1]
    # READ RATE FILE
    raw_df = pd.DataFrame(rfile)
    df = raw_df.transpose().reset_index()
#    df.fillna(value='Date', inplace=True)
    df = pd.DataFrame(df)
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header

    colLoc = df.columns.get_loc(msrate)
    rt_df = df.iloc[:, [colLoc + 1, colLoc + 2]]
    rt_df.columns= ['Date', 'SingleRate']
    rt_df = rt_df.rename(columns={'SingleRate': 'Rate on CM'})
    rt_df = rt_df[['Date', 'Rate on CM']]
    rt_df['Date'] = pd.to_datetime(rt_df.Date, format='%a, %d %b %Y')
    rt_df.Date = pd.to_datetime(rt_df.Date, format='%Y-%m-%d')

    # READ INVENTORY FILE
    raw_idf = pd.DataFrame(ifile)
    i_df = raw_idf.transpose().reset_index()        # Transpose file
    i_df = pd.DataFrame(i_df)
    # CHANGE HEADER LOCATION IN DF
    new_header = i_df.iloc[0]
    i_df = i_df[1:]
    i_df.columns = new_header

    i_df = i_df.rename(columns={'Unnamed: 0': 'Date'})
    colList = list(i_df.columns)
    colList.pop(0)
    i_df['Rooms Avail To Sell Online'] = 0
    for i in colList:
        i_df[i] = pd.to_numeric(exsplit(i_df, i))
        i_df['Rooms Avail To Sell Online'] += i_df[i]

    i_df['Date'] = pd.to_datetime(i_df.Date, format='%a, %d %b %Y')
    i_df['Date'] = pd.to_datetime(i_df.Date, format='%Y-%m-%d')

    # i_df.Date = pd.to_datetime(i_df.Date).dt.date
    inv_df = i_df[['Date', 'Rooms Avail To Sell Online']]
    delx_df = i_df[['Date', ftr]]

    rt_df = iSell_fun_02.frame(rt_df, isellrange)
    inv_df = iSell_fun_02.frame(inv_df, isellrange)
    delx_df = iSell_fun_02.frame(delx_df, isellrange)
    cm_df = iSell_fun_02.merging(delx_df, rt_df)
    
    logging.debug('Availability Frame ::')
    logging.debug(inv_df)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cm_df) 
    
    return(inv_df, cm_df)

def CM_TB(otadata,cmrate):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_TB')

    
    otadata.fillna(value=0,inplace=True)
    otadata = pd.DataFrame(otadata)
    otadata['Date'] = pd.to_datetime(otadata['Date'],format="%Y-%m-%d")
    otadata.rename(columns={'Sold':'OTA_Sold','Revenue':'OTA Revenue'},inplace=True)      
    
    otadata3 = pd.DataFrame(otadata.loc[:,['Date','OTA_Sold']]) 
    otadata4 = otadata.loc[:,['Date','OTA Revenue','ADR OTB']]
    otadata4['OTA Revenue'] = otadata4['OTA Revenue'].astype(float)
    otadata4['ADR OTB'] = otadata4['ADR OTB'].astype(float)   
    
    cmrate = pd.DataFrame(cmrate)
    cmrate3 = pd.DataFrame(cmrate.loc[:,['Date','CMRate']])
    cmrate3.rename(columns={'CMRate':'Rate on CM'},inplace=True)    
    cmrate4 =  iSell_fun_02.merging(otadata4,cmrate3)
    
    logging.debug('Availability Frame ::')
    logging.debug(otadata3)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cmrate4)  
    
    return(otadata3,cmrate4)
    

def CM_RezNext(cmdf,msrate,ftr,chnnel,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_RezNext')
    
    cmdf = pd.DataFrame(cmdf)        
    cmdf2= pd.DataFrame(cmdf.query('MealName == "{}" and ChannelName == "{}"'.format(msrate,chnnel)))
    
    cmdf2['Date'] = pd.to_datetime(cmdf2['Date'],format="%b %d %Y %I:%M%p")
    cmdf2['Date'] = pd.to_datetime(cmdf2['Date'],format="%Y-%m-%d")
    
    #======================FTR Avail ==================================================
    ftravail = pd.DataFrame(cmdf2[cmdf2['RoomName'] == ftr])
    ftravail2 = pd.DataFrame(ftravail.loc[:,['Date','Inventory']])
    ftravail2.rename(columns ={'Inventory':'{}'.format(ftr)},inplace=True)
    
    
    #==================Rooms Avail to Sell Online ============================
    cmavail = pd.DataFrame(cmdf2.groupby('Date')['Inventory'].sum())   
    cmavail.reset_index(inplace=True)
    cmavail2 = pd.DataFrame(cmavail.loc[:,['Date','Inventory']])
    cmavail2.rename(columns = {'Inventory':'Rooms Avail To Sell Online'},inplace=True)
    
    #===================Rate on CM =======================================   
    cmdf3 = pd.DataFrame(cmdf2.loc[:,['Date','RoomName','Single']])
    cmdf4 = pd.DataFrame(cmdf3[cmdf3['RoomName'] == ftr])
    cmdf4.rename(columns={'Single':'Rate on CM'},inplace=True)
    cmdf5 = pd.DataFrame(cmdf4.loc[:,['Date','Rate on CM']])
    cmdf5['Date'] = pd.to_datetime(cmdf5['Date'],format="%Y-%m-%d")
    
    #====================merge Avail and FTR avail ===========================
    availdf = cmavail2.merge(ftravail2,on='Date',how='left')
    availdf['Date'] = pd.to_datetime(availdf['Date'],format="%Y-%m-%d")    
    
    logging.debug('Availability Frame ::')
    logging.debug(availdf)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cmdf5)  
    
    return(availdf,cmdf5)


def CM_ResAvenue(cmdata,pcdata,ftr,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_ResAvenue')
    
    cmdata.drop('Unnamed: 0',axis=1,inplace=True)
    df2 = cmdata.T
    df2.reset_index(inplace=True)
    
    new_header = df2.iloc[0] 
    df3 = df2[1:]
    df3.columns = new_header
    df4=pd.DataFrame(df3.rename(columns={'Rate Type':'Date'}))
    df4['Date']=pd.to_datetime(df4['Date'],format="%Y-%m-%d")


    df5 = iSell_fun_02.frame(df4,isellrange)

    df6 = pd.DataFrame(df5.loc[:,['Date','Single']])
    df6.rename(columns={'Single':'Rate on CM' },inplace=True)
    df6.fillna(value=0,inplace=True)
    df6['Rate on CM'] = df6['Rate on CM'].astype(float)
    df6['Rate on CM'] = df6['Rate on CM'].astype(int)
    
    
    #--------------------Availability and FTR ----------------------------------
    
    ddf2 = pd.DataFrame(pcdata[pcdata.Action=='Inventory'])
    ddf3 = ddf2.T
    ddf3.reset_index(inplace=True)
    ddf3.drop(1,axis=0,inplace=True)

    new_header = ddf3.iloc[0] 
    ddf4 = ddf3[1:]
    ddf4.columns = new_header

    ddf5=ddf4.rename(columns={'Room Type':'Date'})
    ddf5.fillna(value=0,inplace=True)

    colname = list(ddf5.columns)
    colname2 = colname[1:]

    ddf5['Rooms Avail To Sell Online'] = pd.DataFrame(ddf5.loc[:,colname2]).sum(axis=1)
    
    
    ddf5['Date']=pd.to_datetime(ddf5['Date'],format="%Y-%m-%d")
    
    ddf6=iSell_fun_02.frame(ddf5,isellrange)
    
    ddf7 = ddf6.loc[:,['Date',ftr]] #FTR avail
    ddf8 = ddf6.loc[:,['Date','Rooms Avail To Sell Online']] # Rmsavail
    
    ddf9 = iSell_fun_02.merging(ddf8,ddf7)
    
    
    logging.debug('Availability Frame ::')
    logging.debug(ddf9)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(df6)  
    
    
    return(ddf9,df6)


def CM_eZee(cmdata,ratepl,pcdata,ftr,isellrange, htlname):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_eZee')
    
    cmdata = pd.DataFrame(cmdata)
    cmdata['Date'] = pd.to_datetime(cmdata['Date'],format="%d-%m-%Y")
    rmsdf = cmdata.loc[:,['Date','roomtype','availablity']]
    rmsdf.drop_duplicates(inplace=True)
    rmsdf2 = pd.DataFrame(rmsdf.groupby(['Date'])['availablity'].sum())
    rmsdf2.reset_index(inplace=True) 
    rmsdf2.rename(columns={'availablity':'Rooms Avail To Sell Online'},inplace=True)
    rmsdf3= rmsdf2.loc[:,['Date','Rooms Avail To Sell Online']]
    rmsdf4 = iSell_fun_02.frame(rmsdf3,isellrange)
    
    #---------------------FTR Frame -----------------
    rmsdff = pd.DataFrame(rmsdf[rmsdf['roomtype']==ftr])
    rmsdff.drop(['roomtype'],axis=1,inplace=True)
    rmsdff.rename(columns={'availablity':ftr},inplace=True)

    #-------------merging--------------------------------
    rmsdf444 = pd.merge(rmsdf4,rmsdff,on='Date',how='left')    
    
    cm_ezee2 = cmdata[cmdata['rateplan'] == ratepl]
    cm_ezee3 = cm_ezee2.loc[:,['Date','baserate']]
    cm_ezee3['Date']=pd.to_datetime(cm_ezee3['Date'])
    cm_ezee3.rename(columns={'baserate':'Rate on CM'},inplace=True)
    
    #------------------change by Chakradhar------------------------------------
    if htlname == 'Hotel Emerald':
        cm_ezee5 = ezee_new_pc_data(pcdata, ratepl)
        cm_ezee4 = iSell_fun_02.frame(cm_ezee5, isellrange)
    else:
        cm_ezee4 = iSell_fun_02.frame(cm_ezee3, isellrange)
    #--------------------------------------------------------------------------
    
    rmsdf444.drop_duplicates(subset='Date', inplace=True)
    cm_ezee4.drop_duplicates(subset='Date', inplace=True)
    
    logging.debug('Availability Frame ::')
    logging.debug(rmsdf444)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cm_ezee4)  

    return(rmsdf444,cm_ezee4)


def CM_UK(otadata,cmrate,msrate,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_UK')
    
    
    otadata = pd.DataFrame(otadata)
    otadata['Date'] = pd.to_datetime(otadata['Date'],format="%d/%m/%Y %H:%M:%S")
    otadata['Date'] = pd.to_datetime(otadata['Date'],format="%d-%b-%Y")
    otadata.rename(columns={'Avail':'Rooms Avail To Sell Online','Total':'OTA_Sold','Accomm':'OTA Revenue','ARR':'ADR OTB',},inplace=True)
    otadata2 = iSell_fun_02.frame(otadata,isellrange)
    otadata3 =  otadata2.loc[:,['Date','Rooms Avail To Sell Online','OTA_Sold']]    
    otadata4 = otadata2.loc[:,['Date','OTA Revenue','ADR OTB']]    
    
    cmrate = pd.DataFrame(cmrate)
    cmrate2 = iSell_fun_02.frame(cmrate,isellrange)
    cmrate3 = cmrate2.loc[:,['Date',msrate]]
    cmrate3.rename(columns={msrate:'Rate on CM'},inplace=True)    
    cmrate4 =  iSell_fun_02.merging(otadata4,cmrate3)   
    
    logging.debug('Availability Frame ::')
    logging.debug(otadata3)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cmrate4)  
    
    return(otadata3,cmrate4)
    
    
def CM_Djubo(ttlsold,cap,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_Djubo')
    
    ttlsold = pd.DataFrame(ttlsold)
    cap = int(cap)
    ttlsold.rename(columns={'occupancydate':'Date'},inplace=True)
    
    try:
        ttlsold['Date']=pd.to_datetime(ttlsold['Date'],format="%d-%b-%Y")
    except:
        ttlsold['Date']=pd.to_datetime(ttlsold['Date'])
        
    ttlsold = iSell_fun_02.frame(ttlsold,isellrange)
        
    
    
    ttlsold['cap'] = cap
    ttlsold['No_of_Rooms'].fillna(value=0,inplace=True)
    ttlsold['Rooms Avail To Sell Online']=ttlsold['cap']-ttlsold['No_of_Rooms']
    ttlsold['Rooms Avail To Sell Online']=ttlsold['Rooms Avail To Sell Online'].astype('int')
    
    try:
        ttlsold['Date']=pd.to_datetime(ttlsold['Date'],format="%d-%b-%Y")
    except:
        ttlsold['Date']=pd.to_datetime(ttlsold['Date'])
     

    ttlsold3 = ttlsold.loc[:,['Date','Rooms Avail To Sell Online']]
    
    try:
        ttlsold3['Date']=pd.to_datetime(ttlsold3['Date'],format="%d-%b-%Y")
    except:
        ttlsold3['Date']=pd.to_datetime(ttlsold3['Date'])
        
        
    dfa=pd.DataFrame(ttlsold3)
    
    #------blank Rate on CM----------------------------------------------------
    ddmmyy=datetime.now()
    tday = ddmmyy.strftime("%d-%b-%Y")
    index=pd.date_range(tday,periods=isellrange)
    frame=pd.DataFrame({'Date':index})
    frame['Rate on CM']=np.nan
    dfb=frame
    
    
    logging.debug('Availability Frame ::')
    logging.debug(dfa)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(dfb)  
    
    return(dfa,dfb)




def CM_Maximojo(cmdata,msrate,rateid,ftr,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_Maximojo')
    
    df_cmm2 = cmdata[cmdata["RatePlan(Id)"] == rateid]
    
    #----------------------# FTR #-------------------------------------------------
    dff_cmm = df_cmm2[df_cmm2["RoomType(Name)"] == ftr]

    dff_cmm2 = dff_cmm.loc[:,['StayDate','Availability']]
    dff_cmm2.rename(columns={'StayDate':'Date','Availability':ftr},inplace=True)

    try:
        dff_cmm2['Date']=pd.to_datetime(dff_cmm2['Date'],format="%d-%b-%Y")
    except:
        dff_cmm2['Date']=pd.to_datetime(dff_cmm2['Date'])  #ftr frame 

    #-------------------------------Avail Frame ---------------------------
     
    df_cm2 = df_cmm2.groupby(['StayDate'])['Availability'].sum()
    df_cm3 = pd.DataFrame(df_cm2)
    df_cm3.reset_index(inplace=True)
    df_cm3.rename(columns={'StayDate':'Date','Availability':'Rooms Avail To Sell Online'},inplace=True)
    try:
        df_cm3['Date']=pd.to_datetime(df_cm3['Date'],format="%d-%b-%Y")
    except:
        df_cm3['Date']=pd.to_datetime(df_cm3['Date'])
        
    df_avail = iSell_fun_02.frame(df_cm3,isellrange)
    
    #----------------FTR merging ----------------------------------------------
    df_avail22 = pd.merge(df_avail,dff_cmm2,on='Date',how='left')
    
    #----------------Rate CM -----------------------------------------------
    cmrate=cmdata[cmdata['RatePlan(Id)'] == str(rateid)]
    cmrate2 = cmrate[cmrate['RoomType(Name)'] == msrate]
    cmrate3 = cmrate2.loc[:,['StayDate','Single']]
    cmrate3.rename(columns={'StayDate':'Date','Single':'Rate on CM'},inplace=True)
    try:
        cmrate3['Date']=pd.to_datetime(cmrate3['Date'],format="%d-%b-%Y")
    except:
        cmrate3['Date']=pd.to_datetime(cmrate3['Date'])        
        
    cmrate4 = iSell_fun_02.frame(cmrate3,isellrange)
    
    logging.debug('Availability Frame ::')
    logging.debug(df_avail22)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cmrate4)  
    
    return(df_avail22,cmrate4)


def CM_AxisRooms(cmdata,pcdata,ftr,isellrange):  
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_AxisRooms')
    
    df2 = cmdata.T
    df2.reset_index(inplace=True)    
    df2.dropna(axis=1,how='all',inplace=True)
    
    
    new_header = df2.iloc[0] #grab the first row for the header
    df2.columns = new_header
    df2.drop(0,axis=0,inplace=True)
    
    df2.rename(columns={np.nan:'Year','Room':'Day'},inplace=True)    
    df2['month']=[i[:3] for i in df2['Unnamed: 0']]
    
    df2['mon_num']=pd.to_datetime(df2.month, format='%b').dt.month
    for cols in ['Day', 'mon_num', 'Year']:
        df2[cols] = df2[cols].astype(int)
    #==========================================================================     
    for cols in ['Day', 'mon_num', 'Year']:
        df2[cols] = df2[cols].astype(str)
    #==========================================================================
    df2['Date']=df2['Day']+'-'+df2['month']+'-'+df2['Year']

    try:
        df2['Date'] = pd.to_datetime(df2['Date'],format='%d-%b-%Y')
    except:
        df2['Date'] = pd.to_datetime(df2['Date'])
        
    #--------------------FTR addition -----------------------------------------        
    df22 = df2.drop(['Unnamed: 0','Day','Year','month','mon_num'],axis=1)
    df222 = df22.loc[:,['Date',ftr]] #FTR DF
        

    c=['month','mon_num']
    df2.drop(c,axis=1,inplace=True)

    loc1=df2.columns.get_loc('Year')
    loc2=df2.columns.get_loc('Date')
    rooms=list(df2.columns)
    rooms2=rooms[loc1+1:loc2]
    df2[rooms2].fillna(value=0,inplace=True)
    df2.replace(to_replace='NA',value=0,inplace=True)
    df2['Rooms Avail To Sell Online'] = df2[rooms2].sum(axis=1)
    df2['Date']=pd.to_datetime(df2['Date'])
    df2['Rooms Avail To Sell Online'] = df2['Rooms Avail To Sell Online'].astype(int)
    df3=df2.loc[:,['Date','Rooms Avail To Sell Online']]
    
    #-----------------Merging with FTR------------------------
    df33 = pd.merge(df3,df222, on='Date', how='left')

    #---------------------PC Data----------------------------------------------
    pcdata=pd.DataFrame(pcdata)
    cm_df=pcdata.T
    cm_df2=pd.DataFrame(cm_df.iloc[:,0])
    cm_df3=pd.DataFrame(cm_df2)

    cm_df3.reset_index(inplace=True)
    cm_df3.rename(columns={'index':'Date',0:'Rate on CM'},inplace=True)
    cm_df3.drop([0,1],axis=0,inplace=True)
    cm_df3.reset_index(inplace=True)
    cm_df3.drop('index',axis=1,inplace=True)
    
    cm_df3['Rate on CM'].fillna(value=0,inplace=True)
    cm_df3['Rate on CM'] = cm_df3['Rate on CM'].astype(int)

    try:
        cm_df3['Date']=pd.to_datetime(cm_df3['Date'],format='%d-%b-%Y')
    except:
        cm_df3['Date']=pd.to_datetime(cm_df3['Date'])
        
    cm_df4=iSell_fun_02.frame(cm_df3,isellrange)
    
    logging.debug('Availability Frame ::')
    logging.debug(df33)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(cm_df4)    

    return(df33,cm_df4)

        
def CM_Staah(cmdata,msrate,ftr,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_Staah')
    
    cm2=pd.DataFrame(cmdata[cmdata.isnull().all(axis=1)])
    cm3=list(cm2.index)
    cmdata1=pd.DataFrame(cmdata.iloc[1:cm3[0],:])
    cmdata2=pd.DataFrame(cmdata.iloc[cm3[0]+1:cm3[1],:])
    
    #strip
    ll=list(cmdata2.columns)
    cmdata1[ll[0]] = cmdata1[ll[0]].map(lambda x: x.strip())#strip 1st column
    
    msratecode =msrate
    cmshaped=iSell_fun_02.cmreshape(cmdata1)
    cmfin11 = cmshaped.loc[:,['Date',msratecode]]
    cmfin111 = cmfin11.rename(columns={cmfin11.columns[1]:'Rate on CM'})
    msrateframe=iSell_fun_02.frame(cmfin111,isellrange)

    availshaped=iSell_fun_02.cmreshape(cmdata2)
    reqcols=list(availshaped.columns[1:])
    availshaped['Rooms Avail To Sell Online'] = availshaped.loc[:,reqcols].sum(axis=1)
    cmfin3=availshaped.loc[:,['Date','Rooms Avail To Sell Online']]

    availframe= iSell_fun_02.frame(cmfin3,isellrange)

    fthrou =availshaped.loc[:,['Date',ftr]]#flowthrough
    fthrou.columns=['Date',ftr]
    
    availframe2 = pd.merge(availframe,fthrou,on='Date',how='left')
    
    logging.debug('Availability Frame ::')
    logging.debug(availframe2)    
    
    logging.debug('RateonCM Frame ::')
    logging.debug(msrateframe)    
    
    return(availframe2,msrateframe)


def CM_Avails(cmdata,htlname,msrate,ftr,chman,pcdata,ratepl,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:CMAs, SubModule:CM_Avails')
    
    if chman == 'Staah':
        dfa,dfb = CM_Staah(cmdata,msrate,ftr,isellrange)
        
    elif chman == 'AxisRooms':
        print("AxisRooms - CM Availability and Rate Fetch")
        dfa,dfb = CM_AxisRooms(cmdata,pcdata,ftr,isellrange)  
        
    elif chman == 'Maximojo':
        dfa,dfb = CM_Maximojo(cmdata,msrate,ratepl,ftr,isellrange)
        
    elif chman == 'eZee':
        dfa,dfb = CM_eZee(cmdata,ratepl, pcdata,ftr,isellrange, htlname)
        
    elif chman == 'ResAvenue':
        print("ResAvenue - CM Availability and Rate Fetch")
        dfa,dfb = CM_ResAvenue(cmdata,pcdata,ftr,isellrange)
    elif chman == 'BookingHotel':
        print("BookingHotel - CM Availability and Rate Fetch")
        dfa,dfb = BookingHotel_CM(pcdata, cmdata, ftr, msrate, isellrange)
    elif chman == 'TravelClick':
        print("TravelClick - CM Availability and Rate Fetch")
        dfa, dfb = TravelClick(pcdata, cmdata, ftr, msrate, ratepl, isellrange)
        
    logging.debug('availability and rateonCM frames returned to ProcessFlow')
    return(dfa,dfb)

