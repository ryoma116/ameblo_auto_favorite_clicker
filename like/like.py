from random import randrange
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import chromedriver_binary
import urllib.parse

from .config import *


class AutoLiker:

    def __init__(self, *, headless=False):
        self.username = ''
        self.password = ''
        self.url = ''
        self.max_like_count = 10
        self.like_count = 0
        self.driver = None
        self.headless = headless

    def set_account(self, *, username, password):
        self.username = username
        self.password = password

    def set_url(self, *, url, max_like_count=10):
        self.url = url
        self.max_like_count = max_like_count

    def start(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        try:
            self.driver = webdriver.Chrome(options=options)
            self.login()
            self.likes()
        except Exception as e:
            print('Driver Error !!')
        finally:
            if self.driver is not None:
                self.driver.close()

        return {
            'url': self.url,
            'like_count': self.like_count,
        }

    def login(self):
        try:
            self.driver.get(INSTAGRAM_LOGIN_URL)

            auth_inputs = self.find_by_class_name(CLASS_NAME_AUTH)
            if len(auth_inputs) >= 2:
                username_input = auth_inputs[0]
                password_input = auth_inputs[1]
                print(self.username)
                print(self.password)

                username_input.send_keys(self.username)
                password_input.send_keys(self.password)
                password_input.send_keys(Keys.RETURN)
                print('Logged in Success !!')

                # 通知をONにするのポップアップが出る可能性を考慮
                try:
                    mention_popup_close = self.find_by_class_name(CLASS_NAME_MENTION_CLOSE)[0].click()
                except:
                    print('Popup Close Failed !!')
        except:
            print('Logged In Failed !!')

    def likes(self):
        try:
            search_url = INSTAGRAM_TAG_SEARCH_URL.format(urllib.parse.quote(self.url))
            self.driver.get(search_url)

            ###############################
            # タグ検索画面から一番最初の投稿を選択
            ###############################
            self.find_by_class_name(CLASS_NAME_MEDIA)[0].click()

            self.like_count = 0
            while self.like_count < self.max_like_count:
                ###############################
                # いいねボタンが押下済みでないか確認
                ###############################
                favo_span_elem = self.find_by_class_name(FAVO_SPAN_CLASS_NAME)
                favo_svg_elem = favo_span_elem[0].find_element_by_tag_name('svg')

                favo_label = favo_svg_elem.get_attribute('aria-label')
                if favo_label.find('取り消す') > -1:
                    # 押下済みの場合は次の投稿へ移動
                    self.move_next_post()
                    continue

                ###############################
                # いいねボタンを押下
                ###############################
                self.find_by_class_name(FAVO_SPAN_CLASS_NAME)[0].click()
                self.like_count += 1

                sleep(randrange(5, 10))

                ###############################
                # 次の投稿へ移動
                ###############################
                self.move_next_post()

        except Exception as e:
            print(e)
            raise e

    def move_next_post(self):
        self.find_by_class_name(CLASS_NAME_NEXT)[0].click()

    def find_by_class_name(self, class_name):
        WebDriverWait(self.driver, WAIT_SEC_ELEMENT_VISIBLE).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        return self.driver.find_elements_by_class_name(class_name)
