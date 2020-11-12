
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
verbose_output = False
configFileName = "config.ini"

def on_connect(client, userdata, flags, rc):
    print("Connected flags ",str(flags),"result code ",str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main():
     config_object = ConfigParser()
     config_object.read(configFileName)

     try:
          serverConf = config_object["SERVER_CONFIG"]
          mqttServer = serverConf["MQTT_SERVER"]
          mqttPort = int(serverConf["MQTT_PORT"])    
          mqttTopic = serverConf["MQTT_TOPIC"]
          mqttUsername = serverConf["MQTT_USERNAME"]
          mqttPW = serverConf["MQTT_PASSWORD"]
          client_keepalive = int(serverConf["CLIENT_KEEPALIVE"])

          generalConfig = config_object["GENERAL_CONFIG"]
          dataGatheringInterval = int(generalConfig["DATA_GATHERING_INTERVAL"])
          writeToCSV = bool(generalConfig["WRITE_TO_CSV_FILE"])
          verbose_output = bool(generalConfig["VERBOSE_OUTPUT"])

          gpioConfig = config_object["GPIO_CONFIG"]
          data_pin = int(gpioConfig["DATA_PIN"])
          sck_pin = int(gpioConfig["SCK_PIN"])
     except KeyError as kError:
          raise Exception(colored("Configuration Error: Key {0} not found in config file.".format(kError), 'red'))

     if serverConf:
          print(colored("-------------------------------------------------", 'cyan'))
          print(colored("Rasperry Soil Sensor Data Publisher", 'magenta'))
          print(colored("-------------------------------------------------", 'cyan'))
          print(("[i] Using MQTT server " + colored("{}", 'yellow') + " on port " + colored("{}", 'yellow')).format(mqttServer, mqttPort))
          print("[i] Channel: " + colored("{}", 'yellow').format(mqttTopic))
          print("[i] Using user: " + colored("{}", 'yellow').format(mqttUsername))
          print()
          
          client = mqttClient.Client()
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
                              sensor.calculate_dew_point(temp, humidity)
                         
                         jsonData = json.dumps({"temperature": temp, "humidity": humidity })
                         if(verbose_output):
                              print(jsonData)

                         # MQTT publish
                         client.publish(mqttTopic, jsonData)

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
