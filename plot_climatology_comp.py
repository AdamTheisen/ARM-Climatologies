"""
Plot ARM Climatologies Comparison
---------------------------------

Process for plotting comparisons of two climatology files

Author: Adam Theisen

"""
import act
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import scipy


ds = 'nsametC1.b1'
ds2 = 'nsa60noaacrnX1.b1'
variable = 'temp_mean'
variable2 = 'temperature'
averaging = 'M'
units = 'degC'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

filename = './results/' + ds2 + '_' + variable2 + '_' + averaging + '.csv'
obj2 = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

# Set Up Plot

display = act.plotting.TimeSeriesDisplay({'ARM': obj, 'NOAA': obj2}, figsize=(10,5))
if averaging == 'M':
    title = 'Monthly Averages of ' + variable + ' in '+ ds
if averaging == 'Y':
    title = 'Yearly Averages of ' + variable + ' in '+ ds
display.plot('mean', set_title=title, subplot_index=(0,), dsname='ARM', label='ARM')
display.plot('mean', set_title=title, subplot_index=(0,), dsname='NOAA', label='NOAA')
display.axes[0].set_ylabel('(' + units + ')')

# Highlight samples that have less than 28 days worth of samples for monthly
# and less than 334 days for yearly averages
if averaging == 'M':
    idx = np.where(obj['n_samples'] < 28 * 24 * 60)
    #idx = np.where(obj['n_samples'] < 25 * 24) # For hourly averaged data
    idx2 = np.where(obj2['n_samples'] < 25 * 24) # For hourly averaged data
    plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 25 days used in average',
             transform=display.axes[0].transAxes, fontsize=7,
             horizontalalignment='right')
    myFmt = mdates.DateFormatter('%b %Y')
if averaging == 'Y':
    idx = np.where(obj['n_samples'] < 334 * 24 * 60)
    #idx = np.where(obj['n_samples'] < 334 * 24) # For hourly averaged data
    idx2 = np.where(obj2['n_samples'] < 334 * 24) # For hourly averaged data
    plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 334 days used in average',
             transform=display.axes[0].transAxes, fontsize=7,
             horizontalalignment='right')
    myFmt = mdates.DateFormatter('%Y')

print(obj2['time'].values)
display.axes[0].xaxis.set_major_formatter(myFmt)
display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')
display.axes[0].plot(obj2['time'].values[idx2], obj2['mean'].values[idx2], 'ks')
display.axes[0].grid(axis='y')
plt.legend()

#seconds = (pd.to_datetime(obj['time'].values) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
#result = scipy.stats.linregress(seconds, obj['mean'].values)
#display.axes[0].plot(obj['time'].values, result.intercept + result.slope * seconds)

#imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
imagename = './images/' + ds + '_' + variable + '_' + ds2 + '_' + variable2 + '_' + averaging + '.png'
plt.tight_layout()
plt.savefig(imagename)
