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
    dt_sets = FsUtil.open_json_2_json_file(root_path + "/public/input/test.json")

    # 계정 정보 import
    naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
    naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']


    result = []
    for dt_set in dt_sets:
        # create rank using keywords
        kwd_with_rank = []
        for i, kwd in enumerate(dt_set["keywords"]):
            kwd_with_rank.append({
                "keyword": kwd,
                "rank": i+1
            })

        for kwd in kwd_with_rank:
            try:
                keyword, rank = kwd.values()

                ## 쇼핑인사이트 키워드별 트렌드
                Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret,
                                       URI['NAVER_DATALAB']['CAT_BY_KW'])

                # 날짜 설정
                today = datetime.today()
                diff = (today.weekday() - 6) % 7
                end_date = (today - timedelta(days=diff)).strftime('%Y-%m-%d')
                start_date = ((today - timedelta(days=diff)) - relativedelta(months=36)).strftime(
                    '%Y-%m-%d')

                # 쇼핑인사이트 키워드별 트렌드 데이터 수집
                Ndla.add_keywords([{"name": keyword, "param": [keyword]}])
                Ndla.add_categories(dt_set['cat_code'])
                api_r_ndla = Ndla.get_data(start_date, end_date, 'week')

                ## analyze std & growth rate
                for d in api_r_ndla:
                    ll_r = {}
                    period = d['period']
                    value = d['ratio']

                    ## analyze std & growth rate
                    ll_r['cat_code'] = dt_set['cat_code']
                    ll_r['keyword'] = keyword
                    ll_r['rank'] = rank
                    ll_r['date'] = period
                    ll_r['value'] = value

                    result.append(ll_r)

                logger.debug(dt_set['cat_code'] + ":" + keyword + ": done")

            except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
                # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
                kwd_with_rank.append(kwd)

                # 셀레늄 통한 아이디 재생성
                Nakc = NaverApiKeyCreator('NAVER_DATALAB_SHOPPING_INSIGHT')
                client_id, client_secret = Nakc.get_new_key().values()

                naver_datalab_shp_insight_api_c_id = client_id
                naver_datalab_shp_insight_api_c_secret = client_secret
                pass

            except Exception as e:
                logger.error(traceback.format_exc())
                pass

    FsUtil.save_json_2_csv_file(result, root_path + "/public/output/test2.csv")
except Exception as e:
    raise e

