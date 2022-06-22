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
ds = 'nsametC1.b1'
variable = 'temp_mean'
averaging = 'M'
units = 'degC'

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
for g in group.groups:
    years = pd.to_datetime(obj['time'].values[group.groups[g]]).year
    sc = ax.scatter(np.full(len(obj['mean'].values[group.groups[g]]), g), obj['mean'].values[group.groups[g]], c=years)

plt.colorbar(sc)
ax.set_ylabel('Temperature (' + units + ')')
ax.set_xlabel('Month of Year')
ax.grid(axis='y')
plt.title('Plot of All Data By Month For ' + ds +' ' + variable)

plt.text(1.0, -0.1, ' Months with less than 25 days of samples removed',
         transform=ax.transAxes, fontsize=7,
         horizontalalignment='right')

imagename = './images/' + ds + '_' + variable + '_by_month' + '.png'
plt.tight_layout()
plt.savefig(imagename)
