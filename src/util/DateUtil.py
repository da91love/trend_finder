from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DateUtil:
    @staticmethod
    def cut_by_year(data, tg_period_as_month):
        """
        :param data: 네이버 api 결과 도출된 검색량 trend 데이터
        :param tg_period: 네이버 데이터 취득 시 데이터 검색 기간
        :return:
        """
        try:
            sections = int(tg_period_as_month / 12)

            end_date: str = data[-1]['period']
            start_date: str = None
            year_data = []
            for i in range(0, sections):
                a_year_date = []
                start_date = (datetime.strptime(end_date, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d')
                for d in data:
                    if (start_date < d['period']) and (d['period'] <= end_date):
                        a_year_date.append(d)

                end_date = start_date

                year_data.append(a_year_date)

            return year_data

        except Exception as e:
            raise e



