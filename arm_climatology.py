"""
ARM Climatologies
-----------------

Process for reading in ARM datastreams, applying QC and DQRs
and producing monthly/yearly averages in csv files

Author: Adam Theisen

"""

import act
print(act.__file__)
import glob
import numpy as np
from datetime import datetime
import pandas as pd
import dask
from act.utils.data_utils import DatastreamParserARM



def process_data(site, datastream, y, variable, averaging):
    #if int(y) == int(datetime.now().year):
    #    return
    files = glob.glob('./data/'+datastream+'/'+datastream+'.'+y+'*')
    if int(y) == int(datetime.now().year):
        return

    files.sort()
    #ds = act.io.arm.read_arm_netcdf(files, compat='override', coords='minimal')
    ds = act.io.arm.read_arm_netcdf(files, coords='minimal', cleanup_qc='True')
    ds = act.qc.arm.add_dqr_to_qc(ds, variable=variable)
    #if variable == 'temp_mean':
    #    ds = act.qc.arm.add_dqr_to_qc(ds, variable=variable, exclude=['D160215.4'])
    #else:
    #    ds = act.qc.arm.add_dqr_to_qc(ds, variable=variable)

    
    #if 'ecor' in ds:
    #    r = [129, 265]
    #    obj = obj.where((obj['wind_dir'].values < r[1]) & (obj['wind_dir'].values > r[0]))

    try:
        ds = ds.where(ds['qc_'+variable] == 0)
    except:
        print('QC Not applied: ', datastream, ' ', y, ' ', variable)
    
    # For 1 min precip rates
    #data = obj[variable].values / 60.
    #obj[variable].values = data

    # Produce specified averages and print out to a file
    count = ds[variable].resample(time=averaging, skipna=True).count()
    std = ds[variable].resample(time=averaging, skipna=True).std()
    vmin = ds[variable].resample(time=averaging, skipna=True).min()
    vmax = ds[variable].resample(time=averaging, skipna=True).max()
    if 'precip' in variable:
        ds = ds[variable].resample(time=averaging, skipna=True).sum() # For precipitation accumulation
    else:
        ds = ds[variable].resample(time=averaging, skipna=True).mean()

    data = []
    for i in range(len(ds['time'].values)):
        if averaging == 'YE':
            time = str(pd.to_datetime(ds['time'].values[i]).year) + '-01-01T00:00:00.000000000'
        if averaging == 'ME':
            time = str(pd.to_datetime(ds['time'].values[i]).year) + '-' + str(pd.to_datetime(ds['time'].values[i]).month).zfill(2)  + '-01T00:00:00.000000000'

        se = round(std.values[i] / np.sqrt(count.values[i]), 4)
        if (ds['time'].values[i].astype('datetime64[Y]').astype(int) + 1970) == int(y):
            data.append([time, str(ds.values[i]), str(count.values[i]), str(vmin.values[i]), str(vmax.values[i]), str(std.values[i]), str(se)])
    ds.close()

    return data


# Set up the datastream, variable name and averaging interval
# Averaging interval based on xarray resample (M=Month, Y=Year)
ds_dict = {
        #'sgpmetE1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE3.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE4.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE5.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE6.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE7.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE8.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE9.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE11.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE15.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE20.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE24.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE25.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE27.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE31.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE32.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE33.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE34.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE35.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE36.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE37.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE38.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE39.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE40.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},
        #'sgpmetE41.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'M']},

        #'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['YE', 'ME']},
        'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'ME']},
        #'nsamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']},
        'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean', 'tbrg_precip_total'], 'averaging': ['YE', 'ME']},
        #'sgpmawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']},
        #'sgp30ecorE14.b1': {'variables': ['h', 'lv_e', 'k', 'fc'], 'averaging': ['M']},
        #'sgp30ecorE14.b1': {'variables': ['lv_e', 'k', 'fc'], 'averaging': ['M']},
        #'nsatsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['Y', 'M']},
        #'enametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'ME']},
        #'enamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']},
        #'sgpceil10mC1.b1': {'variables': ['first_cbh'], 'averaging': ['YE', 'M']},
        #'nsaceilC1.b1': {'variables': ['first_cbh'], 'averaging': ['YE', 'ME']},
}

for ds in ds_dict:
    site = ds[0:3]

    # Update this path to where your data are
    files = glob.glob('./data/' + ds + '/' + ds + '.*')
    #files = glob.glob('/data/archive/' + site +'/' + ds + '/' + ds + '.*')
    files.sort()
    years = [f.split('.')[-3][0:4] for f in files]
    years = np.unique(years)
    for averaging in ds_dict[ds]['averaging']:
        # Open a file to write the results out to and process each year
        for variable in ds_dict[ds]['variables']:
            print('Processing: ' + ' '.join([ds, variable, averaging]))
            f = open('./results/' + ds + '_' + variable + '_' + averaging + '.csv', 'w')
            task = []
            results = []
            for y in years:
                #task.append(dask.delayed(process_data)(site, ds, y, variable, averaging))
                data = process_data(site, ds, y, variable, averaging)
                results.append(data)
            #results = dask.compute(*task)
            for i, r in enumerate(results):
                if r is None:
                    continue
                if len(r) > 1:
                    for month in r:
                        f.write(','.join(month) + '\n')
                else:
                    f.write(','.join(r[0]) + '\n')
