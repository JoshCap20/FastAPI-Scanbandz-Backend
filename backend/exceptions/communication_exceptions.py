class EmailFailureException(Exception):
    def __init__(self, message = "Email failed to send"):
        super().__init__(message)

class SMSFailureException(Exception):
    def __init__(self, message = "SMS failed to send"):
        super().__init__(message)