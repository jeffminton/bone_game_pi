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
from bonegame import BoneGame

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

    logging.info("Starting Bone Game")

    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    logging.info ('Press Ctrl-C to quit.')
    if not args.clear:
        logging.info('Use "-c" argument to clear LEDs on exit')

    bone_game = BoneGame()

    teensy_heartbeat = False
    teensy_hearbteat_durration = 10000
    teensy_heartbeat_last = bone_game.millis()
    teensy_heartbeat_missed_count = 0
    teensy_heartbeat_missed_count_max = 3

    bone_game.restart_teensy()

    # Ensure the teensy has time to restart
    time.sleep(10)

    bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

    # DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    # DEVICE_REG_MODE1 = 0x00
    # DEVICE_REG_LEDOUT0 = 0x1d
    
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/beeps.wav')

    bone_game.reset_game()

    # selected_bone = None
    # selected_bone_name = None
    # first_choice_time = None

    bone_game.set_button_test_on()

    try:
        while 1:
            if teensy_heartbeat_last + teensy_hearbteat_durration <= bone_game.millis():
                teensy_heartbeat_last = bone_game.millis()
                heartbeat = bone_game.get_heartbeat()
                if heartbeat != '1':
                    teensy_heartbeat_missed_count += 1
                    if teensy_heartbeat_missed_count > teensy_heartbeat_missed_count_max:
                        logging.info('NO Heartbeat returned, restarting')
                        bone_game.restart_teensy()
                        time.sleep(1)
                        bone_game.reset_game()
                else:
                    logging.info('Heartbeat returned')
            # #Wait until the user chooses a bone
            # if bone_game.selected_bone() == None:
            #     bone_game.heartbeat_log('Waiting for bone selection', logging.debug)
            #     bone_game.get_letter('selected_bone')
            #     if(bone_game.selected_bone() not in letter_led_map.keys()):
            #         bone_game.reset_selected_bone()
            #     elif(bone_game.selected_bone() in letter_led_map.keys()):
            #         bone_game.set_first_choice_time()
            #         logging.debug('Selected Bone: %s' % (bone_game.selected_bone()))
            #         bone_game.clear_strip_set_led(letter_led_map[bone_game.selected_bone()], red)

            bone_game.get_buttons()
            logging.debug('Buttons: %s' % (str(bone_game.get_button_states())))
            for key in bone_game.get_button_states().keys():
                logging.debug('Key: %s' % (str(key)))
                if bone_game.get_button_states()[key] == True:
                    bone_game.set_led(BoneGame.LETTER_LED_MAP[bone_game.get_button_states()[key]], red)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if args.clear:
            bone_game.clear_strip()
        bone_game.set_button_test_off()
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

