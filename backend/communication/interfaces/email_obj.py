from abc import abstractmethod
from communication.interfaces.communication_obj import CommunicationClient


class EmailCommunicationClient(CommunicationClient):
    @abstractmethod
    def send(cls, to_email: str, subject: str, body: str, from_email: str):
        pass