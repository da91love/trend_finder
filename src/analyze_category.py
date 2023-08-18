# internal modules
import os
from operator import itemgetter
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
from src.dataAnalysis.DataLabAnalysis import DataLabAnalysis

from util.NaverApiKeyCreator import NaverApiKeyCreator
from util.FsUtil import FsUtil

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')

def analyze_category():
    try:
        # get brands name from csv
        cats: list = FsUtil.open_csv_2_json_file(root_path + CAT_CODE_CSV_DATA_PATH)

        # 계정 정보 import
        naver_dl_shp_inst_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
        naver_dl_shp_inst_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']

        num_of_done_cat = 0
        other_errs_cat = []

        # Loop by brand name
        result = []
        for cat in cats:
            try:
                # create empty dict
                period_result = {}

                # create meta data in variables
                cat_code, cat1, cat2, cat3, cat4 = itemgetter('cat_code', 'category1', 'category2', 'category3', 'category4')(cat)
                cat_name = '_'.join([cat1, cat2, cat3, cat4])
                period_result = _.clone_deep(cat)
                logger.debug(cat_name + ': start')

                ## create params
                today = datetime.today()
                today_date = today.strftime('%Y-%m-%d')

                for period in PERIODS_4_CAT:
                    ## 쇼핑인사이트 키워드별 트렌드 조회 call api
                    Ndla = NaverDataLabAPI(naver_dl_shp_inst_api_c_id, naver_dl_shp_inst_api_c_secret, URI['NAVER_DATALAB']['CAT'])
                    Ndla.add_categories([{"name": cat_name, "param": [cat_code]}])

                    ## create end date and start date: end date as latest sunday
                    diff = (today.weekday() - 6) % 7
                    end_date = (today - timedelta(days=diff)).strftime('%Y-%m-%d')
                    start_date = (datetime.today() - relativedelta(months=period)).strftime('%Y-%m-%d')

                    ## 쇼핑인사이트 get data
                    api_r = Ndla.get_data(startDate=start_date, endDate=end_date, timeUnit='week')

                    ## analyze std & growth rate
                    Dla = DataLabAnalysis(URI['NAVER_DATALAB']['CAT'], api_r)
                    std = Dla.get_std()
                    g_rate = Dla.get_growth_rate()

                    period_result['std_' + str(period)] = std
                    period_result['growth_rate_' + str(period)] = g_rate

                ## add analyzed date
                period_result['analyze_date'] = today_date

                ## add to result
                result.append(period_result)

                # log
                num_of_done_cat += 1
                process = str(_.round_(num_of_done_cat/len(cats) * 100, 2))
                logger.debug(cat_name + ': ' + process + '% done')

            except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
                # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
                cats.append(cat)

                # 셀레늄 통한 아이디 재생성
                Nakc = NaverApiKeyCreator('NAVER_DATALAB_SHOPPING_INSIGHT')
                client_id, client_secret = Nakc.get_new_key().values()

                naver_dl_shp_inst_api_c_id = client_id
                naver_dl_shp_inst_api_c_secret = client_secret
                pass

            except APIcallException as e:
                other_errs_cat.append(cat)
                logger.error(traceback.format_exc())
                logger.error(CAT_EXTRACT_FAIL_ERR_MSG + cat['cat_code'])
                pass

            except Exception as e:
                other_errs_cat.append(cat)
                logger.error(traceback.format_exc())
                logger.error(CAT_EXTRACT_FAIL_ERR_MSG + cat['cat_code'])
                pass

        # save as csv
        FsUtil.save_json_2_csv_file(other_errs_cat, root_path + OTHER_ERRORS_CAT_PATH)

        # save as csv
        FsUtil.save_json_2_csv_file(result, root_path + CAT_ANALYZED_DATA_PATH)

    except Exception as e:
        raise e

# execute function
analyze_category()