import pandas as pd
import numpy  as np
import logging
from datetime import datetime


def TBhnfconv(df_hnf,maxcap,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:TBhnfconv')
    logging.info('You are in TBdfconv')
    df_hnf['Date']=pd.to_datetime(df_hnf['Date'],format="%Y-%m-%d")   
    df_hnf2=frame(df_hnf,isellrange) 
    df_hnf2['Cap'] = int(maxcap)
    df_hnf2['Avail'] = df_hnf2['Cap'] - df_hnf2['Sold']
    df_hnf3=df_hnf2.loc[:,['Date','Avail','Sold']]
    df_hnf3.rename(columns={'Avail':'Hotel Availability','Sold':'Hotel Sold'},inplace=True)
    df_hnf3.fillna(value=0,inplace=True)
    df_hnf4=df_hnf3.loc[:,['Date','Hotel Sold']]
    df_hnf5=df_hnf3.loc[:,['Date','Hotel Availability']]
    logging.info('hotel availability and Sold returned')
    oooflag=0
    return(df_hnf4,df_hnf5,oooflag)

def UKhnfconv(df_hnf,maxcap,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:UKhnfconv')
    
    df_hnf['Date']=pd.to_datetime(df_hnf['Date'],format="%d/%m/%Y %H:%M:%S")    
    df_hnf['Date']=pd.to_datetime(df_hnf['Date'],format="%d-%b-%Y")   
    df_hnf2=frame(df_hnf,isellrange)
    df_hnf3=df_hnf2.loc[:,['Date','Avail','Total']]
    df_hnf3.rename(columns={'Avail':'Hotel Availability','Total':'Hotel Sold'},inplace=True)
    
    df_hnf4=df_hnf3.loc[:,['Date','Hotel Sold']]
    df_hnf5=df_hnf3.loc[:,['Date','Hotel Availability']]  
    oooflag=0
    return(df_hnf4,df_hnf5,oooflag)
  
    
def hnfconv(hnf,totalcap,isellrange):
    hnf.dropna(axis=0, subset=['Date'],inplace=True)
    hnf.fillna(value=0,inplace=True)
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:hnfconv')
    hnf['Date']=pd.to_datetime(hnf['Date'],format="%d-%b-%Y")
    hnf['cap'] = int(totalcap)
    hnf['Sold'].fillna(value=0,inplace=True)
    hnf['Hotel Availability']=hnf['cap']-hnf['Sold']
    
     ################## THIS IS ACTUAL AVAILABILITY WHEN OUT OF ORDER AVAILABILITY IS GIVEN
    logging.debug(hnf.columns)
    try:
        hnf['Hotel Availability']=hnf['Hotel Availability']-hnf['OOO']
        logging.debug('Hotel Availability calculated , Hotel Availability = capacity - Sold')
        oooflag=1
        logging.debug('Actual Availability calculated when out of order is given,Hotel Availability=availability-OOO')
        logging.debug('oooflag set to 1 , Calculated availability by using OOO (hnf)::')
        logging.debug(hnf)       
        
    except:
        oooflag=0
        logging.debug('oooflag set to 0 (hnf) ::')
        logging.debug(hnf)
        
        
    hnf['Hotel Availability']=hnf['Hotel Availability'].astype(int)   
    hnf2 =frame(hnf,isellrange)
    hnf2.rename(columns={'Sold':'Hotel Sold'},inplace=True)
    hnf3 = hnf2.loc[:,['Date','Hotel Sold']]
    
    if oooflag==1:
        hnf4 = pd.DataFrame(hnf2.loc[:,['Date','Hotel Availability','OOO']])
    else:
        hnf4 = pd.DataFrame(hnf2.loc[:,['Date','Hotel Availability']])
    
    logging.debug('Hotel Sold, Hotel Availability Returned ::')
    logging.debug('Hotel Sold(hnf3) ::')    
    logging.debug(hnf3)
    
    logging.debug('Hotel Availability(hnf4) ::')
    logging.debug(hnf4)
    return(hnf3,hnf4,oooflag)
    
    
def occframe(df1,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:occframe') 
       
    ddmmyy = datetime.now()                  
    tday = ddmmyy.strftime("%d-%b-%Y")               
    index=pd.date_range(tday,periods= isellrange)
    frame=pd.DataFrame({'occupancydate':index})
    df_all = pd.merge(frame,df1,on='occupancydate',how='left')
    
    logging.debug('Data merged on occupancydate column ::')
    logging.debug(df_all)
    return(df_all)

def frame(df1,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:frame') 
    
    df1 = pd.DataFrame(df1)
    ddmmyy = datetime.now()                  
    tday = ddmmyy.strftime("%d-%b-%Y")      
    index=pd.date_range(tday,periods= isellrange)
    frame=pd.DataFrame({'Date':index})
    merged = pd.merge(frame,df1,on='Date',how='left')
    
    logging.debug("Merged with iSellFrame on 'Date' column ::")
    logging.debug(merged)
    return(merged)
def frameMax(df1, isellrange):
    df1 = pd.DataFrame(df1)
    ddmmyy = datetime.now()
    tday = ddmmyy.strftime("%b-%d-%Y")
    index = pd.date_range(tday, periods=isellrange)
    frame = pd.DataFrame({'Date': index})
    df1 = pd.DataFrame(df1)
    # df1['Date'] = pd.to_datetime(df1['Date'], format="%Y-%d-%m")
    df1['Date'] = pd.to_datetime(df1['Date'])
    merged = pd.merge(frame, df1, on='Date', how='left')
    return (merged)


def merging(df1,df2):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:merging') 
    mergedf=pd.merge(df1,df2,on='Date',how='left')
    
    logging.debug("Merged two DataFrames on 'Date' column ::")
    logging.debug(mergedf)
    return(mergedf)
    
def dfconv(stdpth,cmfile2,htl,chman):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:dfconv') 
    #------------files required for mapping channel manager columns,DateFormats,Status----
    CMcols = pd.read_excel(stdpth+'\\'+'masters\cm_master.xlsx')
    statusdf = pd.read_excel(stdpth+'\\'+'masters\statuscodes.xlsx')
    statuscode = dict(zip(statusdf['status'],statusdf['code']))
    CMdates=pd.read_excel(stdpth+'\\'+'masters\DateFormats.xlsx')
    #--------------------------------------------------------------------------------------  
    
    stdcols = dict(zip(CMcols[chman],CMcols['stdname']))
    logging.debug('std column names mapping:')  
    logging.debug(stdcols)
    
    dtformat = dict(zip(CMdates['CM'],CMdates[chman]))
    logging.debug('Date Format mapping:')  
    logging.debug(dtformat)    
    
    #---------------renamed OTA data columns with standard name--------------------
    cmfile2.rename(columns=stdcols,inplace=True)
    cmfile2.dropna(axis=0,subset=['CheckIn','CheckOut'],inplace=True)
    logging.debug("Dropped rows having 'CheckIn','CheckOut' values blank") 
    
    cmfile2['CheckIn'] = pd.to_datetime(cmfile2['CheckIn'],format="{}".format(dtformat['CheckIn']))
    cmfile2['CheckOut'] = pd.to_datetime(cmfile2['CheckOut'],format="{}".format(dtformat['CheckOut']))
    logging.debug("Set dateformats as per 'Date Format mapping'") 
    
    logging.debug("DataFrame before exploading the dates ::")
    logging.debug(cmfile2)
    
    df_date=pd.concat([pd.DataFrame({
            'occupancydate' : pd.date_range(row.CheckIn, row.CheckOut),
            'Channel' : row.Channel,         
            'Status' : row.Status,
            'CheckIn': row.CheckIn,
            'CheckOut': row.CheckOut,
            'No_of_Rooms':row.No_of_Rooms,
            'Total_Amount': row.Total_Amount           
            },
    columns=['occupancydate','Channel','Status','CheckIn','CheckOut',
       'No_of_Rooms','Total_Amount']) for i, row in cmfile2.iterrows()], ignore_index=True)
    
    logging.debug("DataFrame after exploading the dates ::")
    logging.debug(df_date)

    df_date['dtDif'] = (df_date['CheckOut']-df_date['occupancydate']).apply(lambda x: x/np.timedelta64(1,'D'))
    logging.debug("dtDif column added,where dtDif = CheckOut - occupancydate")

    df_date['Arrivals'] = np.where((df_date['CheckIn']==df_date['occupancydate']), 1 , 0)
    df_date['Arrivals'] = df_date['Arrivals']*df_date['No_of_Rooms']	
    logging.debug("Arrivals calculated")
	
    df_date['Channel'].fillna(value='YourWeb',inplace=True)
    logging.debug("Blank Channel replaced with YourWeb")
    
    df_date['Total_Amount'].fillna(value=0,inplace=True)
    logging.debug("Blank Total_Amount replaced with 0")
    
    df_date['Status'].fillna(value='Cancelled',inplace=True)
    logging.debug("Replaced Blank Status values with 'Cancelled'")
    
    df_date['statuscode'] = df_date['Status'].map(statuscode)
    logging.debug("statuscode binary column added by mapping Status in data with statuscode dictionary")

    df_date2 = df_date.query('(dtDif > 0)') 
    logging.debug("data sliced as per condition (dtDif > 0) ::")
    logging.debug(df_date2)

    df_date3 = pd.DataFrame(df_date2[df_date2.statuscode == 1])
    logging.debug("data sliced as per condition statuscode == 1 ::")
    logging.debug(df_date3)

    #Add LOS , ADR, RPD
    df_date3['LOS'] = (df_date3['CheckOut'] - df_date3['CheckIn']).apply(lambda x: x/np.timedelta64(1,'D')) #Length of stay
    logging.debug("LOS column added where LOS = CheckOut - CheckIn")
     
    df_date3['RevPD'] = df_date3.loc[:,'Total_Amount'].div(df_date3.loc[:,'LOS'])  #Rev per Day
    logging.debug("RevPD column added where RevPD = Total_Amount/LOS")
    
    df_date3['ADR'] = df_date3.loc[:,'Total_Amount'].div(df_date3.loc[:,'LOS']*df_date3.loc[:,'No_of_Rooms']) #Average Daily Rate
    logging.debug("ADR(Average Daily Rate) column added where ADR = Total_Amount/(LOS x No_of_Rooms) ::")
    logging.debug(df_date3)

    #df_totalsold
    ttlsold = pd.DataFrame(df_date3.groupby(['occupancydate'])['No_of_Rooms'].sum())
    ttlsold.reset_index(inplace=True)
    logging.debug("ttlsold dataframe calculated ::")
    logging.debug(ttlsold)
    
    #df_total
    df_total = pd.DataFrame(df_date3.groupby(['occupancydate'])['No_of_Rooms','RevPD'].sum())
    df_total.reset_index(inplace=True)
    df_total['RevPD'] = df_total['RevPD'].round(2)
    
    logging.debug("df_total dataframe calculated :")
    logging.debug(df_total)

    #df_ota
    df_ota = pd.DataFrame(df_date3.groupby(['occupancydate','Channel'])['No_of_Rooms'].sum())
    df_ota.reset_index(inplace=True)
    logging.debug("df_ota dataframe calculated :")
    logging.debug(df_ota)        
    return(df_total,df_ota,ttlsold)
    


def dfLR(df1,chman):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:dfLR') 
    
    if chman in ['UK','TravelBook']:
        df1.rename(columns={'Hotel Sold':'OTA_Sold'},inplace=True)
    else:
        pass
    
    pos1 = df1.columns.get_loc('LowestRate')+1
    pos2 = df1.columns.get_loc('Market Trend')
    compp = df1.iloc[:,pos1:pos2]
    comp= compp.dropna(axis=1,how='all')
    comp=pd.DataFrame(comp)
    comptrs=list(comp.columns)
    for htls in comptrs:
        comp[htls] = comp[htls].str.split(" ", expand=True)
    #comp = comp.convert_objects(convert_numeric=True)  
    comp.fillna(value=0,inplace=True)
    comp=pd.DataFrame(comp)
    cols=list(comp.columns)
    comp[cols]=comp[cols].apply(pd.to_numeric,errors='coerce')
    comp['LAvg'] = comp.mean(axis=1)
    df_req = df1.loc[:,['Date','OTA_Sold']]
    LRfinal = pd.concat([df_req, comp], axis=1)
    LRfinal = pd.DataFrame(LRfinal)
    try:
        LRfinal['Date']=pd.to_datetime(LRfinal['Date'],format='%d-%b-%Y')
    except:
        LRfinal['Date']=pd.to_datetime(LRfinal['Date'])
        
    LRfinal2=LRfinal.loc[:,['Date','OTA_Sold','LAvg']]
    LRfinal3=LRfinal2.rename(columns={'OTA_Sold':'Last_OTASOLD'})
    LRfinal3['Last_OTASOLD']=LRfinal3['Last_OTASOLD'].astype(int)
        
    return(LRfinal3)


def RShop(rs):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:RShop') 
    
    rs2 = pd.pivot_table(rs,index='Date', columns = 'HotelName', values='Rate')
    comptrs=list(rs.HotelName.unique())
    rs3 = rs2.loc[:,comptrs]
    rs3['CAvg'] = rs3.mean(axis=1)
    rs3.reset_index(inplace=True)
    return(rs3)


def rename(df):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:rename')
    
    df['conditionscode'].replace(3.0, 'B',inplace=True) or df['conditionscode'].replace(2.0, 'S',inplace=True) or df['conditionscode'].replace(1.0, 'R',inplace=True)
    df['taxstatus'].replace(2.0, 'E)',inplace=True) or df['taxstatus'].replace(1.0, 'I)',inplace=True) or df['taxstatus'].replace(-1.0, 'U)',inplace=True)
    df['WebSiteCode'].replace(2.0, '(B',inplace=True) or df['WebSiteCode'].replace(7.0, '(G',inplace=True) or df['WebSiteCode'].replace(1.0, '(E',inplace=True)  or df['WebSiteCode'].replace(1691.0, '(P',inplace=True)
    return(df)

def chdtype(df2):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:chdtype')
    
    df2['WebSiteCode']=df2['WebSiteCode'].astype(str)
    df2['conditionscode']=df2['conditionscode'].astype(str)
    df2['taxstatus']=df2['taxstatus'].astype(str)
    df2['Rate']=df2['Rate'].astype(str)
    df2['conc']=df2['WebSiteCode']+df2['conditionscode']+df2['taxstatus']
    return(df2)

def mergecol(df2):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:mergecol')
    
    df2['Rate'] = df2[['Rate', 'conc']].apply(lambda x: '  '.join(x), axis=1) #space
    return(df2)

def cmreshape(df1):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:cmreshape')
    new_header = df1.iloc[0] 
    cmdata11 = df1[1:] 
    cmdata11.columns = new_header
    cmdata111=cmdata11.T
    new_head = cmdata111.iloc[0]
    cmdatafin = cmdata111[1:] 
    cmdatafin.columns = new_head
    cmdatafin.reset_index(inplace=True)
    cmfin1=cmdatafin.rename(columns={cmdatafin.columns[0]:'Date'})
    cmfin1['Date'] = pd.to_datetime(cmfin1['Date'])
    return(cmfin1)

def cmreshapeMax(df1):
    new_header = df1.iloc[1]
    cmdata11 = df1[2:]
    cmdata11.columns = new_header
    cmdata111 = cmdata11.T
    new_head = cmdata111.iloc[0]
    cmdatafin = cmdata111[1:]
    cmdatafin.columns = new_head
    cmdatafin.reset_index(inplace=True)
    cmfin1 = cmdatafin.rename(columns={cmdatafin.columns[0]: 'Date'})
    cmfin1['Date'] = pd.to_datetime(cmfin1['Date'],format='%d-%m-%Y')
    return (cmfin1)

def seasonminmax(df1):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:seasonminmax')
    df2=df1.iloc[[0,9]]
    df3=df2.loc[:,'Mon':]
    df4=df3.T
    df4.columns=['max_rate','min_rate']
    df5=df4.loc[:,['min_rate','max_rate']]
    return(df5)
    
def nonHNF_rcpalgo(dff1,ft,maxcap,htlcur,chman,lastsz,psy,cmflag,useceiling,usefloor,cussion):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:nonHNF_rcpalgo')
    
    
    df_rcp_season=dff1
    df_rcp_season['max_cap']=maxcap #read from RC
    
    logging.debug('max_capacity column added, max cap read from InputCondition is :{}'.format(maxcap))
    
    df_rcp_season['rate_dif']= (df_rcp_season['max_rate'] - df_rcp_season['min_rate'])
    logging.debug('rate_dif column added , where rate_dif = max_rate - min_rate')
    df_rcp_season['ota_max']= (df_rcp_season['Rooms Avail To Sell Online'] + df_rcp_season['OTA_Sold'])
    logging.debug('ota_max column added , where ota_max = Rooms Avail To Sell Online + OTA_Sold')
#    Changed by Sameer Kulkarni on 10-OCT-2018
#    df_rcp_season['cma_sqrt'] = np.sqrt(df_rcp_season['Rooms Avail To Sell Online'])
    
    df_rcp_season['cma_sqrt'] =np.where(df_rcp_season['Rooms Avail To Sell Online']<=0,1, np.sqrt(df_rcp_season['Rooms Avail To Sell Online']))
    
#    ================================================================================
    
    
#    df_rcp_season['cap_sqrt'] = np.sqrt(df_rcp_season['max_cap'])
    
    df_rcp_season['cap_sqrt'] = np.where(df_rcp_season['max_cap']<=0, 1, np.sqrt(df_rcp_season['max_cap']))
    
    df_rcp_season['cap_sqrt1'] = 1.5*df_rcp_season['cap_sqrt']
    df_rcp_season['cap_sqrt2'] = 2.5*df_rcp_season['cap_sqrt']
    df_rcp_season['ota_cap'] =  np.where((df_rcp_season['ota_max']==0),df_rcp_season['max_cap'],df_rcp_season['ota_max'])
    
#    logging.info("=============================")
#    logging.info(df_rcp_season['max_cap'])
#    logging.info(df_rcp_season['ota_max'])
#    logging.info(df_rcp_season['ota_cap'])
#    logging.info("=============================")

#    Changed by Sameer Kulkarni on 10-OCT-2018
#    df_rcp_season['ota_sqrt'] = np.sqrt(df_rcp_season['ota_cap'])
    df_rcp_season['ota_sqrt'] = np.where(df_rcp_season['ota_cap']<=0, 1, np.sqrt(df_rcp_season['ota_cap']))
#    ================================================================================
    
    df_rcp_season['ota_sqrt1'] = 1.5*df_rcp_season['ota_sqrt']
    df_rcp_season['ota_sqrt2'] = 2.5*df_rcp_season['ota_sqrt']
    df_rcp_season['sqrt0'] = df_rcp_season[['ota_sqrt','OTA_Sold']].max(axis=1)
    df_rcp_season['sqrt1'] = df_rcp_season[['ota_sqrt1','OTA_Sold']].max(axis=1)
    df_rcp_season['sqrt2'] = df_rcp_season[['ota_sqrt2','OTA_Sold']].max(axis=1)
    df_rcp_season['numarator'] = np.where((df_rcp_season['ota_max']<=df_rcp_season['cap_sqrt']),df_rcp_season['sqrt2'],
    np.where((df_rcp_season['ota_max']<=df_rcp_season['cap_sqrt1']),df_rcp_season['sqrt1'],
    np.where((df_rcp_season['ota_max']<=df_rcp_season['cap_sqrt2']),df_rcp_season['sqrt0'], df_rcp_season['OTA_Sold'])))
    df_rcp_season['denominator'] = df_rcp_season['max_cap'] - (df_rcp_season['max_cap'] - np.where((df_rcp_season['ota_max']==0),df_rcp_season['cap_sqrt'],df_rcp_season['ota_max']))
    
    #----------------------------------------------------Cussion Condition 04July2019----------------------------------------------------
    if cussion == 1:
        logging.debug('cussion set to 1, so cussion will be applied ::')
        df_rcp_season['ratio_top'] =np.where((df_rcp_season['ota_max']==0),1,
                 (np.where((df_rcp_season['OTA_Sold']==0), df_rcp_season['cma_sqrt'], 
                           df_rcp_season['OTA_Sold'])/df_rcp_season['ota_max']))
        logging.debug(df_rcp_season)
    else:
        logging.debug('cussion set to 0, so cussion will not be applied, set ratio_top = 1 ::')
        df_rcp_season['ratio_top'] = 1 
        logging.debug(df_rcp_season)
    #--------------------------------------------------------------------------------------------------------------------------   
    
        
    df_rcp_season['rcp']= (((df_rcp_season['rate_dif']*df_rcp_season['numarator'])/df_rcp_season['denominator'])*df_rcp_season['ratio_top']) + df_rcp_season['min_rate']
    logging.debug('rcp column calculated')
    #remove cussion limit for HNF
#    df_rcp_season['rcp']= ((df_rcp_season['rate_dif']*df_rcp_season['numarator'])/df_rcp_season['denominator']) + df_rcp_season['min_rate']
#    df_rcp_season.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\df_rcp_season.csv')
    
    df_rcp_season['rcp'].fillna(value=-1,inplace=True)
    logging.debug('blank rcp replaced with value -1')
    df_rcp_season['rcp']=df_rcp_season['rcp'].astype(int)
    logging.debug('rcp column datatype set to int ::')
    logging.debug(df_rcp_season)
    
    df_rcp_season['rcp'] = df_rcp_season['rcp'].apply(lambda row: applyPsychologicalFactor(row,psy))
    logging.debug('PsychologicalFactor Applied to rcp column  ::')
    logging.debug(df_rcp_season)
    
    #============================Setting for Djubo============================================================
    
    if cmflag ==0:
        logging.debug('cmflag = 0, i.e no Rate on CM column, so calculate SeasonalRate')
        seasonalrate=pd.DataFrame(df_rcp_season.loc[:,['Date','rcp']])
        seasonalrate.rename(columns = {'rcp':'SeasonalRate'},inplace=True)
        logging.info("calculated SeasonRate column from df_rcp_season, where 'rcp':'SeasonalRate' ")
        df_rcp_season = merging(df_rcp_season,lastsz)
        logging.info("merged last seasonal rates from LR ::") 
        logging.debug(df_rcp_season)
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] > df_rcp_season['Max_Rate'],df_rcp_season['Max_Rate'],df_rcp_season['rcp'])
            logging.debug('rcp set to Max_Rate where rcp > Max_Rate , as useceiling condition is 1 ::')
            logging.debug(df_rcp_season)
            
        else:
            logging.debug('useceiling = 0 , no setting of ceiling rate')
            pass
        #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] < df_rcp_season['Min_Rate'],df_rcp_season['Min_Rate'],df_rcp_season['rcp'])
            logging.debug('rcp set to Min_Rate where rcp < Min_Rate , as usefloor condition is 1 ::')
            logging.debug(df_rcp_season)
        else:
            logging.debug('usefloor = 0 , no setting of floor rate')
            pass
        #---------------------------------------------------------------------------------------
        
        df_rcp_season['rcp']=np.where(df_rcp_season['rcp'] == df_rcp_season['Last_szrate'],np.nan,df_rcp_season['rcp'])
        logging.debug('last recommendations(Last_szrate) compared with current rcp column')
        df_rcp_season.drop('Last_szrate',axis=1,inplace=True)
        
        recdf=pd.DataFrame(df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp']])
        recdf2=recdf.rename(columns={'rcp':'Recommended Rate'})
        
        logging.debug('Recommendations and SeasonalRate Returned ::')
        logging.debug('Recommendations (recdf2) ::')
        logging.debug(recdf2)
        
        logging.debug('SeasonalRate(seasonalrate) ::')
        logging.debug(seasonalrate)  
        
        return(recdf2,seasonalrate)
    
    #===============================================================================================================
    elif cmflag == 1:
        logging.debug('cmflag = 1, i.e Rate on CM column present, SeasonalRate not required')
        seasonalrate='NotRequired'          
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] > df_rcp_season['Max_Rate'],df_rcp_season['Max_Rate'],df_rcp_season['rcp'])
            logging.debug('rcp set to Max_Rate where rcp > Max_Rate , as useceiling condition is 1 ::')
            logging.debug(df_rcp_season)
        else:
            logging.debug('useceiling = 0 , no setting of ceiling rate')
            pass
        #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] < df_rcp_season['Min_Rate'],df_rcp_season['Min_Rate'],df_rcp_season['rcp'])
            logging.debug('rcp set to Min_Rate where rcp < Min_Rate , as usefloor condition is 1 ::')
            logging.debug(df_rcp_season)
        else:
            logging.debug('usefloor = 0 , no setting of floor rate')
            pass
        #---------------------------------------------------------------------------------------       
        df_rcp_season['rcp']=np.where(df_rcp_season['rcp'] == df_rcp_season['Rate on CM'],np.nan,df_rcp_season['rcp'])
                    
        recdf=pd.DataFrame(df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp']])
        recdf2=recdf.rename(columns={'rcp':'Recommended Rate'})
        
        logging.debug('Recommendations and SeasonalRate Returned ::')
        logging.debug('Recommendations(recdf2) ::')
        logging.debug(recdf2)
        
        
        return(recdf2,seasonalrate)


def hnf_rcpalgo(dff1,ft,maxcap,htlcur,chman,lastsz,psy,cmflag,useceiling,usefloor,cussion):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:hnf_rcpalgo')
    
    df_rcp_season=pd.DataFrame(dff1)
    df_rcp_season['max_cap']=maxcap #read from RC
    
    df_rcp_season['rate_dif']= df_rcp_season['max_rate'] - df_rcp_season['min_rate']
    #df_rcp_season['ota_max']= (df_rcp_season['Rooms Avail To Sell Online'] + df_rcp_season['OTA_Sold'])

    #================Set -ve Hotel Availability to zero====================================
#    df_rcp_season['ota_max']= (df_rcp_season['Hotel Availability'] + df_rcp_season['Hotel Sold'])
    df_rcp_season['ota_max']= (np.where(df_rcp_season['Hotel Availability'] < 0,0,df_rcp_season['Hotel Availability']) + df_rcp_season['Hotel Sold'])
    
    df_rcp_season['ota_max'] = np.where(df_rcp_season['ota_max']<0,0,df_rcp_season['ota_max'])
    
#    logging.info("========================================")
##    logging.info(df_rcp_season['ota_max'])
#    logging.info("========================================")
#    
    df_rcp_season['cma_sqrt'] =np.where(df_rcp_season['Hotel Availability']<=0, 1, np.sqrt(df_rcp_season['Hotel Availability']))
    
    df_rcp_season['cap_sqrt'] = np.sqrt(df_rcp_season['max_cap'])
    df_rcp_season['cap_sqrt1'] = 1.5*df_rcp_season['cap_sqrt']
    df_rcp_season['cap_sqrt2'] = 2.5*df_rcp_season['cap_sqrt']
    df_rcp_season['ota_cap'] =  np.where((df_rcp_season['ota_max']<=0),df_rcp_season['max_cap'],df_rcp_season['ota_max'])
    
#    logging.info("========================================")
##    logging.info(df_rcp_season['ota_cap'])
##    logging.info(df_rcp_season['max_cap'])
#    logging.info("========================================")
    
    df_rcp_season['ota_sqrt'] = np.where(df_rcp_season['ota_cap']<=0, 1, np.sqrt(df_rcp_season['ota_cap']))
    df_rcp_season['ota_sqrt1'] = 1.5*df_rcp_season['ota_sqrt']
    df_rcp_season['ota_sqrt2'] = 2.5*df_rcp_season['ota_sqrt']
    df_rcp_season['sqrt0'] = df_rcp_season[['ota_sqrt','Hotel Sold']].max(axis=1)
    df_rcp_season['sqrt1'] = df_rcp_season[['ota_sqrt1','Hotel Sold']].max(axis=1)
    df_rcp_season['sqrt2'] = df_rcp_season[['ota_sqrt2','Hotel Sold']].max(axis=1)
    
    df_rcp_season['numarator'] = np.where((df_rcp_season['ota_max']<=df_rcp_season['cap_sqrt']), df_rcp_season['sqrt2'],
                 np.where((df_rcp_season['ota_max'] <= df_rcp_season['cap_sqrt1']), df_rcp_season['sqrt1'],
                          np.where((df_rcp_season['ota_max'] <= df_rcp_season['cap_sqrt2']), df_rcp_season['sqrt0'], 
                                       df_rcp_season['Hotel Sold'])))
    df_rcp_season['denominator'] = df_rcp_season['max_cap'] - (df_rcp_season['max_cap'] - np.where((df_rcp_season['ota_max']==0),
                                         df_rcp_season['cap_sqrt'],df_rcp_season['ota_max']))
    
    #--------------------------------------cussion change 04July2019---------------------------------------------
    if cussion == 1:
        df_rcp_season['ratio_top'] =np.where((df_rcp_season['ota_max']==0),1,(np.where((df_rcp_season['Hotel Sold']==0),df_rcp_season['cma_sqrt'],df_rcp_season['Hotel Sold'])/df_rcp_season['ota_max']))
    else:
        df_rcp_season['ratio_top'] = 1
    #-------------------------------------------------------------------------------------------------------------    
#   removed cussion limit by Sam Sir on 29Mar2019, again cussion limit incorporated on 4july2019---------
    df_rcp_season['rcp']= (((df_rcp_season['rate_dif']*df_rcp_season['numarator'])/df_rcp_season['denominator'])*df_rcp_season['ratio_top']) + df_rcp_season['min_rate']   
#    df_rcp_season['rcp']= (((df_rcp_season['rate_dif']*df_rcp_season['numarator'])/df_rcp_season['denominator'])) + df_rcp_season['min_rate']
    
    df_rcp_season['rcp'].fillna(value=-1,inplace=True)
    df_rcp_season['rcp']=df_rcp_season['rcp'].astype(int)
#    df_rcp_season.to_csv(r'E:\iSell_Project\All_In_One_iSell\Testing\raw_rec.csv')
    df_rcp_season['rcp'] = df_rcp_season['rcp'].apply(lambda row: applyPsychologicalFactor(row,psy))

    
    #===============================Setting for Djubo ============================================================
    
    if cmflag==0:
        seasonalrate=pd.DataFrame(df_rcp_season.loc[:,['Date','rcp']])
        seasonalrate.rename(columns = {'rcp':'SeasonalRate'},inplace=True)
        logging.info("\tcalculated SeasonRates column")        
        df_rcp_season = merging(df_rcp_season,lastsz)        
        logging.info("\tmerged last seasonal rates from LR")   
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] > df_rcp_season['Max_Rate'],df_rcp_season['Max_Rate'],df_rcp_season['rcp'])
        else:
            pass
        #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] < df_rcp_season['Min_Rate'],df_rcp_season['Min_Rate'],df_rcp_season['rcp'])
        else:
            pass
        #---------------------------------------------------------------------------------------
        
        
        df_rcp_season['rcp']=np.where(df_rcp_season['rcp'] == df_rcp_season['Last_szrate'],np.nan,df_rcp_season['rcp'])
        df_rcp_season.drop('Last_szrate',axis=1,inplace=True)
        #recdf=pd.DataFrame(df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp','Season']])
        
        recdf=df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Hotel Sold','Hotel Availability','OOO','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp']]
        recdf2=recdf.rename(columns={'rcp':'Recommended Rate'})
        
        logging.debug('Recommendations and SeasonalRate Returned ::')
        logging.debug('Recommendations (recdf2) ::')
        logging.debug(recdf2)
        
        logging.debug('SeasonalRate(seasonalrate) ::')
        logging.debug(seasonalrate)        
        
        return(recdf2,seasonalrate)
    
    #===============================================================================================================
    elif cmflag==1:
        seasonalrate='NotRequired'  
        
        #-------------------------------set ceiling threshold---------------------------------
        if useceiling == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] > df_rcp_season['Max_Rate'],df_rcp_season['Max_Rate'],df_rcp_season['rcp'])
        else:
            pass
        #-------------------------------set floor threshold---------------------------------
        if usefloor == 1:
            df_rcp_season['rcp'] = np.where(df_rcp_season['rcp'] < df_rcp_season['Min_Rate'],df_rcp_season['Min_Rate'],df_rcp_season['rcp'])
        else:
            pass        
        #---------------------------------------------------------------------------------------
          
        
        df_rcp_season['rcp']=np.where(df_rcp_season['rcp'] == df_rcp_season['Rate on CM'],np.nan,df_rcp_season['rcp'])
        #recdf=pd.DataFrame(df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp','Season']])
        recdf=pd.DataFrame(df_rcp_season.loc[:,['Date', 'Dow', 'Event', 'Capacity','Hotel Sold','Hotel Availability','OOO','Rooms Avail To Sell Online',ft,'OTA_Sold', 'Pickup', 'OTA Revenue','ADR OTB', 'Rate on CM', 'rcp']])
        recdf2=recdf.rename(columns={'rcp':'Recommended Rate'})
        #
        return(recdf2,seasonalrate)



