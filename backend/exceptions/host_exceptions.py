class HostNotFoundException(Exception):
    def __init__(self, msg: str = "Host not found"):
        super().__init__(msg)