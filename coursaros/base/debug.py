#!/usr/bin/env python3
import inspect
import logging
import signal
from inspect import currentframe, getframeinfo
from pathlib import Path

import colorful as cf

class Debugger():
    _debug = None
    increment = 0
    def __init__(self, debug: bool = True,):

        Debugger._debug = debug


    @classmethod

    def __call__(cls,message,   *args):
        cls.increment += 1
        if cls._debug:
            filename2 = inspect.stack()[1]
            filename = Path(getframeinfo(currentframe().f_back).filename).name
            line = getframeinfo(currentframe()).lineno
            s = f"{filename} #:{cls.increment}, Line #{line} :{message}"
            print(s)

    @property
    @classmethod
    def is_debug(cls):
        return cls._debug

    @is_debug.setter
    @classmethod
    def is_debug(cls, value):
        cls._debug = value
class DelayedKeyboardInterrupt:

    def __enter__(self):
        self.signal_received = []
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)



class LogMessage:
    ci_colors = {
        'green': '#42ba96',
        'orange': '#ffc107',
        'red': '#df4759',
        'blue': '#5dade2'
    }

    cf.update_palette(ci_colors)
    output = True
    is_colored = True

    def __init__(self, output: bool = True, is_colored: bool = True):
        LogMessage.output = output
        LogMessage.is_colored = is_colored
    def set_args(self, output:bool=None, is_colored:bool=None):
        '''
        # When it is set False, the log_message()
        # function will not print anything.
        # When this is set to True the log_message()
        # function will print in color.
        param output:
        param is_colored:
        '''
        LogMessage.output = output if output != None else LogMessage.output
        LogMessage.is_colored = is_colored if is_colored != None else LogMessage.is_colored

    @classmethod
    def __call__(cls, message, color=None):
        # Outputs a colorful message to the terminal
        # and only if 'output' prop is set to True.
        # Override colorful palette

        if LogMessage.output :
            if LogMessage.is_colored:
                if color == 'blue':
                    message = cf.bold & cf.blue | message
                elif color == 'orange':
                    message = cf.bold & cf.orange | message
                elif color == 'green':
                    message = cf.bold & cf.green | message
                elif color == 'red':
                    message = cf.bold & cf.red | message
            print(message)

        else:
            pass


log = LogMessage()
d = Debugger()