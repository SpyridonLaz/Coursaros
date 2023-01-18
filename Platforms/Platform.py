from abc import abstractmethod
from pathlib import Path
import pickle
import requests

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
    log = log()
except ImportError:
    log = print
    d = print
    pass





class BasePlatform:
    # This is set True later and is used to
    # avoid unnecessary login attempts


    def __init__(self,
                 email,
                 password,
                 urls,
                 save_to=Path.home(),
                 ):
        self.urls = urls
        # platform name (e.g. edx)
        self._platform = urls.platform

        # default path to save files
        self.save_to = save_to
        # Cookie location

        # The EDX account's email
        self._email = email

        # The EDX account's password
        self._password = password

        self.connector = SessionManager(save_to=self.save_to)

    @property
    def platform(self):
        return self._platform



    @property
    def save_to(self):
        return self._save_to

    @save_to.setter
    def save_to(self, value):
        value = Path(value).resolve()
        path = Path(value, 'Coursaros', self.platform)
        print(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._save_to = path


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

class SessionManager:

    def __init__(self, save_to):
        # Creates a request session
        self._client = requests.Session()
        self.COOKIE_PATH = save_to
        self._user_auth = False
    @property
    def client(self):
        return self._client


    @staticmethod
    def is_authenticated(func):
        def wrapper(self, *args, **kwargs):
            if self.connector.user_auth:
                return func(self, *args, **kwargs)
            else:
                log("Not authenticated", "red")

        return wrapper


    @property
    def user_auth(self):
        return self._user_auth
    @user_auth.setter
    def user_auth(self, value: bool):
        self._user_auth = bool(value)




    def load_cookies(self, ):
        if self.COOKIE_PATH.exists() and self.COOKIE_PATH.stat().st_size > 100:
            with self.COOKIE_PATH.open('rb') as f:
                self.client.cookies = pickle.load(f)

            return True
        else:
            log("pickleJar is empty", "red")

    def save_cookies(self, ):
        cookie_Jar = self.client.cookies
        if cookie_Jar:
            with self.COOKIE_PATH.open('wb') as f:
                pickle.dump(cookie_Jar, f)
            return True
    @abstractmethod
    def sign_in(self):
        pass
    @property
    def COOKIE_PATH(self):
        return self._COOKIE_PATH

    @COOKIE_PATH.setter
    def COOKIE_PATH(self, path: Path):
        # ../Coursaros/edx/.edx
        self._COOKIE_PATH = Path(path, f'.{path.name}_cookies')
