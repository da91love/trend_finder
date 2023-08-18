import csv, json
import pandas as pd
import numpy as np
from pandas.errors import EmptyDataError

class FsUtil:
    @staticmethod
    def save_json_2_csv_file(json_data: list, csv_dir: str, index=False):
        try:
            df = pd.DataFrame.from_dict(json_data)
            df = df.fillna('')
            df.to_csv(csv_dir, index=index)

            # writer = csv.writer(open(csv_dir, 'w', newline='', encoding=encoding))
            # writer.writerow(json_data[-1].keys())
            # for row in json_data:
            #     writer.writerow(row.values())

        except Exception as e:
            raise e

    @staticmethod
    def save_json_2_json_file(json_data: list, json_dir: str, encoding: str):
        try:
            json_result = json.dumps(json_data, ensure_ascii=False)
            with open(json_dir, "w", encoding=encoding) as f:
                f.write(json_result)
                f.close()
        except Exception as e:
            raise e

    @staticmethod
    def open_csv_2_json_file(csv_dir: str, data_type='records'):
        try:
            # df_imported_data = pd.read_csv(csv_dir)
            # nan_2_none = df_imported_data.replace([np.nan], [None])
            # result: list = nan_2_none.to_dict(data_type)
            #
            # return result
            result = []
            with open(csv_dir, 'r', encoding='"utf8"') as data:
                for line in csv.DictReader(data):
                    result.append(dict(line))

            return result
        except EmptyDataError:
            return []

        except Exception as e:
            raise e

    @staticmethod
    def open_json_2_json_file(csv_dir: str):
        with open(csv_dir, 'r', encoding='UTF8') as file:
            data = json.load(file)
            return data