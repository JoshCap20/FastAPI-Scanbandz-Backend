from ...exceptions.communication_exceptions import EmailFailureException
from ..interfaces.email_obj import EmailCommunicationClient
from .services.azure import AzureEmailCommunicationClient


class EmailInterface(EmailCommunicationClient):
    client = AzureEmailCommunicationClient

    @classmethod
    def send(
        cls,
        to_email: str,
        subject: str,
        message: str,
        from_email: str = "tickets@scanbandz.com",
        mime_type: str = "text/plain",
    ) -> bool:
        try:
            cls.client.send_email(
                to_email=to_email,
                subject=subject,
                message=message,
                from_email=from_email,
                mime_type=mime_type,
            )
            return True
        except EmailFailureException as ex:
            cls.handle_error(
                to_email=to_email,
                subject=subject,
                message=message,
                from_email=from_email,
                mime_type=mime_type,
            )
            return False

    @classmethod
    def handle_error(
        cls, to_email: str, subject: str, message: str, from_email: str, mime_type: str
    ) -> None:
        # TODO: Log error
        pass
