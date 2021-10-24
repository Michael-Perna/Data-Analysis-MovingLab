# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:17:43 2021.

@author: Michael

"""

# Import local modules
from lib import gui_statistic as gui
from lib import Concat
from lib import stat


# In[]:
# Call the interface class
app = gui.Interface()
app.title('Measurement statistics')
app.mainloop()
folder_name, zone, save_csv = app.output()

# =============================================================================
# Extract dataframe
# =============================================================================
df_net = Concat(folder_name, 'netr9', zone, save_csv).main()
df_swi = Concat(folder_name, 'swipos', zone, save_csv).main()
df_sap = Concat(folder_name, 'sapcorda', zone, save_csv).main()

# =============================================================================
# Sync Dataframe
# =============================================================================


# =============================================================================
# (A) NetR9
# =============================================================================
if df_net is not None:
    netr9 = stat.Statistic(df_net, 'NetR9 avec swipos')
    accuracy_net = netr9.accuracy(df_net, True)

# =============================================================================
# (B) u-blox with swipos
# =============================================================================
if df_swi is not None:
    swipos = stat.Statistic(df_swi, 'u-blox avec swipos')

    accuracy_swi = swipos.accuracy(df_swi, True)

# =============================================================================
# (C) u-blox with sapcorda
# =============================================================================
if df_sap is not None:
    sapcorda = stat.Statistic(df_sap, 'u-blox avec SAPA')

    accuracy_sap = sapcorda.accuracy(df_sap, True)

# =============================================================================
# PLot Histogram HPE
# =============================================================================
do_xlim = True
save_plt1 = False

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
