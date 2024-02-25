class HostNotFoundException(Exception):
    def __init__(self, msg: str = "Host not found"):
        super().__init__(msg)


class HostPermissionError(Exception):
    def __init__(self, msg: str = "Invalid permissions"):
        super().__init__(msg)


class InvalidCredentialsError(Exception):
    def __init__(self, msg: str = "Invalid credentials"):
        super().__init__(msg)


class HostAlreadyExistsError(Exception):
    def __init__(self, msg: str = "Host already exists"):
        super().__init__(msg)
