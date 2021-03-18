# file containing commands for the DC box so that commands can be imported without calling main

import serial
import numpy as np
import time

#Generates a sin wave of provided amplitude and frequency. The wave can be made more
#continous by decreasing step sizes but below 13 ms it will not be able keep time correctly
#as time.sleep() does not work correctly below that value.
#Right now, this function does not scale correctly with time. It can produce a sin wave,
#but it will not be of specified frequency or for the correct time length.
def sinWave(ser, chanNum, ampl, freq, timeLength):
    #Creates a numpy array of time values for generating the sin wave.
    #Step size should match the time.sleep() later on in an attempt
    #to keep the wave synced with real time.
    timeSteps=np.arange(0,timeLength,.02)
    
    #Generate a numpy array of voltage sin values based on freq and ampl
    voltage=ampl*np.sin(2*np.pi*freq*timeSteps)

    #Applies adjustment to voltage values to reduce error. Channels controlled
    #by board 1 (0,1,4,5) undershoot while the rest overshoot.
    if (chanNum == 0 or chanNum == 1 or chanNum == 4 or chanNum == 5):
        voltage = voltage*1.000407503
        #Command fails if you attempt to set a voltage <-10 or >10, so this
        #ensures all voltage values fall within that range after they've been
        #adjusted. This is only a problem for board 1 channels since the
        #adjustment makes them larger.
        for x in np.nditer(voltage, op_flags = ['readwrite']):
            if x < -10:
                x[...] = -10
            elif x >10:
                x[...] = 10
    else:
        voltage = voltage*0.999360073

    #Sends the set voltage command for each value generated previously
    for i in range(voltage.size):
        #Assembles the "SET" command string to send to the DUE
        commandStr='SET,'+str(chanNum)+','+str(voltage[i])+' \r'
        #Encodes command string to bytes before passing to the DUE
        ser.write(commandStr.encode('utf-8'))
        time.sleep(.02)
        response = ser.readline()

    #Set the output channel back to 0V
    offStr='SET, '+str(chanNum)+', 0 \r'
    ser.write(offStr.encode('utf-8'))
    response = ser.readline()
    
    print("Operation finished")
    
#Generates a square wave of given amplitude and period for a given length of time.
#Will only work correctly if the timeLength is a multiple of period.
def sqWave(ser, chanNum, ampl, period, timeLength):
    #Resets channel to 0V before passing commands
    offStr='SET, '+str(chanNum)+', 0 \r'
    ser.write(offStr.encode('utf-8'))
    time.sleep(1)

    #Applies adjustment to voltage value to reduce error. Channels controlled
    #by board 1 (0,1,4,5) undershoot while the rest overshoot.
    if (chanNum == 0 or chanNum == 1 or chanNum == 4 or chanNum == 5):
        ampl = ampl*1.000407503
        if (ampl > 10):
            ampl = 10
        elif (ampl <-10):
            ampl = -10
    else:
        ampl = ampl*0.999360073

    for i in range(int(timeLength/period)):
        #Generates "SET" command to change output to amplitude voltage,
        #encodes to bytes, and passes to DUE
        commandStr='SET,'+str(chanNum)+','+str(ampl)+' \r'
        ser.write(commandStr.encode('utf-8'))
        #Keep at amplitude voltage for half of one period
        time.sleep(period*.5)
        response = ser.readline()

        #Resets channel to 0V for half of one period
        ser.write(offStr.encode('utf-8'))
        time.sleep(period*.5)
        response= ser.readline()

    #Sets channel back to 0V
    ser.write(offStr.encode('utf-8'))
    time.sleep(.02)
    response = ser.readline()
        
    print("Operation finished")

#Generates a sawtooth wave with a given starting and end voltage. As of now, only repeats
#the wave 5 times, with each period lasting ~(highVolt-lowVolt) seconds
def sawWave(ser, chanNum, lowVolt, highVolt):
    #How many periods the wave will repeat for
    repeatNum = 5
    
    #Generates an array of voltage values for one period of
    #the sawtooth wave. The step size should match the
    #time.sleep() values in order to keep sync with real time.
    voltage = np.arange(lowVolt, highVolt+.02, .02)

    #Applies adjustment to voltage values to reduce error. Channels controlled
    #by board 1 (0,1,4,5) undershoot while the rest overshoot.
    if (chanNum == 0 or chanNum == 1 or chanNum == 4 or chanNum == 5):
        voltage = voltage*1.000407503
        #Command fails if you attempt to set a voltage <-10 or >10, so this
        #ensures all voltage values fall within that range after they've been
        #adjusted. This is only a problem for board 1 channels since the
        #adjustment makes them larger.
        for x in np.nditer(voltage, op_flags = ['readwrite']):
            if x < -10:
                x[...] = -10
            elif x >10:
                x[...] = 10
    else:
        voltage = voltage*0.999360073
    
    #This extends the voltage array by repeating it repeatNum times
    voltage = np.tile(voltage, repeatNum)

    #Iterates thru the voltage array, passing the appropriate "SET" commands
    #for each value
    for i in range (voltage.size):
        commandStr='SET,'+str(chanNum)+','+str(voltage[i])+' \r'
        ser.write(commandStr.encode('utf-8'))
        time.sleep(.02)
        response= ser.readline()

    #Sets the output channel to 0V and reads all previous output from the buffer
    offStr='SET, '+str(chanNum)+', 0 \r'
    ser.write(offStr.encode('utf-8'))
    response = ser.readline()
    #response.strip()
    #while (len(response) > 0):
        #response = ser.readline()
        #response.strip()
    print("Operation finished")

