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


arduino_vcc_pin = 1
arduino_gnd_pin = 4
arduino_rst_pin = 5

heartbeat = False
heartbeat_on_at = None
heartbeat_off_at = None

#milliseconds to wait for a second input
GAME_TIMEOUT = 360000


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


# letter_led_map = {
#     'a': 0, 'b' : 1, 'c': 2, 'd': 3,
#     'A': 4, 'B' : 5, 'C': 6, 'D': 7
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


class Commands(IntEnum):
    set_led = 0
    clear_then_set_led = 1
    clear_strip = 2
    set_multiple_leds = 3
    reset_game = 4
    led_test = 5
    set_button_test_on = 6
    set_button_test_off = 7
    reset_teensy = 8
    heartbeat = 9


class Heartbeat():
    def __init__(self):
        self.heartbeat_interval = 2000
        self.heartbeat_durration = 50
        self.heartbeat = False
        self.heartbeat_on_at = None
        self.heartbeat_off_at = None


    def millis(self):
        return int(round(time.time() * 1000))

    def heartbeat_log(self, log_msg, debug_level):
        # debug_level('millis: %s, on at: %s, off at: %s' % (str(self.millis()), str(self.heartbeat_on_at), str(self.heartbeat_off_at)))
        if self.heartbeat_on_at == None:
            debug_level('Heartbeat is None')
            self.heartbeat_on_at = self.millis() + self.heartbeat_interval
            self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
        if self.millis() >= self.heartbeat_off_at:
            self.heartbeat = False
            self.heartbeat_on_at = self.millis() + self.heartbeat_interval
            self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
            # debug_level('heartbeat off')
        elif self.millis() >= self.heartbeat_on_at:
            # debug_level('heartbeat on')
            self.heartbeat = True
            debug_level(log_msg)


bone_heartbeat = Heartbeat()


red = [255, 0, 0]
green = [0, 255, 0]

# # Define functions which animate LEDs in various ways.
# def clear_strip(strip):
#     """Wipe color across display a pixel at a time."""
#     color = Color(0, 0, 0)
#     for i in range(strip.numPixels()):
#         strip.setPixelColor(i, color)
#     strip.show()




def restart_teensy():
    logging.info(restart_teensy.__name__)
    wiringpi.digitalWrite(arduino_rst_pin, wiringpi.LOW)

    wiringpi.digitalWrite(arduino_gnd_pin, wiringpi.LOW)
    time.sleep(1)
    wiringpi.digitalWrite(arduino_gnd_pin, wiringpi.HIGH)


def write_data(data):
    retry_max = 10
    retry_count = 0

    # logging.debug( 'Write data: %s' % (data) )

    while( retry_count < retry_max ):
        try:
            res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
            return res
        except OSError:
            # logging.debug( 'Retry: %s' % (data) )
            retry_count += 1



def read_data():
    retry_max = 10
    retry_count = 0

    bone_heartbeat.heartbeat_log( 'read_data', logging.debug )

    while( retry_count < retry_max ):
        try:
            bone_heartbeat.heartbeat_log( 'get_letter', logging.debug )
            res = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1)
            return res
        except OSError:
            bone_heartbeat.heartbeat_log( 'Retry read_data', logging.debug )
            retry_count += 1



def clear_strip():
    logging.info(clear_strip.__name__)
    data = [int(Commands.clear_strip)]
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


def clear_strip_set_led(led_num, color):
    logging.info(clear_strip_set_led.__name__)
    data = [int(Commands.clear_then_set_led)]
    data.append(led_num)
    data.extend(color)
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

def set_led(led_num, color):
    logging.info(set_led.__name__)
    data = [int(Commands.set_led)]
    data.append(led_num)
    data.extend(color)
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


def reset_game():
    logging.info(reset_game.__name__)
    data = [int(Commands.reset_game)]
    res = write_data(data)


def get_letter():
    button = ''
    retry_max = 10
    retry_count = 0
    while(button not in letter_led_map.keys() and retry_count < retry_max):
        bone_heartbeat.heartbeat_log( 'get_letter', logging.debug )
        try:
            button = chr(read_data())
            bone_heartbeat.heartbeat_log( 'get_letter: %s' % (str(button)), logging.debug )
        except TypeError:
            button = '0'
        retry_count += 1
    return button


