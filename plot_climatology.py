import act
import matplotlib.pyplot as plt


ds = 'nsametC1.b1'
variable = 'temp_mean'
averaging = 'M'

filename = './results/' + ds + '_' + variable + '_' + averaging + '.csv'
names = ['time', 'mean', 'n_samples']
obj = act.io.read_csv(filename, column_names=names)

display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,8))
display.plot('temp_mean')

imagename = './images/' + ds + '_' + variable + '_' + averaging + '.csv'
plt.savefig(imagename)
