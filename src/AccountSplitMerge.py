'''
------ACCOUNT REPORT------

Account Report for every individual Account manager's.

Report contain all manage data of hotel's that comes under the manager {name}

Create backup file from daily "input_condition_master" file

{cm_f...... - condition_master-file.....}
tdate -  Today date

'''

import pandas as pd
from datetime import date
import numpy as np
import os
import sys

cm_sheet1 = 'Accounts'
cm_sheet2 = 'Monthly_MinRates'
cm_sheet3 = 'Monthly_MaxRates'
cm_sheet4 = 'Monthly_Jump'
# cm_fPath = r'E:\All_In_One_iSell'
cm_fName = 'InputConditionMaster.xlsx'
tdate = date.today().__format__('%d%b%Y')


def var_init(drivepth, accpath ,condn):
    # INPUT FILE NAME "NOTE:- SHOULD NOT CHANGE"

    #    cm_fPath = r'E:\All_In_One_iSell'
    # cm_splitpath = r'E:\Chakradhar\QA_REVNO\AccountSplit_master\Managers'
    cm_splitpath = accpath
    cm_file = drivepth + r'\masters' + '\\' + cm_fName #backup path wo date
    cm_backupath = drivepth+r'\masters\MappingFiles\Backup'  # backup with date

    # COMPLETE PATH INCLUDING FILE NAME AND FILE PATH

    # SHEETS NAME OF ''InputConditionMaster.xlsx' FILE
    #    cm_sheet1 = 'Accounts'
    #    cm_sheet2 = 'Monthly_MinRates'
    #    cm_sheet3 = 'Monthly_MaxRates'
    #    cm_sheet4 = 'Monthly_Jump'

    #  READ SHEET FROM INPUT FILE
    cm_df1 = pd.read_excel(cm_file, sheet_name=cm_sheet1)    # cm_sheet1 = 'Accounts'

    cm_df1 = cm_df1[cm_df1['Status'] == 1]                   # FILTER COLUMN 'Status' by '1'
    cm_df1 = cm_df1.drop(['Sr.No'], axis=1)                  # DROP THE COLUMN NAME 'srno'

    cm_df2 = pd.read_excel(cm_file, sheet_name=cm_sheet2)    # cm_sheet2 = 'Monthly_MinRates'
    cm_df2 = cm_df2.drop(['Sr.No'], axis=1)

    cm_df3 = pd.read_excel(cm_file, sheet_name=cm_sheet3)    # cm_sheet3 = 'Monthly_MaxRates'
    cm_df3 = cm_df3.drop(['Sr.No'], axis=1)                  # DROP THE COLUMN NAME 'Sr.No'

    cm_df4 = pd.read_excel(cm_file, sheet_name=cm_sheet4)    # cm_sheet4 = 'Monthly_Jump'
    cm_df4 = cm_df4.drop(['Sr.No'], axis=1)                  # DROP THE COLUMN NAME 'Sr.No'

    # COLLECTION OF UNIQUE VALUES FROM COLUMN 'AccManager' FROM SHEET1 OF INPUT FILE
    # ----------acc man -> folder name----------------------
    accman_fold = dict(zip(cm_df1['AccManager'],cm_df1['D_Folder']))
    #    cm_df_Manager = accman_fold.keys
    #    print(1)
    # ------------------Backup Function Call ------------------------
    #    backup_cm('', cm_splitpath, cm_backupath, accman_fold,cm_file)

    # -----------------Split Call-------------------------------------
    if condn == 'split':
        split(condn,accman_fold, cm_splitpath, cm_backupath, cm_file)
    else:
        backup_cm('', cm_splitpath, cm_backupath, accman_fold, cm_file)
#        pass

    # DEFINE 'backup_cm' FUNCTION TO CREATE BACKUP AND COLLECT N SAVE ALL CHANGE FROM MANAGERS INDIVIDUAL FILE TO INPUT FILE


