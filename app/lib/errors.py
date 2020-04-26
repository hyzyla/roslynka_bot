

class BaseError(Exception):
    def __init__(self, text: str):
        self.text = text
        super().__init__(text)


class BadInput(Exception):
    def __init__(self, text: str):
        self.text = text
        super().__init__(text)
