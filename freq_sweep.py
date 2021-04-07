from time import sleep
import sys
import pyvisa as pv
from serial import serial
from numpy import geomspace, zeros

def main():
    # command-line argument - python3 freq_sweep.py [low] [high] [number of points]
    a = argv[2]
    b = argv[3]
    N = argv[4]
    rm = pv.ResourceManager()
    print("The following VISA instruments are available:")
    resources = rm.list_resources()
    i = 0
    for res in resources:
        print(f"[{i}] " + res)
        i += 1
    func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
    lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
    
    fun_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    
    tolerance = 1e-4 # precision of the amplitudes of the function generator goes to 4 sigfigs
    
    f_vals = geomspace(a, b, N)
    Vs_vals = zeros(N)
    
    Vx = 10e-3
    
    # initialize function generator output, turn on both simultaneously
    # choose source 2 to be Vs i.e. variable amplitude, hold Vx constant
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR1:VOLT {Vx}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR2:VOLT {Vx}') # select amplitudes that will make convergence fastest
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('PHAS:SYNC')
    func_gen.write('SOUR2:PHAS 180')
    func_gen.write('OUTP1 1; OUTP2 1')
    
    for i in range(1,N):
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
        Vs_vals[i] = amp1
        
       
if __name__ == "__main__":
    main()

