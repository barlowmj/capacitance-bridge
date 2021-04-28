from numpy import genfromtxt, tan, log10
from pylab import plot, show, figure

data = genfromtxt("frequency_sweep.csv", delimiter=",")

figure()
plot(log10(data[0,:]),tan(data[2,:]))
show()
