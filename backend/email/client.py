from services.azure import AzureEmailCommunicationClient

class EmailClient:
    def __init__(self):
        self.client = AzureEmailCommunicationClient

    def send_email(self, to_email: str, subject: str, body: str, from_email: str = "tickets@scanbandz.com"):
        return self.client.send_email(to_email=to_email, subject=subject, body=body, from_email=from_email)