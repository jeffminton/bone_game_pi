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
from bonegame import BoneGame, Heartbeat
import pprint

# arduino_vcc_pin = 1
# arduino_gnd_pin = 4
# arduino_rst_pin = 5

heartbeat = False
heartbeat_on_at = None
heartbeat_off_at = None




# letter_led_map = {
#     'a': 1, 'b' : 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6,
#     'g': 7, 'h' : 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
#     'm': 13, 'n' : 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18,
#     's': 19, 't' : 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24,
#     'A': 25, 'B' : 26, 'C': 27, 'D': 28, 'E': 29, 'F': 30,
#     'G': 31, 'H' : 32, 'I': 33, 'J': 34, 'K': 35, 'L': 36,
#     'M': 37, 'N' : 38, 'O': 39, 'P': 40, 'Q': 41, 'R': 42,
#     'S': 43, 'T' : 44, 'U': 45, 'V': 46, 'W': 47, 'X': 48
# }



answer_key = {
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F',
    'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L',
    'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R',
    's': 'S', 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X'
}


sound_cues = [
    0.061, 0.198, 0.338, 0.494, 0.645,
    0.795, 0.938, 1.075, 1.218, 1.371,
    1.522, 1.672, 1.810, 1.950, 2.095,
    2.246, 2.399, 2.615, 2.895, 3.051,
    3.197, 3.347
]


color_list = [
    [0, 255, 17], [255, 17, 0], 
    [16, 0, 244], [119, 255, 0], 
    [255, 0, 119], [0, 116, 248], 
    [255, 230, 0], [230, 0, 255], 
    [0, 251, 226], [255, 115, 0],
    [115, 0, 255], [0, 251, 113]
]



red = [255, 0, 0]
green = [0, 255, 0]


# Main program logic follows:
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/button_test.log',level=logging.DEBUG)

    print("Starting Button Test")
    logging.info("Starting Button Test")

    # Process arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    # args = parser.parse_args()

    # print ('Press Ctrl-C to quit.')
    # logging.info ('Press Ctrl-C to quit.')
    # if not args.clear:
    #     print('Use "-c" argument to clear LEDs on exit')
    #     logging.info('Use "-c" argument to clear LEDs on exit')

    bone_game = BoneGame(debug = False)

    heartbeat = Heartbeat(bone_game, durration = 10000, missed_count_max = 3)

    bone_game.restart_teensy()

    bone_game.run_led_test()

    time.sleep(5)

    bone_game.reset_game()
    
    bone_game.set_button_test_on()

    try:
        while 1:
            result = heartbeat.get_heartbeat()
            if result == -1:
                bone_game.set_button_test_on()
            letter = bone_game.get_letter_test()
            if letter in bone_game.get_button_states().keys() and bone_game.get_button_states()[letter] == True:
                bone_game.heartbeat_log('Key: %s' % (str(letter)), logging.debug, True)
                bone_game.set_led(BoneGame.LETTER_LED_MAP[letter], red)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        bone_game.reset_game()
        pass

