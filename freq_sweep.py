from time import sleep, time
import sys
import pyvisa as pv
from numpy import zeros, savetxt, linspace, sign
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
    
    # set frequency values to sweep through - need in notation "{m}E0{n}"
    print("Generating frequency values...")
    freq_vals = []
    N = 9 # number of values per order of magnitude
    a = 2
    b = 6
    for n in range(a,b):
        f0 = float(f'1.0E{n}')
        f1 = float(f'1.0E{n+1}')
        freq_points = linspace(f0,f1,N,endpoint=False)
        for f in freq_points:
            freq_vals.append("{:.2E}".format(Decimal(f)))
    
    M = N*(b-a)
    bal_Vx_vals = zeros(M)
    bal_phs_vals = zeros(M)
    Vs = Decimal(0.01)
    
    # init source 1 - Vs
    print("Initializing Source 1...")
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {freq_vals[0]}')
    func_gen.write(f'SOUR1:VOLT {Vs}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR1:PHAS 0')
    
    # init source 2 - Vx
    print("Initializing Source 2...")
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {freq_vals[0]}')
    func_gen.write(f'SOUR2:VOLT {Vs}')
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('SOUR2:PHAS 90')
    
    # synchronize phase
    print("Synchronzing output...")
    func_gen.write('PHAS:SYNC')
    
    # set initial time constant
    print("Initializing TC...")
    lock_in.write('FASTMODE 0')
    lock_in.write('TC 15')
    tc = 100e-3

    # set sensitivity
    print("Setting sensitivity...")
    lock_in.write('SEN 22')

    # turn on output
    print("Turning on function generator output...")
    func_gen.write('OUTP1 1; OUTP2 1')
    
    # loop through frequency values
    print("Beginning frequency value loop...")
    for i in range(M-1):
        # find phase difference so that signal is only in X component of lock-in
        print("Finding phase...")
        phi_1 = Decimal(90)
        sleep(7*tc)
        Y_1 = Decimal(lock_in.query_ascii_values('Y?')[0])
        print(f"Y1 = {Y_1}")
        phi_2 = Decimal(270)
        func_gen.write(f'SOUR2:PHAS {phi_2}')
        sleep(7*tc)
        Y_2 = Decimal(lock_in.query_ascii_values('Y?')[0])
        print(f"Y2 = {Y_2}")
        while (abs(phi_1 - phi_2) > Decimal(1e-2)):
            phi_m = (phi_1 + phi_2)/2
            func_gen.write(f'SOUR2:PHAS {phi_m}')
            sleep(7*tc)
            Y_m = Decimal(lock_in.query_ascii_values('Y?')[0])
            print(f"Ym = {Y_m}")
            if (sign(Y_m) == sign(Y_2)):
                phi_2 = phi_m
            else:
                phi_1 = phi_m
        print(f"Final phi: {phi_m}")
        bal_phs_vals[i] = float(phi_m)
        
        # find amplitude to null lock-in reading
        print("Finding amplitude...")
        a_1 = Vs/10
        sleep(7*tc)
        X_1 = Decimal(lock_in.query_ascii_values('X?')[0])
        print(f"X1 = {X_1}")
        a_2 = Vs*10
        func_gen.write(f'SOUR2:VOLT {a_2}')
        sleep(7*tc)
        X_2 = Decimal(lock_in.query_ascii_values('X?')[0])
        print(f"X2 = {X_2}")
        while (abs(a_1-a_2) > Decimal(1e-2)):
            a_m = (a_1 + a_2)/2
            func_gen.write(f'SOUR2:VOLT {a_m}')
            sleep(7*tc)
            X_m = Decimal(lock_in.query_ascii_values('X?')[0])
            if (sign(X_m) == sign(X_2)):
                a_2 = a_m
            else:
                a_1 = a_m
        print(f"Final amp: {a_m}")
        bal_Vx_vals[i] = float(a_m)
        
        # set new time constant
        print("Setting new time constant...")
        f = float(freq_vals[i+1])
        if f <= 1e6 and f >= 1e5:
            lock_in.write('FASTMODE 1')
            lock_in.write('TC 6')
            tc = 100e-6
        elif f < 1e5 and f >= 1e4:
            lock_in.write('FASTMODE 0')
            lock_in.write('TC 9')
            tc = 1e-3
        elif f < 1e4 and f >= 1e3:
            lock_in.write('FASTMODE 0')
            lock_in.write('TC 12')
            tc = 10e-3
        elif f < 1e3 and f >= 1e2:
            lock_in.write('FASTMODE 0')
            lock_in.write('TC 15')
            tc = 100e-3
        else:
            lock_in.write('FASTMODE 0')
            lock_in.write('TC 18')
            tc = 1
        print(f"TC = {tc}")

        # increase frequency
        print("Increasing frequency...")
        func_gen.write(f'SOUR1:FREQ {freq_vals[i+1]}')
        func_gen.write(f'SOUR2:FREQ {freq_vals[i+1]}')

        # reset amplitude and phase of Vx
        print("Resetting Source 2...")
        func_gen.write(f'SOUR2:VOLT {Vs}')
        func_gen.write('SOUR2:PHS 90')

    # for last frequency value, repeat then turn off

    # find phase difference so that signal is only in X component of lock-in
    print("Finding phase...")
    phi_1 = Decimal(90)
    sleep(7*tc)
    Y_1 = Decimal(lock_in.query_ascii_values('Y?')[0])
    print(f"Y1 = {Y_1}")
    phi_2 = Decimal(270)
    func_gen.write(f'SOUR2:PHAS {phi_2}')
    sleep(7*tc)
    Y_2 = Decimal(lock_in.query_ascii_values('Y?')[0])
    print(f"Y2 = {Y_2}")
    while (abs(phi_1 - phi_2) > Decimal(1e-2)):
        phi_m = (phi_1 + phi_2)/2
        func_gen.write(f'SOUR2:PHAS {phi_m}')
        sleep(7*tc)
        Y_m = Decimal(lock_in.query_ascii_values('Y?')[0])
        print(f"Ym = {Y_m}")
        if (sign(Y_m) == sign(Y_2)):
            phi_2 = phi_m
        else:
            phi_1 = phi_m
    print(f"Final phi: {phi_m}")
    bal_phs_vals[i] = float(phi_m)

    # find amplitude to null lock-in reading
    print("Finding amplitude...")
    a_1 = Vs/10
    func_gen.write(f'SOUR2:VOLT {a_1}')
    sleep(7*tc)
    X_1 = Decimal(lock_in.query_ascii_values('X?')[0])
    print(f"X1 = {X_1}")
    a_2 = Vs*10
    func_gen.write(f'SOUR2:VOLT {a_2}')
    sleep(7*tc)
    X_2 = Decimal(lock_in.query_ascii_values('X?')[0])
    print(f"X2 = {X_2}")
    while (abs(a_1-a_2) > Decimal(1e-2)):
        a_m = (a_1 + a_2)/2
        func_gen.write(f'SOUR2:VOLT {a_m}')
        sleep(7*tc)
        X_m = Decimal(lock_in.query_ascii_values('X?')[0])
        if (sign(X_m) == sign(X_2)):
            a_2 = a_m
        else:
            a_1 = a_m
    print(f"Final amp: {a_m}")
    bal_Vx_vals[i] = float(a_m)

    # turn off output
    print("Turning off output...")
    func_gen.write('OUPT1 0; OUTP2 0')

    # put data into big array then write to txt file
    print("Writing data to csv...")
    data = zeros([3,M])
    freq_vals_float = []
    for f in freq_vals:
        f = float(Decimal(f))
        freq_vals_float.append(f)
    data[0,:] = freq_vals_float
    data[1,:] = bal_Vx_vals
    data[2,:] = bal_phs_vals
    savetxt("frequency_sweep.csv", data, delimiter=',')

    # end program
    print('END')
    return
       
if __name__ == "__main__":
    main()

