# internal modules
import os
import time
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

def discover_keyword():
    try:
        # prepare variables
        today = datetime.today().strftime('%Y-%m-%d')

        # get brands name from csv
        cats: list = FsUtil.open_csv_2_json_file(root_path + CAT_CODE_CSV_DATA_PATH)

        # TODO: 카테고리 분해 로직 외부 함수화
        # extract all keywords from category
        keywords = []
        searched_cats = []
        for cat in cats:
            for key in ['category1','category2','category3','category4']:
                s_cat = cat[key]

                if (not s_cat in searched_cats) and (s_cat):
                    if '/' in s_cat:
                        splited = s_cat.split('/')
                        for kwd in splited:
                            if not kwd in keywords:
                                keywords.append(kwd)

                        searched_cats.append(s_cat)
                    else:
                        if not s_cat in keywords:
                            keywords.append(s_cat)

                        searched_cats.append(s_cat)

        # TODO: 연관검색어 통해 브랜드 추출 로직 추가
        num_of_kwd = len(keywords)
        improved_kw = []
        for idx, keyword in enumerate(keywords):
            try:
                logger.debug(keyword + ': start')
                # call api
                Nsap = NaverSearchAdAPI(AUTH['NAVER_SEARCH_AD']['CUSTOMER_ID'],
                                       AUTH['NAVER_SEARCH_AD']['ACCESS_LICENSE'],
                                       AUTH['NAVER_SEARCH_AD']['SECRET_KEY'],
                                       URI['NAVER_SEARCH_AD']['KWT'])
                Nsap.add_keywords([keyword])

                # get data
                nasap_r = Nsap.get_data()

                # <10 로 되어 있는 값들 모두 10으로 변경
                for rK in nasap_r['keywordList']:
                    if rK['monthlyMobileQcCnt'] == '< 10':
                        rK['monthlyMobileQcCnt'] = 10

                # 검색수에 따라 sorting
                sorted_nasap_r = _.sort_by(nasap_r['keywordList'], 'monthlyMobileQcCnt', reverse=True)

                # TODO: 더 늘리고 싶으면 커버리지 크게 하면 가능
                rel_keyword_coverage = 0.2
                for i in range(0, int(len(sorted_nasap_r) * rel_keyword_coverage)):
                    rel_keyword = sorted_nasap_r[i]['relKeyword']

                    # 기존 카테고리 활용한 키워드에도 없고, 새로 찾은 improved_kw에도 없으면 추가
                    if not rel_keyword in keywords and not rel_keyword in improved_kw:
                        improved_kw.append(rel_keyword)

                # 네이버 api에서 너무 빨리보내면 에러메세지 보내므로 0.5초 sleep
                time.sleep(0.5)

            except APIcallException as e:
                logger.error(traceback.format_exc())
                pass

            finally:
                # log
                logger.debug(keyword + ': ' + str(_.round_(idx / num_of_kwd * 100, 2)) + '% done')

        keywords += improved_kw

        # Get existing brands
        # last_finding_brands_info = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_KEYWORD_PATH)
        # last_finding_brands = [brand_info['brand'] for brand_info in last_finding_brands_info]
        FsUtil.save_json_2_csv_file(keywords, root_path + DISCOVERED_KEYWORD_PATH)

        # TODO: 현재는 브랜드 이름으로만 중복 필터링하는데 중복되는 브랜드 존재시 어떻게 할지 고민


    except Exception as e:
        logger.error(traceback.format_exc())
        raise e

# execute
discover_keyword()