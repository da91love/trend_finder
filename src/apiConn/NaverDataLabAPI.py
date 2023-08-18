import requests
import json
import logging
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pydash as _

# internal module
from src.util.DateUtil import DateUtil

# Exceptions
from src.error.Error import *

# const
from src.const.URL_PATH import *

# declare comm variable
logger = logging.getLogger('sLogger')

class NaverDataLabAPI():

    def __init__(self, client_id: str, client_secret: str, uri: str):
        """
        인증키 설정 및 검색어 그룹 초기화
        """
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.base_url: str = BASE_URL['NAVER_DATALAB']
        self.uri = uri
        self.body = {}

    def add_keywords(self, keyword):
        """

        :param group_dict:
        :return:
        """
        try:
            if self.uri == URI['NAVER_DATALAB']['CAT_BY_KW']:
                self.body['keyword'] = keyword
            elif self.uri == URI['NAVER_DATALAB']['SRC']:
                self.body['keywordGroups'] = keyword

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def add_categories(self, category):
        """

        :param group_dict:
        :return:
        """
        try:
            try:
                if self.uri == URI['NAVER_DATALAB']['CAT_BY_KW']:
                    self.body['category'] = category

                elif self.uri == URI['NAVER_DATALAB']['SRC']:
                    self.body['category'] = category

                elif self.uri == URI['NAVER_DATALAB']['CAT']:
                    self.body['category'] = category

            except Exception as e:
                logger.error(traceback.format_exc())
                raise e


        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def get_data(self, startDate: str, endDate: str, timeUnit: str, device='', ages=[], gender=''):
        """
        :return:
        """
        try:
            f_url = self.base_url + self.uri

            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret
            }

            (self.body)['startDate'] = startDate
            (self.body)['endDate'] = endDate
            (self.body)['timeUnit'] = timeUnit
            (self.body)['device'] = device
            (self.body)['ages'] = ages
            (self.body)['gender'] = gender

            body = json.dumps(self.body, ensure_ascii=False)

            response = requests.post(f_url, headers=headers, data=body.encode('utf-8'))

            if response.status_code == 200:
                res = response.json()
                data = res['results'][0]['data']

                # return 되지 않은 date에 대해선 0을 반환하도록 하는 로직 추가
                # 금주 일요일 까지의 데이터만 취득하게 하므로 반환 데이터는 항상 시행 주보다 한주 저번주 월요일이 되어 6을 뺌
                loop_date = (datetime.strptime(endDate, '%Y-%m-%d') - relativedelta(days=6))
                start_date = datetime.strptime(startDate, '%Y-%m-%d')
                res_as_dict = _.group_by(data, 'period')

                while True:
                    if loop_date <= start_date:
                        break
                    else:
                        loop_date_as_str = loop_date.strftime('%Y-%m-%d')
                        if not res_as_dict.get(loop_date_as_str):
                            data.append({'period': loop_date_as_str, 'ratio': 0})

                        loop_date -= relativedelta(weeks=1)

                sorted_data = _.sort_by(data, 'period')

                DateUtil.cut_by_year(sorted_data, 24)

                return sorted_data

            else:
                error_info = json.loads(response.text)

                if error_info['errorCode'] == '010':
                    if self.uri == URI['NAVER_DATALAB']['CAT_BY_KW']:
                        raise NaverDatalabShoppingInsightAPIQuaryOverCallError

                    elif self.uri == URI['NAVER_DATALAB']['SRC']:
                        raise NaverDataLabSearchTrendAPIQuaryOverCallError

                    elif self.uri == URI['NAVER_DATALAB']['CAT']:
                        raise NaverDatalabShoppingInsightAPIQuaryOverCallError

                else:
                    logger.error(error_info['errorMessage'])
                    raise APIcallException(tg_kw = self.body['keyword'], err_code = error_info['errorCode'], msg = error_info['errorMessage'])

        except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
            logger.error(traceback.format_exc())
            raise e

        except NaverDataLabSearchTrendAPIQuaryOverCallError as e:
            logger.error(traceback.format_exc())
            raise e

        except Exception as e:
            logger.error(traceback.format_exc())
            raise e