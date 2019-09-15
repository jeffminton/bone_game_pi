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
import logging



# Main program logic follows:
if __name__ == '__main__':
    
    pygame.mixer.init()
    
    pygame.mixer.music.load('sounds/beeps.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        pass

    pygame.mixer.music.load('sounds/correct.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        pass

    pygame.mixer.music.load('sounds/wrong.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        pass
