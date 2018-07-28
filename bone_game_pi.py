# External module imports
# import RPi.GPIO as GPIO
import time
from sys import stdin, stdout
# from neopixel import *
import argparse

# Pin Definitons:
# pwmPin = 23 # Broadcom pin 18 (P1 pin 12)
# ledPin = 18 # Broadcom pin 23 (P1 pin 16)
# butPin = 17 # Broadcom pin 17 (P1 pin 11)

# dc = 95 # duty cycle (0-100) for PWM pin

# # Pin Setup:
# GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
# GPIO.setup(ledPin, GPIO.OUT) # LED pin set as output
# GPIO.setup(pwmPin, GPIO.OUT) # PWM pin set as output
# pwm = GPIO.PWM(pwmPin, 50)  # Initialize PWM on pwmPin 100Hz frequency
# GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up

# # Initial state for LEDs:
# GPIO.output(ledPin, GPIO.LOW)
# pwm.start(dc)

# # LED strip configuration:
# LED_COUNT   = 48      # Number of LED pixels.
# LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
# LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
# LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
# LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)


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


letter_led_map = {
    'a': 1, 'b' : 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6,
    'g': 7, 'h' : 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
    'A': 13, 'B' : 14, 'C': 15, 'D': 16, 'E': 17, 'F': 18,
    'G': 19, 'H' : 20, 'I': 21, 'J': 22, 'K': 23, 'L': 24
    
}

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # # Create NeoPixel object with appropriate configuration.
    # strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # # Intialize the library (must be called once before other functions).
    # strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while 1:
            print 'start loop'
            selected_bone = stdin.readline()[:-1]
            print selected_bone
            # strip.setPixelColor(letter_led_map[selected_bone], color)
            selected_bone_name = stdin.readline()[:-1]
            print selected_bone_name
            # strip.setPixelColor(letter_led_map[selected_bone_name], color)
            # GPIO.output(ledPin, GPIO.HIGH)
            # time.sleep(1)
            # GPIO.output(ledPin, GPIO.LOW)
            # time.sleep(1)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        pass
        # pwm.stop() # stop PWM
        # GPIO.cleanup() # cleanup all GPIO

