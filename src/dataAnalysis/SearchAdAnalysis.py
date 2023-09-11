import numpy as np
import pydash as _

# config
from config.development import *

# const
from src.const.URL_PATH import *

class SearchAdAnalysis():
    def __init__(self, tg_data):
        self.tg_data = tg_data

    def get_qc_n_clk_cnt(self):
        data = self.tg_data["keywordList"][0]

        pc_qc_cnt = data.get('monthlyPcQcCnt') if type(data.get('monthlyPcQcCnt')) == int else 10
        mb_qc_cnt = data.get('monthlyMobileQcCnt') if type(data.get('monthlyMobileQcCnt')) == int else 10
        pc_clk_cnt = data.get('monthlyAvePcClkCnt') if type(data.get('monthlyAvePcClkCnt')) == int else 10
        mb_clk_cnt = data.get('monthlyAveMobileClkCnt') if type(data.get('monthlyAveMobileClkCnt')) == int else 10

        qc_cnt = pc_qc_cnt + mb_qc_cnt + pc_clk_cnt + mb_clk_cnt

        return qc_cnt

    def add_qc_cnt(self):
        data = self.tg_data["keywordList"]

        for d in data:
            pc_qc_cnt = d.get('monthlyPcQcCnt') if type(d.get('monthlyPcQcCnt')) == int else 10
            mb_qc_cnt = d.get('monthlyMobileQcCnt') if type(d.get('monthlyMobileQcCnt')) == int else 10

            d['qcCnt'] = pc_qc_cnt + mb_qc_cnt

        return data

    def get_qc_cnt(self):
        data = self.tg_data["keywordList"][0]

        pc_qc_cnt = data.get('monthlyPcQcCnt') if type(data.get('monthlyPcQcCnt')) == int else 10
        mb_qc_cnt = data.get('monthlyMobileQcCnt') if type(data.get('monthlyMobileQcCnt')) == int else 10

        qc_cnt = pc_qc_cnt + mb_qc_cnt

        return qc_cnt
    def get_n_months_cnt(self, a_month_cnt, cnt_trend):
        try:
            if a_month_cnt and cnt_trend:
                last_4_weeks_value_in_trend: list = cnt_trend[-4:]
                sum_last_4_weeks_value = _.sum_by(last_4_weeks_value_in_trend, 'ratio')
                cnt_by_one = a_month_cnt / sum_last_4_weeks_value if not sum_last_4_weeks_value == 0 else 0

                n_month_cnt = 0
                for one_month_trend in cnt_trend:
                    n_month_cnt += one_month_trend['ratio'] * cnt_by_one

                return n_month_cnt
            else:
                return 0

        except Exception as e:
            raise e
    def get_abs_num_trend(self, a_month_cnt, cnt_trend):
        try:
            if a_month_cnt and cnt_trend:
                last_4_weeks_value_in_trend: list = cnt_trend[-4:]
                sum_last_4_weeks_value = _.sum_by(last_4_weeks_value_in_trend, 'ratio')
                cnt_by_one = a_month_cnt / sum_last_4_weeks_value if not sum_last_4_weeks_value == 0 else 0

                abs_num_trend = []
                for one_month_trend in cnt_trend:
                    abs_num_trend.append({
                        "period": one_month_trend['period'],
                        "val": one_month_trend['ratio'] * cnt_by_one
                    })

                return abs_num_trend
            else:
                return []

        except Exception as e:
            raise e

