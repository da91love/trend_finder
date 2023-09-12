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


def getTrendInCat(input):
    keyword, cat_code,start_date, end_date, period = input.values()

    try:
        # 계정 정보 import
        naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
        naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']

        try:

            ## import Class
            Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret, URI['NAVER_DATALAB']['CAT_BY_KW'])

            # 쇼핑인사이트 카태고리 내 키워드별 트렌드 데이터 수집
            Ndla.add_keywords([{"name": keyword, "param": [keyword]}])
            Ndla.add_categories(cat_code)
            api_r_ndla = Ndla.get_data(start_date, end_date, period)

            return api_r_ndla

        except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
            logger.error(traceback.format_exc())
            pass

        except Exception as e:
            logger.error(traceback.format_exc())
            pass

    except Exception as e:
        raise e