import act
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


ds = 'nsametC1.b1'
variable = 'temp_mean'
averaging = 'M'
units = 'degC'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])


# Set Up Plot
myFmt = mdates.DateFormatter('%b %Y')

display = act.plotting.TimeSeriesDisplay(obj, figsize=(10,5))
if averaging == 'M':
    title = 'Monthly Averages of ' + variable + ' in '+ ds
if averaging == 'Y':
    title = 'Yearly Averages of ' + variable + ' in '+ ds
display.plot('mean', set_title=title, subplot_index=(0,))
display.axes[0].xaxis.set_major_formatter(myFmt)
display.axes[0].set_ylabel('(' + units + ')')

# Highlight samples that have less than 28 days worth of samples for monthly
# and less than 334 days for yearly averages
if averaging == 'M':
    idx = np.where(obj['n_samples'] < 28 * 24 * 60)
    plt.text(1.0, -0.075, 'Black Dots = < 28 days used in average', transform=display.axes[0].transAxes,
             horizontalalignment='right')
if averaging == 'Y':
    idx = np.where(obj['n_samples'] < 334 * 24 * 60)
    plt.text(1.0, -0.075, 'Black Dots = < 331 days used in average', transform=display.axes[0].transAxes,
             horizontalalignment='right')
display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')




imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
plt.tight_layout()
plt.savefig(imagename)
