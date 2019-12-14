
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
    set_random_leds = 11


class HeartbeatMessages(IntEnum):
    waiting_for_test_choice = 0
    waiting_for_first_choice = 1
    waiting_for_second_choice = 2
    lighting_pressed_button = 3
    lighting_led = 4
    sent_test_choice = 5
    sent_first_choice = 6
    sent_second_choce = 7
    sent_heartbeat = 8






class BoneGame():

    DEVICE_ADDRESS = 0x08      #7 bit address (will be left shifted to add the read write bit)
    DEVICE_REG_MODE1 = 0x00
    DEVICE_REG_LEDOUT0 = 0x1d
    #milliseconds to wait for a second input
    GAME_TIMEOUT = 30000

    ARDUINO_VCC_PIN = 1
    ARDUINO_GND_PIN = 4
    ARDUINO_RST_PIN = 5

    # LETTER_LED_MAP = {
    #     'a': 0, 'b' : 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5,
    #     'g': 6, 'h' : 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11,
    #     'm': 12, 'n' : 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17,
    #     's': 18, 't' : 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23,
    #     'A': 24, 'B' : 25, 'C': 26, 'D': 27, 'E': 28, 'F': 29,
    #     'G': 30, 'H' : 31, 'I': 32, 'J': 33, 'K': 34, 'L': 35,
    #     'M': 36, 'N' : 37, 'O': 38, 'P': 39, 'Q': 40, 'R': 41,
    #     'S': 42, 'T' : 43, 'U': 44, 'V': 45, 'W': 46, 'X': 47
    # }

    LETTER_LED_MAP = {
        'a': 15, 'b': 23, 'c': 3,  'd': 9,  'e': 12, 'f': 18,
        'g': 0,  'h': 6,  'i': 16, 'j': 22, 'k': 4,  'l': 10,
        'm': 13, 'n': 19, 'o': 1,  'p': 7,  'q': 17, 'r': 21,
        's': 5,  't': 11, 'u': 14, 'v': 20, 'w': 2,  'x': 8,
        'A': 47, 'B': 41, 'C': 29, 'D': 35, 'E': 44, 'F': 38,
        'G': 30, 'H': 24, 'I': 46, 'J': 40, 'K': 28, 'L': 34,
        'M': 43, 'N': 37, 'O': 31, 'P': 25, 'Q': 45, 'R': 39,
        'S': 27, 'T': 33, 'U': 42, 'V': 36, 'W': 32, 'X': 26
    }

    CORRECT = [48, 49, 50]
    INCORRECT = [51, 52, 53]

    SOUND_CUES = [
        0.061, 0.198, 0.338, 0.494, 0.645,
        0.795, 0.938, 1.075, 1.218, 1.371,
        1.522, 1.672, 1.810, 1.950, 2.095,
        2.246, 2.399, 2.615, 2.895, 3.051,
        3.197, 3.347
    ]


    COLOR_LIST = [
        [0, 255, 17], [255, 17, 0], 
        [16, 0, 244], [119, 255, 0], 
        [255, 0, 119], [0, 116, 248], 
        [255, 230, 0], [230, 0, 255], 
        [0, 251, 226], [255, 115, 0],
        [115, 0, 255], [0, 251, 113]
    ]

    def __init__(self, debug = False):
        self.debug = debug
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
        self.button_test = False
        self.led_count = 54

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

        self.led_states = [self.led_off] * self.led_count
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
        wiringpi.digitalWrite(BoneGame.ARDUINO_GND_PIN, wiringpi.HIGH)

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
        self.led_states = [self.led_off] * self.led_count

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
        logging.debug('FUNC CALL: ' + self.restart_teensy.__name__)
        # wiringpi.digitalWrite(BoneGame.ARDUINO_RST_PIN, wiringpi.LOW)

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

        self.heartbeat_log( 'read_data', logging.debug, force=False )

        while( retry_count < retry_max ):
            try:
                self.heartbeat_log( 'read_data attempt', logging.debug )
                res = self.bus.read_byte_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1)
                return res
            except OSError:
                self.heartbeat_log( 'Retry read_data attempt %d' % (retry_count), logging.debug )
                retry_count += 1


    # def read_data(self, bytes):
    #     retry_max = 10
    #     retry_count = 0

    #     self.heartbeat_log( 'read_data bytes', logging.debug, force=True )

    #     while( retry_count < retry_max ):
    #         try:
    #             self.heartbeat_log( 'get_letter', logging.debug )
    #             res = self.bus.read_i2c_block_data(BoneGame.DEVICE_ADDRESS, BoneGame.DEVICE_REG_MODE1, 32)
    #             return res
    #         except OSError:
    #             self.heartbeat_log( 'Retry read_data', logging.debug )
    #             retry_count += 1



    def clear_strip(self):
        logging.debug('FUNC CALL: ' + self.clear_strip.__name__)
        self.clear_led_states()
        data = [int(Commands.clear_strip)]
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)


    def clear_strip_set_led(self, led_num, color):
        logging.debug('FUNC CALL: ' + self.clear_strip_set_led.__name__ + ': ' + str(led_num))
        self.clear_led_states()
        data = [int(Commands.clear_then_set_led)]
        data.append(led_num)
        data.extend(color)
        res = self.write_data(data)
        self.set_led_state(led_num, color)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)

    def set_led(self, led_num, color):
        logging.debug('FUNC CALL: ' + self.set_led.__name__ + ': ' + str(led_num))
        if not self.colors_equal(self.led_states[led_num], color):
            data = [int(Commands.set_led)]
            data.append(led_num)
            data.extend(color)
            res = self.write_data(data)
            self.set_led_state(led_num, color)
            # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
        return res

    def set_random_leds(self, led_count):
        logging.debug('FUNC CALL: ' + self.set_random_leds.__name__ + ': ' + str(led_count))
        self.clear_led_states()
        data = [int(Commands.set_random_leds)]
        data.append(led_count)
        res = self.write_data(data)
        # res = bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, data)
        return res

    def reset_game(self):
        logging.debug('FUNC CALL: ' + self.reset_game.__name__)
        data = [int(Commands.reset_game)]
        res = self.write_data(data)
        self.reset_selected_bone()
        self.reset_selected_bone_name()
        self.clear_button_states()


    def set_button_test_on(self):
        self.button_test = True
        logging.debug('FUNC CALL: ' + self.set_button_test_on.__name__)
        data = [int(Commands.button_test_on)]
        res = self.write_data(data)


    def set_button_test_off(self):
        self.button_test = False
        logging.debug('FUNC CALL: ' + self.set_button_test_off.__name__)
        data = [int(Commands.button_test_off)]
        res = self.write_data(data)


    def run_led_test(self):
        logging.debug('FUNC CALL: ' + self.run_led_test.__name__)
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
        
    def get_letter_test(self):
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
        if button in BoneGame.LETTER_LED_MAP.keys():
            self.button_states[button] = True
        return button
        


    def get_buttons(self):
        button = ''
        byte = 0b00000000
        retry_max = 10
        retry_count = 0
        end_char = '0'
        invalid_data = False
        while(button != end_char and invalid_data == False):
            button = ''
            while(button not in BoneGame.LETTER_LED_MAP.keys() and button != end_char and retry_count < retry_max):
                self.heartbeat_log( 'get_buttons', logging.debug )
                try:
                    byte = self.read_data()
                    button = chr(byte)
                    self.heartbeat_log( 'get_buttons: %s' % (str(button)), logging.debug )
                except TypeError:
                    self.heartbeat_log('get_buttons execption', logging.debug)
                    button = None
                retry_count += 1
                self.heartbeat_log('Is button %s: %s' % (end_char, (button == end_char)), logging.debug)
            retry_count = 0
            if button != end_char and button in BoneGame.LETTER_LED_MAP.keys():
                self.heartbeat_log('set button %s true' % (str(button)), logging.debug)
                self.button_states[button] = True
            elif button != end_char and button not in BoneGame.LETTER_LED_MAP.keys():
                self.heartbeat_log('invalid date: %s' % (str(button)), logging.debug)
                invalid_data = True


    def get_heartbeat(self):

        data = [int(Commands.heartbeat)]
        res = self.write_data(data)
        try:
            return self.read_data()
        except TypeError:
            return -2


    def millis(self):
        return int(round(time.time() * 1000))

    def heartbeat_log(self, log_msg, debug_level, force = False):
        # debug_level('millis: %s, on at: %s, off at: %s' % (str(self.millis()), str(self.heartbeat_on_at), str(self.heartbeat_off_at)))
        if force == True:
            debug_level(log_msg)
        if self.heartbeat_on_at == None:
            # debug_level('Heartbeat is None')
            self.heartbeat_on_at = self.millis() + self.heartbeat_interval
            self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
        elif self.millis() >= self.heartbeat_off_at:
            self.heartbeat = False
            #At the end of the pi heartbeat interval get the teensy logs
            if self.debug:
                debug_level('Get Device Logs')
                # self.get_device_logs(debug_level)
            self.heartbeat_on_at = self.millis() + self.heartbeat_interval
            self.heartbeat_off_at = self.heartbeat_on_at + self.heartbeat_durration
            # debug_level('heartbeat off')
        elif self.millis() >= self.heartbeat_on_at:
            # debug_level('heartbeat on')
            self.heartbeat = True
            debug_level(log_msg)


    def get_device_logs(self, debug_level):
        data = [int(Commands.send_log)]
        #res = self.write_data(data)
        try:
            log_data = None
            while log_data == None or log_data[32] != '0':
                log_data = self.read_data()
                debug_level(log_data)
        except TypeError:
            return '-1'


