
class APIcallException(Exception):
    def __init__(self, tg_kw: str, err_code: str = "", msg = "API call fails"):
        super().__init__(self, msg)

class MissingCategoryException(Exception):
    def __init__(self, cat_info, msg = "Matched category is not found"):
        super().__init__(self, msg)
        self.cat_info = cat_info

    def __str__(self):
        return repr(self.cat_info)

class NoItemFoundException(Exception):
    def __init__(self, msg = "Posted item is not found"):
        super().__init__(self, msg)

class NaverSearchAPIQuaryOverCallError(Exception):
    def __init__(self, msg = "naver search api over call error"):
        super().__init__(self, msg)

class NaverDataLabSearchTrendAPIQuaryOverCallError(Exception):
    def __init__(self, msg = "naver search api over call error"):
        super().__init__(self, msg)

class NaverDatalabShoppingInsightAPIQuaryOverCallError(Exception):
    def __init__(self, msg = "naver search api over call error"):
        super().__init__(self, msg)