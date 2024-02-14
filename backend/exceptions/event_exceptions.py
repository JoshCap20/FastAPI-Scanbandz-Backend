class EventNotFoundException(Exception):
    def __init__(self, id: int | str):
        super().__init__(f"Event not found: {id}")