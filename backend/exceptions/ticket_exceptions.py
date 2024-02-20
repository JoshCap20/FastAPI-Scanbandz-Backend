class TicketNotFoundException(Exception):
    def __init__(self, msg: str = "Ticket not found"):
        super().__init__(msg)


class TicketRegistrationClosedException(Exception):
    def __init__(self, msg: str = "Ticket registration is closed"):
        super().__init__(msg)


class TicketRegistrationFullException(Exception):
    def __init__(self, msg: str = "Ticket registration is full"):
        super().__init__(msg)
