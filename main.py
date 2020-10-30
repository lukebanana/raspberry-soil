import RPi.GPIO as GPIO
import time
import csv
from pi_sht1x import SHT1x
from os import system

# Gelb = Clock
# Blau = Data
# Rot = Strom
# Green = Ground

DATA_PIN = 24;
SCK_PIN = 23;

def main():
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
                    system("clear");
                    temp = sensor.read_temperature()
                    humidity = sensor.read_humidity(temp)
                    sensor.calculate_dew_point(temp, humidity)
                    print(sensor)
                    #print("{\"temperature\" : %5.2f}" % temp)
                    
                    with open(filename, 'a+') as csvfile:  
                         # creating a csv writer object  
                         csvwriter = csv.writer(csvfile, delimiter=';')  
                         fields = [temp, humidity]  
                         csvwriter.writerow(fields)                           
                    time.sleep(2)
               
          

main();
