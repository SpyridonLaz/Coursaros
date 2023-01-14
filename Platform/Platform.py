import html
import json
import os
import re
import sys
import time
import traceback
import validators
from bs4 import BeautifulSoup
from tqdm import tqdm
import selenium_impl.kaltura
from Exceptions import *

from pathlib import Path
import pickle
from fake_useragent import UserAgent
import requests
import ItemCollector
from Urls.PlatformUrls import PlatformUrls
try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass







class Platform(PlatformUrls, ItemCollector):
    # This is set True later and is used to
    # avoid unnecessary login attempts
    __is_authenticated = False

    def __init__(self, email, password, platform,HOSTNAME,SAVE_TO):
        super().__init__(HOSTNAME=HOSTNAME)
        #platform name (e.g. edx)
        self._platform = platform

        #default path to save files
        self.SAVE_TO = SAVE_TO

        # Cookie location
        self.COOKIE_PATH = self.SAVE_TO

        # Creates a request session
        self._client = requests.Session()


        # The EDX account's email
        self.__email = email

        # The EDX account's password
        self.__password = password


        #  Some headers may not be required
        # but sending all is a good practice.
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

    @property
    def SAVE_TO(self):
        return self._SAVE_TO
    @SAVE_TO.setter
    def SAVE_TO(self, value):
        path =Path(value,'Coursaros', self.platform)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._SAVE_TO = path

    @property
    def COOKIE_PATH(self):
        return self._COOKIE_PATH


    @COOKIE_PATH.setter
    def COOKIE_PATH(self,path:Path):
        self._COOKIE_PATH = Path(path, f'.{self.platform}cookie')

    @property
    def headers(self):
        # Generate a fake user-agent to avoid 403 error
        self._headers['user-agent'] = UserAgent(
            fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36').chrome
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers




    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password:str):
        self.__password = password

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email:str):
        self.__email = email


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


