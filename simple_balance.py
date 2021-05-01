from time import sleep, time
import sys
import pyvisa as pv
from numpy import zeros, savetxt, linspace, sign, cos, pi
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

    # set decimal precision
    getcontext().prec = 4

    Vs = Decimal(0.0100)

    # init source 1 - Vs
    print("Initializing Source 1...")
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ 1.0E4')
    func_gen.write(f'SOUR1:VOLT {Vs}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR1:PHAS 0')

    # init source 2 - Vx
    print("Initializing Source 2...")
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ 1.0E4')
    func_gen.write(f'SOUR2:VOLT {Vs}')
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('SOUR2:PHAS 90')

    # synchronize phase
    print("Synchronzing output...")
    func_gen.write('PHAS:SYNC')

    # set initial time constant
    print("Initializing TC...")
    lock_in.write('FASTMODE 0')
    lock_in.write('TC 10')

    # set sensitivity
    print("Setting sensitivity...")
    lock_in.write('SEN 22')

    # turn on output
    print("Turning on function generator output...")
    func_gen.write('OUTP1 1; OUTP2 1')

    # find phase difference so that signal is only in X component of lock-in
    print("Finding phase...")
    phi_1 = Decimal(90)
    sleep(1)
    Y_1 = Decimal(lock_in.query_ascii_values('Y?')[0])
    print(f"Y1 = {Y_1}")
    phi_2 = Decimal(270)
    func_gen.write(f'SOUR2:PHAS {phi_2}')
    sleep(1)
    Y_2 = Decimal(lock_in.query_ascii_values('Y?')[0])
    print(f"Y2 = {Y_2}")
    while (abs(phi_1 - phi_2) > Decimal(1e-1)):
        phi_m = (phi_1 + phi_2)/2
        func_gen.write(f'SOUR2:PHAS {phi_m}')
        sleep(1)
        Y_m = Decimal(lock_in.query_ascii_values('Y?')[0])
        print(f"Ym = {Y_m}")
        if (sign(Y_m) == sign(Y_2)):
            phi_2 = phi_m
        else:
            phi_1 = phi_m
    print(f"Final phi: {phi_m}")
    
    # find amplitude to null lock-in reading
    print("Finding amplitude...")
    a_1 = Vs/10
    sleep(1)
    X_1 = Decimal(lock_in.query_ascii_values('X?')[0])
    print(f"X1 = {X_1}")
    a_2 = Vs*10
    func_gen.write(f'SOUR2:VOLT {a_2}')
    sleep(1)
    X_2 = Decimal(lock_in.query_ascii_values('X?')[0])
    print(f"X2 = {X_2}")
    while (abs(a_1-a_2) > Decimal(1e-5)):
        a_m = (a_1 + a_2)/2
        func_gen.write(f'SOUR2:VOLT {a_m}')
        sleep(1)
        X_m = Decimal(lock_in.query_ascii_values('X?')[0])
        print(f"Xm = {X_m}")
        if (sign(X_m) == sign(X_2)):
            a_2 = a_m
        else:
            a_1 = a_m
    print(f"Final amp: {a_m}")
    
    Cs = Decimal(input("What is the value of Cs? "))
    
    Cx = Vs*Cs/(Decimal(abs(cos(float(phi_m)*pi/180)))*a_m)
    
    print(f"Cx = {Cx}")
    
    # turn off output
    print("Turning off output...")
    func_gen.write('OUTP1 0; OUTP2 0')

    # end program
    print("END")
    return

if __name__ == "__main__":
    main()
        
