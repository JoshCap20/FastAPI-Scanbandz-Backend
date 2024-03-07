class TicketNotFoundException(Exception):
    """
    Exception raised when a ticket is not found.

    Args:
        msg (str, optional): The error message. Defaults to "Ticket not found".
    """

    def __init__(self, msg: str = "Ticket not found"):
        super().__init__(msg)


class TicketRegistrationClosedException(Exception):
    """
    Exception raised when ticket registration is disabled by event host.

    Args:
        msg (str, optional): The error message associated with the exception.
    """

    def __init__(self, msg: str = "Ticket registration is closed"):
        super().__init__(msg)


class TicketRegistrationFullException(Exception):
    """
    Exception raised when the ticket max quantity exceeded.

    Args:
        msg (str, optional): The error message. Defaults to "Ticket registration is full".
    """

    def __init__(self, msg: str = "Ticket registration is full"):
        super().__init__(msg)
