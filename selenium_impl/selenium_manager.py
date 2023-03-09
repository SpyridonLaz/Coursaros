import re
import sys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from selenium import webdriver




class SeleniumSession:

    # original_window = driver.current_window_handle

    #     # Opens a new tab and switches to new tab
    # driver.switch_to.new_window('tab')
    #
    #     # Opens a new window and switches to new window
    # driver.switch_to.new_window('window')
    #

    driver = None
    def __init__(self,  *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.chrome_options = Options()
        self.service = Service(ChromeDriverManager().install())

        # self.client:requests.Session = client
        # self._cookies = None
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        # self.chromeOptions.add_argument("--no-sandbox")
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-dev-shm-using")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--user-data-dir=./Downloads/webdriver.tmp")


    def init_driver(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.implicitly_wait(3)


    def user_agent(self):
        if not self.driver:
            print("No driver found. Initiate WebDriver first.")
            return None
        return  self.driver.execute_script("return navigator.userAgent;")

    def selenium_to_requests(self, client: requests.Session):
        import json
        def eval_d(value):

            if isinstance(value, str):
                if value.startswith("\"{") and value.endswith("}\""):
                    # return json.loads(value[1:-1])

                    # return eval(value)
                    return eval(value).strip("\"")
            return value



        try:
            [client.cookies.set(name=c.pop("name"), value= eval_d(c.pop("value")),domain=c.get('domain'),path=c.get('path')) for c in self.driver.get_cookies()]
            # cookie_dict = [requests. for c in self.driver.get_cookies()]
            # client.cookies.set(cookie_dict)
            # print(client.cookies)
        except Exception as e:
            print("SELENIUM TO REQUESTS COOKIES TRANSFER FAILED", e)
            return False

        return True

    def requests_to_selenium(self, client: requests.Session):
        [(print('name', name,),print( 'value', value)) for name, value in client.cookies.items()]
        try:
            cookiejar = [{'name': name, 'value': value} for name, value in client.cookies.items()]

            [self.driver.add_cookie(c) for c in cookiejar]
        except Exception as e:
            print("REQUESTS TO SELENIUM COOKIES TRANSFER FAILED", e)
            return False
        return True


    def install_webdriver(self):
        if sys.platform == 'win32':
            from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
            with OpenKey(HKEY_CURRENT_USER,
                         r"Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice") as key:
                browser = QueryValueEx(key, 'Progid')[0]
                print(browser)
        elif sys.platform == 'linux':
            import webbrowser
            default_browser = webbrowser.get()
            # //todo: add more browsers
            default_browser_name = default_browser.name
            default_browser_basename = default_browser.basename
            print(default_browser, default_browser_name, default_browser_basename)
        # if browser == 'ChromeHTML':
        #
        #     return
        # elif browser == 'FirefoxURL':
        #     return
        # elif browser == 'OperaStable':
        #     return
        # elif browser == 'Opera':
        #     return
        #
