from time import sleep, time
import sys
import pyvisa as pv
from serial import serial
from numpy import zeros, arange, savetxt
import decimal as dec

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

    # set decimal precision to 3
    dec.getcontext().prec = 3
    
    # set frequency values to sweep through - need in notation "{m}E0{n}"
    freq_vals = []
    N = 20 # number of values per order of magnitude
    a = 3
    b = 6
    for n in range(a,b+1):
        f0 = float(f'1.0E{n}')
        f1 = float(f'1.0E{n+1}')
        freq_points = np.linspace(f0,f1,N,endpoint=False)
        for f in freq_points:
            freq_vals.append("{:.2E}".format(dec.Decimal(f)))
    
    M = N*(b-a)
    bal_Vx_vals = zeros(M)
    bal_phs_vals = zeros(M)
    Vs = Decimal('1.0E-02')
    
    # init source 1 - Vs
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR1:VOLT {Vs}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    
    # init source 2 - Vx
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR2:VOLT {Vs}')
    func_gen.write('SOUR2:VOLT:OFF 0')
    
    # synchronize phase
    func_gen.write('PHAS:SYNC')
    
    # turn on output
    print("Turning on function generator output...")
    func_gen.write('OUTP1 1; OUTP2 1')
    
    # set initial time constant
    lock_in.write('FASTMODE 0')
    lock_in.write('TC 15')
    tc = 100e-3
    
    # loop through frequency values
    print("Begin frequency value loop")
    for i in range(M-1):
    
        # find phase difference so that signal is only in X component of lock-in
        sleep(5*tc)
        Y_n1 = Decimal(lock_in.query_ascii_values('Y?')[0])
        phi_n1 = Decimal(0)
        phi_n = Decimal(180)
        func_gen.write(f'SOUR2:PHAS {phi_n}')
        sleep(5*tc)
        Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
        while (abs(phi_n - phi_n1) > Decimal(1e-2)):
            phi_n2 = phi_n1
            phi_n1 = phi_n
            Y_n2 = Y_n1
            Y_n1 = Y_n
            phi_n = phi_n1 - Y_n1 * ((phi_n1 - phi_n2) / (V_n1 - V_n2))
            func_gen.write(f'SOUR2:PHAS {phi_n}')
            sleep(5*tc)
            Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
        bal_phs_vals[i] = float(phi_n)
        
        # find amplitude to null lock-in reading
        X_n1 = Decimal(lock_in.query_ascii_values('X?')[0])
        a_n1 = Vs
        a_n = Vs / 2
        func_gen.write(f'SOUR2:VOLT {a_n}')
        sleep(5*tc)
        X_n = Decimal(lock_in.query_ascii_values('X?')[0])
        while (abs(a_n - a_n1) > Decimal(1e-3)):
            a_n2 = a_n1
            a_n1 = a_n
            X_n2 = X_n1
            X_n1 = X_n
            a_n = a_n1 - X_n1 * ((a_n1 - a_n2) / (X_n1 - X_n2))
            func_gen.write(f'SOUR2:VOLT {a_n}')
            sleep(5*tc)
            X_n = Decimal(lock_in.query_ascii_values('X?')[0])
        bal_Vx_vals[i] = float(a_n)

        # increase frequency
        func_gen.write(f'SOUR1:FREQ {f_vals[i+1]}')
        func_gen.write(f'SOUR2:FREQ {f_vals[i+1]}')

        # reset amplitude of Vx
        func_gen.write(f'SOUR2:VOLT {Vs}')

        # reset phase of Vx
        func_gen.write('SOUR2:PHS 0')
        
        # set new time constant
        for freq in freq_vals:
            f = float(freq)
            func_gen.write('SOUR1:FREQ ' + freq)
            func_gen.write('SOUR2:FREQ ' + freq)
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

    # for last frequency value, repeat then turn off

    # find phase difference so that signal is only in X component of lock-in
    sleep(5*tc)
    Y_n1 = Decimal(lock_in.query_ascii_values('Y?')[0])
    phi_n1 = Decimal(0)
    phi_n = Decimal(180)
    func_gen.write(f'SOUR2:PHAS {phi_n}')
    sleep(5*tc)
    Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
    while (abs(phi_n - phi_n1) > Decimal(1e-2)):
        phi_n2 = phi_n1
        phi_n1 = phi_n
        Y_n2 = Y_n1
        Y_n1 = Y_n
        phi_n = phi_n1 - Y_n1 * ((phi_n1 - phi_n2) / (V_n1 - V_n2))
        func_gen.write(f'SOUR2:PHAS {phi_n}')
        sleep(5*tc)
        Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
    bal_phs_vals[-1] = float(phi_n)

    # find amplitude to null lock-in reading
    X_n1 = Decimal(lock_in.query_ascii_values('X?')[0])
    a_n1 = Vs
    a_n = Vs / 2
    func_gen.write(f'SOUR2:VOLT {a_n}')
    sleep(5*tc)
    X_n = Decimal(lock_in.query_ascii_values('X?')[0])
    while (abs(a_n - a_n1) > Decimal(1e-3)):
        a_n2 = a_n1
        a_n1 = a_n
        X_n2 = X_n1
        X_n1 = X_n
        a_n = a_n1 - X_n1 * ((a_n1 - a_n2) / (X_n1 - X_n2))
        sleep(5*tc)
        X_n = Decimal(lock_in.query_ascii_values('X?')[0])
    bal_Vx_vals[-1] = float(a_n)

    # turn off output
    func_gen.write('OUPT1 0; OUTP2 0')

    # put data into big array then write to txt file
    data = zeros(3,M)
    freq_vals_float = []
    for f in freq_vals:
        f = float(Decimal(f))
        freq_vals_float.append(f)
    data[0,:] = freq_vals_float
    data[1,:] = bal_Vx_vals
    data[2,:] = bal_phs_vals
    savetxt("frequency-sweep.csv", data, delimiter=',')

    # end program
    print('END')
    return
       
if __name__ == "__main__":
    main()

