import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import pydash as _

# config
from config.development import *

# const
from src.const.URL_PATH import *

# modules
from src.util.CollectionUtil import *

class DataLabAnalysis():
    def __init__(self, uri, tg_data):
        self.uri = uri
        self.tg_data = tg_data

    def get_std(self):
        data = self.tg_data

        if data:
            # std의 경우 1년간의 시즌성만 나타내기 때문에 n년, n-1년, n-2년 .. 데이터가 data로 들어올 경우 가장 첫번째 있는 n년 째 데이터만 취급
            # 이 때문에 data[0]
            cleaned_data = self._extract_ratio(data[0])
            std = np.std(cleaned_data)

            # 실제 계산 시 표준편차가 0 나오면 데이터 유실 막기 위해 0.1로 환산
            if std == 0:
                std = 0.1

            return std
        else:
            return None

    def get_growth_rate(self):
        data = self.tg_data

        # 1년 성장률을 표현해야 하므로 1년 마다 sum
        # 단, 최근 1년 간의 성장률만 취급
        data_by_12m = _.sum_by(data[0], 'ratio')
        data_by_24m = 1 if _.sum_by(data[1], 'ratio') == 0 else _.sum_by(data[1], 'ratio')

        if data:
            # # 최소2승법은 날짜로는 계산 못하므로 날짜에는 단순 range 숫자 추가
            # df = pd.DataFrame(
            #     {'period': [i for i in range(len(data))],
            #      'ratio': map(lambda x: x['ratio'], data)
            #      }
            # )
            #
            # # 선형회귀 통한 기울기
            # fit = ols('ratio ~ period', data=df).fit()
            # slope = fit.params.period

            growth_rate = (data_by_12m / data_by_24m) -1

            return growth_rate
        else:
            return None

    def _extract_ratio(self, data):
        if self.uri == URI["NAVER_DATALAB"]["SRC"]:
            r = list(map(lambda x:x['ratio'],data))

        elif self.uri == URI['NAVER_DATALAB']['CAT_BY_KW']:
            r = list(map(lambda x:x['ratio'],data))

        elif self.uri == URI['NAVER_DATALAB']['CAT']:
            r = list(map(lambda x:x['ratio'],data))

        return r
