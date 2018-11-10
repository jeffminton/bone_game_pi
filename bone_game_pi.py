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


arduino_vcc_pin = 1
arduino_gnd_pin = 4
arduino_rst_pin = 5


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
    wiringpi.digitalWrite(arduino_gnd_pin. wiringpi.LOW)
    time.sleep(1)
    wiringpi.digitalWrite(arduino_gnd_pin. wiringpi.HIGH)


def write_data(data):
    retry_max = 10
    retry_count = 0

    print( 'Write data: %s' % (data) )

    while( retry_count < retry_max ):
        try:
            res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
            return res
        except OSError:
            print( 'Retry: %s' % (data) )
            retry_count += 1



def read_data():
    retry_max = 10
    retry_count = 0

    print( 'Read Data' )

    while( retry_count < retry_max ):
        try:
            res = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1)
            return res
        except OSError:
            print( 'Retry Read Data' )
            retry_count += 1



def clear_strip():
    data = [int(Commands.clear_strip)]
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


def clear_strip_set_led(led_num, color):
    data = [int(Commands.clear_then_set_led)]
    data.append(led_num)
    data.extend(color)
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

def set_led(led_num, color):
    data = [int(Commands.set_led)]
    data.append(led_num)
    data.extend(color)
    res = write_data(data)
    # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


def reset_game():
    data = [int(Commands.reset_game)]
    res = write_data(data)


def get_letter():
    button = ''
    while(button not in letter_led_map.keys()):
        button = chr(read_data())
        print( 'Read: %s' % (str(button)))
    return button




# Main program logic follows:
if __name__ == '__main__':

    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    wiringpi.wiringPiSetup()

    wiringpi.pinMode(arduino_gnd_pin, wiringpi.OUTPUT)
    wiringpi.pinMode(arduino_rst_pin, wiringpi.OUTPUT)

    bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

    DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    DEVICE_REG_MODE1 = 0x00
    DEVICE_REG_LEDOUT0 = 0x1d
    
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/beeps.wav')

    reset_game()

    try:
        while 1:
            #Wait until the user chooses a bone
            selected_bone = get_letter()
            print('Selected Bone: %s' % (selected_bone))
            clear_strip_set_led(letter_led_map[selected_bone], red)

            #Waituntil the user chooses a bone name
            selected_bone_name = get_letter()
            print('Selected Bone Name: %s' % (selected_bone_name))
            set_led(letter_led_map[selected_bone_name], green)
            
            # time.sleep(5)

            pygame.mixer.music.play()

            start_time = time.time()
            current_cue = 0
            while pygame.mixer.music.get_busy() == True and current_cue < len(sound_cues):
                if time.time() - start_time >= sound_cues[current_cue]:
                    clear_strip_set_led(random.randint(0, LED_COUNT - 1), color_list[random.randint(0, len(color_list) - 1)])
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

            
            reset_game()
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if args.clear:
            clear_strip()
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

