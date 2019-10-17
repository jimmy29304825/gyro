#!/usr/bin/python
import smbus
import math
import time
import pandas as pd 
import requests, json
from datetime import datetime
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pygame
clf = joblib.load('model_32_py3.pkl')

music_first = True
now_music_station = ""
music_station = ""
music_name = ""
run_music_list = ['01.mp3']
fast_music_list = ['01.mp3']
slow_music_list = ['01.mp3']
pygame.mixer.init()
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def change_music(music_station):
    global now_music_station
    global music_name
    #抓取外部變數
    #進行現在的狀態和下的命令，如果一樣則不執行，直接回傳上一次的音樂名稱
    if music_station != now_music_station:
        global music_first
        # global run_music_list
        # global fast_music_list
        # global slow_music_list
        # 檢查音樂撥放狀態，如果撥放中，就淡出結束音樂
        if music_station != now_music_station and music_first != True:
            # print(pygame.mixer.music.get_busy())
            if pygame.mixer.music.get_busy() == 1:
                # print("停止音樂")
                pygame.mixer.music.fadeout(3000)
                time.sleep(3)
        # 檢查相對應狀態，載入相對應歌曲
        if music_station == "run":
            pygame.mixer.music.load('03.mp3')
            music_name = '03.mp3'
        elif music_station == "fast":
            pygame.mixer.music.load('02.mp3')
            music_name = '02.mp3'
        elif music_station == "slow":
            pygame.mixer.music.load('01.mp3')
            music_name = '01.mp3'
        # 撥放音樂
        # pygame.mixer.music.play(n,start,stop)#第一个参数为播放次数，如果是-1表示循环播放，省略表示只播放1次。第二个参数和第三个参数分别表示播放的起始和结束位置。
        pygame.mixer.music.play(-1)
        # print("撥放音樂")
        #修改狀態為執行中的狀態
        now_music_station = music_station
        #將第一次執行設為False
        music_first = False
    return music_name

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
status_dict = {'null': 0, 'run': 1, 'fast': 2, 'slow': 3}
df = pd.DataFrame(columns=["X","Y","Z",
                           "Xr","Yr","Zr",'DateTime', 'ID'])
                           
df_new = pd.DataFrame(columns=['X_avg', 'Y_avg', 'Z_avg', 'Xr_avg', 'Yr_avg', 'Zr_avg', 
                               'X_sd', 'Y_sd', 'Z_sd', 'Xr_sd', 'Yr_sd', 'Zr_sd', 
                               'X_range', 'Y_range', 'Z_range', 'Xr_range', 'Yr_range', 'Zr_range'])
id = 'jimmy'
status_list = []
# kafka's ip and port
status_kafka="http://54.95.97.151:8082/topics/status"
headers = { "Content-Type" : "application/vnd.kafka.json.v2+json" }

count = 1

while(True):        
    t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    if count > 2:
        if t > df['DateTime'].iloc[-1]:
   # if 1 == 2:
            X = df['X']/131
            Y = df['Y']/131
            Z = df['Z']/131
            Xr = df['Xr']/16384
            Yr = df['Yr']/16384
            Zr = df['Zr']/16384
        # average
            X_avg = round(sum(X)/len(df), 2)
            Y_avg = round(sum(Y)/len(df), 2)
            Z_avg = round(sum(Z)/len(df), 2)
            Xr_avg = round(sum(Xr)/len(df), 2)
            Yr_avg = round(sum(Yr)/len(df), 2)
            Zr_avg = round(sum(Zr)/len(df), 2)
        # std
            X_sd = round(np.std(X))
            Y_sd = round(np.std(Y))
            Z_sd = round(np.std(Z))
            Xr_sd = round(np.std(Xr))
            Yr_sd = round(np.std(Yr))
            Zr_sd = round(np.std(Zr))
        # range
            X_range = max(X) - min(X)
            Y_range = max(Y) - min(Y)
            Z_range = max(Z) - min(Z)
            Xr_range = max(Xr) - min(Xr)
            Yr_range = max(Yr) - min(Yr)
            Zr_range = max(Zr) - min(Zr)
            data = {'X_avg': X_avg, 'Y_avg': Y_avg, 'Z_avg': Z_avg, 
                    'Xr_avg': Xr_avg, 'Yr_avg': Yr_avg, 'Zr_avg': Zr_avg, 
                    'X_sd': X_sd, 'Y_sd': Y_sd, 'Z_sd': Z_sd, 
                    'Xr_sd': Xr_sd, 'Yr_sd': Yr_sd, 'Zr_sd': Zr_sd,
                    'X_range': X_range, 'Y_range': Y_range, 
                    'Z_range': Z_range, 'Xr_range': Xr_range, 'Yr_range': Yr_range, 'Zr_range': Zr_range}
            df_new = df_new.append(data, ignore_index = True)
            status_index = clf.predict(df_new)[0]
            status_list.append(status_index)
            if len(status_list) == 10:
                counts = np.bincount(status_list)
                status_music = np.argmax(counts)
                status = list(status_dict.keys())[list(status_dict.values()).index(status_music)]
                music = change_music(status)
                print(status_list)
                status_list = []
                kafka_data = {"records":[{"value":{"status": status,"music": music, "DateTime": t,"ID": id}}]}
                r = requests.post(status_kafka, data=json.dumps(kafka_data), headers=headers)
                print('status: {}, music: {}'.format(status, music), r)
            df.drop(df.index, inplace=True)
            df_new.drop(df_new.index, inplace=True)
 
    gyroskop_xout = read_word_2c(0x43) #x route
    gyroskop_yout = read_word_2c(0x45) #y route
    gyroskop_zout = read_word_2c(0x47) #z route
     
    beschleunigung_xout = read_word_2c(0x3b) #x
    beschleunigung_yout = read_word_2c(0x3d) #y
    beschleunigung_zout = read_word_2c(0x3f) #z

    X = gyroskop_xout / 131
    Y = gyroskop_yout / 131
    Z = gyroskop_zout / 131
    
    Xr = beschleunigung_xout / 16384
    Yr = beschleunigung_yout / 16384
    Zr = beschleunigung_zout / 16384
    
    data3={"X":gyroskop_xout,"Y":gyroskop_yout,"Z":gyroskop_zout,
           "Xr":beschleunigung_xout,"Yr":beschleunigung_yout,"Zr":beschleunigung_zout,
           "DateTime":t,"ID":id}        
    df = df.append(data3, ignore_index = True)
    count += 1    
    
    




