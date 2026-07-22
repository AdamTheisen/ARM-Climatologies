import act
import glob
import time
import xarray as xr
from xarray.coding.times import encode_cf_datetime
import json

dirs = glob.glob('/Users/atheisen/Code/ARM-Climatologies/data/*enamaws*')
dirs.sort()
for d in dirs:
    files = glob.glob(d + '/*')
    files.sort()
    print(d)
    start_time = time.perf_counter()
    ds = act.io.read_arm_netcdf(
        files,
        combine='nested',
        concat_dim='time',
        join='outer',
        data_vars='all',
        parallel=True,
        chunks={}
    )
    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.6f} seconds")

    try:
        ds = act.qc.arm.add_dqr_to_qc(ds)
        ds.qcfilter.datafilter(del_qc_var=True, rm_assessments=['Bad', 'Incorrect', 'Indeterminate', 'Suspect'])
    except:
        pass

    drop_vars = [v for v in list(ds) if v.startswith('qc')]
    ds =ds.drop_vars(drop_vars)

    keys = list(ds.attrs.keys())

    for attr in keys:
        value = ds.attrs[attr]
        if attr.startswith('_'):
            del ds.attrs[attr]
            continue
        if isinstance(value, dict):
            ds.attrs[attr] = json.dumps(value)
            continue

    try:
        if 'maws' in d:
            t = ds['base_time'].attrs['string'].split(' ')
            t = t[0] + 'T' + t[1] + ' ' + t[2]
            atts = {'units': 'Minutes since ' + t}
        else:
            atts = {'units': 'Minutes since ' + ds['base_time'].attrs['string'].replace(',', 'T')}
    except:
        atts = {'units': 'Minutes since ' + ds['base_time'].attrs['String']}

    ds['time'].encoding = {
        'units': atts['units'],
        'calendar': 'gregorian',
        'dtype': 'int64'
    }

    try:
        ds = ds.drop_vars(['time_bounds'])
    except:
        pass

    ds = ds.chunk({'time': 1440})
    ds.to_zarr('./zarr_data/' + d.split('/')[-1] + '.zarr', mode='w')
    ds.close()
