# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:17:43 2021.

@author: Michael

"""

import sys

# Import local modules
from lib import gui_statistic as gui
from lib import stat_df
from lib import Concat
from lib import stat


# Lpocal function
def _err_msg(valid1, valid2, valid3, file_name1, file_name2, file_name3):
    if valid1:
        pass
    else:
        raise Exception("Failed importation of " + file_name1 + '\n' +
                        '_columns doesn\'t apply to the .csv file')
        sys.exit(1)
    if valid2:
        pass
    else:
        raise Exception("Failed importation of : " + file_name2 + '\n' +
                        '_columns doesn\'t apply to the .csv file')
        sys.exit(1)
    if valid3:
        pass
    else:
        raise Exception("Failed importation of : " + file_name3 + '\n' +
                        '_columns doesn\'t apply to the .csv file')
        sys.exit(1)


# In[]:
# Call the interface class
app = gui.Interface()
app.title('Measurement statistics')
app.mainloop()
_folder_name, zone, save_csv = app.output()

_columns = ['timestamp', 'lon', 'lat', 'posMode', 'numSV', 'difAge',
            'HDOP', 'dist']

# =============================================================================
# Extract dataframe
# =============================================================================
if 'DataBase' in _folder_name:
    df_net = Concat(_folder_name, 'NetR9', zone, save_csv).main()
    df_swi = Concat(_folder_name, 'swipos_ublox', zone, save_csv).main()
    df_sap = Concat(_folder_name, 'sapcorda', zone, save_csv).main()
elif 'res/data' in _folder_name:
    _file_name1 = _folder_name + '/NetR9_' + zone + '.csv'
    _file_name2 = _folder_name + '/swipos_ublox_' + zone + '.csv'
    _file_name3 = _folder_name + '/sapcorda_' + zone + '.csv'
    df_net, _valid1 = stat_df(_file_name1, _columns)
    df_swi, _valid2 = stat_df(_file_name2, _columns)
    df_sap, _valid3 = stat_df(_file_name3, _columns)
    _err_msg(_valid1, _valid2, _valid3, _file_name1, _file_name2, _file_name3)

# =============================================================================
# "Sync" Dataframe
# =============================================================================
df_net = df_net.set_index('timestamp', drop=False)
df_swi = df_swi.set_index('timestamp', drop=False)
df_sap = df_sap.set_index('timestamp', drop=False)

df_net = df_net.loc[df_net.index.intersection(df_sap.index)]
df_swi = df_swi.loc[df_swi.index.intersection(df_sap.index)]

# =============================================================================
# (A) NetR9
# =============================================================================
if df_net is not None:
    netr9 = stat.Statistic(df_net, 'NetR9 avec swipos')

    df_net = netr9.rmv_bad_days(df_net)
    # netr9.plt_bad_days(df_net, ['2021-06-23', '2021-07-06'])
    # netr9.spatial_analysis(df_net, 100)

    accuracy_net = netr9.accuracy(df_net, True)
    integrity_net = netr9.integrity(df_net)
# =============================================================================
# (B) u-blox with swipos
# =============================================================================
if df_swi is not None:
    swipos = stat.Statistic(df_swi, 'u-blox avec swipos')

    df_swi = swipos.rmv_bad_days(df_swi)
    # swipos.spatial_analysis(df_swi, 100)
    accuracy_swi = swipos.accuracy(df_swi, True)
    integrity_swi = swipos.integrity(df_swi)

# =============================================================================
# (C) u-blox with sapcorda
# =============================================================================
if df_sap is not None:
    sapcorda = stat.Statistic(df_sap, 'u-blox avec SAPA')

    df_sap = sapcorda.rmv_bad_days(df_sap)
    # sapcorda.spatial_analysis(df_sap, 100)
    accuracy_sap = sapcorda.accuracy(df_sap, True)
    integrity_sap = sapcorda.integrity(df_sap)

# =============================================================================
# PLot Histogram HPE
# =============================================================================
# TODO: This part need to be adapted
# do_xlim = True
# save_plt1 = False

# if False:
#     fname2 = './res/stat/Accuracy_PDF_CFD_swipos_sapos.png'
#     fname3 = './res/stat/Accuracy_PDF_CFD_netr9_ublox.png'

#     receiver = 'u-blox avec RTK VRS GIS/GEO swipos'
#     receiver2 = 'u-blox avec PPP-RTK SAPOS'
#     receiver3 = 'NetR9 avec RTK VRS GIS/GEO swipos'

#     fname2 = [save_plt1, fname2]
#     fname3 = [save_plt1, fname3]

#     dist, bins, weights, CDF, quantile = _pdf_cdf(df)
#     dist2, bins2, weights2, CDF2, quantile2 = _pdf_cdf(df2)
#     dist3, bins3, weights3, CDF3, quantile3 = _pdf_cdf(df3)

#     tools.plotHistAcc2(dist, bins, weights, CDF, quantile, receiver, 'blue',
#                        dist2, bins2, weights2, CDF2, quantile2, fname2, receiver2, 'orange', do_xlim)

#     tools.plotHistAcc2(dist, bins, weights, CDF, quantile, receiver, 'blue',
#                        dist3, bins3, weights3, CDF3, quantile3, fname3, receiver3, 'red', do_xlim)

#     # Plot HPE
#     tools.plot_HPE(df, df2, df3, receiver, receiver2,
#                    receiver3, posMode, posMode2, posMode2)
#                    receiver3, posMode, posMode2, posMode2)
