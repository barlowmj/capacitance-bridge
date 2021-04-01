from time import sleep
import sys
import pyvisa as pv
from serial import serial
from numpy import linspace, zeros

def main():
    # command-line argument - python3 freq_sweep.py [low] [high] [number of points]
    a = argv[2]
    b = argv[3]
    N = argv[4]
    
    open_ports = comports()
    print("The following USB instruments are available:")
    i = 0
    for com in open_ports:
        print(f"[{i}] " + com.device)
        i += 1
    dc_box_loc = open_ports[int(input("At which serial port is the DC Box located? "))]
    print("The following VISA instruments are available:")
    resources = rm.list_resources()
    i = 0
    for res in resources:
        print(f"[{i}] " + res)
        i += 1
    func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
    lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
    
    tolerance = 1e-4 # precision of the amplitudes of the function generator goes to 4 sigfigs
    
    f_vals = linspace(a, b, N) # how many steps? maybe program parameter?
    Vs_vals = zeros(1, N)
    
    sour1_amp = 10e-3
    
    # initialize function generator output, turn on both simultaneously
    # choose source 2 to be Vs i.e. variable amplitude, hold Vx constant
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR1:VOLT {sour1_amp}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR2:VOLT {sour1_amp}') # select amplitudes that will make convergence fastest
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('PHAS:SYNC')
    func_gen.write('SOUR2:PHAS 180')
    func_gen.write('OUTP1 1; OUTP2 1')
    
    
    
    for i in range(N-1):
        amp0 = func_gen.query_ascii_values('SOUR2:VOLT?')[0]
        # time.sleep ? need to wait for value to settle based on time const
        # time const can range 1 us - 200 us for FASTMODE (need fixed point), ranges from 500 us - 100 ks otherwise but time.sleep() only accurate to 10-13 ms; may need another method? or will exxecution time be longer than time const in this case?
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
        Vs_vals[i] = amp1
        
       
if __name__ == "__main__":
    main()

