import time
import csv
import json
import random
import sys
import RPi.GPIO as GPIO
from termcolor import colored
from pi_sht1x import SHT1x
from configparser import ConfigParser
from os import system

import paho.mqtt.client as mqttClient

# Gelb = Clock
# Blau = Data
# Rot = Strom
# Green = Ground

debug = False
configFileName = "config.ini"
pumpIsActive = False

def on_connect(client, userdata, flags, rc):
    print("Connected flags ",str(flags),"result code ",str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main():
     config_object = ConfigParser()
     config_object.read(configFileName)

     try:
          mqttServer = config_object.get("SERVER_CONFIG", "MQTT_SERVER", fallback="127.0.0.1")
          mqttPort = config_object.getint("SERVER_CONFIG", "MQTT_PORT", fallback=1883)    
          mqttTopic = config_object.get("SERVER_CONFIG", "MQTT_TOPIC", fallback="home/plant")     
          client_keepalive = config_object.getint("SERVER_CONFIG", "CLIENT_KEEPALIVE", fallback=60)
          mqttUseUsernamePWAuth = config_object.getboolean("SERVER_CONFIG", "MQTT_USE_USERNAME_PW_AUTH", fallback=False)

          if(mqttUseUsernamePWAuth):
               mqttUsername = config_object.get("SERVER_CONFIG", "MQTT_USERNAME")
               mqttPW = config_object.get("SERVER_CONFIG", "MQTT_PASSWORD")
      
          dataGatheringInterval = config_object.getint("GENERAL_CONFIG", "DATA_GATHERING_INTERVAL", fallback=5)
          writeToCSV = config_object.getboolean("GENERAL_CONFIG", "WRITE_TO_CSV_FILE", fallback=False)
          verboseOutput = config_object.getboolean("GENERAL_CONFIG", "VERBOSE_OUTPUT", fallback=False)
          useWaterPump = config_object.getboolean("GENERAL_CONFIG", "USE_WATER_PUMP", fallback=False)
          humidityMinThreshold = config_object.getint("GENERAL_CONFIG", "PUMP_HUMIDITY_MIN_THRESHOLD", fallback=25)     
          humidityMaxThreshold = config_object.getint("GENERAL_CONFIG", "PUMP_HUMIDITY_MAX_THRESHOLD", fallback=50)
     
          data_pin = config_object.getint("GPIO_CONFIG", "DATA_PIN", fallback=24)
          sck_pin = config_object.getint("GPIO_CONFIG", "SCK_PIN", fallback=23)
     except KeyError as kError:
          raise Exception(colored("Configuration Error: Key {0} not found in config file.".format(kError), 'red'))

     if mqttServer and mqttTopic:
          print(colored("-------------------------------------------------", 'cyan'))
          print(colored("Rasperry Soil Sensor Data Publisher", 'magenta'))
          print(colored("-------------------------------------------------", 'cyan'))
          print(("[i] Using MQTT server " + colored("{}", 'yellow') + " on port " + colored("{}", 'yellow')).format(mqttServer, mqttPort))
          print("[i] Channel: " + colored("{}", 'yellow').format(mqttTopic))
          print("[i] Using user: " + colored("{}", 'yellow').format(mqttUsername))
          print()
          
          client = mqttClient.Client()
          if(mqttUseUsernamePWAuth):
               client.username_pw_set(mqttUsername, mqttPW)
          client.on_connect = on_connect
          client.on_message = on_message

          client.connect(mqttServer, mqttPort, client_keepalive)

          with SHT1x(data_pin, sck_pin, gpio_mode=GPIO.BCM) as sensor:
               if(writeToCSV):
                    fields = ['Temp', 'Humidity']
                    filename = "measurements.csv"
                    csvfile = open(filename, 'w')
                    try:
                         # Further file processing goes here
                         # creating a csv writer object  
                         csvwriter = csv.writer(csvfile, delimiter=';')  
                         
                         # writing the fields  
                         csvwriter.writerow(fields)  
                    finally:
                         csvfile.close()
                    
               try:
                    print(colored("Sensor is collecting and sending data...", 'green'))
                    while 1:
                         if debug:
                              temp = 12.65 + random.randint(1,18)
                              humidity = 35.102 + random.randint(1, 10)
                         else:
                              temp = sensor.read_temperature()
                              humidity = sensor.read_humidity(temp)
                              #sensor.calculate_dew_point(temp, humidity)
                         
                         jsonData = json.dumps({"temperature": temp, "humidity": humidity })
                         if(verboseOutput):
                              print(jsonData)

                         # MQTT publish
                         client.publish(mqttTopic, jsonData)

                         if(useWaterPump):
                            

                              if(humidity >= humidityMinThreshold and humidity <= humidityMaxThreshold):                    
                                   if(not pumpIsActive):
                                        # activate pump
                                        print(colored("Pump set active...", 'green'))
                                        pumpIsActive = True                              
                              else:       
                                   # stop pump
                                   pumpIsActive = False  
                                   print(colored("Pump stopped.", 'green'))
                         

                         if(writeToCSV):
                              with open(filename, 'a+') as csvfile: 
                                   csvwriter = csv.writer(csvfile, delimiter=';')  
                                   fields = [temp, humidity]  
                                   csvwriter.writerow(fields)                           
                                  

                         time.sleep(dataGatheringInterval)
               except (KeyboardInterrupt, SystemExit):
                    print("Received keyboard interrupt, quitting ...")


               print("Closing connection..")

main()
