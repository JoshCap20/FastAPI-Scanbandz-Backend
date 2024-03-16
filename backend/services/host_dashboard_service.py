"""
This class is dedicated to providing summary statistics for the host dashboard.
"""
from fastapi import Depends
from sqlalchemy import and_, select, func
from sqlalchemy.orm import Session
from datetime import datetime

from ..entities import EventEntity, TicketEntity, GuestEntity
from ..database import db_session
from sqlalchemy.orm import joinedload

class HostDashboardService:
    def __init__(self, session: Session = Depends(db_session)):
        self._session = session

    def get_upcoming_events(self, host_id: int, limit: int = 5) -> list[dict]:
        events = self._session.execute(
            select(EventEntity)
            .options(joinedload(EventEntity.tickets))  # Load tickets relationship
            .filter(EventEntity.host_id == host_id, EventEntity.start > datetime.now())
            .order_by(EventEntity.start.asc())
            .limit(limit)
        ).scalars().all()

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

    def get_dashboard_stats(self, host_id: int, start_date_str: str, end_date_str: str) -> dict:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        stats = self._session.execute(
            select(
                func.count(EventEntity.id).label("events_count"),
                func.sum(TicketEntity.tickets_sold).label("tickets_sold_count"),
                (func.sum(TicketEntity.price * TicketEntity.tickets_sold)).label("revenue")
            ).select_from(EventEntity)
            .join(EventEntity.tickets)
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
        upcoming_events = self.get_upcoming_events(host_id)

        return {
            "events_count": stats.events_count,
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
            select(func.count())
            .select_from(GuestEntity)
            .join(EventEntity, GuestEntity.event_id == EventEntity.id)
            .where(
                and_(
                    EventEntity.host_id == host_id,
                    EventEntity.start >= start_date,
                    EventEntity.start <= end_date,
                    GuestEntity.scan_timestamp.isnot(None),
                )
            )
        ).scalar_one()
        return guests_attended_count
    
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