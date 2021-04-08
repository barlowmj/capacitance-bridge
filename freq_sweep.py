from time import sleep
import sys
import pyvisa as pv
from serial import serial
from numpy import zeros, arange

def main():
    # select lock-in, function generator devices from GPIB
    rm = pv.ResourceManager()
    print("The following VISA instruments are available:")
    resources = rm.list_resources()
    i = 0
    for res in resources:
        print(f"[{i}] " + res)
        i += 1
    func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
    lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
    
    # open function generator and lock-in resources
    fun_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    
    # set frequency values to sweep through - need in notation "{m}E0{n}"
    # orders of magnitude n
    order_begin = 3
    order_end = 6
    order_vals = range(order_begin, order_end+1)
    # mantissa values m
    num_mantissa = 18
    mant_vals = linspace(1, 10, num_mantissa, endpoint=False)
    N = num_mantissa * len(order_vals)
    
    f_vals = []
    for n in order_vals:
        for m in mant_vals:
            f_vals.append(f"{str(m)}E0{}")
            
    bal_Vs_vals = zeros(N)
    bal_phs_vals = zeros(N)
    Vx = '1.0E-02'
    
    # init source 1 - Vx
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {f_vals[0]}')
    func_gen.write('SOUR1:VOLT ' + Vx)
    func_gen.write('SOUR1:VOLT:OFF 0')
    
    # init source 2 - Vs
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR2:VOLT ' + Vx)
    func_gen.write('SOUR2:VOLT:OFF 0')
    
    # synchronize phase
    func_gen.write('PHAS:SYNC')
    
    # set Vs to have phase offset of 180 deg initially
    func_gen.write('SOUR2:PHAS 180')
    
    # turn on output
    func_gen.write('OUTP1 1; OUTP2 1')
    
    # find phase difference so that signal is only in x component of lock-in
    Y1 = lock_in.query_ascii_values('X?')
    
    
    
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

