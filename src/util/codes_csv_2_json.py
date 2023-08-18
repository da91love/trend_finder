# internal modules
import os

# moduels
import numpy as np
import pydash as _

# const
from src.const.LOCAL_PATH import *

# other moduels
from src.util.FsUtil import FsUtil

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def convert_cat_csv_2_json():
    r = {}
    brand_codes: list = FsUtil.open_csv_2_json_file(root_path + CAT_CODE_CSV_DATA_PATH)

    cat1_by_g = _.group_by(brand_codes, 'category1')
    for cat1 in cat1_by_g.keys():
        codes_in_cat1 = cat1_by_g[cat1]
        r[cat1] = {}

        cat2_by_g = _.group_by(codes_in_cat1, 'category2')
        for cat2 in cat2_by_g.keys():
            codes_in_cat2 = cat2_by_g[cat2]
            r[cat1][cat2] = {}

            cat3_by_g = _.group_by(codes_in_cat2, 'category3')
            for cat3 in cat3_by_g.keys():
                codes_in_cat3 = cat3_by_g[cat3]
                r[cat1][cat2][cat3] = {}

                for code in codes_in_cat3:
                    if code['category4'] == '':
                        # print(code['cat_code'])
                        r[cat1][cat2][cat3] = code['cat_code']
                    else:
                        # print(code['cat_code'])
                        r[cat1][cat2][cat3][code['category4']] = code['cat_code']

    FsUtil.save_json_2_json_file(r, root_path + CAT_CODE_JSON_DATA_PATH, '"utf-8"')