from selenium import webdriver



class SeleniumManager:

    def __init__(self, cookies=None):
        # selenium
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
        self.Sessioncookies = self.getCookies(cookies)
        self.driver = webdriver.Chrome(chrome_options=self.chromeOptions)
        self.driver.implicitly_wait(2)



    def getCookies(self, cookies: dict):
        #
        return [{'name': c.name,
                 'value': c.value,
                 'domain': c.domain,
                 'path': c.path,
                 # 'expiry': c.expires,
                 } for c in cookies]

    def loadCookies(self):
        [self.driver.add_cookie(cookie) for cookie in self.Sessioncookies]
        return

    def unloadCookies(self):
        all_cookies = self.driver.get_cookies()
        cookies_dict = {}

        [cookies_dict.update({name.get('name'): value.get('value')}) for name, value in all_cookies]

        print(cookies_dict)

        self.driver.delete_all_cookies()
        [self.driver.add_cookie(cookie) for cookie in self.Sessioncookies]
        return
