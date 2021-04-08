import pyvisa as pv
import numpy as np
import time as time

def main():
    rm = pv.ResourceManager()
    resources = rm.list_resources()
    func_gen_loc = resources[0]
    lock_in_loc = resources[1]
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write('SOUR1:FREQ +1.0E+02')
    func_gen.write('SOUR1:VOLT +0.5')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ +1.0E+04')
    func_gen.write('SOUR2:VOLT +0.25')
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('PHAS:SYNC')
    func_gen.write('OUTP1 1; OUTP2 1')
    freq_array = []
    N = 20
    for i in range(3,5):
        f0 = float(f'1.0E{i}')
        f1 = float(f'1.0E{i+1}')
        freq_points = np.linspace(f0,f1,N,endpoint=False)
        for f in freq_points:
            freq_array.append("{:.2E}".format(dec.Decimal(f)))
    n = 0
    for freq in freq_array:
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
        time.sleep(10)
        XY = lock_in.query_ascii_values('XY?')
        print(freq[n],XY[0],XY[1])
        n += 1
    func_gen.write('OUTP1 0; OUTP2 0')
    return

if __name__ == "__main__":
    main()

