import glob
import act
import matplotlib.pyplot as plt

year = '2007'

files = glob.glob('./data/sgpmetE13.b1/*.' + year + '*')
files.sort()

variable = 'rh_mean'
ds = act.io.read_arm_netcdf(files)
ds = act.qc.arm.add_dqr_to_qc(ds, variable=variable)
ds = ds.where(ds['qc_'+variable] == 0)
#files = glob.glob('./data/nsa60noaacrnX1.b1/*.' + year + '*')
#files.sort()
#ds2 = act.io.read_arm_netcdf(files)
#ds2 = act.qc.arm.add_dqr_to_qc(ds2)

#display = act.plotting.TimeSeriesDisplay({'ARM': ds, 'NOAA': ds2}, figsize=(15, 10), subplot_shape=(2,))
#display.plot('temp_mean', subplot_index=(0,), dsname='ARM')
#display.plot('temperature', subplot_index=(0,), dsname='NOAA')
#display.qc_flag_block_plot('rh_mean', subplot_index=(1,), dsname='ARM')

display = act.plotting.TimeSeriesDisplay(ds, subplot_shape=(2,))
display.plot(variable, subplot_index=(0,))
display.qc_flag_block_plot(variable, subplot_index=(1,))

plt.show()
