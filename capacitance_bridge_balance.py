## Auto-balance the capacitance bridge

from serial.tools.list_ports import comports
from time import sleep
import sys
import pyvisa as pv
from serial import Serial
from numpy import linspace, zeros
from dc_voltage_box_cmd import readChannel, setChannel

def main():
    # uses command-line arguments for locations of devices
    # if the user hasn't listed 3 objects, it will disregard command line input and request that the user input the lcoations of the 3 devices
    rm = pv.ResourceManager()
    if (sys.argc != 4):
        open_ports = comports()
        print("Listing available USB instruments... \nThe following serial ports are available:\n")
        for coms in open_ports:
            print(com.device+"\n")
        dc_box_loc = input("At which serial port is the DC Box located? ")
        print("Listing VISA intruments... \nThe following VISA instruments are available:\n")
        rm.list_resources()
        func_gen_loc = input("Which device corresponsds to the function generator? ")
        lock_in_loc = input("Which device corresponds the the lock-in amplifier? ")
    else if (sys.argc == 4)
        dc_box_loc = argv[1]
        func_gen_loc = argv[2]
        lock_in_loc = argv[3]
    dc_box = Serial(dc_box_loc, 115200, timeout=3)
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    
    tolerance = 1e-6 # what accuracy do we want to know the amplitude to?
    Cs = 1e-12 # known capacitance - hopefully somewhere near target magnitude
    
    N, a, b = 100, 0 , 10 # have as user input in the future?
    
    dc_vals = linspace(a, b, N) # how many steps? maybe program parameter?
    cx_vals = zeros(1, N)
    
    sour1_amp = 10e-3
    
    # initialize function generator output, turn on both simultaneously
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write('SOUR1:FREQ 1e6')
    func_gen.write(f'SOUR1:VOLT {sour1_amp}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ 1e6')
    func_gen.write(f'SOUR2:VOLT {sour1_amp}') # select amplitudes that will make convergence fastest
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('PHAS:SYNC')
    func_gen.write('SOUR2:PHAS 180')
    func_gen.write('OUTP1 1; OUTP2 1')
    
    for i in range(1,N):
        setChannel(dc_box, 0, dc_vals[i]) # not sure how many channels we need to set for this but this is the command format from aric's code
        amp0 = func_gen.query_ascii_values('SOUR2:VOLT?')[0]
        VL0 = lock_in.query_ascii_values('X.')[0]
        amp1 = amp0/2
        while (abs(amp1-amp0) > tolerance):
            func_gen.write(f'SOUR2:VOLT {amp1}')
            time.sleep(1) # optimize
            VL1 = lock_in.query_ascii_values('X.')[0]
            new_amp = amp1 - VL1*(amp1-amp0)/(VL1-VL0)
            amp0 = amp1
            VL0 = VL1
            amp1 = new_amp
        Cx = Cs*amp1/sour1_amp
        cx_vals[i] = Cx
       
if __name__ == "__main__":
	main()
