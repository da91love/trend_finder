# internal modules
import os
import logging
import traceback

# moduels
import pydash as _

# exception
from src.error.Error import *

# const
from src.const.COMM import *
from src.const.LOCAL_PATH import *
from src.const.ERR_MSG import *

# other moduels
from src.util.FsUtil import FsUtil

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = logging.getLogger('sLogger')

class SearchAnalysis():
    def __init__(self, tg_data):
        self.tg_data = tg_data

    def get_channels(self):
        try:
            mall_names = list(map(lambda x: x['mallName'], self.tg_data['items']))
            uniq_mall_names = _.uniq(mall_names)

            return uniq_mall_names

        except Exception as e:
            raise e
    def get_avg_price(self):
        try:
            items_price = list(map(lambda x: int(x['lprice']), self.tg_data['items']))
            items_price.sort()

            # 상하위 10% index 추출
            lower_10_index = int(len(items_price) * 0.1) - 1
            upper_10_index = int(len(items_price) * 0.9) + 1

            # list slicing
            sliced_items_price = items_price[lower_10_index : upper_10_index]
            avg_price = sum(sliced_items_price) / len(sliced_items_price)

            return  avg_price

        except Exception as e:
            raise e


    def get_categories(self, tg_cat_num: int = 100):
        """
        frequency가 0.2가 넘는 카테고리를 list로 반환
        :return: list:
        """
        try:
            # 가능성 높은 category 추출
            all_cat_names:list = []
            num_by_cat_name:list = []

            # 쇼핑몰 검색 안될 시 None 리턴
            if len(self.tg_data['items']) == 0:
                raise NoItemFoundException()

            # display 갯수만큼 items 수 cut
            items = []
            for idx, item in enumerate(self.tg_data['items']):
                if idx < tg_cat_num:
                    items.append(item)

            # full cat name list 작성
            for item in items:
                cat_list = []
                for cat_key in CAT_KEY_NAMES:
                    if not _.is_empty(item[cat_key]):
                        cat_list.append(item[cat_key])

                cat_name: str = '_'.join(cat_list)
                all_cat_names.append(cat_name)

            # cat name 별 등장 횟수 계산
            uniq_cat_names: list = _.uniq(all_cat_names)

            # get brand code
            for cat_name in uniq_cat_names:
                t = {}
                t['cat_name'] = cat_name
                t['frequency'] = all_cat_names.count(cat_name) / len(items)

                num_by_cat_name.append(t)

            # select final cat names
            # 카테고리 프리퀀시가 10% 이상 시 카테고리로 인정
            selected_cats = []
            for cat in num_by_cat_name:
                if cat['frequency'] >= 0.1:
                    selected_cats.append(cat)

            # set category code
            brand_codes: dict = FsUtil.open_json_2_json_file(root_path + CAT_CODE_JSON_DATA_PATH)
            cat_infos = []
            for selected_cat in selected_cats:

                # max_num_cat = _.max_by(num_by_cat_name, 'frequency')
                devided_cat = (selected_cat.get('cat_name')).split('_')

                category1 = devided_cat[0]
                category2 = devided_cat[1]
                category3 = devided_cat[2]
                category4 = devided_cat[3] if len(devided_cat) > 3 else ''

                cat_info = {'category1': category1, 'category2': category2, 'category3': category3, 'category4': category4,}


                try:
                    cat_code = None
                    matched_cat3 = (((brand_codes.get(category1)).get(category2)).get(category3))
                    if _.is_string(matched_cat3):
                        cat_code = matched_cat3

                    elif _.is_dict(matched_cat3):
                        matched_cat4 = (((brand_codes.get(category1)).get(category2)).get(category3)).get(category4)

                        if _.is_string(matched_cat4):
                            cat_code = matched_cat4

                        else:
                            # cats_in_upper_cat3 = list(
                            #     (((brand_codes.get(category1)).get(category2)).get(category3)).keys())
                            # cat_code = (((brand_codes.get(category1)).get(category2)).get(category3))[
                            #     cats_in_upper_cat3[0]]
                            logger.error(NO_CAT_FOUND_ERR_MSG + category1 + category2 + category3 + category4)

                            raise MissingCategoryException(cat_info=cat_info)
                    else:
                        logger.error(NO_CAT_FOUND_ERR_MSG + category1 + category2 + category3 + category4)
                        raise MissingCategoryException(cat_info=cat_info)

                except Exception:
                    logger.error(traceback.format_exc())
                    raise MissingCategoryException(cat_info)

                cat_info['frequency'] = selected_cat.get('frequency')
                cat_info['cat_code'] = cat_code

                cat_infos.append(cat_info)

            return cat_infos

        except Exception as e:
            raise e
