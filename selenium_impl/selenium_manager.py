import sys

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
        self.chromeOptions.add_argument("--user-data-dir=./Downloads/webdriver.tmp")
        # self.chromeOptions.add_argument("--profile-directory=Default");
        self.cookies = self.client.cookies
        self.driver = webdriver.Chrome(chrome_options=self.chromeOptions)
        self.driver.implicitly_wait(2)
        self.session_to_driver()





    @property
    def cookies(self, ):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        #driver to session

        cookies_dict ={name.get('name'): value.get('path') for name, value in cookies.items()}
        self._cookies = self.client.cookies.set(**cookies_dict)
        self._cookies = cookies

    def session_to_driver(self,):
        _cookies = [{'name': c.name,
                     'value': c.value,
                     'domain': c.domain,
                     'path': c.path,
                     # 'expiry': c.expires,
                     } for c in self.cookies]
        [self.driver.add_cookie(cookie) for cookie in _cookies]




    def unloadCookies(self):



        self.driver.delete_all_cookies()
        [self.driver.add_cookie(cookie) for cookie in self.cookies]
        return

    def install_webdriver(self):
        if  sys.platform == 'win32':
            from winreg import HKEY_CURRENT_USER ,OpenKey, QueryValueEx
            with OpenKey(HKEY_CURRENT_USER,r"Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice") as key:
                browser = QueryValueEx(key, 'Progid')[0]
        elif sys.platform == 'linux':
            import webbrowser
            default_browser = webbrowser.get()
            #//todo: add more browsers
            default_browser_name = default_browser.name
            default_browser_basename = default_browser.basename


        if browser == 'ChromeHTML':
            return
        elif browser == 'FirefoxURL':
            return
        elif browser == 'OperaStable':
            return
        elif browser == 'Opera':
            return