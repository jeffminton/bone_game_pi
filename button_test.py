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




letter_led_map = {
    'a': 1, 'b' : 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6,
    'g': 7, 'h' : 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
    'm': 13, 'n' : 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18,
    's': 19, 't' : 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24,
    'A': 25, 'B' : 26, 'C': 27, 'D': 28, 'E': 29, 'F': 30,
    'G': 31, 'H' : 32, 'I': 33, 'J': 34, 'K': 35, 'L': 36,
    'M': 37, 'N' : 38, 'O': 39, 'P': 40, 'Q': 41, 'R': 42,
    'S': 43, 'T' : 44, 'U': 45, 'V': 46, 'W': 47, 'X': 48
}



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


# class Commands(IntEnum):
#     set_led = 0
#     clear_then_set_led = 1
#     clear_strip = 2
#     set_multiple_leds = 3
#     reset_game = 4
#     led_test = 5
#     set_button_test_on = 6
#     set_button_test_off = 7
#     reset_teensy = 8
#     heartbeat = 9


# class Heartbeat():
#     def __init__(self):
        


#     def millis(self):
#         return int(round(time.time() * 1000))

#     def heartbeat_log(self, log_msg, debug_level):
#         # debug_level('millis: %s, on at: %s, off at: %s' % (str(self.millis()), str(self.heartbeat_on_at), str(self.heartbeat_off_at)))
#         if self.heartbeat_on_at == None:
#             debug_level('Heartbeat is None')
#             self.heartbeat_on_at = self.millis() + self.heartbeat_interval
#             self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
#         if self.millis() >= self.heartbeat_off_at:
#             self.heartbeat = False
#             self.heartbeat_on_at = self.millis() + self.heartbeat_interval
#             self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
#             # debug_level('heartbeat off')
#         elif self.millis() >= self.heartbeat_on_at:
#             # debug_level('heartbeat on')
#             self.heartbeat = True
#             debug_level(log_msg)



# class BoneGame():

#     DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
#     DEVICE_REG_MODE1 = 0x00
#     DEVICE_REG_LEDOUT0 = 0x1d
#     #milliseconds to wait for a second input
#     GAME_TIMEOUT = 360000

#     def __init__(self):
#         self.heartbeat_interval = 2000
#         self.heartbeat_durration = 50
#         self.heartbeat = False
#         self.heartbeat_on_at = None
#         self.heartbeat_off_at = None
#         self.selections = {
#             'selected_bone': None,
#             'selected_bone_name': None        
#         }
#         self.first_choice_time = None

#         # self.game_heartbeat = game_heartbeat

#         self.button_states = {
#             'a': False, 'b' : False, 'c': False, 'd': False, 'e': False, 'f': False,
#             'g': False, 'h' : False, 'i': False, 'j': False, 'k': False, 'l': False,
#             'm': False, 'n' : False, 'o': False, 'p': False, 'q': False, 'r': False,
#             's': False, 't' : False, 'u': False, 'v': False, 'w': False, 'x': False,
#             'A': False, 'B' : False, 'C': False, 'D': False, 'E': False, 'F': False,
#             'G': False, 'H' : False, 'I': False, 'J': False, 'K': False, 'L': False,
#             'M': False, 'N' : False, 'O': False, 'P': False, 'Q': False, 'R': False,
#             'S': False, 'T' : False, 'U': False, 'V': False, 'W': False, 'X': False
#         }

#         wiringpi.wiringPiSetup()
#         wiringpi.pinMode(arduino_gnd_pin, wiringpi.OUTPUT)
#         wiringpi.pinMode(arduino_rst_pin, wiringpi.OUTPUT)

#     def get_button_states(self):
#         return self.button_states

#     def clear_button_states(self):
#         for key in self.button_states.keys():
#             self.button_states[key] = False

#     def set_first_choice_time(self):
#         self.first_choice_time = self.millis()

#     def selected_bone(self):
#         return self.selections['selected_bone']

#     def reset_selected_bone(self):
#         self.selections['selected_bone'] = None

#     def selected_bone_name(self):
#         return self.selections['selected_bone_name']

#     def reset_selected_bone_name(self):
#         self.selections['selected_bone_name'] = None

#     def restart_teensy(self):
#         logging.info(self.restart_teensy.__name__)
#         wiringpi.digitalWrite(arduino_rst_pin, wiringpi.LOW)

#         wiringpi.digitalWrite(arduino_gnd_pin, wiringpi.LOW)
#         time.sleep(1)
#         wiringpi.digitalWrite(arduino_gnd_pin, wiringpi.HIGH)


#     def write_data(self, data):
#         retry_max = 10
#         retry_count = 0

#         # logging.debug( 'Write data: %s' % (data) )

