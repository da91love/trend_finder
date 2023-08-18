# internal modules
import requests
import json
import time
import logging
import traceback

# Exceptions
from src.error.Error import APIcallException

# const
from src.const.URL_PATH import *

# other modules
from src.util.create_signature import create_signature

# declare comm variable
logger = logging.getLogger('sLogger')

class NaverSearchAdAPI():

    def __init__(self, customer_id, access_key, secret_key, uri):
        """
        인증키 설정 및 검색어 그룹 초기화
        """
        self.customer_id: str = customer_id
        self.access_key: str = access_key
        self.secret_key: str= secret_key
        self.hintKeywords: str = None
        self.base_url: str = BASE_URL["NAVER_SEARCH_AD"]
        self.uri: str = uri

    def add_keywords(self, hintKeywords: list):
        """

        :param group_dict:
        :return:
        """
        try:
            hintKeywords = ','.join(hintKeywords)
            self.hintKeywords = hintKeywords

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def get_data(self):
        """
        :return:
        """
        try:
            method = 'GET'
            timestamp = str(round(time.time() * 1000))
            signature = create_signature(timestamp, method, self.uri, self.secret_key)

            f_url = self.base_url + self.uri

            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Timestamp': timestamp,
                'X-API-KEY': self.access_key,
                'X-Customer': str(self.customer_id),
                'X-Signature': signature
            }

            ## param에 space 존재시 오류남
            params = {
                "hintKeywords": (self.hintKeywords).replace(" ", ""),
                "showDetail": 1
            }

            response = requests.get(f_url, headers=headers, params=params)

            if response.status_code == 200:
                res = response.json()
                return res
                # Do something with the data
            else:
                error_info = json.loads(response.text)
                logger.error(error_info["message"])
                raise APIcallException(tg_kw = self.hintKeywords, err_code = error_info["code"], msg = error_info["message"])

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e