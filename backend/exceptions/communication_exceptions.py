class EmailFailureException(Exception):
    """
    Exception raised when an email fails to send.

    Args:
        message (str): Optional. The error message associated with the exception.
    """

    def __init__(self, message="Email failed to send"):
        super().__init__(message)


class SMSFailureException(Exception):
    """
    Exception raised when an SMS fails to send.

    Args:
        message (str): Optional. The error message associated with the exception.
    """

    def __init__(self, message="SMS failed to send"):
        super().__init__(message)