def backup_cm(condition,cm_splitpath,cm_backupath, accman_fold, cm_file):
    #    print(2)
    #    # SHEETS NAME OF ''InputConditionMaster.xlsx' FILE
    #    cm_sheet1 = 'Accounts'
    #    cm_sheet2 = 'Monthly_MinRates'
    #    cm_sheet3 = 'Monthly_MaxRates'
    #    cm_sheet4 = 'Monthly_Jump'
    
    # CALCULATING TODAY'S DATE IN form '27Apr2019'
    tdate = date.today().__format__('%d%b%Y')
    list_dir = os.listdir(cm_backupath)  
    #    print(list_dir)       # list of dir collect all files from backup folder
    # 'if' will check both condition, both are true call goes in the 'if' otherwise 'else' will execute.
    if 'backup_cm_{}.xlsx'.format(tdate) in list_dir and condition != 'split':
        #        print(4)
        pass
    else:
        #        print(5)
        # LIST TO COLLECT EVERY DF FROM LOOP
        df_list1 = []      # FIRST LIST TO COLLECT ALL DF FROM SHEET 1 OF INPUT FILE READ IN LOOP
        df_list2 = []
        df_list3 = []
        df_list4 = []
                
        for i in accman_fold:
            #  print(i)
            # split_file = cm_splitpath + r'\{}\'.format(accman_fold[i]) +'InputConditionMaster_{}.xlsx'.format(i)
            split_file = cm_splitpath + '\\' + str(accman_fold[i])+r'\All_In_One_iSell\masters\InputConditionMaster_{}.xlsx'.format(i)
#            print(split_file)
            backup_df1 = pd.read_excel(split_file, sheet_name=cm_sheet1)      # READ SHEET USING FILTER VALUE i
            backup_df2 = pd.read_excel(split_file, sheet_name=cm_sheet2)      # i GET VALUE FROM LIST (cm_df_manager)
            backup_df3 = pd.read_excel(split_file, sheet_name=cm_sheet3)
            backup_df4 = pd.read_excel(split_file, sheet_name=cm_sheet4)
            df_list1.append(backup_df1)                                    # APPEND DF TO DF_LIST1
            df_list2.append(backup_df2)
            df_list3.append(backup_df3)
            df_list4.append(backup_df4)

        df_list1 = pd.concat(df_list1)                      # CONCAT USED TO CREATE SINGLE DF FROM LIST OF DF
        df_list1 = df_list1.drop(['Sr.No'], axis=1)          # DROP THE PREVIOUS COLUMN NAME 'srno' TO CREATE NEW INDEX
        df_list1.index = np.arange(1, len(df_list1) + 1)    # TO START INDEX FROM 1 BY DEFAULT IT START FROM 0
        df_1 = df_list1.reset_index().rename(columns={'index': 'Sr.No'})   # RENAME INDEX COLUMN AS 'srno'

        df_list2 = pd.concat(df_list2)
        df_list2 = df_list2.drop(['Sr.No'], axis=1)          # DROP THE PREVIOUS COLUMN NAME 'srno' TO CREATE NEW INDEX
        df_list2.index = np.arange(1, len(df_list2) + 1)    # TO START INDEX FROM 1 BY DEFAULT IT START FROM 0
        df_2 = df_list2.reset_index().rename(columns={'index': 'Sr.No'})

        df_list3 = pd.concat(df_list3)                       # CONCAT USED TO CREATE SINGLE DF FROM LIST OF DF
        df_list3 = df_list3.drop(['Sr.No'], axis=1)          # DROP THE PREVIOUS COLUMN NAME 'srno' TO CREATE NEW INDEX
        df_list3.index = np.arange(1, len(df_list3) + 1)     # TO START INDEX FROM 1 BY DEFAULT IT START FROM 0
        df_3 = df_list3.reset_index().rename(columns={'index': 'Sr.No'})    # RENAME INDEX COLUMN AS 'Sr.No'

        df_list4 = pd.concat(df_list4)
        df_list4 = df_list4.drop(['Sr.No'], axis=1)
        df_list4.index = np.arange(1, len(df_list4) + 1)
        df_4 = df_list4.reset_index().rename(columns={'index': 'Sr.No'})

    #        try:
        if condition == 'split':
            backup_path = cm_backupath + '\\' + 'backup_cm_{}_beforesplit.xlsx'.format(tdate)
        else:
            backup_path = cm_backupath + '\\' + 'backup_cm_{}.xlsx'.format(tdate)
        backup(backup_path, df_1, df_2, df_3, df_4, 0)           # CALL 'backup' FUNCTION PROVIDED PATH IS 'backup_path'
        backup(cm_file, df_1, df_2, df_3, df_4, 1)                  # CALL 'backup' FUNCTION PROVIDED PATH IS  'cm_file'
    # THIS CALL OVERWRITE MAIN INPUT FILE LOGIC BEHIND WRITEN IN TOP COMMENT


