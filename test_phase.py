from time import sleep, time
import sys
import pyvisa as pv
from numpy import zeros, linspace, savetxt
from decimal import *

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
    func_gen.write('SOUR1:FREQ 1E4')
    func_gen.write('SOUR1:VOLT 0.5')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR1:PHAS 0')
    
    # init source 2 - Vx
    print("Initializing Source 2...")
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ 1E4')
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
    tc = 1

    # set lock_in sensitivity
    print("Setting SEN...")
    lock_in.write('SEN 25')

    # turn on output
    print("Turning on function generator output...")
    func_gen.write('OUTP1 1; OUTP2 1')

    # find phase difference so that signal is only in X component of lock-in
    print("Starting loop...")
    sleep(5*tc)
    Y_n1 = lock_in.query_ascii_values('Y?')[0]
    print(f"Y_n1 = {Y_n1}")
    phi_n1 = 0
    phi_n = 359
    func_gen.write(f'SOUR2:PHAS {phi_n}')
    sleep(5*tc)
    Y_n = lock_in.query_ascii_values('Y?')[0]
    print(f"Y_n = {Y_n}")
    while (abs(phi_n - phi_n1) > 1e-2):
        phi_n2 = phi_n1
        phi_n1 = phi_n
        Y_n2 = Y_n1
        Y_n1 = Y_n
        phi_n = (phi_n1 - Y_n1 * ((phi_n1 - phi_n2) / (Y_n1 - Y_n2))) % 360
        func_gen.write(f'SOUR2:PHAS {phi_n}')
        sleep(5*tc)
        Y_n = lock_in.query_ascii_values('Y?')[0]
        print(f"Y_n = {Y_n}")
    print(f" Final phi value: {phi_n}")

    # turn off output
    print('Turning off output...')
    func_gen.write('OUTP1 0; OUTP2 0')

    # end program
    print('End')
    return

if __name__ == "__main__":
    main()
    
