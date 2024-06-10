import pandas as pd
from datetime import datetime, timedelta

# Set up variables
basepath = r'C:\All_In_One_iSell\InputData\OutPut_CSV'
names = 'Hotel Lakend'

ddmmyy = datetime.now()
somd = ddmmyy.replace(day=1)
dr = pd.date_range(start=somd, end=ddmmyy)

df = pd.DataFrame()
for date in dr:
    tdayfold = date.strftime('%d_%b_%Y')
    tdayfold1 = date.strftime('%d%b%Y')
    idate = date.strftime('%Y-%m-%d')
    try:
        SOTM = pd.read_csv(basepath + '\{}\{}'.format(tdayfold, 'iSell_' + names + f'_{tdayfold1}.CSV')).iloc[:, 1:]
        temp_df = SOTM[SOTM['Date'] == idate]
        df = df.append(temp_df)
    except FileNotFoundError:
        next_date = date
        idate_next = next_date.strftime('%Y-%m-%d')
        temp_df_next = SOTM[SOTM['Date'] == idate_next]
        df = df.append(temp_df_next)

        # df = df.reindex(columns=SOTM.columns)

df
SOTM