"""
ARM Climatologies
-----------------

Process for reading in ARM datastreams, applying QC and DQRs
and producing monthly/yearly averages in csv files

Author: Adam Theisen

"""

import act
import glob
import numpy as np
from datetime import datetime
import pandas as pd


# Set up the datastream, variable name and averaging interval
# Averaging interval based on xarray resample (M=Month, Y=Year)
ds_dict = {
        'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['Y', 'M']},
        'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['Y', 'M']},
}

for ds in ds_dict:
    site = ds[0:3]

    # Update this path to where your data are
    files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '.*cdf')
    years = [f.split('.')[-3][0:4] for f in files]
    years = np.unique(years)

    for averaging in ds_dict[ds]['averaging']:
        # Open a file to write the results out to and process each year
        for variable in ds_dict[ds]['variables']:
            print('Processing: ' + ' '.join([ds, variable, averaging]))
            f = open('./results/' + ds + '_' + variable + '_' + averaging + '.csv', 'w')
            for y in years:
                if int(y) == int(datetime.now().year):
                    continue
                files = glob.glob('/data/archive/'+site+'/'+ds+'/'+ds+'.'+y+'*cdf')

                files.sort()
                obj = act.io.armfiles.read_netcdf(files)
                obj = act.qc.arm.add_dqr_to_qc(obj, variable=variable)
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

                for i in range(len(obj['time'].values)):
                    if averaging == 'Y':
                        time = str(pd.to_datetime(obj['time'].values[i]).year) + '-01-01T00:00:00.000000000'
                    if averaging == 'M':
                        time = str(pd.to_datetime(obj['time'].values[i]).year) + '-' + str(pd.to_datetime(obj['time'].values[i]).month).zfill(2)  + '-01T00:00:00.000000000'
                    if (obj['time'].values[i].astype('datetime64[Y]').astype(int) + 1970) == int(y):
                        f.write(','.join([time, str(obj[variable].values[i]), str(count[variable].values[i])]) + '\n')
                obj.close()

            f.close()