def backup(backup_path, df_1, df_2, df_3, df_4, c):
    #    cm_sheet1 = 'Accounts'
    #    cm_sheet2 = 'Monthly_MinRates'
    #    cm_sheet3 = 'Monthly_MaxRates'
    #    cm_sheet4 = 'Monthly_Jump'
    #  WRITE DF INTO A EXCEL FILE
    df_1 = df_1[['Sr.No','Status','AccManager','hotelname','ChannelMan','staahid','cap','otacap','msrate','flowthrough','rateplan','RateOnCM','HNF','Currency','PricingType','PsychologicalFactor','GridType','PriceJump','ClusterName','JumpType','use_CeilingRate','use_FloorRate','use_Grid','cussion','isellwindow','clientwindow(180)','City','D_Folder']]
    df_2 = df_2[['Sr.No','hotelname','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','use_MaxRate']]
    df_3 = df_3[['Sr.No','hotelname','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']]
    df_4 = df_4[['Sr.No','hotelname','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Season1','Season2']]
    writer = pd.ExcelWriter(backup_path, engine='xlsxwriter')
    df_1.to_excel(writer, sheet_name=cm_sheet1, index=False, na_rep='NA')
    df_2.to_excel(writer, sheet_name=cm_sheet2, index=False)
    df_3.to_excel(writer, sheet_name=cm_sheet3, index=False)
    df_4.to_excel(writer, sheet_name=cm_sheet4, index=False)
    writer.save()
    if c == 0:
        print("Daily backup generated of accountants.")
    else:
        print('InputConditionMaster Updated')


def lost_accont(lost_df, cm_backupath):
    lost_df1 = lost_df[lost_df['Status'] == 0]
    if lost_df1.empty:
        print('NO lost Account')
        pass
    else:
        print("Lost account captured")
        lost_path = cm_backupath + '\\' + 'Lost_Account_{}.xlsx'.format(tdate)
        lost_df1.to_excel(lost_path)


# DEFINE 'split' FUNCTION TO CREATE  MANAGERS INDIVIDUAL FILE by SPLITTING INPUT FILE


