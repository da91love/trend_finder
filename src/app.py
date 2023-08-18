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
    # get brands name from csv
    # discovered_brands: list = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_BRAND_PATH)
    # brands: list = [ discovered_brand['brand'] for discovered_brand in discovered_brands]
    brands: list = [discovered_brand['brand'] for discovered_brand in FsUtil.open_csv_2_json_file(root_path + BRAND_DATA_PATH)]

    # create empty variable
    result = []
    other_errs_brand = []
    cat_not_found_err_brand = []
    no_item_found_err_brand = []

    # 계정 정보 import
    naver_search_api_c_id = AUTH['NAVER_SEARCH']['SHP']['CLIENT_ID']
    naver_search_api_c_secret = AUTH['NAVER_SEARCH']['SHP']['CLIENT_SECRET']

    naver_datalab_shp_insight_api_c_id = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_ID']
    naver_datalab_shp_insight_api_c_secret = AUTH['NAVER_DATALAB']['SHP_INSIGHT']['CLIENT_SECRET']

    naver_datalab_src_api_c_id = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_ID']
    naver_datalab_src_api_c_secret = AUTH['NAVER_DATALAB']['SRC_TREND']['CLIENT_SECRET']

    naver_search_ad_api_c_id = AUTH['NAVER_SEARCH_AD']['CUSTOMER_ID']
    naver_search_ad_api_acs_license = AUTH['NAVER_SEARCH_AD']['ACCESS_LICENSE']
    naver_search_ad_api_scrt_key = AUTH['NAVER_SEARCH_AD']['SECRET_KEY']

    # Loop by brand name
    for idx, brand in enumerate(brands):
        try:
            logger.debug(brand + ': start')

            # 네이버 API Call 위한 Class instance 생성
            ## 네이버 쇼핑 검색
            Nsa = NaverSearchAPI(naver_search_api_c_id, naver_search_api_c_secret, URI['NAVER_SEARCH']['SHP'])
            ## 쇼핑인사이트 키워드별 트렌드
            Ndla = NaverDataLabAPI(naver_datalab_shp_insight_api_c_id, naver_datalab_shp_insight_api_c_secret,URI['NAVER_DATALAB']['CAT_BY_KW'])
            ## 통합 검색 트렌드
            Ndla_s = NaverDataLabAPI(naver_datalab_src_api_c_id, naver_datalab_src_api_c_secret, URI['NAVER_DATALAB']['SRC'])
            ## 검색 광고 트렌드 (절대 검색량)
            Nsap = NaverSearchAdAPI(naver_search_ad_api_c_id, naver_search_ad_api_acs_license, naver_search_ad_api_scrt_key,URI['NAVER_SEARCH_AD']['KWT'])

            # 네이버 쇼핑 검색 데이터 수집
            Nsa.add_query(brand)
            nsa_r = Nsa.get_data(display=100)
            Sa = SearchAnalysis(nsa_r)

            # 네이버 검색 광고 (절대검색량) 데이터 수집
            Nsap.add_keywords([brand])
            nasap_r = Nsap.get_data()
            Saa = SearchAdAnalysis(nasap_r)

            # 카테고리 추출 로직 Run
            categories = Sa.get_categories(tg_cat_num=30)
            if not categories: continue

            for category in categories:
                # initiate keyword result dict
                kwd_result = _.clone_deep(category)

                # create keywords
                cat_as_kwd = category['category4'] if category['category4'] else category['category3']
                cat_code = category['cat_code']

                # dataLabShoppingInsightKeywordTrend
                # week 데이터는 월요일 ~ 일요일 간 데이터를 취합해서 반환하는데, 예를 들어 수요일날 call 할 경우 월요일 ~ 수요일 데이터만 취득하여 왜곡 발생
                # 이에 따라, 금주 일요일 까지의 데이터만 취득하도록 설정
                today = datetime.today()
                diff = (today.weekday() - 6) % 7
                end_date = (today - timedelta(days=diff)).strftime('%Y-%m-%d')
                start_date = ((today - timedelta(days=diff)) - relativedelta(months=PERIODS_4_BRAND)).strftime('%Y-%m-%d')

                # 쇼핑인사이트 키워드별 트렌드 데이터 수집
                Ndla.add_keywords([{"name": brand, "param": [brand]}])
                Ndla.add_categories(cat_code)
                api_r_ndla = Ndla.get_data(start_date, end_date, 'week')
                cut_by_year_ndla = DateUtil.cut_by_year(api_r_ndla, PERIODS_4_BRAND)

                ## analyze std & growth rate
                Dla = DataLabAnalysis(URI['NAVER_DATALAB']['CAT_BY_KW'], cut_by_year_ndla)
                std = Dla.get_std()
                g_rate = Dla.get_growth_rate()

                # 통합 검색 트렌드 데이터 수집
                # TODO: 쇼핑인사이트 키워드별 데이터는 카테고리 별로 call 해야하지만 통합 검색 트렌드는 카테고리 별로 던질 필요가 없어 api 낭비 중
                Ndla_s.add_keywords([{"groupName": brand, "keywords": [brand]}])
                api_r_ndla_s = Ndla_s.get_data(start_date, end_date, 'week')
                cut_by_year_ndla_s = DateUtil.cut_by_year(api_r_ndla_s, PERIODS_4_BRAND)

                ## analyze std & growth rate
                Dla_s = DataLabAnalysis(URI['NAVER_DATALAB']['SRC'], cut_by_year_ndla_s)
                std_s = Dla_s.get_std()
                g_rate_s = Dla_s.get_growth_rate()

                ## 네이버 쇼핑 검색량과 네이버 검색량에서 추출한 std 및 성장률을 지정 비율로 가중 평균
                weighted_std = NumUtil.weighted_avg([std, std_s], [RATIO_BY_SRC_TYPE['CAT_BY_KW'], RATIO_BY_SRC_TYPE['SRC']])
                weighted_gr = NumUtil.weighted_avg([g_rate, g_rate_s], [RATIO_BY_SRC_TYPE['CAT_BY_KW'], RATIO_BY_SRC_TYPE['SRC']])

                ## 연간 검색량 계산
                ## TODO: 연간 검색량 계산도 카테고리안에서 할 필요 없음
                qc_cnt_by_period = Saa.get_n_months_cnt(Saa.get_qc_n_clk_cnt(), cut_by_year_ndla_s[0])

                ## 쇼핑인사이트 키워드별 및 통합 검색 트렌드 데이터 격납 및 시기별 절대 검색량 격납
                kwd_result['seasonality'] = weighted_std
                kwd_result['growth_rate'] = weighted_gr
                kwd_result['qc_cnt_per_12_month_by_brand'] = qc_cnt_by_period
                kwd_result['qc_cnt_per_12_month_by_cat'] = int(qc_cnt_by_period * kwd_result['frequency'])

                # 수집 데이터 격납
                # 메타 데이터 격납
                kwd_result['brand'] = brand
                kwd_result['search_keyword'] = brand

                ## 쇼핑 검색 데이터 격납
                kwd_result['avg_price'] = Sa.get_avg_price()
                kwd_result['channels_num'] = len(Sa.get_channels())
                kwd_result['channels_name'] = ','.join(Sa.get_channels())

                ## 네이버 광고 검색 데이터 격납
                kwd_result['qc_cnt_per_month_by_brand'] = Saa.get_qc_n_clk_cnt()
                kwd_result['qc_cnt_per_month_by_cat'] = int(Saa.get_qc_n_clk_cnt() * kwd_result['frequency'])

                ## add analyzed date
                kwd_result['analyze_date'] = today.strftime('%Y-%m-%d')

                # Save keyword result to result
                result.append(kwd_result)

                    # DataLabShoppingInsightKeywordByAge
                    # TODO: 연령별 데이터는 중요도 낮으므로 잠시 보류

        # TODO: specify exception name
        except NoItemFoundException as e:
            no_item_found_err_brand.append({'brand': brand})
            logger.error(traceback.format_exc())
            logger.error(BRAND_EXTRACT_FAIL_ERR_MSG + brand)
            pass


        except MissingCategoryException as e:
            cat_not_found_err_brand.append({'brand': brand} | e.cat_info)
            logger.error(traceback.format_exc())
            logger.error(BRAND_EXTRACT_FAIL_ERR_MSG + brand)
            pass

        except NaverSearchAPIQuaryOverCallError as e:
            # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
            brands.append(brand)

            # 셀레늄 통한 아이디 재생성
            Nakc = NaverApiKeyCreator('NAVER_SEARCH_SHOPPING')
            client_id, client_secret = Nakc.get_new_key().values()

            naver_search_api_c_id = client_id
            naver_search_api_c_secret = client_secret
            pass

        except NaverDataLabSearchTrendAPIQuaryOverCallError as e:
            # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
            brands.append(brand)

            # 셀레늄 통한 아이디 재생성
            Nakc = NaverApiKeyCreator('NAVER_DATALAB_SEARCH_TREND')
            client_id, client_secret = Nakc.get_new_key().values()

            naver_datalab_src_api_c_id = client_id
            naver_datalab_src_api_c_secret = client_secret
            pass

        except NaverDatalabShoppingInsightAPIQuaryOverCallError as e:
            # 기존 brand를 brands 리스트 최상단에 추가하여 다시 검색하도록
            brands.append(brand)

            # 셀레늄 통한 아이디 재생성
            Nakc = NaverApiKeyCreator('NAVER_DATALAB_SHOPPING_INSIGHT')
            client_id, client_secret = Nakc.get_new_key().values()

            naver_datalab_shp_insight_api_c_id = client_id
            naver_datalab_shp_insight_api_c_secret = client_secret
            pass

        except Exception as e:
            other_errs_brand.append({'brand': brand})
            logger.error(traceback.format_exc())
            logger.error(BRAND_EXTRACT_FAIL_ERR_MSG + brand)
            pass

        finally:
            # Save as temp
            process_rate: int = (idx + 1) / len(brands)

            isMidSaveDone = T_save.save_file_in_mid(process_rate, [
                {
                    'data': result,
                    'save_path': root_path + BRAND_ANALYZED_DATA_PATH,
                },
                {
                    'data': other_errs_brand,
                    'save_path': root_path + OTHER_ERRORS_BRAND_PATH,
                },
                {
                    'data': no_item_found_err_brand,
                    'save_path': root_path + NO_ITEM_FOUND_BRAND_PATH,
                },
                {
                    'data': cat_not_found_err_brand,
                    'save_path': root_path + CAT_NOT_FOUND_BRAND_PATH,
                },
            ])

            # initiate results
            if isMidSaveDone:
                result = []
                other_errs_brand = []
                cat_not_found_err_brand = []
                no_item_found_err_brand = []

            # log
            logger.debug(brand + ': ' + str(_.round_(process_rate * 100, 2)) + '% done')

except Exception as e:
    raise e