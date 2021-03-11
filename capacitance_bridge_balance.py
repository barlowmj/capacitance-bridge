## Auto-balance the capacitance bridge

from serial.tools.list_ports import comports
from time import sleep
import sys
import pyvisa as pv
from serial import Serial

def main():
    # uses command-line arguments for locations of devices
    # if the user hasn't listed 3 objects, it will disregard command line input
    # and request that the user input the lcoations of the 3 devices
    if (sys.argc != 4):
        open_ports = comports()
        print("Listing available USB instruments... \nThe following serial ports are available:\n")
        for coms in open_ports:
            print(com.device+"\n")
        dc_box_loc = input("At which serial port is the DC Box located? ")
        print("Listing VISA intruments... \nThe following VISA instruments are available:\n")
        rm = pv.ResourceManager()
        rm.list_resources()
        func_gen_loc = input("Which device corresponsds to the function generator? ")
        lock_in_loc = input("Which device corresponds the the lock-in amplifier? ")
    else if (sys.argc == 4)
        dc_box_loc = argv[1]
        func_gen_loc = argv[2]
        lock_in_loc = argv[3]
        dc_box = Serial(dc_box_loc, 115200, timeout=3)
        rm.ResourceManager()
        func_gen = rm.open_resource(func_gen_loc)
        lock_in = rm.open_resource(lock_in_loc)
   
if __name__ == "__main__":
	main()
