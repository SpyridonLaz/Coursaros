#!/usr/bin/env python3 
from inspect import currentframe, getframeinfo
from pathlib import Path

import colorful as cf


class Debugger():
    increment = 0


    @classmethod
    def __call__(cls,message, *args):
        cls.increment += 1

        s = "{filename} #:{increment}, Line #{line} :{message}".format(
            filename=Path(getframeinfo(currentframe()).filename).name, line=getframeinfo(currentframe()).lineno,
            message=message, increment=cls.increment)

        return print(s)


class LogMessage:
    ci_colors = {
        'green': '#42ba96',
        'orange': '#ffc107',
        'red': '#df4759',
        'blue': '#5dade2'
    }

    cf.update_palette(ci_colors)
    is_debug = 'is_debug'
    is_colored = 'is_colored'

    @classmethod
    def set_args(cls, is_debug, is_colored):
        '''
        # When it is set False, the log_message()
        # function will not print anything.
        # When this is set to True the log_message()
        # function will print in color.
        param is_debug:
        param is_colored:
        '''
        cls.is_debug = is_debug
        cls.is_colored = is_colored

    @classmethod
    def log_message(cls, message, color='blue', ):
        # Outputs a colorful message to the terminal
        # and only if 'is_debug' prop is set to True.
        # Override colorful palette

        if cls.is_debug:
            if cls.is_colored:
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
                print(message)
