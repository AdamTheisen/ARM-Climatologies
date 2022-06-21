import act
import matplotlib.pyplot as plt


ds = 'nsametC1.b1'
variable = 'temp_mean'
averaging = 'M'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names, index_col=0, parse_dates=['time'])


display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,8))
title = 'Averages of ' + variable + ' in '+ ds
display.plot('mean', set_title=title)

imagename = './images/' + ds + '_' + variable + '_' + averaging + '.png'
plt.savefig(imagename)
