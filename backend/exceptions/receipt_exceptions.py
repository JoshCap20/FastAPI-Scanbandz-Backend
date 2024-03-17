class ReceiptNotFoundException(Exception):
    """
    Exception raised when a queried receipt is not found.
    """
    def __init__(self, msg: str = "Receipt not found"):
        super().__init__(msg)