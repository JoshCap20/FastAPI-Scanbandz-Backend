class EventNotFoundException(Exception):
    """
    Exception raised when an event is not found.

    Args:
        id (int | str): The ID of the event that was not found.
    """

    def __init__(self, id: int | str):
        super().__init__(f"Event not found: {id}")
