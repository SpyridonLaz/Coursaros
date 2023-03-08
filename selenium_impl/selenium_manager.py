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
    def __init__(self, driver=False, *args, **kwargs):

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

        if driver:
            self.init_driver()

    def init_driver(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.implicitly_wait(3)


    def user_agent(self):
        if not self.driver:
            print("No driver found. Initiate WebDriver first.")
            return None
        return  self.driver.execute_script("return navigator.userAgent;")

    def selenium_to_requests(self, client: requests.Session):
        cookies = self.driver.get_cookies()

        for cookie in cookies:
            print(cookie['name'], cookie['value'], cookie['path'])
            _cookie_dict = client.cookies.set(cookie['name'], cookie['value'],cookie['path'])

        # client.cookies.set


        # cookie_list = self.driver.get_cookies()
        # for index in range(len(cookie_list)):
        #     for item in cookie_list[index]:
        #         if type(cookie_list[index][item]) != str:
        #             print("Fix cookie value: ", cookie_list[index][item]) if cookie_list[index][item] is not None else None
        #             cookie_list[index][item] = str(cookie_list[index][item])
        #     cookies = requests.utils.cookiejar_from_dict(cookie_list[index])
        #     client.cookies.update(cookies)


    # def session_to_driver(self,):
    #     _cookies = [{'name': c.name,
    #                  'value': c.value,
    #                  'domain': c.domain,
    #                  'path': c.path,
    #                  # 'expiry': c.expires,
    #                  } for c in self.cookies]
    #     [self.driver.add_cookie(cookie) for cookie in _cookies]
    #

    #
    # def unloadCookies(self):
    #
    #
    #
    #     self.driver.delete_all_cookies()
    #     [self.driver.add_cookie(cookie) for cookie in self.cookies]
    #     return

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
