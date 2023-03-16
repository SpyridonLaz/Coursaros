import sys

from coursaros.connection_manager import SessionManager

sys.path.append('../..')
from abc import abstractmethod
from pathlib import Path
import requests

from coursaros.item_collector import Collector
from coursaros.debug import LogMessage, Debugger


class FileManager:
    def __init__(self,platform,  save_to, ):

        self.relative_path = Path( 'Coursaros', platform)
        self.save_to = save_to
        self.config_file = self.save_to
        # path to save cookies
        self.COOKIE_PATH = self.save_to


    @property
    def COOKIE_PATH(self):
        # gets Cookie location
        return self._COOKIE_PATH
    @COOKIE_PATH.setter
    def COOKIE_PATH(self, path: Path):
        # sets Cookie location
        # ../Coursaros/edx/.edx
        self._COOKIE_PATH = Path(path, f'.{self.relative_path.name}_cookies')

    @property
    def save_to(self):
        return self._save_to
    @property
    def config_file(self):
        return self._config_file
    @save_to.setter
    def save_to(self, value):
        path = self._root_folder(value)

        print(f"Download directory set to: {path}")

        self._save_to = path


    @config_file.setter
    def config_file(self, value):
        path = self._root_folder(value)
        self.pdf_results = path
        self.positive = path
        self.negative = path
        self._config_file = path

    def _root_folder(self,value):
        value = Path(value).resolve()
        path = Path(value, self.relative_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path


class BasePlatform(FileManager, Collector,SessionManager,):
    # This is set True later and is used to
    # avoid unnecessary login attempts

    def __init__(self, email, password,
                 urls, save_to=Path.home(),*args ,
                  **kwargs):
        # The account's email
        self._email = email
        # The account's password
        self._password = password
        # Command args
        self.kwargs = kwargs
        # is user authenticated. boolean
        self._user_auth = False
        self._courses = []

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
        # default path to save files
        FileManager.__init__( self,  platform=self.urls.platform, save_to=Path(save_to))
        Collector.__init__(self, save_to=self.save_to)
        SessionManager.__init__(self, *args,**kwargs)
        if True:

            self.init_driver()
            self.main_tab = self.driver.current_window_handle
            self.client.headers.update({'User-Agent': self.user_agent() or self.urls.fake_user_agent(),'Referer':self.urls.DASHBOARD_URL})

    @property
    def credentials(self):
        data = {
            'email': self.email,
            'password': self.password
        }
        return data
    @property
    def platform(self):
        return self._platform


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

    @staticmethod
    def is_authenticated(func):
        def wrapper(self, *args, **kwargs):
            if self.check_if_logged_in_browser():
                return func(self, *args, **kwargs)
            else:
                self.login()
                return func(self, *args, **kwargs)
        return wrapper

    @property
    def user_auth(self):
        return self._user_auth

    @user_auth.setter
    def user_auth(self, value: bool):
        self._user_auth = bool(value)



    @abstractmethod
    def sign_in(self):
        pass