#         while( retry_count < retry_max ):
#             try:
#                 res = bus.write_block_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1, data)
#                 return res
#             except OSError:
#                 # logging.debug( 'Retry: %s' % (data) )
#                 retry_count += 1



#     def read_data(self):
#         retry_max = 10
#         retry_count = 0

#         self.heartbeat_log( 'read_data', logging.debug )

#         while( retry_count < retry_max ):
#             try:
#                 self.heartbeat_log( 'get_letter', logging.debug )
#                 res = bus.read_byte_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1)
#                 return res
#             except OSError:
#                 self.heartbeat_log( 'Retry read_data', logging.debug )
#                 retry_count += 1



#     def clear_strip(self):
#         logging.info(self.clear_strip.__name__)
#         data = [int(Commands.clear_strip)]
#         res = self.write_data(data)
#         # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


#     def clear_strip_set_led(self, led_num, color):
#         logging.info(self.clear_strip_set_led.__name__)
#         data = [int(Commands.clear_then_set_led)]
#         data.append(led_num)
#         data.extend(color)
#         res = self.write_data(data)
#         # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

#     def set_led(self, led_num, color):
#         logging.info(self.set_led.__name__)
#         data = [int(Commands.set_led)]
#         data.append(led_num)
#         data.extend(color)
#         res = self.write_data(data)
#         # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


#     def reset_game(self):
#         logging.info(self.reset_game.__name__)
#         data = [int(Commands.reset_game)]
#         res = self.write_data(data)
#         self.reset_selected_bone()
#         self.reset_selected_bone_name()


#     def get_letter(self, selection_name):
#         button = None
#         retry_max = 10
#         retry_count = 0
#         while(button not in letter_led_map.keys() and retry_count < retry_max):
#             self.heartbeat_log( 'get_letter', logging.debug )
#             try:
#                 button = chr(self.read_data())
#                 self.heartbeat_log( 'get_letter: %s' % (str(button)), logging.debug )
#             except TypeError:
#                 button = None
#             retry_count += 1
#         self.selections[selection_name] = button

#     def get_buttons(self):
#         button = ''
#         retry_max = 10
#         retry_count = 0
#         while(button != '0'):
#             while((button not in letter_led_map.keys() or button != '0') and retry_count < retry_max):
#                 self.heartbeat_log( 'get_buttons', logging.debug )
#                 try:
#                     button = chr(self.read_data())
#                     self.heartbeat_log( 'get_buttons: %s' % (str(button)), logging.debug )
#                 except TypeError:
#                     button = None
#                 retry_count += 1
#             self.button_states[button] = True


#     def get_heartbeat(self):

#         data = [int(Commands.heartbeat)]
#         res = self.write_data(data)
#         try:
#             return chr(self.read_data())
#         except TypeError:
#             return '0'


#     def millis(self):
#         return int(round(time.time() * 1000))

#     def heartbeat_log(self, log_msg, debug_level):
#         # debug_level('millis: %s, on at: %s, off at: %s' % (str(self.millis()), str(self.heartbeat_on_at), str(self.heartbeat_off_at)))
#         if self.heartbeat_on_at == None:
#             debug_level('Heartbeat is None')
#             self.heartbeat_on_at = self.millis() + self.heartbeat_interval
#             self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
#         if self.millis() >= self.heartbeat_off_at:
#             self.heartbeat = False
#             self.heartbeat_on_at = self.millis() + self.heartbeat_interval
#             self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
#             # debug_level('heartbeat off')
#         elif self.millis() >= self.heartbeat_on_at:
#             # debug_level('heartbeat on')
#             self.heartbeat = True
#             debug_level(log_msg)




# bone_heartbeat = Heartbeat()


red = [255, 0, 0]
green = [0, 255, 0]


# Main program logic follows:
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/bone_game_pi.log',level=logging.DEBUG)

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
            #Wait until the user chooses a bone
            if bone_game.selected_bone() == None:
                bone_game.heartbeat_log('Waiting for bone selection', logging.debug)
                bone_game.get_letter('selected_bone')
                if(bone_game.selected_bone() not in letter_led_map.keys()):
                    bone_game.reset_selected_bone()
                elif(bone_game.selected_bone() in letter_led_map.keys()):
                    bone_game.set_first_choice_time()
                    logging.debug('Selected Bone: %s' % (bone_game.selected_bone()))
                    bone_game.clear_strip_set_led(letter_led_map[bone_game.selected_bone()], red)

            bone_game.get_buttons()
            for key in bone_game.get_button_states().keys():
                if bone_game.get_button_states()[key] == True:
                    bone_game.set_led(letter_led_map[bone_game.get_button_states()[key]], red)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if args.clear:
            bone_game.clear_strip()
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

