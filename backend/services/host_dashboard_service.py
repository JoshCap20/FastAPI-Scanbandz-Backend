"""
This class is dedicated to providing summary statistics for the host dashboard.
"""
from fastapi import Depends
from sqlalchemy import and_, select, func
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from ..entities import EventEntity, TicketEntity, GuestEntity, TicketReceiptEntity
from ..database import db_session

class HostDashboardService:
    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def get_dashboard_stats(self, host_id: int, start_date_str: str, end_date_str: str) -> dict:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

         # Query for counting distinct events
        events_count = self._session.execute(
            select(
                func.count(func.distinct(EventEntity.id)).label("events_count")
            ).select_from(EventEntity)
            .where(
                and_(
                    EventEntity.host_id == host_id,
                    EventEntity.start >= start_date,
                    EventEntity.start <= end_date,
                )
            )
        ).scalar()
        
        # Assuming you've already defined start_date, end_date, and host_id

        stats = self._session.execute(
            select(
                func.sum(TicketReceiptEntity.quantity).label("tickets_sold_count"),
                func.sum(TicketReceiptEntity.total_paid).label("revenue")
            ).select_from(EventEntity)
            .join(EventEntity.ticket_receipts)
            .where(
                and_(
                    EventEntity.host_id == host_id,
                    EventEntity.start >= start_date,
                    EventEntity.start <= end_date,
                )
            )
        ).one()


        guests_attended_count = self._get_guests_attended_count(host_id, start_date, end_date)
        top_events = self._get_top_events(host_id, start_date, end_date)
        upcoming_events = self._get_upcoming_events(host_id)

        return {
            "events_count": events_count or 0,
            "guests_attended": guests_attended_count,
            "tickets_sold": stats.tickets_sold_count,
            "revenue": str(stats.revenue),
            "top_events": top_events,
            "upcoming_events": upcoming_events,
            "start_date": start_date.strftime("%m/%d/%Y"),
            "end_date": end_date.strftime("%m/%d/%Y"),
        }

    def _get_guests_attended_count(self, host_id: int, start_date: datetime, end_date: datetime) -> int:
        guests_attended_count = self._session.execute(
            select(func.sum(GuestEntity.used_quantity))
            .select_from(GuestEntity)
            .join(EventEntity, GuestEntity.event_id == EventEntity.id)
            .where(
                and_(
                    EventEntity.host_id == host_id,
                    EventEntity.start >= start_date,
                    EventEntity.start <= end_date
                )
            )
        ).scalar_one_or_none()
        return guests_attended_count or 0
    
    def _get_top_events(self, host_id: int, start_date: datetime, end_date: datetime, limit: int = 3) -> list[dict]:
        events = self._session.execute(
            select(EventEntity.id, EventEntity.name, func.sum(TicketEntity.tickets_sold).label("tickets_sold"))
            .join(EventEntity.tickets)
            .group_by(EventEntity.id)
            .where(
                and_(
                    EventEntity.host_id == host_id,
                    EventEntity.start >= start_date,
                    EventEntity.start <= end_date,
                )
            )
            .order_by(func.sum(TicketEntity.tickets_sold).desc())
            .limit(limit)
        ).all()

        return [
            {
                "id": event.id,
                "name": event.name,
                "tickets_sold": event.tickets_sold,
            }
            for event in events
        ]
        
    def _get_upcoming_events(self, host_id: int, limit: int = 5) -> list[dict]:
        events_query = (
            select(EventEntity)
            .filter(EventEntity.host_id == host_id, EventEntity.start > datetime.now())
            .order_by(EventEntity.start.asc())
            .limit(limit)
        )
        
        events = self._session.execute(events_query).scalars().unique().all()

        return [
            {
                "id": event.id,
                "name": event.name,
                "start": event.start.strftime("%m/%d/%Y"),
                "location": event.location,
                "tickets_sold": sum(ticket.tickets_sold for ticket in event.tickets),  # Aggregate tickets_sold directly
            }
            for event in events
        ]

    def get_event_tickets_sold(self, event_id: int) -> int:
        result = self._session.execute(
            select(func.sum(TicketEntity.tickets_sold)).filter_by(event_id=event_id)
        )
        return result.scalar_one_or_none() or 0
        
    def get_revenue_and_ticket_count_year_chart_data(
        self, host_id: int, year: int
    ) -> dict:
        """
        Get the revenue data and total ticket receipts count for a host for a given year.

        Args:
            host_id (int): The ID of the host for which to retrieve the data.
            year (int): The year to retrieve the data for.

        Returns:
            dict: A dictionary containing the revenue data and total ticket receipts count for the year.
        """
        event_ids_for_host = (
            self._session.query(EventEntity.id)
            .filter(EventEntity.host_id == host_id)
            .subquery()
        )

        query = (
            self._session.query(
                func.extract("month", TicketReceiptEntity.created_at).label("month"),
                func.sum(TicketReceiptEntity.total_price).label("total_revenue"),
                func.count(TicketReceiptEntity.id).label("total_tickets"),
            )
            .filter(
                    TicketReceiptEntity.event_id.in_(select(event_ids_for_host)),
                    func.extract("year", TicketReceiptEntity.created_at) == year,
            )
            .group_by("month")
        )

        result_data = {
            month: {"total_revenue": 0, "total_tickets": 0} for month in range(1, 13)
        }
        for month, total_revenue, total_tickets in query:
            result_data[month]["total_revenue"] = float(total_revenue)
            result_data[month]["total_tickets"] = total_tickets

        return result_data