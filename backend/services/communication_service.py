from communication.email.client import EmailClient


class CommunicationService:
    @staticmethod
    def send_email(to_email: str, subject: str, message: str) -> bool:
        return EmailClient.send(to_email=to_email, subject=subject, message=message)
    
    @staticmethod
    def send_sms(to_phone_number: str, body: str) -> bool:
        # TODO: Implement SMS client
        return True