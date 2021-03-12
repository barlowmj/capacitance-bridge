## Auto-balance the capacitance bridge

from serial.tools.list_ports import comports
from time import sleep
import sys
import pyvisa as pv
from serial import Serial
from numpy import arange
from DC Voltage Box

def main():
    # uses command-line arguments for locations of devices
    # if the user hasn't listed 3 objects, it will disregard command line input
    # and request that the user input the lcoations of the 3 devices
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
    tolerance = 1e-6 # lock-in sensitivity for <2MHz = 1e-6
    Cs = 1e-12 # known capacitance
    dc_vals = arange(0, 10, 50)
    cx_vals = []
    sour1_amp = 10e-3
    func_gen.write('SOUR1:APPL:SIN 1e6, {sour1_amp}') # select amplitude that will make convergence happen faster by using Cx = Ve/Vs * Cs
    for Vdc in dc_vals
        
        VL0 = 1
        VL1 = 0
        amp0 = 10e-3
        amp1 = 5e-3
        while (abs(VL1-VL0) > tolerance):
            func_gen.write(f'SOUR2:APPL:SIN 1e6,{amp0}') # synchronize before channel on?
            func_gen.write('PHAS:SYNC')
            func_gen.write('SOUR2:PHAS:ARB 180')
            time.sleep(1) # based on time const of lock-in
            VL0 = lock_in.query('X.')
            # change SOUR2 amplitude and measure lock-in again
            fun_gen.write(f'SOUR2:FUNC:ARB:PTP {2*amp1}')
            time.sleep(1) # again, based on time const of lock-in
            VL1 = lock_in.query('X.')
            amp = amp1 - VL1*(amp1 - amp0)/(VL1-VL0)
            amp0 = amp1
            amp1 = amp
        Cx = Cs*amp1/sour1_amp
        cx_vals.append(Cx)
       
if __name__ == "__main__":
	main()
