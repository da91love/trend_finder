# internal modules
import os
import pydash as _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging.config
import logging
import traceback

# error
from src.error.Error import *

# config
from config.development import *

# const
from src.const.LOCAL_PATH import *
from src.const.URL_PATH import *
from src.const.COMM import *
from src.const.ERR_MSG import *

# other modules
from src.apiConn.NaverSearchAdAPI import NaverSearchAdAPI
from src.dataAnalysis.SearchAdAnalysis import SearchAdAnalysis

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')


def getRelKeywords(keyword):

    try:
        # 계정 정보 import
        naver_search_ad_api_c_id = AUTH['NAVER_SEARCH_AD']['CUSTOMER_ID']
        naver_search_ad_api_acs_license = AUTH['NAVER_SEARCH_AD']['ACCESS_LICENSE']
        naver_search_ad_api_scrt_key = AUTH['NAVER_SEARCH_AD']['SECRET_KEY']

        try:

            ## import Class
            Nsap = NaverSearchAdAPI(naver_search_ad_api_c_id, naver_search_ad_api_acs_license,naver_search_ad_api_scrt_key, URI['NAVER_SEARCH_AD']['KWT'])

            # 네이버 검색 광고 연관검색어 후집
            Nsap.add_keywords([keyword])
            nasap_r = Nsap.get_data()
            keyword_list = nasap_r.get('keywordList')

            return keyword_list

        except Exception as e:
            logger.error(traceback.format_exc())
            pass

    except Exception as e:
        raise e

a = getRelKeywords('12grabs')
print(a)