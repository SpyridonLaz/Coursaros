 
import ast
import html
import json
import os
import pickle
import re
import sys
import time
import traceback
from os.path import expanduser
import concurrent.futures
import colorful as cf
import pdfkit
import requests
import validators
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
 
 
 #//TODO
 
 
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

	# # TODO
	# def get_url(self, url):
	#     try:
	#         self.driver.get(url)
	#         time.sleep(2)
	#     except Exception as e:
	#         print(traceback.format_exc())
	#         # self.driver.quit()

	def getCookies(self, cookies: dict):
		#
		return [{'name'  : c.name,
				 'value' : c.value,
				 'domain': c.domain,
				 'path'  : c.path,
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

