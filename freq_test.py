import pyvisa as pv

def main():
    rm = pv.ResourceManager()
    print("The following VISA instruments are available:")
    resources = rm.list_resources()
    i = 0
    for res in resources:
        print(f"[{i}] " + res)
        i += 1
    func_gen_loc = resources[int(input("Which device corresponsds to the function generator? "))]
    lock_in_loc = resources[int(input("Which device corresponds the the lock-in amplifier? "))]
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    print("Loading default excitation...")
    func_gen.write('SOUR1:FUNC SIN')
    func_gen.write('SOUR1:FREQ +1.0E+02')
    func_gen.write('SOUR1:VOLT +0.5')
    func_gen.write('SOUR1:VOLT:OFF 0')
    print("Writing reference output from SOUR2...")
    func_gen.write('SOUR2:FUNC SIN')
    func_gen.write('SOUR2:FREQ +1.0E+04')
    func_gen.write('SOUR2:VOLT +0.25')
    func_gen.write('SOUR2:VOLT:OFF 0')
    command1 = input("Turn on output [y when ready]: ")
    if (command1 == 'y'):
        return
    print("Turning on output...")
    func_gen.write('OUTP1 1; OUTP2 1')
    command = input("Input frequency here or select 'exit': ")
    while (command != 'exit'):
        func_gen.write('SOUR1:FREQ' + input)
    return
    
if __name__ == "__main__":
    main()
