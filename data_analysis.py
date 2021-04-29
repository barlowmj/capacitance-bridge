from numpy import genfromtxt, tan, log10, pi
from pylab import plot, show, figure, ylim

data = genfromtxt("frequency_sweep.csv", delimiter=",")

figure()
plot(log10(data[0,:]),tan(data[2,:]*(180/pi)))
ylim(-10,30)
show()
