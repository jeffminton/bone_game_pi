
import wiringpi
import smbus
import logging
from enum import IntEnum
import time


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


class BoneGame():

    DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    DEVICE_REG_MODE1 = 0x00
    DEVICE_REG_LEDOUT0 = 0x1d
    #milliseconds to wait for a second input
    GAME_TIMEOUT = 360000

    ARDUINO_VCC_PIN = 1
    ARDUINO_GND_PIN = 4
    ARDUINO_RST_PIN = 5

    LETTER_LED_MAP = {
        'a': 1, 'b' : 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6,
        'g': 7, 'h' : 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
        'm': 13, 'n' : 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18,
        's': 19, 't' : 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24,
        'A': 25, 'B' : 26, 'C': 27, 'D': 28, 'E': 29, 'F': 30,
        'G': 31, 'H' : 32, 'I': 33, 'J': 34, 'K': 35, 'L': 36,
        'M': 37, 'N' : 38, 'O': 39, 'P': 40, 'Q': 41, 'R': 42,
        'S': 43, 'T' : 44, 'U': 45, 'V': 46, 'W': 47, 'X': 48
    }

    def __init__(self):
        self.bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self.heartbeat_interval = 2000
        self.heartbeat_durration = 50
        self.heartbeat = False
        self.heartbeat_on_at = None
        self.heartbeat_off_at = None
        self.selections = {
            'selected_bone': None,
            'selected_bone_name': None        
        }
        self.first_choice_time = None

        # self.game_heartbeat = game_heartbeat

        self.button_states = {
            'a': False, 'b' : False, 'c': False, 'd': False, 'e': False, 'f': False,
            'g': False, 'h' : False, 'i': False, 'j': False, 'k': False, 'l': False,
            'm': False, 'n' : False, 'o': False, 'p': False, 'q': False, 'r': False,
            's': False, 't' : False, 'u': False, 'v': False, 'w': False, 'x': False,
            'A': False, 'B' : False, 'C': False, 'D': False, 'E': False, 'F': False,
            'G': False, 'H' : False, 'I': False, 'J': False, 'K': False, 'L': False,
            'M': False, 'N' : False, 'O': False, 'P': False, 'Q': False, 'R': False,
            'S': False, 'T' : False, 'U': False, 'V': False, 'W': False, 'X': False
        }

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(BoneGame.ARDUINO_GND_PIN, wiringpi.OUTPUT)
        wiringpi.pinMode(BoneGame.ARDUINO_RST_PIN, wiringpi.OUTPUT)


    def get_button_states(self):
        return self.button_states

    def clear_button_states(self):
        for key in self.button_states.keys():
            self.button_states[key] = False

    def set_first_choice_time(self):
        self.first_choice_time = self.millis()

    def selected_bone(self):
        return self.selections['selected_bone']

    def reset_selected_bone(self):
        self.selections['selected_bone'] = None

    def selected_bone_name(self):
        return self.selections['selected_bone_name']

    def reset_selected_bone_name(self):
        self.selections['selected_bone_name'] = None

    def restart_teensy(self):
        logging.info(self.restart_teensy.__name__)
        wiringpi.digitalWrite(BoneGame.ARDUINO_RST_PIN, wiringpi.LOW)

        wiringpi.digitalWrite(BoneGame.ARDUINO_GND_PIN, wiringpi.LOW)
        time.sleep(1)
        wiringpi.digitalWrite(BoneGame.ARDUINO_GND_PIN, wiringpi.HIGH)


    def write_data(self, data):
        retry_max = 10
        retry_count = 0

        # logging.debug( 'Write data: %s' % (data) )

        while( retry_count < retry_max ):
            try:
                res = self.bus.write_block_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1, data)
                return res
            except OSError:
                # logging.debug( 'Retry: %s' % (data) )
                retry_count += 1



    def read_data(self):
        retry_max = 10
        retry_count = 0

        self.heartbeat_log( 'read_data', logging.debug )

        while( retry_count < retry_max ):
            try:
                self.heartbeat_log( 'get_letter', logging.debug )
                res = self.bus.read_byte_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1)
                return res
            except OSError:
                self.heartbeat_log( 'Retry read_data', logging.debug )
                retry_count += 1



    def clear_strip(self):
        logging.info(self.clear_strip.__name__)
        data = [int(Commands.clear_strip)]
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


    def clear_strip_set_led(self, led_num, color):
        logging.info(self.clear_strip_set_led.__name__)
        data = [int(Commands.clear_then_set_led)]
        data.append(led_num)
        data.extend(color)
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

    def set_led(self, led_num, color):
        logging.info(self.set_led.__name__)
        data = [int(Commands.set_led)]
        data.append(led_num)
        data.extend(color)
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


    def reset_game(self):
        logging.info(self.reset_game.__name__)
        data = [int(Commands.reset_game)]
        res = self.write_data(data)
        self.reset_selected_bone()
        self.reset_selected_bone_name()


    def get_letter(self, selection_name):
        button = None
        retry_max = 10
        retry_count = 0
        while(button not in BoneGame.LETTER_LED_MAP.keys() and retry_count < retry_max):
            self.heartbeat_log( 'get_letter', logging.debug )
            try:
                button = chr(self.read_data())
                self.heartbeat_log( 'get_letter: %s' % (str(button)), logging.debug )
            except TypeError:
                button = None
            retry_count += 1
        self.selections[selection_name] = button

    def get_buttons(self):
        button = ''
        retry_max = 10
        retry_count = 0
        while(button != '0'):
            while((button not in BoneGame.LETTER_LED_MAP.keys() or button != '0') and retry_count < retry_max):
                self.heartbeat_log( 'get_buttons', logging.debug )
                try:
                    button = chr(self.read_data())
                    self.heartbeat_log( 'get_buttons: %s' % (str(button)), logging.debug )
                except TypeError:
                    button = None
                retry_count += 1
            self.button_states[button] = True


    def get_heartbeat(self):

        data = [int(Commands.heartbeat)]
        res = self.write_data(data)
        try:
            return chr(self.read_data())
        except TypeError:
            return '0'


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
