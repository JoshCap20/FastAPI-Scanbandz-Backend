class InvalidMediaTypeException(Exception):
    """
    Exception raised when an invalid media type is provided.

    Args:
        message (str, optional): The error message. Defaults to 'Invalid media type'.
    """

    def __init__(self, message: str = "Invalid media type"):
        super().__init__(message)