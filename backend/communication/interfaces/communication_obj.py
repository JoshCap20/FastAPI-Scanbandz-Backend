from abc import abstractmethod


class CommunicationClient:
    @abstractmethod
    def send(*args, **kwargs) -> bool:
        pass

    @abstractmethod
    def handle_error(*args, **kwargs) -> None:
        pass