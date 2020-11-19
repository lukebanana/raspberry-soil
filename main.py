from time import sleep
from datetime import datetime
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

class RaspberrySoil:
     debug = False
     config_file_name = "config.ini"
     config_object = ConfigParser()

     def _on_connect(self, client, userdata, flags, rc):
          print("Connected flags ",str(flags),"result code ",str(rc))

     def _on_message(self, client, userdata, msg):
          print(msg.topic+" "+str(msg.payload))

     def _setup_config(self):
          self.config_object.read(self.config_file_name)

     def __init__(self):
          self._setup_config()

          try:
               mqttServer = self.config_object.get("SERVER_CONFIG", "MQTT_SERVER", fallback="127.0.0.1")
               mqttPort = self.config_object.getint("SERVER_CONFIG", "MQTT_PORT", fallback=1883)    
               mqttTopic = self.config_object.get("SERVER_CONFIG", "MQTT_TOPIC", fallback="home/plant")     
               client_keepalive = self.config_object.getint("SERVER_CONFIG", "CLIENT_KEEPALIVE", fallback=60)
               mqttUseUsernamePWAuth = self.config_object.getboolean("SERVER_CONFIG", "MQTT_USE_USERNAME_PW_AUTH", fallback=False)

               if(mqttUseUsernamePWAuth):
                    mqttUsername = self.config_object.get("SERVER_CONFIG", "MQTT_USERNAME")
                    mqttPW = self.config_object.get("SERVER_CONFIG", "MQTT_PASSWORD")
          
               dataGatheringInterval = self.config_object.getint("GENERAL_CONFIG", "DATA_GATHERING_INTERVAL", fallback=5)
               writeToCSV = self.config_object.getboolean("GENERAL_CONFIG", "WRITE_TO_CSV_FILE", fallback=False)
               verboseOutput = self.config_object.getboolean("GENERAL_CONFIG", "VERBOSE_OUTPUT", fallback=False)
               useWaterPump = self.config_object.getboolean("GENERAL_CONFIG", "USE_WATER_PUMP", fallback=False)
               humidityMinThreshold = self.config_object.getfloat("GENERAL_CONFIG", "PUMP_HUMIDITY_MIN_THRESHOLD", fallback=0.0)     
               humidityMaxThreshold = self.config_object.getfloat("GENERAL_CONFIG", "PUMP_HUMIDITY_MAX_THRESHOLD", fallback=50.0)
          
               data_pin = self.config_object.getint("GPIO_CONFIG", "DATA_PIN", fallback=24)
               sck_pin = self.config_object.getint("GPIO_CONFIG", "SCK_PIN", fallback=23)
               relay_pin = self.config_object.getint("GPIO_CONFIG", "RELAY_PIN", fallback=18)
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
               client.on_connect = self._on_connect
               client.on_message = self._on_message

               client.connect(mqttServer, mqttPort, client_keepalive)

               GPIO.setmode(GPIO.BCM)
               GPIO.setup(relay_pin, GPIO.OUT)        
               
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
                         pumpIsActive = False
                         while 1:
                              todayStr = "[" +  datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "]"
                              if self.debug:
                                   temp = 12.65 + random.randint(1,18)
                                   humidity = 35.102 + random.randint(1, 10)
                              else:
                                   temp = sensor.read_temperature()
                                   humidity = sensor.read_humidity(temp)
                                   #sensor.calculate_dew_point(temp, humidity)
                              
                              jsonData = json.dumps({"temperature": temp, "humidity": humidity })
                              if(verboseOutput):
                                   print(todayStr + " " + jsonData)

                              if(useWaterPump):                        
                                   
                                   if(humidity >= humidityMinThreshold and humidity <= humidityMaxThreshold):                    
                                        if(not pumpIsActive):                              
                                             GPIO.output(relay_pin, GPIO.HIGH)  # activate relay                         
                                             pumpIsActive = True                                            
                                             print(todayStr + " " + colored("Pump set active...", 'green'))
                                   else:                                   
                                        if(pumpIsActive):
                                             GPIO.output(relay_pin, GPIO.LOW)  # stop relay
                                             pumpIsActive = False  
                                             print(todayStr + " " + colored("Pump stopped.", 'green'))                    

                              # MQTT publish
                              client.publish(mqttTopic, jsonData)
                         
                              if(writeToCSV):
                                   with open(filename, 'a+') as csvfile: 
                                        csvwriter = csv.writer(csvfile, delimiter=';')  
                                        fields = [temp, humidity]  
                                        csvwriter.writerow(fields)          

                              sleep(dataGatheringInterval)
                    except (KeyboardInterrupt, SystemExit):
                         print()
                         print(colored("Received keyboard interrupt, quitting ...", 'red'))


                    print("Closing connection..")
                    if(useWaterPump):
                         GPIO.output(relay_pin, GPIO.LOW)  # stop relay
                         pumpIsActive = False  


if __name__ == '__main__':
     soil = RaspberrySoil()