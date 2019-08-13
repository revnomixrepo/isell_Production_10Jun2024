import os
os.chdir(r'E:\All_In_One_iSell\GIT_Repo\iSell_Production\src')

import AccountSplitMerge as asm
import ProcessFlow
# ==============================================================================

# ----------All_In_One_iSell folder structure path------------------------------
stdpth = r'E:\All_In_One_iSell'
splitpath = r"D:"
path = stdpth+r'\masters'

accpath = r'D:\Ashwin Vanarase\All_In_One_iSell\masters'
logflag='INFO'

# ==============================================================================
Account_Managers = ['Ashwin']

# ==============================================================================
asm.var_init(stdpth, splitpath, '')
LR_date = '{}'.format(input("Please enter last report created date(format:mm/dd/YYYY) :"))

ProcessFlow.Flow(path, stdpth, LR_date, Account_Managers, accpath, logflag)

