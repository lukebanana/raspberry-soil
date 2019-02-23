import RPi.GPIO as GPIO

from pi_sht1x import SHT1x


def main():
     print("start");
     with SHT1x(18, 23, gpio_mode=GPIO.BCM) as sensor:
         temp = sensor.read_temperature()
         humidity = sensor.read_humidity(temp)
         sensor.calculate_dew_point(temp, humidity)
         print(sensor)


main();
