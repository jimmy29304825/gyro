# gyro
This repo is build for raspberry pi 3B+ to get sensors' data into local or send to kafka
## sensor 1: pulse sensor + sda1015 
  * heartBeats.py
    - it will send every bpm to kafka using 8082 port(restproxy)
    - remember to change id, kafka's ip and toopic name
## sensor 2: MPU6050 Gyro Sensor
  * ```gyro_test.py```
    - get data from the sensor and write into csv
    - csv file will be written when df's length = 300(about 8 - 10 sec)
    - each csv file will contain 15,000 row's data
    - remember to change id
  * ```gyro_kafka.py```
    - get data from the sensor and send to kafka
    - data will be send when the list_dict's length = 300(about 8 - 10 sec)
    - remember to change id, kafka's ip and toopic name
  * ```status_kafka_py3.py``` / ```status_test_py3.py```
    - these file is work with the randomforest model(model_32_py3.pkl)
    - each model's return value will append into a list, until list's length = 10 (10 sec), then get the mode from the list
    - misuc function will be called by status mode
    - status mode and music name will appear on the terminal or send to kafka
    - remember to change id, kafka's ip and toopic name
  * ```steps_record.py```(not using)
    - code to caculate the step per minute
    - sensor is too sensitive, could not get correct spm now
## sensor 3: gps module
  * TBC
