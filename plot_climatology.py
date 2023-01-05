"""
Plot ARM Climatologies
----------------------

Process for plotting up a single climatology file

Author: Adam Theisen

"""

import act
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import scipy


ds = 'nsametC1.b1'
variable = 'temp_mean'
ds = 'nsa60noaacrnX1.b1'
variable = 'temperature'
variable = 'precipitation'
averaging = 'M'
units = 'mm'

# Read in data file from results area
filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

# Set Up Plot
display = act.plotting.TimeSeriesDisplay(obj, figsize=(10,5))
if averaging == 'M':
    title = 'Monthly Averages of ' + variable + ' in '+ ds
if averaging == 'Y':
    title = 'Yearly Averages of ' + variable + ' in '+ ds
display.plot('mean', set_title=title)
display.axes[0].set_ylabel('(' + units + ')')

# Highlight samples that have less than 28 days worth of samples for monthly
# and less than 334 days for yearly averages
if averaging == 'M':
    idx = np.where(obj['n_samples'] < 25 * 24 * 60)
    if '60noaa' in ds:
        print('test')
        idx = np.where(obj['n_samples'] < 25 * 24) # For hourly averaged data
    plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 25 days used in average',
             transform=display.axes[0].transAxes, fontsize=7,
             horizontalalignment='right')
    myFmt = mdates.DateFormatter('%b %Y')
if averaging == 'Y':
    idx = np.where(obj['n_samples'] < 334 * 24 * 60)
    if '60noaa' in ds:
        idx = np.where(obj['n_samples'] < 334 * 24) # For hourly averaged data
    plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 334 days used in average',
             transform=display.axes[0].transAxes, fontsize=7,
             horizontalalignment='right')
    myFmt = mdates.DateFormatter('%Y')

display.axes[0].xaxis.set_major_formatter(myFmt)
display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')
display.axes[0].grid(axis='y')

# Excluded for now but could use to plot lin regression line
#seconds = (pd.to_datetime(obj['time'].values) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
#result = scipy.stats.linregress(seconds, obj['mean'].values)
#display.axes[0].plot(obj['time'].values, result.intercept + result.slope * seconds)

imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
plt.tight_layout()
plt.savefig(imagename)