def recvalue(df,s,l,d,ptype):
    #-------------Filter Grid as per pricingType------------------------
    if ptype == 'Seasonal':
        sgrid=df[df.Season==s]
    elif ptype == 'Monthly':
        sgrid=df[df.Month==s]
    #-------------------------------------------------------------------        
    sgrid.reset_index(inplace=True)
#    v = sgrid.loc[l,d]
    v = sgrid.iloc[l][d]
    return(v)


def applyPsychologicalFactor(n,psyfact):
#    logging.info(psyfact)
    if n > 0:            
        if str(psyfact) == "nan":
            rval= int(n)  
        elif str(psyfact) == "NA":
            rval= int(n) 
        elif int(psyfact) == 1:
            rval= int(n) 
        else:
            psyfact = int(psyfact)
            rval=(int((round(n,-1))/psyfact)*psyfact)-1         
        return rval
    else:
        return(n)

def RateShop(rsfile,isellrange):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:RateShop')
    
    rsfile['Date'] = pd.to_datetime(rsfile['Date'])
    rsfile['Rate'] = rsfile['Rate'].astype(int)
    rsfile['LowestRate'] = rsfile['LowestRate'].astype(int)
    lrate=rsfile.loc[:,['Date','LowestRate']]
    lrate2 = lrate[lrate['LowestRate'] != 0]
    lrate3=lrate2.loc[:,['Date','LowestRate']]
    lrate4= frame(lrate3,isellrange)
    lrate4.fillna(value='SOLD',inplace=True)#lrate df

    rsfile1=rsfile.loc[:,['HotelName', 'Date', 'Rate']]
    finalrs1=RShop(rsfile1)
    cavg=finalrs1.loc[:,['Date','CAvg']]  #cavg df

    rsfile2 = rsfile.loc[:,['HotelName', 'Date', 'Rate', 'WebSiteCode','conditionscode', 'taxstatus']]
    rsfile3=rename(rsfile2)
    rsfile4=chdtype(rsfile3)
    rsfile5=mergecol(rsfile4)
    rsfile6=rsfile5.loc[:,['HotelName', 'Date', 'Rate']]
    comptrs=list(rsfile6.HotelName.unique())
    rstable = rsfile6.pivot_table(index='Date',columns='HotelName', values='Rate',aggfunc=lambda x: ' '.join(x))
    rstable2 = rstable.loc[:,comptrs]
    rstable2.reset_index(inplace=True)
    rstable2.replace(to_replace='0  0.00.00.0', value='NA', inplace=True)
    rstable2[comptrs[0]].replace(to_replace='NA', value='SOLD', inplace=True)
    
    logging.debug('lowest rate df, Pivoted RS_Data , Current Average Rates Returned ::')
    logging.debug('lowst rate df (lrate4) ::')
    logging.debug(lrate4)
    
    logging.debug('Pivoted RS_Data (rstable2) ::')
    logging.debug(rstable2)
    
    logging.debug('Current Average Rates  (cavg) ::')
    logging.debug(cavg)
    
    return(lrate4,rstable2,cavg)


