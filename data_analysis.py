from numpy import genfromtxt, tan, log10, pi
from pylab import plot, show, figure, ylim

data1 = genfromtxt("frequency_sweep ref 100pF meas 330 pF 10M series.csv", delimiter=",")
data2 = genfromtxt("frequency_sweep ref 100pF meas 330pF 5M series.csv", delimiter=",")

figure()
plot(log10(data1[0,:]),tan(data1[2,:]*(pi/180)))
plot(log10(data2[0,:]),tan(data2[2,:]*(pi/180)))
show()
