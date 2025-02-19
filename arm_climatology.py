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



def process_data(site, ds, y, variable, averaging):
    #if int(y) == int(datetime.now().year):
    #    return
    files = glob.glob('./data/'+ds+'/'+ds+'.'+y+'*')

    files.sort()
    #obj = act.io.arm.read_arm_netcdf(files, compat='override', coords='minimal')
    obj = act.io.arm.read_arm_netcdf(files, coords='minimal')
    if variable == 'temp_mean':
        obj = act.qc.arm.add_dqr_to_qc(obj, variable=variable, exclude=['D160215.4'])
    else:
        obj = act.qc.arm.add_dqr_to_qc(obj, variable=variable)

    
    #if 'ecor' in ds:
    #    r = [129, 265]
    #    obj = obj.where((obj['wind_dir'].values < r[1]) & (obj['wind_dir'].values > r[0]))

    try:
        obj = obj.where(obj['qc_'+variable] == 0)
    except:
        pass
    
    # For 1 min precip rates
    #data = obj[variable].values / 60.
    #obj[variable].values = data

    # Produce specified averages and print out to a file
    count = obj.resample(time=averaging, skipna=True).count()
    if 'precip' in variable:
        obj = obj.resample(time=averaging, skipna=True).sum() # For precipitation accumulation
    else:
        obj = obj.resample(time=averaging, skipna=True).mean()

    data = []
    for i in range(len(obj['time'].values)):
        if averaging == 'Y':
            time = str(pd.to_datetime(obj['time'].values[i]).year) + '-01-01T00:00:00.000000000'
        if averaging == 'M':
            time = str(pd.to_datetime(obj['time'].values[i]).year) + '-' + str(pd.to_datetime(obj['time'].values[i]).month).zfill(2)  + '-01T00:00:00.000000000'
        if (obj['time'].values[i].astype('datetime64[Y]').astype(int) + 1970) == int(y):
            data.append([time, str(obj[variable].values[i]), str(count[variable].values[i])])
    obj.close()

    return data


# Set up the datastream, variable name and averaging interval
# Averaging interval based on xarray resample (M=Month, Y=Year)
ds_dict = {
        #'sgpmetE1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE3.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE4.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE5.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE6.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE7.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE8.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE9.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE11.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE15.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE20.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE24.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE25.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE27.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE31.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE32.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE33.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE34.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE35.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE36.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE37.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE38.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE39.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE40.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'sgpmetE41.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},

        #'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['Y', 'M']},
        #'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        #'nsamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['Y', 'M']},
        #'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean', 'tbrg_precip_total'], 'averaging': ['Y', 'M']},
        'sgpmawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['Y', 'M']},
        #'sgp30ecorE14.b1': {'variables': ['h', 'lv_e', 'k', 'fc'], 'averaging': ['M']},
        #'sgp30ecorE14.b1': {'variables': ['lv_e', 'k', 'fc'], 'averaging': ['M']},
        #'nsatsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['Y', 'M']},
}

for ds in ds_dict:
    site = ds[0:3]

    # Update this path to where your data are
    files = glob.glob('./data/' + ds + '/' + ds + '.*')
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
