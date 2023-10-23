from exceptions.communication_exceptions import EmailFailureException
from communication.interfaces.email_obj import EmailCommunicationClient
from services.azure import AzureEmailCommunicationClient

class EmailClient(EmailCommunicationClient):
    client = AzureEmailCommunicationClient

    @classmethod
    def send(cls, to_email: str, subject: str, body: str, from_email: str = "tickets@scanbandz.com"):
        try:
            cls.client.send_email(to_email=to_email, subject=subject, body=body, from_email=from_email)
        except EmailFailureException as ex:
            cls.handle_error(to_email=to_email, subject=subject, body=body, from_email=from_email)

    @classmethod
    def handle_error(cls, to_email: str, subject: str, body: str, from_email: str) -> None:
        # TODO: Log error
        pass
    