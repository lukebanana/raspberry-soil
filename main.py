import RPi.GPIO as GPIO
import time
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
          while 1:
               system("clear");
               temp = sensor.read_temperature()
               humidity = sensor.read_humidity(temp)
               sensor.calculate_dew_point(temp, humidity)
               print(sensor)
               time.sleep(2)
               
          


main();
