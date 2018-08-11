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
from enum import IntEnum

arduino_rst_pin = 5

# Main program logic follows:
if __name__ == '__main__':

    wiringpi.wiringPiSetup()

    wiringpi.pinMode(arduino_rst_pin, wiringpi.OUTPUT)

    wiringpi.digitalWrite(arduino_rst_pin, wiringpi.HIGH)
    time.sleep(.01)
    wiringpi.digitalWrite(arduino_rst_pin, wiringpi.LOW)
    