def Adopcal(df,day180,day90):
    logging.debug('------------------------------------------------------------')
    logging.debug('Module:iSell_fun_02, SubModule:Adopcal')
    
    df=pd.DataFrame(df.loc[:,['Recommended Rate','Pickup']])
#    df.to_csv(r'E:\iSell_Project\Djubo\df.csv')
    df180 = pd.DataFrame(df.iloc[:day180,:])
    df90 = pd.DataFrame(df.iloc[:day90,:])
#    df30 = df.iloc[:30,:]
#    df15 = df.iloc[:15,:] 
   
    def daysadop(df3,daynum):
        logging.debug('------------------------------------------------------------')
        logging.debug('Module:Adopcal, SubModule:daysadop')
        
        df3.fillna(value=1,inplace=True)
        df4 = pd.DataFrame(df3[df3['Recommended Rate'] != 1])   
        df5 = pd.DataFrame(df4[df4['Pickup']==0])  
        logging.debug('Filtered iSell dataframe as (Recommended Rate != Blank and Pickup = 0)')
        
        if df5.empty:
            logging.debug('Filtered isell dataframe is empty, returned Adoption as 100') 
            return(100)
        else:
            rnum=list(df5.shape)
            rnum2 = rnum[0]        
            upnum = daynum-rnum2
            adop = (upnum/daynum)*100
            adop2 = int(adop)
            return(adop2)
    
    ad_180=daysadop(df180,day180)
    logging.debug('180 days Adoption calculated :{}'.format(ad_180))
    ad_90=daysadop(df90,day90)
    logging.debug('90 days Adoption calculated :{}'.format(ad_90))
#    ad_30=daysadop(df30,day30)
#    ad_15=daysadop(df15,day15)
    
    adoplist=[ad_90,ad_180]
    dayslist=['90days','180days']
    finaldf = dict(zip(dayslist,adoplist))
    
    finaldf2 = pd.DataFrame.from_dict(finaldf, orient='index')
    finaldf2.reset_index(inplace=True)
    finaldf2.columns = ['Adoption','Pct(%)']    
    logging.debug('Returned Adoption DataFrame(finaldf2) ::')
    logging.debug(finaldf2)
    return(finaldf2)






