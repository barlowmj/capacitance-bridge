from numpy import genfromtxt, tan
from pylab import plot, show, figure

data = genfromtxt("frequency_sweep.csv", delimiter=",")

figure()
plot(data[0,:],tan(data[2,:]))
show()
