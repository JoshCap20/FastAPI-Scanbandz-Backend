class TicketNotFoundException(Exception):
    def __init__(self, msg: str = "Ticket not found"):
        super().__init__(msg)