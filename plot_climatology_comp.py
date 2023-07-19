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


plot_dict = {
    'p1': {'ds': {'nsametC1.b1': 'temp_mean', 'nsa60noaacrnX1.b1': 'temperature'}, 'averaging': ['Y', 'M'], 'units': 'degC'},
}

#ds = 'nsametC1.b1'
#ds2 = 'nsa60noaacrnX1.b1'
#variable = 'temp_mean'
#variable2 = 'temperature'
#averaging = 'Y'
#units = 'degC'

for plot in plot_dict:
    ds = list(plot_dict[plot]['ds'].keys())[0]
    ds2 = list(plot_dict[plot]['ds'].keys())[1]
    variable = plot_dict[plot]['ds'][ds]
    variable2 = plot_dict[plot]['ds'][ds2]
    units = plot_dict[plot]['units']

    for averaging in plot_dict[plot]['averaging']:
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
            if 'nsa60noaa' in ds:
                idx = np.where(obj['n_samples'] < 25 * 24) # For hourly averaged data
            idx2 = np.where(obj2['n_samples'] < 25 * 24 * 60)
            if 'nsa60noaa' in ds2:
                idx2 = np.where(obj2['n_samples'] < 25 * 24) # For hourly averaged data
            plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 25 days used in average',
                     transform=display.axes[0].transAxes, fontsize=7,
                     horizontalalignment='right')
            myFmt = mdates.DateFormatter('%b %Y')
        if averaging == 'Y':
            idx = np.where(obj['n_samples'] < 334 * 24 * 60)
            if 'nsa60noaa' in ds:
                idx = np.where(obj['n_samples'] < 334 * 24) # For hourly averaged data
            idx2 = np.where(obj2['n_samples'] < 334 * 24 * 60)
            if 'nsa60noaa' in ds2:
                idx2 = np.where(obj2['n_samples'] < 334 * 24) # For hourly averaged data

            plt.text(1.0, -0.1, 'Black Dots (ARM ) and Squares (NOAA) = < 334 days used in average',
                     transform=display.axes[0].transAxes, fontsize=7,
                     horizontalalignment='right')
            myFmt = mdates.DateFormatter('%Y')

        display.axes[0].xaxis.set_major_formatter(myFmt)
        display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')
        display.axes[0].plot(obj2['time'].values[idx2], obj2['mean'].values[idx2], 'ks')
        display.axes[0].grid(axis='y')
        plt.legend()

        #imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
        imagename = './images/' + ds + '_' + variable + '_' + ds2 + '_' + variable2 + '_' + averaging + '.png'
        plt.tight_layout()
        plt.savefig(imagename)
