# internal modules
import os
import pydash as _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging.config
import logging
import traceback
import requests
from bs4 import BeautifulSoup
import time
import multiprocessing

# error
from src.error.Error import *

# config
from config.development import *

# const
from src.util.FsUtil import FsUtil
from src.const.ERR_MSG import *

# other modules
from src.apiConn.NaverDataLabAPI import NaverDataLabAPI

# declare comm variable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(os.path.join(root_path, 'logging.ini'))
logger = logging.getLogger('sLogger')


def cosmeticElePpsCollector(url):
    try:
        res = requests.get(url)
        print(url)
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        table_trs = soup.find('table', class_='table_list').find_all('tr')

        ing_code = ''
        ing_name_kr_new = ''
        ing_name_kr_old = ''
        ing_name_en = ''
        origin_text = ''
        purpose_text = ''
        for idx, tr in enumerate(table_trs):
            th = tr.find_all('th')
            if th[0].get_text() == "성분코드":
                ing_code = (tr.find_all('td')[0].get_text()).replace('\n', '')
            elif th[0].get_text() == "성분명":
                ing_name_kr_new = (tr.find_all('td')[0].get_text()).replace('\n', '')
                if th[1].get_text() == "구명칭":
                    ing_name_kr_old = (tr.find_all('td')[1].get_text()).replace('\n', '')
            elif th[0].get_text() == "영문명":
                ing_name_en = (tr.find_all('td')[0].get_text()).replace('\n', '')
            elif th[0].get_text() == "기원 및 정의":
                origin_text = (tr.find_all('td')[0].get_text()).replace('\n', '')
            elif th[0].get_text() == "배합목적":
                purpose_text = (tr.find_all('td')[0].get_text()).replace('\n', '')


        return {
            "ing_code": ing_code,
            "ing_name_kr_new": ing_name_kr_new,
            "ing_name_kr_old": ing_name_kr_old,
            "ing_name_en": ing_name_en,
            "origin": origin_text,
            "purpose": purpose_text
        }

    except AttributeError as e:
        logger.error("AttributeError pass")
        return {
            "ing_code": '',
            "ing_name_kr_new": '',
            "ing_name_kr_old": '',
            "ing_name_en": '',
            "origin": '',
            "purpose": ''
        }

    except Exception as e:
        raise e


ing_nums = [i["ing_num"] for i in FsUtil.open_csv_2_json_file(root_path + "/public/input/ing_num.csv")]
api_urls = []

for ing_num in ing_nums:
    api_urls.append("https://kcia.or.kr/cid/search/ingd_view.php?no=" + str(ing_num))

if __name__ == "__main__":

    # Create a multiprocessing pool with a specified number of processes
    num_processes = 16  # Adjust this based on your system's capabilities
    pool = multiprocessing.Pool(processes=num_processes)

    # Use the pool to send requests to the API URLs
    results = pool.map(cosmeticElePpsCollector, api_urls)

    # Close the pool and wait for the worker processes to finish
    pool.close()
    pool.join()

    # Process the results
    FsUtil.save_json_2_csv_file(results, root_path + "/public/output/ing_info.csv")