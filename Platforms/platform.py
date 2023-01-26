import sys
sys.path.append('..')
from abc import abstractmethod, ABC
from collections import deque
from pathlib import Path
import pickle
import requests

from item_collector import Collector
from debug import LogMessage, Debugger


class BasePlatform(ABC,Collector):
    # This is set True later and is used to
    # avoid unnecessary login attempts

    def __init__(self, email, password,
                 urls, save_to=Path.home(),
                 config_save_to=Path.home(), args=None):
        # The account's email
        self._email = email
        # The account's password
        self._password = password
        # Command args
        self.args = args
        # is user authenticated. boolean
        self._user_auth = False
        self._courses = deque()

        # platform's urls
        self.urls = urls
        # platform name (e.g. edx,Coursera,etc)
        self._platform = self.urls.platform
        try:
            self.log = LogMessage()#output=args.get('output',None )if args else None ,
                               #   is_colored=args.get('is_colored',None)if args else None)
            self.d = Debugger()#args.get('debug', None) if args else None)
        except ImportError:
            self.log = print
            self.d = print


        self._client = requests.Session()
        super().__init__(self,  save_to=save_to)

        # default path to save files
        self.save_to = save_to
        # configuration file path
        self.config_file = config_save_to
        # path to save cookies
        self.COOKIE_PATH = self.config_file

        #if not self.user_auth : self.sign_in()
    @property
    def platform(self):
        return self._platform


    @property
    def save_to(self):
        return self._save_to
    @property
    def config_file(self):
        return self._config_file
    @save_to.setter
    def save_to(self, value):
        path = self._root_folder(value)

        print(f"Saving to path:{path}")

        self._save_to = path
    def _root_folder(self,value):
        value = Path(value).resolve()
        path = Path(value, 'Coursaros', self.platform)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path


    @config_file.setter
    def config_file(self, value):
        path = self._root_folder(value)
        self.pdf_results = path
        self.positive = path
        self.negative = path
        self._config_file = path
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password: str):
        self._password = password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email: str):
        self._email = email




    @property
    def client(self):
        return self._client

    @staticmethod
    def is_authenticated(func):
        def wrapper(self, *args, **kwargs):
            if self.user_auth:
                return func(self, *args, **kwargs)
            else:
                self.log("Not authenticated", "red")

        return wrapper

    @property
    def user_auth(self):
        return self._user_auth

    @user_auth.setter
    def user_auth(self, value: bool):
        self._user_auth = bool(value)

    def save_cookies(self, ):
        # saves cookiejar to avoid repeated logins
        cookie_Jar = self.client.cookies
        if cookie_Jar:
            with self.COOKIE_PATH.open('wb') as f:
                pickle.dump(cookie_Jar, f)
            return True

    def load_cookies(self, ):
        # loads previously saved cookiejar to avoid repeated logins
        print(self.COOKIE_PATH)
        if self.COOKIE_PATH.exists() and self.COOKIE_PATH.stat().st_size > 100:
            with self.COOKIE_PATH.open('rb') as f:
                self.client.cookies = pickle.load(f)
            self.user_auth = True

            return True
        else:
            self.log("pickleJar is empty", "red")

    @abstractmethod
    def sign_in(self):
        pass

    @property
    def COOKIE_PATH(self):
        # gets Cookie location

        return self._COOKIE_PATH

    @COOKIE_PATH.setter
    def COOKIE_PATH(self, path: Path):
        # sets Cookie location
        # ../Coursaros/edx/.edx

        self._COOKIE_PATH = Path(path, f'.{path.name}_cookies')

