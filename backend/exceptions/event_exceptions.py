class EventNotFoundException(Exception):
    def __init__(self, id: int):
        super().__init__(f"Event not found with ID: {id}")