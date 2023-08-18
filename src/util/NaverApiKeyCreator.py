# internal module
import os
import logging
import traceback
import time

# external module
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException
import pyperclip

from bs4 import BeautifulSoup

# Exceptions
from src.error.Error import *

# auth
from config.development import *

# const
from src.const.NAVER_API import *

# declare comm variable
logger = logging.getLogger('sLogger')

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class NaverApiKeyCreator:
    def __init__(self, api_type):
        self.api_type = api_type
        self.driver = webdriver.Chrome()

        self.driver.get(NAVER_API[self.api_type]['url'])
        self.actions = ActionChains(self.driver)
        self.alert = Alert(self.driver)

        self.client_id = None
        self.client_secret = None

        self.driver.maximize_window()
    def get_new_key(self):
        try:
            self.login()
            self.delete_key()
            self.register_key()

            self.driver.close()

            return {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

        except IndexError as e:
            self.delete_key()
            self.register_key()

            self.driver.close()

            return {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

        except ValueError as e:
            self.register_key()

            self.driver.close()

            return {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

        except NoSuchElementException as e:
            self.delete_key()
            self.register_key()

            self.driver.close()

            return {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

        except Exception as e:
            raise e

    def delete_key(self):
        try:
            # 타겟 API검색
            api_name_elmts = self.driver.find_elements(By.XPATH, '// div [contains(@class, "f1meouu2")] / descendant::ul [contains(@class, "depth0")]/ li[1] / ul / li')

            api_names = [api_name_elmt.text for api_name_elmt in api_name_elmts]

            tg_api_idx = api_names.index(NAVER_API[self.api_type]['name'])
            self.actions.click(self.driver.find_element(By.XPATH, f'// div [contains(@class, "f1meouu2")] / descendant::ul [contains(@class, "depth0")]/ li[1] / descendant::li[{tg_api_idx + 1}]')).perform()

            # api 삭제
            ## api 설정 클릭
            self.actions.click(self.driver.find_element(By.XPATH, '// ul [contains(@class, "tab_menu")] / descendant::li[2]')).perform()

            ## 삭제버튼 클릭 및 삭제 확인
            self.actions.click(self.driver.find_element(By.CLASS_NAME, "field-button")).perform()
            self.alert.accept()
            time.sleep(0.5)

            ## 삭제위한 비밀번호 입력
            tabs = self.driver.window_handles
            self.driver.switch_to.window(tabs[1])

            self.actions.key_down(Keys.TAB).perform()
            self.actions.send_keys(AUTH['NAVER_ACCOUNT']['PW']).perform()
            self.actions.key_down(Keys.ENTER).perform()
            self.driver.switch_to.window(tabs[0])
            time.sleep(1.5)

        except ValueError as e:
            raise e

        except NoSuchElementException as e:
            raise e

        except Exception as e:
            raise e
    
    def register_key(self):
        try:
            # 새로운 api 생성
            self.actions.click(self.driver.find_element(By.XPATH, f'// div [contains(@class, "f1meouu2")] / descendant::ul [contains(@class, "depth0")]/ li[2]')).perform()

            ## 어플리케이션 이름 등록
            self.actions.click(self.driver.find_element(By.CLASS_NAME, "field-input")).perform()
            self.actions.send_keys(NAVER_API[self.api_type]['name']).perform()

            ## 사용 api 등록
            self.actions.click(self.driver.find_element(By.XPATH, f'// div [@id = "content"] / descendant::button')).perform()
            time.sleep(0.5)
            self.actions.click(self.driver.find_element(By.XPATH,
                                              f'// div [@id = "content"] / descendant::button / following-sibling::ul / li[{NAVER_API[self.api_type]["api_idx"]}]')).perform()

            self.actions.click(self.driver.find_element(By.XPATH, f'// div [@id = "content"] / descendant::button[2]')).perform()
            time.sleep(0.5)
            self.actions.click(self.driver.find_element(By.XPATH,
                                              f'// div [@id = "content"] / descendant::button[2] / following-sibling::ul / li[{NAVER_API[self.api_type]["api_env_idx"]}]')).perform()

            self.actions.send_keys(NAVER_API[self.api_type]['env']).perform()

            ## 서비스 환경 등록
            self.actions.click(self.driver.find_element(By.XPATH, '// div [@id = "content"] / descendant::button[3]')).perform()
            time.sleep(3)

            # 새로운 key 정보 취득
            client_id = (self.driver.find_elements(By.XPATH, '// input [@class = "inp"]')[0]).get_attribute("value")
            client_secret = (self.driver.find_elements(By.XPATH, '// input [@class = "inp"]')[1]).get_attribute("value")

            self.client_id = client_id
            self.client_secret = client_secret

        except NoSuchElementException as e:
            raise e

        except IndexError as e:
            raise e

        except Exception as e:
            raise e

    def login(self):
        try:
            # 1. id 복사 붙여넣기
            pyperclip.copy(AUTH['NAVER_ACCOUNT']['ID'])

            self.actions \
                .click(self.driver.find_element(By.ID, "id"))\
                .key_down(Keys.CONTROL)\
                .send_keys("v") \
                .key_up(Keys.CONTROL) \
                .perform()
            time.sleep(0.5)

            # 2. pw 복사 붙여넣기
            pyperclip.copy(AUTH['NAVER_ACCOUNT']['PW'])

            self.actions \
                .click(self.driver.find_element(By.ID, "pw"))\
                .key_down(Keys.CONTROL)\
                .send_keys("v") \
                .key_up(Keys.CONTROL) \
                .perform()
            time.sleep(0.5)

            # 3. 로그인 버튼 클릭
            self.actions.click(self.driver.find_element(By.ID, "log.login")).perform()
            time.sleep(1)

        except NoSuchElementException as e:
            raise e

        except Exception as e:
            raise e