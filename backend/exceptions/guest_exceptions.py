class GuestNotFoundException(Exception):
    """
    Exception raised when a guest is not found.

    Args:
        msg (str, optional): Custom error message. Defaults to "Guest not found".
    """

    def __init__(self, msg: str = "Guest not found"):
        super().__init__(msg)


class IllegalGuestOperationException(Exception):
    """
    Exception raised when an illegal operation is performed by a guest (registering for an event that is not open, etc).

    Args:
        msg (str, optional): Custom error message. Defaults to "Illegal guest operation".
    """

    def __init__(self, msg: str = "Illegal guest operation"):
        super().__init__(msg)


class NoAvailableTicketsException(Exception):
    """
    Exception raised when there are no available tickets.

    Args:
        msg (str, optional): Custom error message. Defaults to "No available tickets".
    """

    def __init__(self, msg: str = "No available tickets"):
        super().__init__(msg)
