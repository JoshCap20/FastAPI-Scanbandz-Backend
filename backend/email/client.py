from services.azure import AzureEmailCommunicationClient

class EmailClient:
    client = AzureEmailCommunicationClient

    @classmethod
    def send_email(cls, to_email: str, subject: str, body: str, from_email: str = "tickets@scanbandz.com"):
        return cls.client.send_email(to_email=to_email, subject=subject, body=body, from_email=from_email)