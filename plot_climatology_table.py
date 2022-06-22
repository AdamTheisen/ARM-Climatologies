"""
Plot ARM Climatologies Tables
-----------------------------

Process for plotting up a table of climatology values on
a month (x) by year (y) grid

Author: Adam Theisen

"""
import act
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


# Set information and read in data
ds = 'nsametC1.b1'
variable = 'temp_mean'
averaging = 'M'
units = 'degC'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

# Set Up Plot
if averaging == 'M':
    title = 'Monthly Averages of ' + variable + ' in '+ ds

# Exclude data when there's less than 25 days of data in a month
obj = obj.where(obj['n_samples'] >= 25 * 24 * 60)

# Group data by year and run through each month/year
# selecting the exact match in time and entering nan
# if not available.
group = obj.groupby('time.year')
obj = xr.decode_cf(obj)
years = []
data = []
for y in group.groups:
    y_data = []
    for m in range(1,13):
        date = str(y) + '-' + str(m).zfill(2) + '-01T00:00:00.000000000'
        try:
            y_data.append(str(np.around(obj['mean'].sel(time=date).values, decimals=1)))
        except:
            y_data.append('nan')

    data.append(y_data)
    years.append(y)

# Set up table and plot it
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
fig, ax = plt.subplots(figsize=(10,8))
ax.axis('off')
ax.axis('tight')

table = plt.table(data, rowLabels=years, colLabels=months, bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(12)
plt.title('Grid of Monthly Averages for ' + ds + ' ' + variable + '\n' + 'Months with less than 25 days of samples have been removed')

imagename = './images/' + ds + '_' + variable + '_table' + '.png'
plt.tight_layout()
plt.savefig(imagename)
