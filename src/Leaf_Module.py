'''

Automate Report for Leaf hotel iSell

'''

import pandas as pd

def lhd(fname1, fname2, outpath, htl):

    fread1 = pd.DataFrame(fname1)
    fread2 = pd.DataFrame(fname2)

    # Date format change for column 'Date'
    fread1["Date"] = pd.to_datetime(fread1["Date"], format='%Y/%m/%d')
    fread1["Date"] = pd.to_datetime(fread1["Date"], format='%Y/%m/%d')

    # Date format change for column 'PP_Date'
    fread2["PP_DATE"] = pd.to_datetime(fread2["PP_DATE"], format='%d/%m/%Y')
    fread2["PP_DATE"] = pd.to_datetime(fread2["PP_DATE"], format='%d/%m/%Y')

    c1 = ['Date', 'BFR (OSNN)']
    fread1 = fread1[c1]

    c2 = ['PP_DATE', 'PP_RMS', 'PP_REV']
    fread2 = fread2[c2]

    # REQUIRED REPORT DF
    m_fileD1 = fread1.rename(columns={'Date': 'Date', 'BFR (OSNN)':'CMRate'})
    m_fileD2 = fread2.rename(columns={'PP_DATE': 'Date','PP_RMS': 'Sold','PP_REV':'Revenue'})
    df_fscema = m_fileD1.merge(m_fileD2, on='Date', how='right')

    # ADR calculation Revenu/Sold
    adr_C = df_fscema['Revenue'] / df_fscema['Sold']
    adr_C = adr_C.fillna(0)
    df_fscema['ADR OTB'] = adr_C
    df_fscema.fillna(0)


    # EXPORT RESULT REPORT
    export_path = outpath + '\\' + '{}_HNF.csv'.format(htl)

    df_fscema.to_csv(export_path)
    print('LHD Report generated successfully')
