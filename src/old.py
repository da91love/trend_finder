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
    dt_sets = FsUtil.open_csv_2_json_file(root_path + "/public/input/keyword.csv")

    # 계정 정보 import
    naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
    naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']

    naver_datalab_src_api_c_id = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_ID']
    naver_datalab_src_api_c_secret = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_SECRET']

    naver_search_ad_api_c_id = AUTH['NAVER_SEARCH_AD']['CUSTOMER_ID']
    naver_search_ad_api_acs_license = AUTH['NAVER_SEARCH_AD']['ACCESS_LICENSE']
    naver_search_ad_api_scrt_key = AUTH['NAVER_SEARCH_AD']['SECRET_KEY']

    result = []
    for dt_set in dt_sets:
        try:
            brand = dt_set['brand']
            cat_code = dt_set['cat_code']

            ## import Class
            Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret, URI['NAVER_DATALAB']['CAT_BY_KW'])
            Ndla_s = NaverDataLabAPI(naver_datalab_src_api_c_id, naver_datalab_src_api_c_secret, URI['NAVER_DATALAB']['SRC'])
            Nsap = NaverSearchAdAPI(naver_search_ad_api_c_id, naver_search_ad_api_acs_license,naver_search_ad_api_scrt_key, URI['NAVER_SEARCH_AD']['KWT'])

            # 네이버 검색 광고 (절대검색량) 데이터 수집
            Nsap.add_keywords([brand])
            nasap_r = Nsap.get_data()
            Saa = SearchAdAnalysis(nasap_r)
            search_vol = Saa.get_qc_cnt()

            # 날짜 설정
            today = datetime.today()
            diff = (today.weekday() - 6) % 7
            end_date = (today - timedelta(days=diff)).strftime('%Y-%m-%d')
            start_date = ((today - timedelta(days=diff)) - relativedelta(months=24)).strftime(
                '%Y-%m-%d')

            # 쇼핑인사이트 카태고리 내 키워드별 트렌드 데이터 수집
            Ndla.add_keywords([{"name": brand, "param": [brand]}])
            Ndla.add_categories(cat_code)
            api_r_ndla = Ndla.get_data(start_date, end_date, 'week')

            # 통합 검색 트렌드 데이터 수집
            Ndla_s.add_keywords([{"groupName": brand, "keywords": [brand]}])
            api_r_ndla_s = Ndla_s.get_data(start_date, end_date, 'week')

            ## 연간 검색량 트렌드 계산
            qc_cnt_by_period = Saa.get_abs_num_trend(search_vol, api_r_ndla_s)

            # Qlik 위한 데이터 가공
            ## 1. 카테고리 내 키워드 트렌드
            for d in api_r_ndla:
                ll_r = {}
                ll_r['brand'] = brand
                ll_r['data_type'] = '쇼핑인사이트_카테고리_검색'
                ll_r['date'] = d['period']
                ll_r['value'] = d['ratio']

                result.append(ll_r)

            ## 2. 네이버 통합검색 절대 검색량
            for d in qc_cnt_by_period:
                ll_r = {}
                ll_r['brand'] = brand
                ll_r['data_type'] = '통합_검색'
                ll_r['date'] = d['period']
                ll_r['value'] = d['val']

                result.append(ll_r)

            logger.debug(brand + ":" + ": done")

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

    FsUtil.save_json_2_csv_file(result, root_path + "/public/output/trend.csv")
except Exception as e:
    raise e