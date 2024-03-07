class HostNotFoundException(Exception):
    """
    Exception raised when a host is not found in the database.

    Args:
        msg (str, optional): The error message. Defaults to "Host not found".
    """

    def __init__(self, msg: str = "Host not found"):
        super().__init__(msg)


class HostPermissionError(Exception):
    """
    Exception raised when a host does not have the required permissions to perform an operation.

    Args:
        msg (str, optional): The error message. Defaults to "Invalid permissions".
    """

    def __init__(self, msg: str = "Invalid permissions"):
        super().__init__(msg)


class InvalidCredentialsError(Exception):
    """
    Exception raised when invalid credentials are provided for host authentication.

    Args:
        msg (str, optional): The error message. Defaults to "Invalid credentials".
    """

    def __init__(self, msg: str = "Invalid credentials"):
        super().__init__(msg)


class HostAlreadyExistsError(Exception):
    """
    Exception raised when a host already exists with same phone number or email.

    Args:
        msg (str, optional): The error message. Defaults to "Host already exists".
    """

    def __init__(self, msg: str = "Host already exists"):
        super().__init__(msg)