def get_heartbeat():

    data = [int(Commands.heartbeat)]
    res = write_data(data)
    try:
        return chr(read_data())
    except TypeError:
        return '0'




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

    teensy_heartbeat = False
    teensy_hearbteat_durration = 10000
    teensy_heartbeat_last = bone_heartbeat.millis()
    teensy_heartbeat_missed_count = 0
    teensy_heartbeat_missed_count_max = 3


    wiringpi.wiringPiSetup()

    wiringpi.pinMode(arduino_gnd_pin, wiringpi.OUTPUT)
    wiringpi.pinMode(arduino_rst_pin, wiringpi.OUTPUT)

    restart_teensy()

    # Ensure the teensy has time to restart
    time.sleep(10)

    bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

    DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    DEVICE_REG_MODE1 = 0x00
    DEVICE_REG_LEDOUT0 = 0x1d
    
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/beeps.wav')

    reset_game()

    selected_bone = None
    selected_bone_name = None
    first_choice_time = None

    try:
        while 1:
            if teensy_heartbeat_last + teensy_hearbteat_durration <= bone_heartbeat.millis():
                teensy_heartbeat_last = bone_heartbeat.millis()
                heartbeat = get_heartbeat()
                if heartbeat != '1':
                    teensy_heartbeat_missed_count += 1
                    if teensy_heartbeat_missed_count > teensy_heartbeat_missed_count_max:
                        logging.info('NO Heartbeat returned, restarting')
                        restart_teensy()
                        time.sleep(1)
                        reset_game()
                else:
                    logging.info('Heartbeat returned')
            #Wait until the user chooses a bone
            if selected_bone == None:
                bone_heartbeat.heartbeat_log('Waiting for bone selection', logging.debug)
                selected_bone = get_letter()
                if(selected_bone not in letter_led_map.keys()):
                    selected_bone = None
                elif(selected_bone in letter_led_map.keys()):
                    first_choice_time = bone_heartbeat.millis()
                    logging.debug('Selected Bone: %s' % (selected_bone))
                    clear_strip_set_led(letter_led_map[selected_bone], red)

            #Wait until the user chooses a bone name
            if selected_bone != None and selected_bone_name == None:
                #Check is the timeout to reset has been reached
                if bone_heartbeat.millis() >= first_choice_time + GAME_TIMEOUT:
                    logging.debug('Timeout reached. Restart Game')
                    selected_bone = None
                    reset_game()
                bone_heartbeat.heartbeat_log('Waiting for bone name selection', logging.debug)
                selected_bone_name = get_letter()
                if(selected_bone_name not in letter_led_map.keys()):
                    selected_bone_name = None
                elif(selected_bone_name in letter_led_map.keys()):
                    logging.debug('Selected Bone Name: %s' % (selected_bone_name))
                    set_led(letter_led_map[selected_bone_name], green)
            
            if selected_bone != None and selected_bone_name != None:
                # time.sleep(5)
                logging.info('Selections chosen. play song')
                pygame.mixer.music.play()

                start_time = time.time()
                current_cue = 0
                while pygame.mixer.music.get_busy() == True and current_cue < len(sound_cues):
                    if time.time() - start_time >= sound_cues[current_cue]:
                        clear_strip_set_led(random.randint(0, len(letter_led_map) - 1), color_list[random.randint(0, len(color_list) - 1)])
                        current_cue += 1


                if answer_key[selected_bone] == selected_bone_name:
                    clear_strip_set_led(letter_led_map[selected_bone], green)
                    set_led(letter_led_map[selected_bone_name], green)
                    #Play correct sound
                else:
                    clear_strip_set_led(letter_led_map[selected_bone], green)
                    set_led(letter_led_map[selected_bone_name], red)
                    set_led(letter_led_map[answer_key[selected_bone]], green)
                    #play wrong sound

                selected_bone = None
                selected_bone_name = None
                reset_game()
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if args.clear:
            clear_strip()
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

