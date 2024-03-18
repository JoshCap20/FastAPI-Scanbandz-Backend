from azure.communication.email import EmailClient

from ....exceptions.communication_exceptions import EmailFailureException
from ....settings.config import AZURE_EMAIL_CONNECTION_KEY


class AzureEmailCommunicationClient:
    client: EmailClient = EmailClient.from_connection_string(AZURE_EMAIL_CONNECTION_KEY)

    @classmethod
    def send_email(
        cls,
        to_email: str,
        from_email: str,
        subject: str,
        message: str,
        mime_type: str,
    ) -> None:
        if mime_type == "text/html":
            msg = cls.create_html_email_message(to_email, from_email, subject, message)
        else:
            msg = cls.create_plain_email_message(to_email, from_email, subject, message)

        try:
            cls.client.begin_send(msg)
        except Exception as ex:
            raise EmailFailureException(str(ex))

    @classmethod
    def create_plain_email_message(
        cls, to_email: str, from_email: str, subject: str, message: str
    ) -> dict:
        return {
            "senderAddress": from_email,
            "recipients": {
                "to": [{"address": to_email}],
            },
            "content": {
                "subject": subject,
                "plainText": message,
            },
            "replyTo": [
                {
                    "address": "support@scanbandz.com",
                    "displayName": "ScanBandz Support",
                }
            ],
        }

    @classmethod
    def create_html_email_message(
        cls, to_email: str, from_email: str, subject: str, message: str
    ) -> dict:
        return {
            "senderAddress": from_email,
            "recipients": {
                "to": [{"address": to_email}],
            },
            "content": {
                "subject": subject,
                "html": message,
            },
            "replyTo": [
                {
                    "address": "support@scanbandz.com",
                    "displayName": "ScanBandz Support",
                }
            ],
        }
