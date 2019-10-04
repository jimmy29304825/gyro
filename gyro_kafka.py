#!/usr/bin/python
import smbus
import math
import time
# import pandas as pd 
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


id="jimmy"
# kafka's ip and port
xyz="http://52.199.46.56:8082/topics/xyz"
headers = { "Content-Type" : "application/vnd.kafka.json.v2+json" }
list_dict = []
i = 1
while(True):
    time.sleep(0.01)    
        
    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           
#        print "Gyroskop"
#        print "--------"
 
    gyroskop_xout = read_word_2c(0x43) #x route
    gyroskop_yout = read_word_2c(0x45) #y route
    gyroskop_zout = read_word_2c(0x47) #z route
     
#        print "gyroskop_xout: ", ("%5d" % gyroskop_xout), " skaliert: ", (gyroskop_xout / 131)
#        print "gyroskop_yout: ", ("%5d" % gyroskop_yout), " skaliert: ", (gyroskop_yout / 131)
#        print "gyroskop_zout: ", ("%5d" % gyroskop_zout), " skaliert: ", (gyroskop_zout / 131)
     
#        print
#        print "Beschleunigungssensor"
#        print "---------------------"
     
    beschleunigung_xout = read_word_2c(0x3b) #x
    beschleunigung_yout = read_word_2c(0x3d) #y
    beschleunigung_zout = read_word_2c(0x3f) #z
     
    # beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
    # beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
    # beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0
     
#        print "beschleunigung_xout: ", ("%6d" % beschleunigung_xout), " skaliert: ", beschleunigung_xout_skaliert
#        print "beschleunigung_yout: ", ("%6d" % beschleunigung_yout), " skaliert: ", beschleunigung_yout_skaliert
#        print "beschleunigung_zout: ", ("%6d" % beschleunigung_zout), " skaliert: ", beschleunigung_zout_skaliert
    dict_xyz = {"value":{"X": gyroskop_xout,"Y": gyroskop_yout,"Z": gyroskop_zout,
                "Xr": beschleunigung_xout,"Yr": beschleunigung_yout,"Zr": beschleunigung_zout,
                "DateTime": t,"ID": id, "CID": i}}
    
    list_dict.append(dict_xyz)
    if len(list_dict) == 300: 
        data3 = {"records": list_dict}
        r = requests.post(xyz, data=json.dumps(data3), headers=headers)
        list_dict = []
        print('posted', i)

    i += 1
    
    




