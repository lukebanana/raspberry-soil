
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
import paho.mqtt.publish as publish

# Gelb = Clock
# Blau = Data
# Rot = Strom
# Green = Ground

debug = False
configFileName = "config.ini"

def main():
     config_object = ConfigParser()
     config_object.read(configFileName)

     serverConf = config_object["SERVER_CONFIG"]
     mqttServer = serverConf["MQTT_SERVER"]
     mqttPort = int(serverConf["MQTT_PORT"])    
     client_keepalive = int(serverConf["CLIENT_KEEPALIVE"])
     mqttTopic = serverConf["MQTT_TOPIC"]
     mqttUsername = serverConf["MQTT_USERNAME"]
     mqttPW = serverConf["MQTT_PASSWORD"]

     gpioConfig = config_object["GPIO_CONFIG"]
     data_pin = int(gpioConfig["DATA_PIN"])
     sck_pin = int(gpioConfig["SCK_PIN"])

     if mqttServer:
          print(colored("-------------------------------------------------", 'cyan'))
          print(colored("Rasperry Soil Sensor Data Publisher", 'magenta'))
          print(colored("-------------------------------------------------", 'cyan'))
          print(("[i] Using MQTT server " + colored("{}", 'yellow') + " on port " + colored("{}", 'yellow')).format(mqttServer, mqttPort))
          print("[i] Channel: " + colored("{}", 'yellow').format(mqttTopic))
          print("[i] Using user: " + colored("{}", 'yellow').format(mqttUsername))
          print()
          
          client = mqttClient.Client()
          client.connect(mqttServer, mqttPort, client_keepalive)
          client.username_pw_set(mqttUsername, password=mqttPW)
   
          with SHT1x(data_pin, sck_pin, gpio_mode=GPIO.BCM) as sensor:
          
               fields = ['Temp', 'Humidity']
               filename = "measurements.csv"
               
               # writing to csv file  
               with open(filename, 'w') as csvfile:  
                    # creating a csv writer object  
                    csvwriter = csv.writer(csvfile, delimiter=';')  
                    
                    # writing the fields  
                    csvwriter.writerow(fields)  
                    
                    try:
                         print(colored("Sensor is collecting and sending data...", 'green'))
                         while 1:
                              if debug:
                                   temp = 12.65 + random.randint(1,18)
                                   humidity = 35.102 + random.randint(1, 10)
                              else:
                                   temp = sensor.read_temperature()
                                   humidity = sensor.read_humidity(temp)
                                   sensor.calculate_dew_point(temp, humidity)
                                   #system("clear")
                                   #print(sensor)
                                   #print("{\"temperature\" : %5.2f}" % temp)
                              
                              jsonData = json.dumps({"temperature": temp, "humidity": humidity })
                              # MQTT publish
                              publish.single(mqttTopic, jsonData, hostname=mqttServer)

                              with open(filename, 'a+') as csvfile: 
                                   csvwriter = csv.writer(csvfile, delimiter=';')  
                                   fields = [temp, humidity]  
                                   csvwriter.writerow(fields)                           
                                   time.sleep(5)

                    except (KeyboardInterrupt, SystemExit):
                         print("Received keyboard interrupt, quitting ...")


               print("Closing connection..")

main()
