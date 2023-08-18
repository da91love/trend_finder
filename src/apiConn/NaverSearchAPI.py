import requests
import json
import logging
import traceback

# Exceptions
from src.error.Error import *

# const
from src.const.URL_PATH import *

# declare comm variable
logger = logging.getLogger('sLogger')


class NaverSearchAPI():

    def __init__(self, client_id: str, client_secret: str, uri: str):
        """
        인증키 설정 및 검색어 그룹 초기화
        """
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.query: str = ""
        self.base_url: str = BASE_URL["NAVER_SEARCH"]
        self.uri = uri
        self.body = {}

    def add_query(self, query: str):
        """

        :param group_dict:
        :return:
        """
        try:
            self.query = query

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def get_data(self, display: int = 1, start: int = 1, sort: str = "sim", filter: str = "", exclude: str =""):
        """
        :return:
        """
        try:
            f_url = self.base_url + self.uri

            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }

            params = {
                "query": self.query,
                "display": display,
                "start": start,
                "sort": sort,
                "filter": filter,
                "exclude": exclude,
            }

            response = requests.get(f_url, headers=headers, params=params)

            if response.status_code == 200:
                res = response.json()
                return res
                # Do something with the data
            else:
                error_info = json.loads(response.text)

                if error_info['errorCode'] == '010':
                    raise NaverSearchAPIQuaryOverCallError

                else:
                    logger.error(error_info["errorMessage"])
                    raise APIcallException(tg_kw = self.body['keyword'], err_code = error_info["errorCode"], msg = error_info["errorMessage"])

        except NaverSearchAPIQuaryOverCallError as e:
            logger.error(traceback.format_exc())
            raise e

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e