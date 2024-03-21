from ...exceptions.communication_exceptions import EmailFailureException
from ..interfaces.email_obj import EmailCommunicationClient
from .services.azure import AzureEmailCommunicationClient
from ...settings.celery_worker import celery_app


@celery_app.task(name="send_email_task")
def send_email_task(
    to_email: str,
    subject: str,
    message: str,
    from_email: str = "tickets@scanbandz.com",
    mime_type: str = "text/plain",
):
    AzureEmailCommunicationClient.send_email(
        to_email=to_email,
        subject=subject,
        message=message,
        from_email=from_email,
        mime_type=mime_type,
    )


class EmailInterface(EmailCommunicationClient):
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
            # Enqueue the email sending task
            send_email_task.delay(
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
            # Consider how you want to handle failures in enqueuing tasks
            return False

    @classmethod
    def handle_error(
        cls, to_email: str, subject: str, message: str, from_email: str, mime_type: str
    ) -> None:
        # TODO: Log error
        pass
