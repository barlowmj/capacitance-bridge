from numpy import genfromtxt, tan, log10, pi, cos
from pylab import plot, show, figure, xlim, ylim

data = genfromtxt("frequency_sweep 1uF 1M series.csv", delimiter=",")

figure(1)
plot(log10(data[0,:]), tan(data[2,:]*(180/pi)))

figure(2)
plot(log10(data[0,:]), abs(cos(data[2,:])*data[1,:])/0.01)

show()
