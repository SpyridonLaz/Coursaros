import requests
from selenium import webdriver



class SeleniumManager:

    def __init__(self, SessionManager ):
        # selenium
        self.SessionManager = SessionManager
        self.client:requests.Session = SessionManager.client
        self._cookies = None
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--headless')
        self.chromeOptions.add_argument("--no-sandbox")
        self.chromeOptions.add_argument("--disable-setuid-sandbox")
        self.chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.chromeOptions.add_argument("--ignore-certificate-errors")
        self.chromeOptions.add_argument("--remote-debugging-port=9222")  # this
        self.chromeOptions.add_argument("--disable-dev-shm-using")
        self.chromeOptions.add_argument("--disable-extensions")
        self.chromeOptions.add_argument("--disable-gpu")
        # self.chromeOptions.add_argument("start-maximized")
        self.chromeOptions.add_argument("disable-infobars")
        self.chromeOptions.add_argument("--user-data-dir=./Downloads/firefox.tmp")
        # self.chromeOptions.add_argument("--profile-directory=Default");
        self.cookies = self.client.cookies
        self.driver = webdriver.Chrome(chrome_options=self.chromeOptions)
        self.driver.implicitly_wait(2)


    @property
    def cookies(self, ):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        _driver_cookies = self.driver.get_cookies()

        cookies_dict ={name.get('name'): value.get('path') for name, value in _driver_cookies}
        self._cookies = self.client.cookies.set(**cookies_dict)

        self._cookies = cookies

    def session_to_driver(self,cookies):
        _cookies = [{'name': c.name,
                     'value': c.value,
                     'domain': c.domain,
                     'path': c.path,
                     # 'expiry': c.expires,
                     } for c in cookies]
        [self.driver.add_cookie(cookie) for cookie in _cookies]




    def unloadCookies(self):



        self.driver.delete_all_cookies()
        [self.driver.add_cookie(cookie) for cookie in self.cookies]
        return
