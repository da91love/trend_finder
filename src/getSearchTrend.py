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
from src.apiConn.NaverDataLabAPI import NaverDataLabAPI

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')


def getSearchTrend(input):
    keyword = input.get('keyword')
    start_date = input.get('start_date')
    end_date = input.get('end_date')
    period = input.get('period')
    age = input.get('age')
    gender = input.get('gender')

    try:
        # 계정 정보 import
        naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_ID']
        naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_SECRET']

        try:

            ## import Class
            Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret, URI['NAVER_DATALAB']['SRC'])

            # 쇼핑인사이트 카태고리 내 키워드별 트렌드 데이터 수집
            Ndla.add_keywords([{"groupName": keyword, "keywords": [keyword]}])
            api_r_ndla = Ndla.get_data(startDate=start_date, endDate=end_date, timeUnit=period, gender=gender, ages=age)

            return api_r_ndla

        except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
            logger.error(traceback.format_exc())
            pass

        except Exception as e:
            logger.error(traceback.format_exc())
            pass

    except Exception as e:
        raise e