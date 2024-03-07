from ..entities import TicketReceiptEntity
from ..models import BaseTicketReceipt, Host, TicketReceipt
from ..database import db_session
from ..services.communication_service import CommunicationService

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

    def generate_ticket_receipt(
        self, base_ticket_receipt: BaseTicketReceipt
    ) -> TicketReceipt:
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

        try:
            self._session.add(entity)
            self._session.commit()
        except:
            self._session.rollback()
            raise Exception("Failed to save ticket receipt")

        self.send_ticket_receipt(entity)

        return entity.to_model()

    def send_ticket_receipt(self, ticket_receipt: TicketReceiptEntity) -> None:
        """
        Sends a ticket receipt to the guest.

        Args:
            ticket_receipt (TicketReceiptEntity): The ticket receipt to send.
        """
        self.communication_service.send_ticket_payment_receipt(ticket_receipt)

    ## FETCHING METHODS ##

    def get_receipts_by_host(self, host: Host) -> list[TicketReceipt]:
        """
        Returns all ticket receipts for a given host.

        Args:
            host (Host): The host to get receipts for.

        Returns:
            list[TicketReceipt]: A list of ticket receipts.
        """
        query = select(TicketReceiptEntity).where(
            TicketReceiptEntity.host_id == host.id
        )

        entities: list[TicketReceiptEntity] = (
            self._session.execute(query).scalars().all()
        )

        return [entity.to_model() for entity in entities]

    ### DEVELOPMENT ONLY ###
    def dev_all(self) -> list[TicketReceiptEntity]:
        """
        Returns all ticket receipts.

        Returns:
            Sequence[TicketReceiptEntity]: A list of ticket receipt entities.
        """
        query = select(TicketReceiptEntity)
        return self._session.execute(query).scalars().all()
