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

# Set up the datastream, variable name and averaging interval
# Averaging interval based on xarray resample (M=Month, Y=Year)
ds_dict = {
    'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M'], 'units': ['degC', '%']},
    'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['Y', 'M'], 'units': ['degC', '%']},
    'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean', 'tbrg_precip_total'], 'averaging': ['Y', 'M'], 'units': ['degC', '%', 'mm']},
    #'sgp30ecorE14.b1': {'variables': ['fc', 'h', 'lv_e', 'k'], 'averaging': ['Y', 'M'], 'units':['W/m^2', 'W/m^2', 'kg/(m s^2)', 'umol/(s m^2)']},
    #'sgptsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['YE', 'M'], 'units': ['%', '%']},
    #'nsatsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['Y', 'M'], 'units': ['%', '%']},

}

# Read in data file from results area
for ds in ds_dict:
    for i, variable in enumerate(ds_dict[ds]['variables']):
        units = ds_dict[ds]['units'][i]
        for averaging in ds_dict[ds]['averaging']:
            filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
            names = ['time', 'mean', 'n_samples']
            obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])

            # Set Up Plot
            display = act.plotting.TimeSeriesDisplay(obj, figsize=(10,5))
            if averaging == 'M':
                title = 'Monthly Averages of ' + variable + ' in '+ ds
                if 'nsa60noaa' in ds:
                    title = 'Monthly Total of Precipitation in ' + ds
            if averaging == 'Y' or averaging == 'YE':
                title = 'Yearly Averages of ' + variable + ' in '+ ds
                if 'nsa60noaa' in ds:
                    title = 'Yearly Total of Precipitation in ' + ds
            display.plot('mean', set_title=title)
            display.axes[0].set_ylabel('(' + units + ')')

            # Highlight samples that have less than 28 days worth of samples for monthly
            # and less than 334 days for yearly averages
            if averaging == 'M':
                idx = np.where(obj['n_samples'] < 25 * 24 * 60)
                text = 'Black Dots = < 25 days used in average'
                if '60noaa' in ds:
                    idx = np.where(obj['n_samples'] < 25 * 24) # For hourly averaged data
                    text = 'Black Dots (ARM ) and Squares (NOAA) = < 25 days used in average'
                elif 'ecor' in ds:
                    idx = np.where(obj['n_samples'] < 25 * 24 / 0.5) # For hourly averaged data
                elif 'tsisky' in ds:
                    idx = np.where(obj['n_samples'] < 25 * 8 * 60) # For daily data

                plt.text(1.0, -0.1, text, transform=display.axes[0].transAxes, fontsize=7,
                         horizontalalignment='right')
                myFmt = mdates.DateFormatter('%b %Y')
            if averaging == 'Y' or averaging == 'YE':
                idx = np.where(obj['n_samples'] < 334 * 24 * 60)
                text = 'Black Dots = < 334 days used in average'
                if '60noaa' in ds:
                    idx = np.where(obj['n_samples'] < 334 * 24) # For hourly averaged data
                    text = 'Black Dots (ARM ) and Squares (NOAA) = < 334 days used in average'
                elif 'ecor' in ds:
                    idx = np.where(obj['n_samples'] < 180 * 24 / 0.5) # For hourly averaged data
                    text = 'Black Dots (ARM ) = < 180 days used in average'
                elif 'tsisky' in ds:
                    idx = np.where(obj['n_samples'] < 334 * 8 * 60)

                plt.text(1.0, -0.1, text, transform=display.axes[0].transAxes, fontsize=7,
                         horizontalalignment='right')
                myFmt = mdates.DateFormatter('%Y')

            display.axes[0].xaxis.set_major_formatter(myFmt)
            display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')
            display.axes[0].grid(axis='y')

            imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
            plt.tight_layout()
            plt.savefig(imagename)
