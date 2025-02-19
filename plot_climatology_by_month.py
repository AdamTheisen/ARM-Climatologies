"""
Plot ARM Climatologies by Month
-------------------------------

Process for plotting up a single climatology file
by month to see the spread in values over the years

Author: Adam Theisen

"""

import act
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set up the datastream and info to read in
#ds = 'nsametC1.b1'
ds = 'sgpmetE13.b1'
variable = 'tbrg_precip_total'
averaging = 'M'
units = 'mm'
#variable = 'temp_mean'
#averaging = 'M'
#units = 'degC'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

# Set Up Plot
display = act.plotting.TimeSeriesDisplay(obj, figsize=(10,5))
if averaging == 'M':
    title = 'Monthly Averages of ' + variable + ' in '+ ds

# Remove months with less than 25 days
obj = obj.where(obj['n_samples'] >= 25 * 24 * 60)

# Run through the months and plot scatter plots
group = obj.groupby('time.month')
fig, ax = plt.subplots(figsize=(10,6))
ct = 1
for g in group.groups:
    years = pd.to_datetime(obj['time'].values[group.groups[g]]).year
    sc = ax.scatter(np.full(len(obj['mean'].values[group.groups[g]]), g), obj['mean'].values[group.groups[g]], c=years)
    std = np.nanstd(obj['mean'].values[group.groups[g]])
    plt.text(ct, -34.5, str(round(std, 1)), transform=ax.transData, fontsize=7, horizontalalignment='center')
    ct += 1

plt.text(0, -34.5, 'Std Dev', transform=ax.transData, fontsize=7, horizontalalignment='center')
plt.xticks(np.arange(1, 13, 1))

cbar = plt.colorbar(sc)
cbar.set_ticks(np.arange(2003, 2024, 5))
ax.set_ylabel('Precipitation Total (' + units + ')')
ax.set_xlabel('Month of Year')
ax.grid(axis='y')
plt.title('Plot of All Data By Month For ' + ds +' ' + variable)

plt.text(1.0, -0.1, ' Months with less than 25 days of samples removed',
         transform=ax.transAxes, fontsize=7,
         horizontalalignment='right')

imagename = './images/' + ds + '_' + variable + '_by_month' + '.png'
plt.tight_layout()
plt.savefig(imagename)
