

import os
import datetime
import sys
sys.path.insert(0,r'C:\All_In_One_iSell\GIT_Repo\iSell_Production\src')
os.chdir(r'C:\All_In_One_iSell\GIT_Repo\iSell_Production\src')



import AccountSplitMerge as asm
import ProcessFlow
# ==============================================================================

# ----------All_In_One_iSell folder structure path------------------------------
stdpth = r'C:\All_In_One_iSell'
splitpath = r"C:"
path = stdpth+r'\masters'

accpath = r'C:\Anand\All_In_One_iSell\masters'
logflag='INFO'

# ==============================================================================
Account_Managers = ['Anand']

# ==============================================================================
asm.var_init(stdpth, splitpath, '')
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday=yesterday.strftime("%m/%d/%Y")
#print(yesterday)
weekday = datetime.date.today().strftime('%A')
print(weekday)
if (weekday == 'Monday'):
    d3 = datetime.date.today() - datetime.timedelta(days=1)
    friday_date = d3.strftime("%m/%d/%Y")
#    print(friday_date)    
#    LR_date = '{}'.format(input("Please enter last report created date(format:mm/dd/YYYY) :"))
    LR_date=friday_date
else:
#    LR_date = '{}'.format(input("Please enter last report created date(format:mm/dd/YYYY) :"))    
        LR_date=yesterday
ProcessFlow.Flow(path, stdpth, LR_date, Account_Managers, accpath, logflag)


