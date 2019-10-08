#!/usr/bin/python
import smbus
import math
import time
import pandas as pd 
import datetime
import requests, json

 
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
def dist(a,b):
    return math.sqrt((a*a)+(b*b))
 
def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
 
bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect
 
# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)

df = pd.DataFrame(columns=["Y","SPM","DateTime","ID",])
id="ausitn"
s = 1
count = 1

if __name__ == '__main__':

    # adc = Adafruit_ADS1x15.ADS1015()
    # initialization 
    
    GAIN = 2/3  
    curState = 0
    thresh = 0  # mid point in the waveform
    P = 0
    T = 0
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100

    lastTime = int(time.time()*1000)

    # Main loop. use Ctrl-c to stop the code
    while True:
        
        for j in range(1, 15001):
            gyroskop_xout = read_word_2c(0x43) #x route
            gyroskop_yout = read_word_2c(0x45) #y route
            gyroskop_zout = read_word_2c(0x47) #z route
            beschleunigung_xout = read_word_2c(0x3b) #x
            beschleunigung_yout = read_word_2c(0x3d) #y
            beschleunigung_zout = read_word_2c(0x3f) #z
            SS = (gyroskop_zout) / 131
            
            # read from the ADC
            if abs(SS) <= 5:
                Signal = 0
            else:
                Signal = SS
            ## TODO: Select the correct ADC channel. I have selected A0 here
            ## print out every sensor data as a wave chart
            # print '-'*int(round((Signal), 0)), '|', Signal
            # print Signal
            curTime = int(time.time()*1000)

            sampleCounter += curTime - lastTime;      ## keep track of the time in mS with this variable
            lastTime = curTime
            N = sampleCounter - lastBeatTime;         ## monitor the time since the last beat to avoid noise

            ##  find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3.0 :  ## avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T :                           ## T is the trough
                  T = Signal;                               ## keep track of lowest point in pulse wave 

            if Signal > thresh and  Signal > P:         ## thresh condition helps avoid noise
                P = Signal;                               ## P is the peak
                                                        ## keep track of highest point in pulse wave

            ## NOW IT'S TIME TO LOOK FOR THE HEART BEAT
            ## signal surges up in value every time there is a pulse

            if N > 250 :                                   ## avoid high frequency noise
                if  (Signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
                  Pulse = True;                               ## set the Pulse flag when we think there is a pulse
                  IBI = sampleCounter - lastBeatTime;         ## measure time between beats in mS
                  lastBeatTime = sampleCounter;               ## keep track of time for next pulse

                  if secondBeat :                        ## if this is the second beat, if secondBeat == TRUE
                    secondBeat = False;                    ## clear secondBeat flag
                    for i in range(0,10):                  ## seed the running total to get a realisitic SPM at startup
                      rate[i] = IBI;                      

                  if firstBeat :                         ## if it's the first time we found a beat, if firstBeat == TRUE
                    firstBeat = False;                     ## clear firstBeat flag
                    secondBeat = True;                     ## set the second beat flag
                    continue                               ## IBI value is unreliable so discard it


                  ## keep a running total of the last 10 IBI values
                  runningTotal = 0;                      ## clear the runningTotal variable    

                  for i in range(0,9):                   ## shift data in the rate array
                    rate[i] = rate[i+1];                   ## and drop the oldest IBI value 
                    runningTotal += rate[i];               ## add up the 9 oldest IBI values

                  rate[9] = IBI;                         ## add the latest IBI to the rate array
                  runningTotal += rate[9];               ## add the latest IBI to runningTotal
                  runningTotal /= 10;                    ## average the last 10 IBI values 
                  SPM = (60000/runningTotal)*2;            ## how many beats can fit into a minute? that's SPM!
                  #print 'SPM: {}, T{}, P{}'.format(SPM, T, P)
                  try:
                      ## get time data
                      t = datetime.datetime.now()
                      # fd = str(t).split(' ')[0].replace("-", "_")
                      data3 = {"Y":SS, "SPM":SPM, "DateTime":t, "ID":id}
                      df = df.append(data3, ignore_index = True)
                      
                      if s == 1:
                          print 'first'
                          df.to_csv(' SMP_' + id + '_' + str(count) + '.csv', encoding="utf-8", mode='a', index=False)
                          df.drop(df.index, inplace=True)
                          s += 1
                      elif s % 10 == 0:
                          print 'loop'
                          df.to_csv(' SMP_' + id + '_' + str(count) + '.csv', encoding="utf-8", mode='a', index=False, header=False)
                          df.drop(df.index, inplace=True)
                          s += 1
                      else:
                          s += 1
                      #if SPM != "" :
                          # rd for ksql join key
                          #payload = {"records": [{"value": {"device_id": id, "timestamp": t, "SPM": str(SPM)}}]}
                          # send data to kafka
                          #r = requests.post(heart, data=json.dumps(payload), headers=headers)
                          # if link error
                          #if r.status_code != 200:
                          #    print "Status Code(SPM): " + str(r.status_code)
                          #    print r.text
                          #else:
                              #print "SPM updated"

                  except Exception as ex:
                      print ex

            if Signal < thresh and Pulse == True :     ## when the values are going down, the beat is over
                Pulse = False;                           ## reset the Pulse flag so we can do it again
                amp = P - T;                             ## get amplitude of the pulse wave
                thresh = amp/2 + T;                      ## set thresh at 50% of the amplitude
                P = thresh;                              ## reset these for next time
                T = thresh;

            if N > 2500 :                              ## if 2.5 seconds go by without a beat
                thresh = 0;                              ## set thresh default
                P = 0;                                   ## set P default
                T = 0;                                   ## set T default
                lastBeatTime = sampleCounter;            ## bring the lastBeatTime up to date        
                firstBeat = True;                        ## set these to avoid noise
                secondBeat = False;                      ## when we get the heartbeat back
                print "no steps found"
                print Signal

            #print j
            time.sleep(0.01)
            
        ##write
        # df.to_csv(' SMP_' + id + '_' + str(count) + '.csv',
                  # encoding="utf-8", mode='a', index=False)
        print count, 'saved'
        
        count += 1
        s = 1
