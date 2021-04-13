from time import sleep
import sys
import pyvisa as pv
from serial import serial
from numpy import zeros, arange
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
    Vs = '1.0E-02'
    
    # init source 1 - Vs
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write(f'SOUR1:FREQ {f_vals[0]}')
    func_gen.write('SOUR1:VOLT ' + Vs)
    func_gen.write('SOUR1:VOLT:OFF 0')
    
    # init source 2 - Vx
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write(f'SOUR2:FREQ {f_vals[0]}')
    func_gen.write(f'SOUR2:VOLT ' + Vs)
    func_gen.write('SOUR2:VOLT:OFF 0')
    
    # synchronize phase
    func_gen.write('PHAS:SYNC')
    
    # turn on output
    func_gen.write('OUTP1 1; OUTP2 1')
    
    # set initial time constant
    tc = 1
    
    # set decimal precision to 3
    dec.getcontext().prec = 3
    
    # loop through frequency values
    for i in range(M):
    
        # find phase difference so that signal is only in X component of lock-in
        time.sleep(5*tc)
        Y_n1 = Decimal(lock_in.query_ascii_values('Y?')[0])
        phi_n1 = Decimal(0)
        phi_n = Decimal(180)
        func_gen.write(f'SOUR2:PHAS {phi_n}')
        time.sleep(5*tc)
        Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
        while (abs(phi_n - phi_n1) > Decimal(1e-2)):
            phi_n2 = phi_n1
            phi_n1 = phi_n
            Y_n2 = Y_n1
            Y_n1 = Y_n
            phi_n = phi_n1 - Y_n1 * ((phi_n1 - phi_n2) / (V_n1 - V_n2))
            func_gen.write(f'SOUR2:PHAS {phi_n}')
            time.sleep(5*tc)
            Y_n = Decimal(lock_in.query_ascii_values('Y?')[0])
        bal_phs_vals[i] = float(phi_n)
        
        # find amplitude to null lock-in reading
        amp0 = func_gen.query_ascii_values('SOUR2:VOLT?')[0]
        VL0 = lock_in.query_ascii_values('X.')[0]
        amp1 = amp0/2
        while (abs(amp1-amp0) > tolerance):
            func_gen.write(f'SOUR2:VOLT {amp1}')
            time.sleep(5*tc)
            VL1 = lock_in.query_ascii_values('X.')[0]
            new_amp = amp1 - VL1*(amp1-amp0)/(VL1-VL0)
            amp0 = amp1
            VL0 = VL1
            amp1 = new_amp
        bal_Vx_vals = float(amp1)
        
        # set new time constant
        for freq in freq_vals:
            f = float(freq)
            func_gen.write('SOUR1:FREQ ' + freq)
            func_gen.write('SOUR2:FREQ ' + freq)
            if f <= 1e6 and f >= 1e5:
                lock_in.write(f'TC {6}')
            elif f <= 1e5 and f >= 1e4:
                lock_in.write(f'TC {9}')
            elif f <= 1e4 and f >= 1e3:
                lock_in.write(f'TC {12}')
            elif f <= 1e3 and f >= 1e2:
                lock_in.write(f'TC {15}')
            else:
                lock_in.write(f'TC {18}')
        
       
if __name__ == "__main__":
    main()

