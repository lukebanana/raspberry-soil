import RPi.GPIO as GPIO
import time
import csv
from pi_sht1x import SHT1x
from configparser import ConfigParser
from os import system
import paho.mqtt.client as mqttClient
import paho.mqtt.publish as publish

# Gelb = Clock
# Blau = Data
# Rot = Strom
# Green = Ground

DATA_PIN = 24;
SCK_PIN = 23;

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def main():
     config_object = ConfigParser()
     config_object.read("config.ini")

     #Get the password
     serverConf = config_object["SERVER_CONFIG"]
     mqttServer = serverConf["MQTT_SERVER"];
     if mqttServer:
          print("Using MQTT server {}".format(serverConf["MQTT_SERVER"]))
          print("Channel: {}".format(serverConf["MQTT_PATH"]))

          #client = mqttClient.Client()
          #client.on_connect = on_connect
          #client.on_message = on_message
          #client.connect(MQTT_SERVER, 1883, 60)
          
          # Blocking call that processes network traffic, dispatches callbacks and
          # handles reconnecting.
          # Other loop*() functions are available that give a threaded interface and a
          # manual interface.
          #client.loop_forever()

          with SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM) as sensor:
               # field names  
               fields = ['Temp', 'Humidity']  
          
               # name of csv file  
               filename = "measurements.csv"
               
               # writing to csv file  
               with open(filename, 'a+') as csvfile:  
                    # creating a csv writer object  
                    csvwriter = csv.writer(csvfile, delimiter=';')  
                    
                    # writing the fields  
                    csvwriter.writerow(fields)  
                    
               
                    while 1:
                         #system("clear");
                         temp = sensor.read_temperature()
                         humidity = sensor.read_humidity(temp)
                         sensor.calculate_dew_point(temp, humidity)
                         print(sensor)
                         #print("{\"temperature\" : %5.2f}" % temp)

                         # MQTT Publsih
                         #publish.single(MQTT_PATH, "Testicle", hostname=MQTT_SERVER)

                         with open(filename, 'a+') as csvfile:  
                              # creating a csv writer object  
                              csvwriter = csv.writer(csvfile, delimiter=';')  
                              fields = [temp, humidity]  
                              csvwriter.writerow(fields)                           
                              time.sleep(5)


               

          client.disconntect()
          print("Closing connection..")
main();
