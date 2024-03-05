class GuestNotFoundException(Exception):
    def __init__(self, msg: str = "Guest not found"):
        super().__init__(msg)


class IllegalGuestOperationException(Exception):
    def __init__(self, msg: str = "Illegal guest operation"):
        super().__init__(msg)


class NoAvailableTicketsException(Exception):
    def __init__(self, msg: str = "No available tickets"):
        super().__init__(msg)
