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
    #'sgpceil10mC1.b1': {'variables': ['first_cbh'], 'averaging': ['YS', 'M'], 'units': ['m']},
    #'nsaceilC1.b1': {'variables': ['first_cbh'], 'averaging': ['YS', 'MS'], 'units': ['m']},
    'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    'nsamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['YS', 'MS'], 'units': ['degC', 'mm']},
    'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    'sgpmawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    'enametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    'enamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YS', 'MS'], 'units': ['degC', '%']},
    #'sgp30ecorE14.b1': {'variables': ['fc', 'h', 'lv_e', 'k'], 'averaging': ['Y', 'M'], 'units':['W/m^2', 'W/m^2', 'kg/(m s^2)', 'umol/(s m^2)']},
    #'sgptsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['YS', 'M'], 'units': ['%', '%']},
    #'nsatsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['Y', 'M'], 'units': ['%', '%']},

}
min_max = False

# Read in data file from results area
for ds in ds_dict:
    for i, variable in enumerate(ds_dict[ds]['variables']):
        units = ds_dict[ds]['units'][i]
        for averaging in ds_dict[ds]['averaging']:
            print(ds, variable, averaging)
            filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
            names = ['time', 'mean', 'n_samples', 'min', 'max', 'std_dev', 'standard_error']
            obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'], date_format="%Y-%m-%dT%H:%M:%S", header=0)
            # Set Up Plot
            display = act.plotting.TimeSeriesDisplay(obj, figsize=(10,5))
            if averaging == 'M':
                title = 'Monthly Averages of ' + variable + ' in '+ ds
                #if 'nsa60noaa' in ds:
                #    title = 'Monthly Total of Precipitation in ' + ds
            if averaging == 'Y' or averaging == 'YS':
                title = 'Yearly Averages of ' + variable + ' in '+ ds
                #if 'nsa60noaa' in ds:
                #    title = 'Yearly Total of Precipitation in ' + ds
            display.plot('mean', set_title=title)
            display.axes[0].set_ylabel('(' + units + ')')

            # Display Errors and min/max limits
            if min_max:
                display.axes[0].fill_between(obj['time'].values, obj['mean'].values + obj['standard_error'].values,
                                             obj['mean'].values - obj['standard_error'].values, color='skyblue', alpha=0.5)
                display.axes[0].fill_between(obj['time'].values, obj['max'].values,
                                             obj['min'].values, color='gray', alpha=0.1)

                display.set_yrng([obj['min'].min(), obj['max'].max()])

            # Highlight samples that have less than 28 days worth of samples for monthly
            # and less than 334 days for yearly averages
            if averaging == 'M' or averaging == 'MS':
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
            if averaging == 'Y' or averaging == 'YS':
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

            idy = [i for i in range(len(obj['time'].values)) if i not in idx[0]]

            # Display trend lines
            result = scipy.stats.linregress(range(len(obj['time'].values[idy])), obj['mean'].values[idy], nan_policy='omit')
            display.axes[0].plot(obj['time'].values, range(len(obj['time'].values)) * result.slope + result.intercept,
                                 linestyle=':', color='black')
            #display.axes[0].text(obj['time'].values[0], result.slope + result.intercept * 1.1, 'Slope: ' + str(round(result.slope, 2))) 
            display.axes[0].text(0, -0.1, 'Mean Slope: ' + str(round(result.slope, 3)), transform=display.axes[0].transAxes, fontsize=7,
                         horizontalalignment='left')

            if min_max:
                result = scipy.stats.linregress(range(len(obj['time'].values[idy])), obj['min'].values[idy], nan_policy='omit')
                display.axes[0].plot(obj['time'].values, range(len(obj['time'].values)) * result.slope + result.intercept,
                                     linestyle=':', color='black')
                #display.axes[0].text(obj['time'].values[0], result.slope + result.intercept, 'Slope: ' + str(round(result.slope, 2))) 
                display.axes[0].text(0, -0.125, 'Min Slope: ' + str(round(result.slope, 3)), transform=display.axes[0].transAxes, fontsize=7,
                             horizontalalignment='left')

                result = scipy.stats.linregress(range(len(obj['time'].values[idy])), obj['max'].values[idy], nan_policy='omit')
                display.axes[0].plot(obj['time'].values, obj['max'].values * result.slope + result.intercept,
                                     linestyle=':', color='black')
                #display.axes[0].text(obj['time'].values[0], result.slope + result.intercept, 'Slope: ' + str(round(result.slope, 2))) 
                display.axes[0].text(0, -0.075, 'Max Slope: ' + str(round(result.slope, 3)), transform=display.axes[0].transAxes, fontsize=7,
                             horizontalalignment='left')



            imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
            plt.tight_layout()
            plt.savefig(imagename)
