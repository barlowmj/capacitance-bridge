import pyvisa as pv
import numpy as np
import time as time

def main():
    rm = pv.ResourceManager()
    resources = rm.list_resources()
<<<<<<< HEAD
    i = 0
    for res in resources:
        print(f"[{i}] " + res)
        i += 1
    func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
    lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
=======
    func_gen_loc = resources[0]
    lock_in_loc = resources[1]
>>>>>>> ad9d0722dce034a2b651251ab6f0ffae10ee3a60
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
<<<<<<< HEAD
    command1 = input("Turn on output [y when ready]: ")
    if (command1 == 'y'):
        return
    print("Turning on output...")
=======
    func_gen.write('PHAS:SYNC')
>>>>>>> ad9d0722dce034a2b651251ab6f0ffae10ee3a60
    func_gen.write('OUTP1 1; OUTP2 1')
    freq_array = []
    for i in range(3,6):
        for j in range(1,10):
            freq_array.append(f"{j}.0E0{i}")
    X = np.zeros(27,float)
    Y = np.zeros(27,float)
    n = 0
    for freq in freq_array:
        func_gen.write('SOUR1:FREQ ' + freq)
        func_gen.write('SOUR2:FREQ ' + freq)
        time.sleep(10)
        XY_value = lock_in.query_ascii_values('XY?')
        X[n] = XY_value[0]
        Y[n] = XY_value[1]
        n += 1
    print(freq_array)
    print(X)
    print(Y)
    func_gen.write('OUTP1 0; OUTP2 0')
    return

if __name__ == "__main__":
    main()
