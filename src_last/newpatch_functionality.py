import pandas as pd
import numpy as np
from datetime import timedelta
import os.path

def Lrdate_outputCSV(LRdt,basepath,names):
    dt_dt = pd.to_datetime(LRdt)

    # + str('_{}.csv'.format(LRdt))
    for i in np.arange(1,20,1):
        lrdate12 = dt_dt - timedelta(days=int(i))
        lastfoldname1 = lrdate12.strftime('%d_%b_%Y')
        LRdt1 = lrdate12.strftime("%d%b%Y")
        # pathFind = path + str('_{}.csv'.format(LRdt1))
        adj_path = basepath + '\{}\{}\{}'.format('OutPut_CSV', lastfoldname1,
                                                 str('iSell_') + names + str('_{}.csv'.format(LRdt1)))
        pathExist = os.path.exists(adj_path)
        if pathExist == True:
            break
        else:
            continue

    return adj_path

    # lrdate12 = LRdt - timedelta(days=1)
    # lastfoldname = lrdate12.strftime('%d_%b_%Y')
    # LRdt = lrdate12.strftime("%d%b%Y")