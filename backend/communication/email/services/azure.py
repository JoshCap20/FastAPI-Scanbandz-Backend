from azure.communication.email import EmailClient
from exceptions.communication_exceptions import EmailFailureException
from settings.env import getenv

class AzureEmailCommunicationClient:
    client: EmailClient = EmailClient.from_connection_string(getenv("AZURE_EMAIL_CONNECTION_KEY")) # type: ignore

    @classmethod
    def send_email(cls, to_email: str, from_email: str, subject: str, body: str) -> None:
        message = cls.create_email_message(to_email, from_email, subject, body)
        try:
            cls.client.begin_send(message)
        except Exception as ex:
            raise EmailFailureException(str(ex))
    
    @classmethod
    def create_email_message(cls, to_email: str, from_email: str, subject: str, body: str) -> dict:
        return {
                "senderAddress": from_email,
                "recipients": {
                    "to": [{"address": to_email}],
                },
                "content": {
                    "subject": subject,
                    "plainText": body,
                },
                "replyTo": [
                    {
                        "address": "support@scanbandz.com",
                        "displayName": "ScanBandz Support",
                    }
                ],
            }

