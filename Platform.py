import html
import json
import os
import pickle
import re
import sys
import time
import traceback
from pathlib import Path

import requests
import validators
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

import ItemCollector
import selenium_impl.kaltura
from Exceptions import *
from edx.Urls import EdxUrls as const

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass





class Platform(const):
    _headers = {
        'Host': const.HOSTNAME,
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': None,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': const.PROTOCOL_URL,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': const.LOGIN_URL,
        'accept-language': 'en-US,en;q=0.9',
    }

    def __init__(self, email, password, platform ):
        self._platform = platform
        # Creates a request session
        self._client = requests.Session()

        # The EDX account's email
        self._email = email
        self.collector = ItemCollector.Collector()

        # The EDX account's password
        self._password = password

        # This is set True later and is used to
        # avoid unnecessary login attempts
        self.is_authenticated = False

        # Cookie location
        # These headers are required. Some may not be required
        # but sending all is a good practice.


        self._SAVED_SESSION_PATH = Path(Path.home(), f'.{platform}cookie')

    @property
    def password(self):
        return self._password


    @password.setter
    def password(self, password:str):
        self._password = password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email:str):
        self._email = email


    @property
    def SAVED_SESSION_PATH(self):
        return self._SAVED_SESSION_PATH


    @SAVED_SESSION_PATH.setter
    def SAVED_SESSION_PATH(self,path:Path):
        self._SAVED_SESSION_PATH = Path(path, '.edxcookie')

    def load(self, ):
        if self.SAVED_SESSION_PATH.exists() and self.SAVED_SESSION_PATH.stat().st_size > 100:
            with open(self.SAVED_SESSION_PATH, 'rb') as f:
                self.client = pickle.load(f)
            return True
        else:
            log("pickleJar is empty", "red")
            return False

    def dump(self, ):
        with open(self.SAVED_SESSION_PATH, 'wb') as f:
            pickle.dump(self.client, f)


