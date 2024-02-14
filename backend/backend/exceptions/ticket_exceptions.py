class TicketNotFoundException(Exception):
    def __init__(self, msg: str = "Ticket not found with ID"):
        super().__init__(msg)