import act
import glob
import numpy as np
from datetime import datetime


# Set up the datastream, variable name and averaging interval
# Averaging interval based on xarray resample (M=Month, Y=Year)
ds = 'nsametC1.b1'
ds = 'nsa60noaacrnX1.b1'
variable = 'temp_mean'
variable = 'temperature'
averaging = 'M'
site = ds[0:3]

# Update this path to where your data are
files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '.*cdf')
years = [f.split('.')[-3][0:4] for f in files]
years = np.unique(years)

# Open a file to write the results out to and process each year
f = open('./results/' + ds + '_' + variable + '_' + averaging + '.csv', 'w')
years = list(years[0])
for y in years:
    print(y)
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

    # Produce specified averages and print out to a file
    count = obj.resample(time=averaging, skipna=True).count()
    obj = obj.resample(time=averaging, skipna=True).mean()
    print(y, obj['time'].values)
    for i in range(len(obj['time'].values)):
        #print(','.join([str(obj['time'].values[i]), str(obj[variable].values[i]), str(count[variable].values[i])]))
        if (obj['time'].values[i].astype('datetime64[Y]').astype(int) + 1970) == int(y):
            f.write(','.join([str(obj['time'].values[i]), str(obj[variable].values[i]), str(count[variable].values[i])]) + '\n')
    obj.close()

f.close()
