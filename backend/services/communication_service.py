"""
TODO

Used to send emails and SMS messages to users.

This is a core class, used to send emails and SMS messages.
"""

from ..entities import TicketReceiptEntity
from ..models import Guest
from ..communication import EmailClient


class CommunicationService:
    def __init__(self):
        pass

    def send_email(self, email: str, subject: str, message: str):
        """
        Sends an email to a recipient.

        Args:
            email (str): The email address of the recipient.
            subject (str): The subject of the email.
            message (str): The message to send in the email.

        Returns:
            None
        """
        print(
            f"Sending email:\n\tAddress: {email}\n\tSubject: {subject}\n\tMessage: {message}"
        )
        EmailClient.send(to_email=email, subject=subject, message=message)

    def send_sms(self, phone_number: str, message: str):
        """
        Sends an SMS message to a recipient.

        Args:
            phone_number (str): The phone number of the recipient.
            message (str): The message to send in the SMS.

        Returns:
            None
        """
        print(f"Sending SMS:\n\tNumber: {phone_number}\n\tMessage: {message}")

    def send_ticket_payment_receipt(self, ticket_receipt_entity: TicketReceiptEntity):
        """
        Sends a ticket payment receipt to the guest.

        Args:
            ticket_receipt (TicketReceipt): The ticket receipt to send.

        Returns:
            None
        """
        # TODO: Better email templates
        email: str = ticket_receipt_entity.guest.email
        quantity: int = ticket_receipt_entity.quantity
        total_paid: float = ticket_receipt_entity.total_paid

        event_name: str = ticket_receipt_entity.event.name
        ticket_name: str = ticket_receipt_entity.ticket.name

        template: str = f"""
        Thank you for your purchase!
        
        You have successfully purchased {quantity} tickets for the event {event_name}.
        
        Ticket: {ticket_name}
        Quantity: {quantity}
        
        
        Total Paid: ${total_paid}
        """
        return self.send_email(
            email=email, subject="Ticket Payment Receipt", message=template
        )

    def send_guest_ticket_link(self, guest: Guest):
        """
        Sends a link to the guest to download their ticket.

        Args:
            ticket_receipt (TicketReceipt): The ticket receipt to send.

        Returns:
            None
        """
        ticket_link: str = (
            f"https://v2.scanbandz.com/ticket.html?guest={guest.public_key}&event={guest.event.public_key}"
        )

        EMAIL_TEMPLATE: str = f"""
        Here is your ticket link: {ticket_link}
        
        Have a great time at the event!
        """

        self.send_email(
            email=guest.email,
            subject=f"Your Ticket for {guest.event.name}",
            message=EMAIL_TEMPLATE,
        )