class Heartbeat():

    def __init__(self, bone_game, 
        durration = 10000,
        missed_count_max = 3
    ):
        self.bone_game = bone_game
        self.teensy_heartbeat = False
        self.teensy_heartbeat_durration = 10000
        self.teensy_heartbeat_last = self.bone_game.millis()
        self.teensy_heartbeat_missed_count = 0
        self.teensy_heartbeat_missed_count_max = 3
        self.teensy_heartbeat_last_response = -1
        self.teensy_heartbeat_same_response_count = 0
        self.teensy_heartbeat_same_response_count_max = 3
        self.heartbeat = -1
        logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/bone_game_pi.log',level=logging.INFO)


    def heartbeat_fail_reset(self):
        self.bone_game.restart_teensy()
        time.sleep(1)
        self.bone_game.reset_game()
        self.teensy_heartbeat_missed_count = 0
        self.teensy_heartbeat_same_response_count = 0


    def get_heartbeat(self): 
        ret = 0   
        if self.teensy_heartbeat_last + self.teensy_heartbeat_durration <= self.bone_game.millis():
            self.teensy_heartbeat_last = self.bone_game.millis()
            self.heartbeat = self.bone_game.get_heartbeat()
            try:
                logging.debug('heartbeat returned RAW value: %s' % (str(self.heartbeat)))
                logging.debug('heartbeat returned value: %s' % (HeartbeatMessages(self.heartbeat)))
                if HeartbeatMessages(self.heartbeat) == HeartbeatMessages.waiting_for_test_choice and self.bone_game.button_test == False:
                    self.heartbeat_fail_reset()
                elif self.heartbeat == self.teensy_heartbeat_last_response:
                    self.teensy_heartbeat_same_response_count += 1
                    logging.debug('Same Heartbeat returned, count %d' % (self.teensy_heartbeat_same_response_count))
                    if self.teensy_heartbeat_same_response_count > self.teensy_heartbeat_same_response_count_max:
                        logging.debug('Same Heartbeat returned, restarting')
                        self.heartbeat_fail_reset()
                else:
                    self.teensy_heartbeat_last_response = self.heartbeat
                    self.teensy_heartbeat_same_response_count = 0

            except ValueError as e:
                logging.debug('Exception: Heartbeat returned value: %s' % (str(self.heartbeat)))
                self.heartbeat = -1
            if self.heartbeat == -1:
                self.teensy_heartbeat_missed_count += 1
                logging.debug('NO Heartbeat returned, Fail count %d' % (self.teensy_heartbeat_missed_count))
                if self.teensy_heartbeat_missed_count > self.teensy_heartbeat_missed_count_max:
                    logging.debug('NO Heartbeat returned, restarting')
                    self.heartbeat_fail_reset()
                    ret = -1
            else:
                logging.debug('Heartbeat returned')
            self.heartbeat = -1
        return ret