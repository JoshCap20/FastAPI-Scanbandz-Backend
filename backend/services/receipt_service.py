from ..exceptions import (
    TicketNotFoundException,
    HostPermissionError,
    EventNotFoundException,
)
from ..entities import TicketReceiptEntity
from ..models import BaseTicketReceipt
from ..database import db_session
from ..services.communication_service import CommunicationService

from typing import Sequence
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select


class ReceiptService:
    _session: Session
    communication_service: CommunicationService

    def __init__(
        self,
        session: Session = Depends(db_session),
        communication_service: CommunicationService = Depends(CommunicationService),
    ):
        self._session = session
        self.communication_service = communication_service

    def generate_ticket_receipt(self, base_ticket_receipt: BaseTicketReceipt):
        """
        Generates a receipt for a ticket purchase.

        Args:
            base_ticket_receipt (BaseTicketReceipt): The base ticket receipt object.

        Returns:
            TicketReceipt: The ticket receipt object.
        """
        entity: TicketReceiptEntity = TicketReceiptEntity.from_model(
            base_ticket_receipt
        )

        self._session.add(entity)
        self._session.commit()

        self.send_ticket_receipt(entity)

        return entity.to_model()

    def send_ticket_receipt(self, ticket_receipt: TicketReceiptEntity):
        """
        Sends a ticket receipt to the guest.

        Args:
            ticket_receipt (TicketReceiptEntity): The ticket receipt to send.
        """
        self.communication_service.send_ticket_payment_receipt(ticket_receipt)
