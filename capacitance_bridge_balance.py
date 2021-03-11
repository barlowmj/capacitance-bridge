## Auto-balance the capacitance bridge

from serial.tools.list_ports import comports
from
from time import sleep
import sys
from AD9854 import AD9854
from AD5764_dual import AD5764
from AD5764-AD7734 import AD5764_AD7734

def main():
    if (sys.argc != 3):
        if (sys.argc != 1):
            print("Invalid number of command line arguments. Please execute\
            the following prompts to continue."
        open_ports = comports()
        print("The following serial ports are available:\n")
        for coms in open_ports:
            print(com.device+"\n")
        ac_box_location = input("At which serial port is the AC Box located? ")
        dc_box_location = input("At which serial port is the DC Box located? ")
    else if (sys.argc == 3)
        ac_box_location = argv[1]
        dc_box_location = argv[2]
    val = input("Please type \"1\" if you are using the dual AD5764 DC Voltage \
    Box,or \"2\" if you are using the AD5764-AD7734 DC Voltage Box. ")
    while (val > 2 or val < 1):
        val = input("Invalid value. Please input \"1\" or \"2\". ")
    if (val == 1):
        dc_box = AD5764(dc_box_location)
    else:
        dc_box = AD5764_AD7734(dc_box_location)
    
    
    
if __name__ == "__main__":
	main()
