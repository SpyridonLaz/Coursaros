import pickle

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from requestium import Session
from selenium import webdriver



class SessionManager:

    # original_window = driver.current_window_handle

    #     # Opens a new tab and switches to new tab
    # driver.switch_to.new_window('tab')
    #
    #     # Opens a new window and switches to new window
    # driver.switch_to.new_window('window')
    #


    def __init__(self, log = True, options:list[str,] =None, *args, **kwargs):


        if log:
            from coursaros.base.debug import LogMessage
            self.log = LogMessage()
        self.chrome_options = Options()
        self.service = Service(executable_path=ChromeDriverManager().install())

        # self.client:requests.Session = client
        # self._cookies = None
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.options.add_argument("--user-data-dir=./Downloads/webdriver.tmp")

        map(self.options.add_argument,options) if options else None
    def init_driver(self):
        chromedriver = webdriver.Chrome(service=self.service, options=self.options)
        self.client = Session(driver=chromedriver)
        self.driver= self.client.driver
        self.driver.implicitly_wait(3)



    def user_agent(self):
        if not self.driver:
            print("No driver found. Initiate WebDriver first.")
            return None
        return  self.driver.execute_script("return navigator.userAgent;")


    def save_session(self, COOKIE_PATH ):
        # saves cookiejar to avoid repeated logins
        print('Saving Session to ')
        if COOKIE_PATH.exists():
            with COOKIE_PATH.open('wb') as f:
                pickle.dump(self.client, f)

    def load_session(self,COOKIE_PATH ):
        # loads previously saved cookiejar to avoid repeated logins
        print("Loading Session", COOKIE_PATH)
        if COOKIE_PATH.exists():
            with COOKIE_PATH.open('rb') as f:
                self.client = pickle.load(f)
            print("Cookies loaded")
            return True
        else:
            if hasattr(self,'log'):
                self.log("pickleJar is empty", "red")
            return None
