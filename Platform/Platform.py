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
from Urls.EdxUrls import EdxUrls as const

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass





class Platform(const):

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

        self._headers = {
            'Host': self.HOSTNAME,
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': None,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': self.PROTOCOL_URL,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.LOGIN_URL,
            'accept-language': 'en-US,en;q=0.9',
        }

    def headers(self):
        # Generate a fake user-agent to avoid 403 error
        self._headers['user-agent'] = UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome
        return self._headers




    @property
    def password(self):
        return self._password

    @property
    def platform(self):
        return self._platform


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
        self._SAVED_SESSION_PATH = Path(path, f'.{self.platform}cookie')

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


