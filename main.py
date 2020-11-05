import RPi.GPIO as GPIO
import time
import csv
import json
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

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def main():
     config_object = ConfigParser()
     config_object.read("config.ini")

     #Get the password
     serverConf = config_object["SERVER_CONFIG"]
     mqttServer = serverConf["MQTT_SERVER"]
     mqttPort = serverConf["MQTT_PORT"]     
     client_keepalive = serverConf["CLIENT_KEEPALIVE"]
     mqttTopic = serverConf["MQTT_TOPIC"]
     mqttUsername = serverConf["MQTT_USERNAME"]
     mqttPW = serverConf["MQTT_PASSWORD"]

     gpioConfig = config_object["GPIO_CONFIG"]
     data_pin = gpioConfig["DATA_PIN"]
     sck_pin = gpioConfig["SCK_PIN"]

     if mqttServer:
          print("-------------------------------------------------")
          print("Starting Rasperry Soil Sensor Data Publisher")
          print("-------------------------------------------------")
          print("[i] Using MQTT server {} on port {}".format(mqttServer, mqttPort))
          print("[i] Channel: {}".format(mqttTopic))
          print("[i] Using user: {}".format(mqttUsername))

          client = mqttClient.Client()
          client.on_connect = on_connect
          client.on_message = on_message
          client.connect(mqttServer, int(mqttPort),  int(client_keepalive))
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
                         print("Running...")
                         while 1:
                              if debug:
                                   temp = 25.65
                                   humidity = 35.102
                              else:
                                   system("clear")
                                   temp = sensor.read_temperature()
                                   humidity = sensor.read_humidity(temp)
                                   sensor.calculate_dew_point(temp, humidity)
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

               # Blocking call that processes network traffic, dispatches callbacks and
               # handles reconnecting.
               # Other loop*() functions are available that give a threaded interface and a
               # manual interface.
               #client.loop_forever()

               print("Closing connection..")

main()
