from time import sleep, time
import sys
import pyvisa as pv
from numpy import zeros, linspace, savetxt
from decimal import *
from matplotlib.pyplot import plot, show, figure

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
    print("Opening resources...")
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)

    # set decimal precision to 3
    getcontext().prec = 3

    # init source 1 - Vs
    print("Initializing Source 1...")
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write('SOUR1:FREQ 4E4')
    func_gen.write('SOUR1:VOLT 0.5')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR1:PHAS 0')
    
    # init source 2 - Vx
    print("Initializing Source 2...")
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ 4E4')
    func_gen.write('SOUR2:VOLT 0.5')
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('SOUR2:PHAS 0')
    
    # synchronize phase
    print("Synchronizing phase...")
    func_gen.write('PHAS:SYNC')
        
    # set initial time constant
    print("Setting FASTMODE and TC...")
    lock_in.write('FASTMODE 0')
    lock_in.write('TC 9')
    tc = 0.25

    # set lock_in sensitivity
    print("Setting SEN...")
    lock_in.write('SEN 25')

    # turn on output
    print("Turning on function generator output...")
    func_gen.write('OUTP1 1; OUTP2 1')

    x_vals = []
    y_vals = []
    phase_vals = linspace(0, 360, 100, endpoint=False)
    for phs in phase_vals:
        func_gen.write(f'SOUR2:PHAS {phs}')
        sleep(5*tc)
        Y = lock_in.query_ascii_values('Y?')
        X = lock_in.query_ascii_values('X?')
        x_vals.append(X)
        y_vals.append(Y)
    
    figure(1)
    plot(phase_vals, y_vals)

    figure(2)
    plot(phase_vals, x_vals)

    show()

    func_gen.write('OUTP1 0; OUTP2 0')
    return

if __name__ == "__main__":
    main()
    
