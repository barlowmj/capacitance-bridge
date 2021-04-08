import pyvisa as pv

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
    func_gen = rm.open_resource(func_gen_loc)
    lock_in = rm.open_resource(lock_in_loc)
    
    device = input("State which device you would like to write a command to ['l' or 'f' or 'exit']: ")
    command = input("Write command here: ")
    while (device != "exit"):
        if (device == "f"):
            func_gen.write(command)
        else:
            lock_in.write(command)
        device = input("State which device you would like to write a command to ['l' or 'f' or 'exit']: ")
        command = input("Write command here: ")
    return
    
if __name__ == "__main__":
    main()