def split(condn, accman_fold, cm_splitpath, cm_backupath,  cm_file):

    ch = str(input('Do you want to split?[Yes/No] :'))         # ch accept input from your as 1 or 0

    if ch == 'Yes':
        print('Please wait all account manager master files are merging......')
        backup_cm(condn, cm_splitpath, cm_backupath, accman_fold, cm_file)                                 # call backup_cm function then execution goes down for split
    else:
        print('enter correct choice')                # when the condition false execution come in else statement
        sys.exit()                                   # sys.exit() stop/end execution
    kk = str(input('Please update account managers in InputConditionMaster and press Yes after saving file :'))
    
    if kk != 'Yes':
        print('Pl enter correct choice !!!')
        sys.exit()
    else: 
        cm_df1 = pd.read_excel(cm_file, sheet_name=cm_sheet1)    # cm_sheet1 = 'Accounts'

        cm_df1 = cm_df1.drop(['Sr.No'], axis=1)                  # DROP THE COLUMN NAME 'srno'
        lost_df = cm_df1

        cm_df1 = cm_df1[cm_df1['Status'] == 1]                   # FILTER COLUMN 'Status' by '1'

        cm_df2 = pd.read_excel(cm_file, sheet_name=cm_sheet2)    # cm_sheet2 = 'Monthly_MinRates'
        cm_df2 = cm_df2.drop(['Sr.No'], axis=1)
        cm_df3 = pd.read_excel(cm_file, sheet_name=cm_sheet3)    # cm_sheet3 = 'Monthly_MaxRates'
        cm_df3 = cm_df3.drop(['Sr.No'], axis=1)                  # DROP THE COLUMN NAME 'Sr.No'
        
        cm_df4 = pd.read_excel(cm_file, sheet_name=cm_sheet4)    # cm_sheet4 = 'Monthly_Jump'
        cm_df4 = cm_df4.drop(['Sr.No'], axis=1)
    lost_accont(lost_df, cm_backupath)
    accman_fold = dict(zip(cm_df1['AccManager'], cm_df1['D_Folder']))
    count = 0
    for i in accman_fold:
        split_path = cm_splitpath + '\\' + accman_fold[i] + r'\All_In_One_iSell\masters'
        # CREATE SPLIT PATH WITH MANAGERS NAME FOLDER

        split_path1 = split_path + '\\' + 'InputConditionMaster_{}.xlsx'.format(i)
        writer = pd.ExcelWriter(split_path1, engine='xlsxwriter')

        cm_df_Sheet1 = cm_df1[cm_df1['AccManager'] == i]
        cm_df_Sheet1 = cm_df_Sheet1.reset_index(drop='Sr.No')
        cm_df_Sheet1.index = np.arange(1, len(cm_df_Sheet1) + 1)
        cm_df_Sheet1 = cm_df_Sheet1.reset_index().rename(columns={'index': 'Sr.No'})
        cm_df_Sheet1 = cm_df_Sheet1.drop_duplicates(subset='hotelname')

        cm_dfs = cm_df2['hotelname'].isin(cm_df_Sheet1['hotelname'])
        cm_df_Sheet2 = cm_df2[cm_dfs]
        cm_df_Sheet2.index = np.arange(1, len(cm_df_Sheet2) + 1)
        cm_df_Sheet2 = cm_df_Sheet2.reset_index().rename(columns={'index': 'Sr.No'})
        cm_df_Sheet2 = cm_df_Sheet2.drop_duplicates(subset='hotelname')

        cm_dfs = cm_df3['hotelname'].isin(cm_df_Sheet1['hotelname'])
        cm_df_Sheet3 = cm_df3[cm_dfs]
        cm_df_Sheet3.index = np.arange(1, len(cm_df_Sheet3) + 1)
        cm_df_Sheet3 = cm_df_Sheet3.reset_index().rename(columns={'index': 'Sr.No'})
        cm_df_Sheet3 = cm_df_Sheet3.drop_duplicates(subset='hotelname')

        cm_dfs = cm_df4['hotelname'].isin(cm_df_Sheet1['hotelname'])
        cm_df_Sheet4 = cm_df4[cm_dfs]
        cm_df_Sheet4.index = np.arange(1, len(cm_df_Sheet4) + 1)
        cm_df_Sheet4 = cm_df_Sheet4.reset_index().rename(columns={'index': 'Sr.No'})
        cm_df_Sheet4 = cm_df_Sheet4.drop_duplicates(subset='hotelname')

        # WRITE EXCEL FILE IN ACCOUNT MANAGER FOLDER
        cm_df_Sheet1.to_excel(writer, sheet_name=cm_sheet1, index=False)
        cm_df_Sheet2.to_excel(writer, sheet_name=cm_sheet2, index=False)
        cm_df_Sheet3.to_excel(writer, sheet_name=cm_sheet3, index=False)
        cm_df_Sheet4.to_excel(writer, sheet_name=cm_sheet4, index=False)
        writer.save()
        count += 1
    print('{} File created in their relative folder '.format(count))



'''

THE END  

'''
