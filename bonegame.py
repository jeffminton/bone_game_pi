
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
    button_test_on = 6
    button_test_off = 7
    reset_teensy = 8
    heartbeat = 9
    send_log = 10


class BoneGame():

    DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    DEVICE_REG_MODE1 = 0x00
    DEVICE_REG_LEDOUT0 = 0x1d
    #milliseconds to wait for a second input
    GAME_TIMEOUT = 30000

    ARDUINO_VCC_PIN = 1
    ARDUINO_GND_PIN = 4
    ARDUINO_RST_PIN = 5

    LETTER_LED_MAP = {
        'a': 0, 'b' : 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5,
        'g': 6, 'h' : 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11,
        'm': 12, 'n' : 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17,
        's': 18, 't' : 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23,
        'A': 24, 'B' : 25, 'C': 26, 'D': 27, 'E': 28, 'F': 29,
        'G': 30, 'H' : 31, 'I': 32, 'J': 33, 'K': 34, 'L': 35,
        'M': 36, 'N' : 37, 'O': 38, 'P': 39, 'Q': 40, 'R': 41,
        'S': 42, 'T' : 43, 'U': 44, 'V': 45, 'W': 46, 'X': 47
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
        self.led_off = [0, 0, 0]

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

        self.led_states = [self.led_off] * 48
        # {
        #     'a': False, 'b' : False, 'c': False, 'd': False, 'e': False, 'f': False,
        #     'g': False, 'h' : False, 'i': False, 'j': False, 'k': False, 'l': False,
        #     'm': False, 'n' : False, 'o': False, 'p': False, 'q': False, 'r': False,
        #     's': False, 't' : False, 'u': False, 'v': False, 'w': False, 'x': False,
        #     'A': False, 'B' : False, 'C': False, 'D': False, 'E': False, 'F': False,
        #     'G': False, 'H' : False, 'I': False, 'J': False, 'K': False, 'L': False,
        #     'M': False, 'N' : False, 'O': False, 'P': False, 'Q': False, 'R': False,
        #     'S': False, 'T' : False, 'U': False, 'V': False, 'W': False, 'X': False
        # }

        wiringpi.wiringPiSetup()
        wiringpi.pinMode(BoneGame.ARDUINO_GND_PIN, wiringpi.OUTPUT)
        wiringpi.pinMode(BoneGame.ARDUINO_RST_PIN, wiringpi.OUTPUT)

    def colors_equal(self, color_1, color_2):
        for i in range(len(color_1)):
            if color_1[i] != color_2[i]:
                return False
        return True

    def get_button_states(self):
        return self.button_states

    def clear_button_states(self):
        for key in self.button_states.keys():
            self.button_states[key] = False

    def set_led_state(self, led_num, color):
        self.led_states[led_num] = color

    def clear_led_states(self):
        self.led_states = [self.led_off] * 48

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
        time.sleep(.3)
        wiringpi.digitalWrite(BoneGame.ARDUINO_GND_PIN, wiringpi.HIGH)

        time.sleep(.3)
        self.reset_game()


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
        self.clear_led_states()
        data = [int(Commands.clear_strip)]
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


    def clear_strip_set_led(self, led_num, color):
        logging.info(self.clear_strip_set_led.__name__)
        self.clear_led_states()
        data = [int(Commands.clear_then_set_led)]
        data.append(led_num)
        data.extend(color)
        res = self.write_data(data)
        self.set_led_state(led_num, color)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

    def set_led(self, led_num, color):
        if not self.colors_equal(self.led_states[led_num], color):
            logging.info('%s: %d' % (self.set_led.__name__, led_num))
            data = [int(Commands.set_led)]
            data.append(led_num)
            data.extend(color)
            res = self.write_data(data)
            self.set_led_state(led_num, color)
            # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


    def reset_game(self):
        logging.info(self.reset_game.__name__)
        data = [int(Commands.reset_game)]
        res = self.write_data(data)
        self.reset_selected_bone()
        self.reset_selected_bone_name()
        self.clear_button_states()


    def set_button_test_on(self):
        logging.info(self.set_button_test_on.__name__)
        data = [int(Commands.button_test_on)]
        res = self.write_data(data)


    def set_button_test_off(self):
        logging.info(self.set_button_test_off.__name__)
        data = [int(Commands.button_test_off)]
        res = self.write_data(data)


    def run_led_test(self):
        logging.info(self.set_button_test_off.__name__)
        data = [int(Commands.led_test)]
        res = self.write_data(data)


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
        while(button != '\0'):
            button = ''
            while(button not in BoneGame.LETTER_LED_MAP.keys() and button != '\0' and retry_count < retry_max):
                self.heartbeat_log( 'get_buttons', logging.debug )
                try:
                    button = chr(self.read_data())
                    self.heartbeat_log( 'get_buttons: %s' % (str(button)), logging.debug )
                except TypeError:
                    logging.debug('get_buttons execption')
                    button = None
                retry_count += 1
            if button != '\0':
                self.heartbeat_log('sett button %s true' % (str(button)), logging.debug)
                self.button_states[button] = True


    def get_heartbeat(self):

        data = [int(Commands.heartbeat)]
        res = self.write_data(data)
        try:
            return chr(self.read_data())
        except TypeError:
            return '-1'


    def millis(self):
        return int(round(time.time() * 1000))

    def heartbeat_log(self, log_msg, debug_level, force = False):
        # debug_level('millis: %s, on at: %s, off at: %s' % (str(self.millis()), str(self.heartbeat_on_at), str(self.heartbeat_off_at)))
        if force == True:
            debug_level(log_msg)
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
