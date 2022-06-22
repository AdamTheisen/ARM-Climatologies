import act
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


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

obj = obj.where(obj['n_samples'] >= 25 * 24 * 60)

group = obj.groupby('time.year')
data = []
obj = xr.decode_cf(obj)
years = []
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
