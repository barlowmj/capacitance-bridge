## Auto-balance the capacitance bridge

from serial.tools.list_ports import comports
from time import sleep
import sys
import pyvisa as pv
from serial import Serial
from numpy import linspace, zeros
from dc_box_commands import readChannel, setChannel

def main():
    # uses command-line arguments for locations of devices
    # if the user hasn't listed 3 objects, it will disregard command line input and request that the user input the lcoations of the 3 devices
    # try to automate by recognizing substrings and using find(substr, start, end) - gives lowest index, returns -1 if not found -> if find(substr) != -1 -> use that device
    rm = pv.ResourceManager()
    if (len(sys.argv) != 5):
        open_ports = comports()
        print("The following USB instruments are available:")
        i = 0
        for com in open_ports:
            print(f"[{i}] " + com.device)
            i += 1
        dc_box_loc = open_ports[int(input("At which serial port is the DC Box located? "))]
        print("The following VISA instruments are available:")
        resources = rm.list_resources()
        i = 0
        for res in resources:
            print(f"[{i}] " + res)
            i += 1
        func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
        lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
    else:
        dc_box_loc = argv[1]
        func_gen_loc = argv[2]
        lock_in_loc = argv[3]
    dc_box = Serial(dc_box_loc, 115200, timeout=3)
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    
    timer = False
    if argv[-1] == "--timer":
        timer = True
        print("Timer mode ON")
    
    tolerance = 1e-4 # precision of the amplitudes of the function generator goes to 4 sigfigs
    Cs = 1e-12 # known capacitance - hopefully somewhere near target magnitude
    
    N, a, b = 100, 0 , 10 # have as user input in the future?
    
    dc_vals = linspace(a, b, N) # how many steps? maybe program parameter?
    cx_vals = zeros(1, N)
    
    sour1_amp = 10e-3
    
    # initialize function generator output, turn on both simultaneously
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write('SOUR1:FREQ 1e6')
    func_gen.write(f'SOUR1:VOLT {sour1_amp}')
    func_gen.write('SOUR1:VOLT:OFF 0')
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ 1e6')
    func_gen.write(f'SOUR2:VOLT {sour1_amp}') # select amplitudes that will make convergence fastest
    func_gen.write('SOUR2:VOLT:OFF 0')
    func_gen.write('PHAS:SYNC')
    func_gen.write('SOUR2:PHAS 180')
    func_gen.write('OUTP1 1; OUTP2 1')
    
    for i in range(N-1):
        if timer:
            meas_time_start = time.time()
        setChannel(dc_box, 0, dc_vals[i]) # not sure how many channels we need to set for this but this is the command format from aric's code
        amp0 = func_gen.query_ascii_values('SOUR2:VOLT?')[0]
        # time.sleep ? need to wait for value to settle based on time const
        VL0 = lock_in.query_ascii_values('X.')[0]
        amp1 = amp0/2
        while (abs(amp1-amp0) > tolerance):
            if timer:
                begin = time.time()
                
            func_gen.write(f'SOUR2:VOLT {amp1}')
            time.sleep(1) # optimize
            VL1 = lock_in.query_ascii_values('X.')[0]
            new_amp = amp1 - VL1*(amp1-amp0)/(VL1-VL0)
            amp0 = amp1
            VL0 = VL1
            amp1 = new_amp
            if timer:
                end = time.time()
                loop_duration = end - begin
                print(f"Loop lasted {loop_duration} s")
        Cx = Cs*amp1/sour1_amp
        if timer:
            meas_time_end = time.time()
            meas_time = end - begin
            print(f"    Measurement {i} required {meas_time} s")
            meas_num += 1
        cx_vals[i] = Cx
       
if __name__ == "__main__":
	main()
