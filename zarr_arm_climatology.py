import act
import glob
import xarray as xr
import numpy as np
import pandas as pd

ds_dict = {
        'nsa60noaacrnX1.b1': {'variables': ['temperature', 'precipitation'], 'averaging': ['YE', 'ME']},
        'nsametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'ME']},
        'nsamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']},
        'sgpmetE13.b1': {'variables': ['temp_mean', 'rh_mean', 'tbrg_precip_total'], 'averaging': ['YE', 'ME']},
        'sgpmawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']},
        'sgp30ecorE14.b1': {'variables': ['h', 'lv_e', 'k', 'fc'], 'averaging': ['M']},
        'nsatsiskycoverC1.b1': {'variables': ['percent_opaque', 'percent_thin'], 'averaging': ['Y', 'M']},
        'enametC1.b1': {'variables': ['temp_mean', 'rh_mean'], 'averaging': ['YE', 'ME']},
        'enamawsC1.b1': {'variables': ['atmospheric_temperature', 'atmospheric_relative_humidity'], 'averaging': ['YE', 'ME']}, 
        'sgpceil10mC1.b1': {'variables': ['first_cbh'], 'averaging': ['YE', 'M']},
        'nsaceilC1.b1': {'variables': ['first_cbh'], 'averaging': ['YE', 'ME']},
}



files = glob.glob('/Users/atheisen/Code/ARM-Climatologies/zarr_data/*')
files.sort()
result_dir = './results/'

for f in files:
    datastream = '.'.join(f.split('/')[-1].split('.')[-3:-1])
    print(datastream)
    variables = ds_dict[datastream]['variables']

    ds = xr.open_zarr(f)
    ds = ds.sortby("time")

    print(ds['time'].values)

    ds_month = ds[variables].resample(time='MS', skipna=True, label='left')
    ds_year = ds[variables].resample(time='YS', skipna=True, label='left')

    m_count = ds_month.count()
    m_std  = ds_month.std()
    m_vmin = ds_month.min()
    m_vmax = ds_month.max()
    m_sum = ds_month.sum()
    m_mean = ds_month.mean()

    y_count = ds_year.count()
    y_std  = ds_year.std()
    y_vmin = ds_year.min()
    y_vmax = ds_year.max()
    y_sum = ds_year.sum()
    y_mean = ds_year.mean()

    for variable in variables:
        m_result_file = datastream + '_'+variable + '_MS.csv'
        y_result_file = datastream + '_'+variable + '_YS.csv'

        m_se = m_std[variable] / np.sqrt(m_count[variable])
        y_se = y_std[variable] / np.sqrt(y_count[variable])
        if 'precip' in variable:
            m_data = m_sum[variable]
            y_data = y_sum[variable]
        else:
            m_data = m_mean[variable]
            y_data = y_mean[variable]

        df = pd.DataFrame(
            {
                'time': m_count.time.values,
                'average': m_data.values,
                'count': m_count[variable].values,
                'minimum': m_vmin[variable].values,
                'maximum': m_vmax[variable].values,
                'standard_deviation': m_std[variable].values,
                'standard_error': m_se.values,
            }
        )
        df.to_csv(result_dir + m_result_file, index=False, date_format='%Y-%m-%dT%H:%M:%S')

        df = pd.DataFrame(
            {
                'time': y_count.time.values,
                'average': y_data.values,
                'count': y_count[variable].values,
                'minimum': y_vmin[variable].values,
                'maximum': y_vmax[variable].values,
                'standard_deviation': y_std[variable].values,
                'standard_error': y_se.values,
            }
        )
        df.to_csv(result_dir + y_result_file, index=False, date_format='%Y-%m-%dT%H:%M:%S')
