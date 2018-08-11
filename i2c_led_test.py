# External module imports
# import RPi.GPIO as GPIO
import time
from sys import stdin, stdout
# from neopixel import *
import argparse
import pygame
import serial
import random
import wiringpi
import os

import smbus



# Main program logic follows:
if __name__ == '__main__':

    fd = wiringpi.wiringPiI2CSetup(0x8)

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

        DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
        DEVICE_REG_MODE1 = 0x00
        DEVICE_REG_LEDOUT0 = 0x1d

        #Write a single register
        # bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x80)

        #Write an array of registers
        # ledout_values = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
        # bus.write_i2c_block_data(DEVICE_ADDRESS, DEVICE_REG_LEDOUT0, ledout_values)

        data = [0, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        data[0] = 1
        res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
        time.sleep(.001)

        data = [0, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        data[0] = 4
        res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
        time.sleep(.001)

        data = [0, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        data[0] = 6
        res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
        time.sleep(.001)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

