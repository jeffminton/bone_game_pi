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


heartbeat = False
heartbeat_on_at = None
heartbeat_off_at = None



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

    # teensy_heartbeat = False
    # teensy_hearbteat_durration = 10000
    # teensy_heartbeat_last = bone_game.millis()
    # teensy_heartbeat_missed_count = 0
    # teensy_heartbeat_missed_count_max = 3

    heartbeat = Heartbeat(bone_game, durration = 10000, missed_count_max = 3)

    bone_game.run_led_test()

    time.sleep(5)

    bone_game.reset_game()
    
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/beeps.wav')

    bone_game.set_button_test_off()

    try:
        while 1:
            # if teensy_heartbeat_last + teensy_hearbteat_durration <= bone_game.millis():
            #     teensy_heartbeat_last = bone_game.millis()
            #     heartbeat = bone_game.get_heartbeat()
            #     if heartbeat != '1':
            #         teensy_heartbeat_missed_count += 1
            #         logging.info('NO Heartbeat returned, Fail count %d' % (teensy_heartbeat_missed_count))
            #         if teensy_heartbeat_missed_count > teensy_heartbeat_missed_count_max:
            #             logging.info('NO Heartbeat returned, restarting')
            #             bone_game.restart_teensy()
            #             time.sleep(1)
            #             bone_game.reset_game()
            #             teensy_heartbeat_missed_count = 0
            #     else:
            #         logging.info('Heartbeat returned')
            #Wait until the user chooses a bone
            heartbeat.get_heartbeat()
            if bone_game.selected_bone() == None:
                bone_game.heartbeat_log('Waiting for bone selection', logging.debug)
                bone_game.get_letter('selected_bone')
                if(bone_game.selected_bone() not in bone_game.LETTER_LED_MAP.keys()):
                    bone_game.reset_selected_bone()
                elif(bone_game.selected_bone() in bone_game.LETTER_LED_MAP.keys()):
                    if(bone_game.selected_bone() in answer_key.keys()):
                        bone_game.set_first_choice_time()
                        logging.debug('Selected Bone: %s' % (bone_game.selected_bone()))
                        bone_game.clear_strip_set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone()], red)
                    else:
                        logging.debug('Did not get a propber bone selection. Selection was %s. Resetting Game' % (bone_game.selected_bone()))
                        bone_game.reset_game()

            #Wait until the user chooses a bone name
            if bone_game.selected_bone() != None and bone_game.selected_bone_name() == None:
                #Check is the timeout to reset has been reached
                if bone_game.millis() >= bone_game.first_choice_time + bone_game.GAME_TIMEOUT:
                    logging.debug('Timeout reached. Restart Game')
                    bone_game.reset_game()
                bone_game.heartbeat_log('Waiting for bone name selection', logging.debug)
                bone_game.get_letter('selected_bone_name')
                if(bone_game.selected_bone_name() not in bone_game.LETTER_LED_MAP.keys()):
                    bone_game.reset_selected_bone_name()
                elif(bone_game.selected_bone_name() in bone_game.LETTER_LED_MAP.keys()):
                    logging.debug('Selected Bone Name: %s' % (bone_game.selected_bone_name()))
                    bone_game.set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone_name()], green)
            
            if bone_game.selected_bone() != None and bone_game.selected_bone_name() != None:
                # time.sleep(5)
                logging.info('Selections chosen. play song')
                pygame.mixer.music.play()

                start_time = time.time()
                current_cue = 0
                while pygame.mixer.music.get_busy() == True and current_cue < len(sound_cues):
                    if time.time() - start_time >= sound_cues[current_cue]:
                        bone_game.clear_strip_set_led(random.randint(0, len(bone_game.LETTER_LED_MAP) - 1), color_list[random.randint(0, len(color_list) - 1)])
                        current_cue += 1


                if answer_key[bone_game.selected_bone()] == bone_game.selected_bone_name():
                    bone_game.clear_strip_set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone()], green)
                    bone_game.set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone_name()], green)
                    #Play correct sound
                else:
                    bone_game.clear_strip_set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone()], green)
                    bone_game.set_led(bone_game.LETTER_LED_MAP[bone_game.selected_bone_name()], red)
                    bone_game.set_led(bone_game.LETTER_LED_MAP[answer_key[bone_game.selected_bone()]], green)
                    #play wrong sound

                bone_game.reset_game()
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if args.clear:
            bone_game.clear_strip()
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

