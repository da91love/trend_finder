import pydash as _
import math
class NumUtil():
    @staticmethod
    def is_digit(target):
        try:
            # 숫자 vs str, None 등 구분
            float(target)

            # nan 구분
            if not math.isnan(target):
                return True
            else:
                return False

        except Exception:
            return False

    @staticmethod
    def c_float_if_digit(target):
        try:
          c_float = float(target)
          return c_float
        except Exception:
          return target


    @staticmethod
    def weighted_avg(num: list, ratio: list):
        try:
            weigh = 0

            # validation
            non_valid_idx = []
            for i in range(len(num)):
                if not NumUtil.is_digit(num[i]):
                    non_valid_idx.append(i)

            # Create validated num and ratio list
            valid_num = [i for j, i in enumerate(num) if j not in non_valid_idx]
            valid_ratio = [i for j, i in enumerate(ratio) if j not in non_valid_idx]


            # distribute non-valid ratio to valid ratio
            if non_valid_idx:
                non_valid_ratio = 0
                for i in non_valid_idx:
                    non_valid_ratio += ratio[i]

                non_valid_ratio = non_valid_ratio / len(valid_num)

                for i in range(len(valid_ratio)):
                    valid_ratio[i] += non_valid_ratio

            for i in range(len(valid_num)):
                weigh += valid_num[i] * valid_ratio[i]

            return weigh

        except ZeroDivisionError:
            return None

        except Exception as e:
            raise e