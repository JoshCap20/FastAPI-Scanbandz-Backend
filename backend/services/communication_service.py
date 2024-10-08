"""
Used to send emails and SMS messages to users.
"""

from ..entities import TicketReceiptEntity, RefundReceiptEntity, DonationReceiptEntity, HostEntity
from ..models import Guest
from ..communication import EmailInterface
from ..utils.email_template_render import render_email_template


class CommunicationService:
    def __init__(self):
        pass
    
    ##############################
    ### CORE EMAIL/SMS METHODS ###
    ##############################

    def send_html_email(self, email: str, subject: str, message: str) -> None:
        """
        Sends an HTML email to a recipient.

        Args:
            email (str): The email address of the recipient.
            subject (str): The subject of the email.
            message (str): The message to send in the email.

        Returns:
            None
        """
        EmailInterface.send(
            to_email=email, subject=subject, message=message, mime_type="text/html"
        )

    def send_email(self, email: str, subject: str, message: str) -> None:
        """
        Sends a plain text email to a recipient.

        Args:
            email (str): The email address of the recipient.
            subject (str): The subject of the email.
            message (str): The message to send in the email.

        Returns:
            None
        """
        EmailInterface.send(to_email=email, subject=subject, message=message)

    def send_sms(self, phone_number: str, message: str) -> None:
        """
        Sends an SMS message to a recipient.

        Args:
            phone_number (str): The phone number of the recipient.
            message (str): The message to send in the SMS.

        Returns:
            None
        """
        # TODO: Implement SMS sending
        print(f"Sending SMS:\n\tNumber: {phone_number}\n\tMessage: {message}")

    ##############################
    ### SPECIFIC EMAIL METHODS ###
    ##############################

    def send_ticket_payment_receipt(
        self, ticket_receipt_entity: TicketReceiptEntity
    ) -> None:
        """
        Sends a ticket payment receipt to the guest.

        Args:
            ticket_receipt (TicketReceipt): The ticket receipt to send.

        Returns:
            None
        """
        email: str = ticket_receipt_entity.guest.email

        EMAIL_TEMPLATE = render_email_template(
            template_name="ticket_receipt_email.html",
            variables={
                "event_name": ticket_receipt_entity.event.name,
                "ticket_name": ticket_receipt_entity.ticket.name,
                "quantity": ticket_receipt_entity.quantity,
                "total_paid": ticket_receipt_entity.total_paid,
                "total_price": ticket_receipt_entity.total_price,
                "total_fee": ticket_receipt_entity.total_fee,
                "unit_price": ticket_receipt_entity.unit_price,
            },
        )
        self.send_html_email(
            email=email, subject="Ticket Payment Receipt", message=EMAIL_TEMPLATE
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
            f"https://scanbandz.com/ticket?guest={guest.public_key}&event={guest.event.public_key}"
        )

        EMAIL_TEMPLATE = render_email_template(
            template_name="guest_ticket_email.html",
            variables={
                "ticket_link": ticket_link,
                "event_start_date": guest.event.start.strftime("%B %d, %Y, %I:%M %p"),
                "event_end_date": guest.event.end.strftime("%B %d, %Y, %I:%M %p"),
                "event_name": guest.event.name,
                "ticket_quantity": guest.quantity,
                "location": guest.event.location,
            },
        )

        self.send_html_email(
            email=guest.email,
            subject=f"Your Ticket for {guest.event.name}",
            message=EMAIL_TEMPLATE,
        )
        
    def send_refund_receipt(self, receipt: RefundReceiptEntity):
        """
        Sends a refund receipt to the guest.

        Args:
            receipt (TicketReceipt): The ticket receipt to send.

        Returns:
            None
        """
        email: str = receipt.ticket_receipt.guest.email
        event: str = receipt.ticket_receipt.event.name
        refunded_amount: str = receipt.refund_amount

        EMAIL_TEMPLATE = render_email_template(
            template_name="refund_receipt_email.html",
            variables={
                "event_name": event,
                "refund_amount": refunded_amount,
                "refund_date": receipt.created_at.strftime("%B %d, %Y"),
            },
        )
        self.send_html_email(
            email=email, subject="Ticket Refund Receipt", message=EMAIL_TEMPLATE
        )
        
    def send_donation_receipt(self, donation_receipt: DonationReceiptEntity):
        """
        Sends a donation receipt to the guest.

        Args:
            donation_receipt (DonationReceipt): The donation receipt to send.

        Returns:
            None
        """
        email: str = donation_receipt.email
        event: str = donation_receipt.event.name
        host: HostEntity = donation_receipt.host
        donated_amount: str = donation_receipt.total_paid

        EMAIL_TEMPLATE = render_email_template(
            template_name="donation_receipt_email.html",
            variables={
                "donor_name": f"{donation_receipt.first_name} {donation_receipt.last_name}",
                "donor_phone": donation_receipt.phone,
                "donor_email": donation_receipt.email,
                "host_name": f"{host.first_name} {host.last_name}",
                "host_email": host.email,
                "event_name": event,
                "donated_amount": donated_amount,
                "donation_date": donation_receipt.created_at.strftime("%B %d, %Y"),
            },
        )
        self.send_html_email(
            email=email, subject="Donation Receipt", message=EMAIL_TEMPLATE
        )