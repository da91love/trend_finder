# internal modules
import os
import pydash as _
from datetime import datetime
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
from src.const.ERR_MSG import *

# other modules
from src.apiConn.NaverSearchAPI import NaverSearchAPI
from src.apiConn.NaverSearchAdAPI import NaverSearchAdAPI

from src.util.FsUtil import FsUtil

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')

def discover_brand():
    try:
        # prepare variables
        cached_progress_rate = 0
        today = datetime.today().strftime('%Y-%m-%d')

        # get brands name from csv
        kwds_as_json: list = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_KEYWORD_PATH)
        keywords = [i['0'] for i in kwds_as_json] #TODO: dict의 key명을 임시로 0로 설정

        # Get existing brands
        last_finding_brands_info = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_BRAND_PATH)
        last_finding_brands = [brand_info['brand'] for brand_info in last_finding_brands_info]
        # TODO: 현재는 브랜드 이름으로만 중복 필터링하는데 중복되는 브랜드 존재시 어떻게 할지 고민

        # extract brand from keywords
        # brands 변수는 찾은 brands의 전체 info를 dict로 격납, old_brands는 중복 brand 격납 방지 위한 용도로 string 격납
        # old_brands 초기 값으로 기존 찾은 discovered brand 값 사용
        new_brands = []
        old_brands = _.clone_deep(last_finding_brands)
        for idx, keyword in enumerate(keywords):
            try:
                ## call api
                Nsa = NaverSearchAPI(AUTH['NAVER_SEARCH']['SHP']['CLIENT_ID'],
                                     AUTH['NAVER_SEARCH']['SHP']['CLIENT_SECRET'],
                                     URI['NAVER_SEARCH']['SHP'])
                Nsa.add_query(keyword)
                nsa_r = Nsa.get_data(display=100)
                items = nsa_r['items']

                if items:
                    for item in items:
                        t_brand = item['brand']
                        is_t_brand_in_s_brands: bool = t_brand in old_brands

                        if t_brand and not is_t_brand_in_s_brands:
                            brand = {}

                            brand['brand'] = t_brand
                            brand['maker'] = item['maker']
                            brand['keyword'] = keyword
                            brand['category1'] = item['category1']
                            brand['category2'] = item['category2']
                            brand['category3'] = item['category3']
                            brand['category4'] = item['category4']
                            brand['analyze_date'] = today

                            old_brands.append(t_brand)
                            new_brands.append(brand)

                # update progress
                progress_rate = idx/len(keywords)*100

                # TODO: 일시 저장 부분 함수화
                # temp save
                if (progress_rate >= (cached_progress_rate + 20)) or (_.last(keywords) == keyword):
                    # concat with existing data
                    db = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_BRAND_PATH)
                    db += new_brands

                    # save the file
                    FsUtil.save_json_2_csv_file(db, root_path + DISCOVERED_BRAND_PATH)

                    # update progress_rate
                    cached_progress_rate = idx/len(keywords)*100

                    # initiate brands
                    new_brands = []

                    # log
                    logger.debug(FILE_SAVE_SUCCESS_MSG)

                # log
                logger.debug((BRAND_EXTRACT_SUCCESS_MSG + keyword +  '_' + str(_.round_(progress_rate, 2)) + '% (' + str(idx) + '/' + str(len(keywords)) + ')'))

            except APIcallException as e:
                logger.error(traceback.format_exc())
                pass

            except Exception as e:
                logger.error(traceback.format_exc())
                pass

    except Exception as e:
        logger.error(traceback.format_exc())
        raise e

# execute
discover_brand()