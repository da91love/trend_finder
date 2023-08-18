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
from src.apiConn.NaverSearchAPI import NaverSearchAPI
from src.apiConn.NaverSearchAdAPI import NaverSearchAdAPI

from src.dataAnalysis.DataLabAnalysis import DataLabAnalysis
from src.dataAnalysis.SearchAnalysis import SearchAnalysis
from src.dataAnalysis.SearchAdAnalysis import SearchAdAnalysis

from util.FsUtil import FsUtil
from util.NumUtil import NumUtil
from util.DateUtil import DateUtil
from util.TempSave import TempSave
from util.NaverApiKeyCreator import NaverApiKeyCreator

from util.codes_csv_2_json import convert_cat_csv_2_json

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')

# prepare import data
convert_cat_csv_2_json()

# declare instance
T_save = TempSave()

try:
    dt_sets = FsUtil.open_csv_2_json_file(root_path + "/public/input/test.csv")

    # 계정 정보 import
    naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
    naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']


    result = []
    for dt_set in dt_sets:
        # create rank using keywords

        try:
            cat_code,category1,category2,category3,category4 = dt_set.values()

            ## 쇼핑인사이트 키워드별 트렌드
            Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret,
                                   URI['NAVER_DATALAB']['CAT'])

            # 날짜 설정
            today = datetime.today()
            diff = (today.weekday() - 6) % 7
            end_date = (today - timedelta(days=diff)).strftime('%Y-%m-%d')
            start_date = ((today - timedelta(days=diff)) - relativedelta(months=PERIODS_4_BRAND)).strftime(
                '%Y-%m-%d')

            # 쇼핑인사이트 키워드별 트렌드 데이터 수집
            Ndla.add_categories([{"name": cat_code, "param": [cat_code]}])
            api_r_ndla = Ndla.get_data(start_date, end_date, 'week')
            cut_by_year_ndla = DateUtil.cut_by_year(api_r_ndla, PERIODS_4_BRAND)

            ## analyze std & growth rate
            Dla = DataLabAnalysis(URI['NAVER_DATALAB']['CAT_BY_KW'], cut_by_year_ndla)
            g_rate = Dla.get_growth_rate()

            ## 격납
            dt_set['growth_rate'] = g_rate

            result.append(dt_set)

            logger.debug(dt_set['cat_code'] + ":" + dt_set['cat_code'] + ": done")

        except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
            # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
            dt_sets.append(dt_set)

            # 셀레늄 통한 아이디 재생성
            Nakc = NaverApiKeyCreator('NAVER_DATALAB_SHOPPING_INSIGHT')
            client_id, client_secret = Nakc.get_new_key().values()

            naver_datalab_shp_insight_api_c_id = client_id
            naver_datalab_shp_insight_api_c_secret = client_secret
            pass

        except Exception as e:
            logger.error(traceback.format_exc())
            pass

    FsUtil.save_json_2_csv_file(result, root_path + "/public/output/test3.csv")
except Exception as e:
    raise e
