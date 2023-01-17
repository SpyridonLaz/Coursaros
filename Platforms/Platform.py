from abc import abstractmethod
from pathlib import Path
import pickle
import requests

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
except ImportError:
    log = print
    d = print
    pass


class BasePlatform:
    # This is set True later and is used to
    # avoid unnecessary login attempts
    _is_authenticated = False

    def __init__(self,
                 email,
                 password,
                 platform,
                 save_to=Path.home(),
                 ):

        # platform name (e.g. edx)
        self._platform = platform

        # default path to save files
        self._save_to = save_to
        # Cookie location

        # Creates a request session
        self._client = requests.Session()

        # The EDX account's email
        self._email = email

        # The EDX account's password
        self._password = password

        #  Some headers may not be required
        # but sending all is a good practice.

    @property
    def client(self):
        return self._client

    @property
    def platform(self):
        return self._platform

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value: bool):

        self._is_authenticated = bool(value)

    @property
    def save_to(self):
        return self._save_to

    @save_to.setter
    def save_to(self, value):
        path = Path(value, 'Coursaros', self.platform)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._save_to = path

    @property
    def COOKIE_PATH(self):
        return self._COOKIE_PATH

    @COOKIE_PATH.setter
    def COOKIE_PATH(self, path: Path):
        self._COOKIE_PATH = Path(path, f'.{self.platform}cookie')

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

    def load_cookies(self, ):
        if self.COOKIE_PATH.exists() and self.COOKIE_PATH.stat().st_size > 100:
            with self.COOKIE_PATH.open('rb') as f:
                self._client = pickle.load(f)
            return True
        else:
            log("pickleJar is empty", "red")
            return False

    def save_cookies(self, ):
        self.COOKIE_PATH = self.save_to
        with self.COOKIE_PATH.open('wb') as f:
            pickle.dump(self.client, f)

    @abstractmethod
    def sign_in(self):
        pass
