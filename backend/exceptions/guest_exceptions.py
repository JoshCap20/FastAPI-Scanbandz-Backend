class GuestNotFoundException(Exception):
    def __init__(self, msg: str = "Guest not found"):
        super().__init__(msg)