#Reads the voltage set on a given channel
def readChannel(ser, chanNum):
    commandStr='GET_DAC,'+str(chanNum)+' \r'
    ser.write(commandStr.encode('utf-8'))
    time.sleep(.02)
    #Prints response from Seekat with trailing characters stripped
    print(ser.readline().strip())

#Sets the voltage of one output channel
def setChannel(ser, chanNum, volt):
    #Applies adjustment to voltage value to reduce error.
    if (chanNum == 0 or chanNum == 1 or chanNum == 4 or chanNum == 5):
        volt = volt*1.000407503
        if (volt > 10):
            volt = 10
        elif (volt <-10):
            volt = -10
    else:
        volt = volt*0.999360073
    
    commandStr='SET,'+str(chanNum)+','+str(volt)+' \r'
    ser.write(commandStr.encode('utf-8'))
    time.sleep(.02)
    #Prints response from Seekat with trailing characters stripped
    print(ser.readline().strip())

#Ramps one channel using given start and end voltages, # of steps, and delay time between
#steps. Channel will remain at endVolt after the ramp is finished.
#This function can't be adjusted to reduce error as it uses a built in
#Seekat operation which does not allow you to access the voltage values.
def ramp1(ser, chanNum, stVolt, endVolt, numSteps, delayTime):
    commandStr='RAMP1,'+str(chanNum)+','+str(stVolt)+','+str(endVolt)+','+str(numSteps)+','+str(delayTime)+' \r'
    ser.write(commandStr.encode('utf-8'))
    #Waits until operations is finished, converts delayTime to seconds from microseconds in
    #order to work with time.sleep()
    time.sleep(numSteps*delayTime*(10**(-6))+.1)
    #Prints response from Seekat with trailing characters stripped
    print(ser.readline().strip())

#Ramps two channels simultaneously. numSteps needs to be the TOTAL number of steps
#for both channels, not the number of steps you want for each channel.
#Both channels will remain at endVolt once the ramp is finished.
#This function can't be adjusted to reduce error as it uses a built in
#Seekat operation which does not allow you to access the voltage values.
def ramp2(ser, chanNum1, chanNum2, stVolt1, stVolt2, endVolt1, endVolt2, numSteps, delayTime):
    commandStr='RAMP1,'+str(chanNum1)+','+str(chanNum2)+','+str(stVolt1)+','+str(stVolt2)+','+str(endVolt1)+','+str(endVolt2)+','+str(numSteps)+','+str(delayTime)+' \r'
    ser.write(commandStr.encode('utf-8'))
    time.sleep(.02)
    #Only sleep half the time since numSteps is double what either channel is doing
    time.sleep(.5*numSteps*delayTime*(10**(-6))+.1)
    #Prints response from Seekat with trailing characters stripped
    print(ser.readline().strip())

#This ramp function has to voltage adjustment but can not take a delay time <13ms due to
#time.sleep() limitations.
def rampAdj(ser, chanNum, stVolt, endVolt, numSteps, delayTime):
    #Generates an array of voltage values between the start and end voltage, with an
    #appropriate step size for the given number of steps.
    #The end voltage has the added (endVolt-stVolt)/numSteps since np.arange() does
    #not include the end value by default, so we need to go one step past where we want
    #to end.
    voltage = np.arange(stVolt, endVolt+(endVolt-stVolt)/numSteps, (endVolt-stVolt)/numSteps)

    #Voltage adjustment
    if (chanNum == 0 or chanNum == 1 or chanNum == 4 or chanNum == 5):
        voltage = voltage*1.000407503
        for x in np.nditer(voltage, op_flags = ['readwrite']):
            if x < -10:
                x[...] = -10
            elif x >10:
                x[...] = 10
    else:
        voltage = voltage*0.999360073

    #Passes "SET" commands for each voltage values with the delay time between each command
    for i in range(voltage.size):
        commandStr='SET,'+str(chanNum)+','+str(voltage[i])+' \r'
        ser.write(commandStr.encode('utf-8'))
        time.sleep(delayTime)
        response=ser.readline()

    #Sets channel back to 0V and reads responses from the buffer
    commandStr='SET,'+str(chanNum)+',0 \r'
    ser.write(commandStr.encode('utf-8'))
    response = ser.readline()
    print("Operation finished")

#Print the IDN for the Seekat
def IDN(ser):
    ser.write(b'*IDN? \r')
    time.sleep(.02)
    #Prints response from Seekat with trailing characters stripped
    print(ser.readline().strip())
    
