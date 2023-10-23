from abc import abstractmethod


class CommunicationClient:
    @abstractmethod
    def send(*args, **kwargs):
        pass

    @abstractmethod
    def handle_error(*args, **kwargs):
        pass