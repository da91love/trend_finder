class CollectionUtil:
    @staticmethod
    def last_by(collection, num):
        try:
            pass

        except Exception as e:
            raise e

    @staticmethod
    def sum_by(collection, num):
        try:
            result = []
            sum = 0
            for idx,col in enumerate(collection):
                if (idx + 1) % num != 0:
                    sum += col
                else:
                    sum += col
                    result.append(sum)
                    sum = 0

            return result
        except Exception as e:
            raise e
