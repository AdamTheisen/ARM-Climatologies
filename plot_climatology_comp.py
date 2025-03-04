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
    'p1': {'ds': {'nsametC1.b1': 'temp_mean', 'nsa60noaacrnX1.b1': 'temperature', 'nsamawsC1.b1': 'atmospheric_temperature'}, 'averaging': ['Y', 'M'], 'units': 'degC'},
    'p2': {'ds': {'sgpmetE13.b1': 'temp_mean', 'sgpmawsC1.b1': 'atmospheric_temperature'}, 'averaging': ['Y', 'M'], 'units': 'degC'},
}

for plot in plot_dict:
    ds = list(plot_dict[plot]['ds'].keys())[0]
    ds2 = list(plot_dict[plot]['ds'].keys())[1]
    variable = plot_dict[plot]['ds'][ds]
    variable2 = plot_dict[plot]['ds'][ds2]

    if len(plot_dict[plot]['ds']) == 3:
        ds3 = list(plot_dict[plot]['ds'].keys())[2]
        variable3 = plot_dict[plot]['ds'][ds3]
    else:
        ds3=None
        variable3=None
    units = plot_dict[plot]['units']
    ds_dict = {}
    for averaging in plot_dict[plot]['averaging']:
        filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
        names = ['time', 'mean', 'n_samples']
        obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])
        ds_dict['ARM MET'] = obj

        filename = './results/' + ds2 + '_' + variable2 + '_' + averaging + '.csv'
        obj2 = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])
        if 'sgp' in ds:
            ds_dict['ARM MAWS'] = obj2
        else:
            ds_dict['NOAA'] = obj2
       
        if len(plot_dict[plot]['ds']) == 3:
            filename = './results/' + ds3 + '_' + variable3 + '_' + averaging + '.csv'
            obj3 = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])
            if 'nsa' in ds:
                ds_dict['ARM MAWS'] = obj3

        # Set Up Plot
        display = act.plotting.TimeSeriesDisplay(ds_dict, figsize=(10,5))
        if averaging == 'M':
            title = 'Monthly Averages of ' + variable + ' in '+ ds
        if averaging == 'Y':
            title = 'Yearly Averages of ' + variable + ' in '+ ds

        # Highlight samples that have less than 28 days worth of samples for monthly
        # and less than 334 days for yearly averages
        if averaging == 'M':
            idx = np.where(obj['n_samples'] < 28 * 24 * 60)
            sub_text = 'Black Dots (ARM MET) and Squares (ARM MAWS),\n = < 25 days used in average'
            if 'nsa60noaa' in ds:
                idx = np.where(obj['n_samples'] < 25 * 24) # For hourly averaged data
            idx2 = np.where(obj2['n_samples'] < 25 * 24 * 60)
            if 'nsa60noaa' in ds2:
                idx2 = np.where(obj2['n_samples'] < 25 * 24) # For hourly averaged data
            if len(plot_dict[plot]['ds']) == 3:
                idx3 = np.where(obj3['n_samples'] < 25 * 24 * 60)
                if 'nsa60noaa' in ds3:
                    idx3 = np.where(obj3['n_samples'] < 25 * 24) # For hourly averaged data
                    sub_text = 'Black Dots (ARM MET), Triangles (ARM MAWS),\nand Squares (NOAA) = < 25 days used in average'
            plt.text(1.0, -0.15, sub_text, transform=display.axes[0].transAxes, fontsize=7,
                     horizontalalignment='right')
            myFmt = mdates.DateFormatter('%b %Y')
        if averaging == 'Y':
            sub_text = 'Black Dots (ARM MET) and Squares (ARM MAWS),\n = < 334 days used in average'
            idx = np.where(obj['n_samples'] < 334 * 24 * 60)
            if 'nsa60noaa' in ds:
                idx = np.where(obj['n_samples'] < 334 * 24) # For hourly averaged data
            idx2 = np.where(obj2['n_samples'] < 334 * 24 * 60)
            if 'nsa60noaa' in ds2:
                idx2 = np.where(obj2['n_samples'] < 334 * 24) # For hourly averaged data


            if len(plot_dict[plot]['ds']) == 3:
                idx3 = np.where(obj3['n_samples'] < 334 * 24 * 60)
                if 'nsa60noaa' in ds3:
                    idx3 = np.where(obj3['n_samples'] < 334 * 24) # For hourly averaged data
                    sub_text = 'Black Dots (ARM MET), Triangles (ARM MAWS),\nand Squares (NOAA) = < 334 days used in average'

            plt.text(1.0, -0.15, sub_text, transform=display.axes[0].transAxes, fontsize=7,
                     horizontalalignment='right')
            myFmt = mdates.DateFormatter('%Y')

        #obj['mean'][idx] = np.nan
        #obj2['mean'][idx2] = np.nan
        if averaging == 'Y':
            #obj['mean'][0] = np.nan
            #obj2['mean'][0] = np.nan
            if len(plot_dict[plot]['ds']) == 3:
                obj3['mean'][0] = np.nan

        names = list(ds_dict)
        display.plot('mean', set_title=title, subplot_index=(0,), dsname=names[0], label=names[0])
        display.plot('mean', set_title=title, subplot_index=(0,), dsname=names[1], label=names[1])
        if len(plot_dict[plot]['ds']) == 3:
            display.plot('mean', set_title=title, subplot_index=(0,), dsname=names[2], label=names[2])
            display.axes[0].plot(obj3['time'].values[idx3], obj3['mean'].values[idx3], 'k^')

        display.axes[0].set_ylabel('(' + units + ')')
        display.axes[0].xaxis.set_major_formatter(myFmt)
        display.axes[0].plot(obj['time'].values[idx], obj['mean'].values[idx], 'ko')
        display.axes[0].plot(obj2['time'].values[idx2], obj2['mean'].values[idx2], 'ks')
        display.axes[0].grid(axis='y')
        plt.legend()

        #imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
        imagename = './images/' + ds + '_' + variable + '_' + ds2 + '_' + variable2 + '_' + averaging + '.png'
        plt.tight_layout()
        plt.savefig(imagename)
        del obj
        del obj2
        try:
            del obj3
        except:
            pass
        idx=None
        idx2=None
        idx3=None
