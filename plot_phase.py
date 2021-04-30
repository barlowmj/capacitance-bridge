from matplotlib.pyplot import plot, show, figure, xscale
import numpy as np
import pandas as pd
import csv

file = "frequency_sweep.csv"
with open(file,mode='r') as csv_file:
    data = csv.reader(csv_file,dialect='excel')
    i = 0
    for row in data:
        if i == 0:
            data_freq = row
        if i == 1:
            data_Vx = row
        if i == 2:
            data_phase = row
        i+=1

M = len(data_freq)
frequency = np.zeros(M,float)
Vx = np.zeros(M,float)
phase = np.zeros(M,float)
for i in range(M):
    frequency[i] = float(data_freq[i])
    Vx[i] = float(data_Vx[i])
    phase[i] = float(data_phase[i])
print(phase)
figure(1)
plot(frequency, phase)
xscale("log")
figure(2)
plot(frequency,np.tan(phase*(np.pi/180)-np.pi))
xscale("log")
show()
