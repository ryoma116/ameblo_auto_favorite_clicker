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
            self.driver.get(LOGIN_URL)

            username_input = self.driver.find_elements_by_name('accountId')
            password_input = self.driver.find_elements_by_name('password')
            print(self.username)
            print(self.password)

            username_input[0].send_keys(self.username)
            password_input[0].send_keys(self.password)
            password_input[0].send_keys(Keys.RETURN)
            print('Logged in Success !!')

        except:
            print('Logged In Failed !!')

    def likes(self):

        user_ids = self.get_target_users()

        for user_id in user_ids:
            try:
                url = USER_ARTICLE_LIST_URL.format(user_id)
                self.driver.get(url)
                sleep(randrange(3, 5))

                ###############################
                # タグ検索画面から一番最初の投稿を選択
                ###############################
                try:
                    div_elems = self.driver.find_elements_by_class_name('skin-borderQuiet')
                    if len(div_elems) == 0:
                        div_elems = self.driver.find_elements_by_class_name('listContentsArea')

                    if len(div_elems) == 0:
                        continue

                    a_elem = div_elems[0].find_element_by_tag_name('a')
                    a_elem.click()
                    sleep(randrange(3, 5))
                except Exception as e:
                    print('contents none!')
                    print(e)
                    continue

                ###############################
                # いいねボタンが押下済みでないか確認
                ###############################
                try:
                    favo_clicked_elems = self.driver.find_elements_by_class_name('_3jVZEr7d')
                    if len(favo_clicked_elems) > 0:
                        continue

                except Exception as e:
                    pass

                ###############################
                # いいねボタンを押下
                ###############################
                favo_elems = self.driver.find_elements_by_class_name('_SRPdpszF')
                if len(favo_elems) > 0:
                    favo_elems[0].click()
                    self.like_count += 1
                    if self.like_count >= self.max_like_count:
                        break

            except Exception as e:
                print(e)
                continue

    def move_next_post(self):
        self.find_by_class_name(CLASS_NAME_NEXT)[0].click()

    def find_by_class_name(self, class_name):
        WebDriverWait(self.driver, WAIT_SEC_ELEMENT_VISIBLE).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        return self.driver.find_elements_by_class_name(class_name)

    def get_target_users(self):
        try:
            ###############################
            # 属性の近いユーザの記事を開く
            ###############################
            url = f'https://ameblo.jp/{self.url}'
            self.driver.get(url)
            sleep(randrange(3, 5))

            ###############################
            # いいね一覧を開く
            ###############################
            self.driver.find_elements_by_class_name('iineEntryCnt')[0].click()
            sleep(3)
            try:
                loop_cnt = 0
                while True:
                    loop_cnt += 1

                    more_btn_elems = self.driver.find_elements_by_class_name('ico_more_btm')

                    if loop_cnt > 1 or len(more_btn_elems) == 0:
                        break

                    more_btn_elems[0].click()
                    sleep(1)

            except Exception as e:
                pass

            ###############################
            # いいねしたユーザを抽出
            ###############################
            user_elems = self.driver.find_elements_by_class_name('iineListItem')
            print(len(user_elems))
            user_ids = [self.extract_user_id(x) for x in user_elems]
            print('Logged in Success !!')
        except:
            print('Logged In Failed !!')

        return user_ids

    @staticmethod
    def extract_user_id(elem):
        a_elem = elem.find_element_by_tag_name('a')
        user_id = a_elem.get_attribute('href').split('/')[3]
        return user_id
