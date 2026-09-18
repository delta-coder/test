from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import Seat, SeatHold, Showtime, Ticket
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete

settings = get_settings()


def utcnow() -> datetime:
    """Trả về naive UTC datetime để tương thích với SQLite (không lưu timezone)."""
    return datetime.utcnow()


def purge_expired_holds(db: Session, showtime_id: int | None = None) -> None:
    stmt = delete(SeatHold).where(SeatHold.expires_at < utcnow())
    if showtime_id is not None:
        stmt = stmt.where(SeatHold.showtime_id == showtime_id)
    db.execute(stmt)
    db.commit()


def get_seat_snapshot(db: Session, showtime_id: int, user_id: int | None) -> dict:
    purge_expired_holds(db, showtime_id)

    booked = list(
        db.scalars(
            select(Ticket.seat_id).where(Ticket.showtime_id == showtime_id)
        ).all()
    )

    holds = db.scalars(
        select(SeatHold).where(
            and_(
                SeatHold.showtime_id == showtime_id,
                SeatHold.expires_at >= utcnow(),
            )
        )
    ).all()

    mine: list[int] = []
    held: list[int] = []
    for hold in holds:
        if user_id and hold.user_id == user_id:
            mine.append(hold.seat_id)
        else:
            held.append(hold.seat_id)

    st = db.get(Showtime, showtime_id)
    seats = []
    if st:
        seats = db.scalars(
            select(Seat).where(Seat.room_id == st.room_id).order_by(Seat.number)
        ).all()

    return {
        "booked": booked,
        "held": held,
        "mine": mine,
        "seats": seats,
    }


def hold_seat(db: Session, showtime_id: int, seat_id: int, user_id: int) -> dict:
    purge_expired_holds(db, showtime_id)

    booked = db.scalar(
        select(Ticket.id).where(
            Ticket.showtime_id == showtime_id, Ticket.seat_id == seat_id
        )
    )
    if booked:
        return {"ok": False, "state": "booked", "message": "Ghế đã được đặt."}

    existing = db.scalar(
        select(SeatHold).where(
            SeatHold.showtime_id == showtime_id, SeatHold.seat_id == seat_id
        )
    )
    expires = utcnow() + timedelta(seconds=settings.hold_ttl_seconds)

    if existing:
        if existing.user_id != user_id and existing.expires_at >= utcnow():
            return {
                "ok": False,
                "state": "holding",
                "message": "Ghế đang được người khác chọn.",
            }
        existing.user_id = user_id
        existing.expires_at = expires
    else:
        db.add(
            SeatHold(
                showtime_id=showtime_id,
                seat_id=seat_id,
                user_id=user_id,
                expires_at=expires,
            )
        )
    db.commit()
    return {"ok": True, "state": "mine", "message": "Đã giữ ghế."}


def release_seat(db: Session, showtime_id: int, seat_id: int, user_id: int) -> dict:
    hold = db.scalar(
        select(SeatHold).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.seat_id == seat_id,
            SeatHold.user_id == user_id,
        )
    )
    if hold:
        db.delete(hold)
        db.commit()
    return {"ok": True, "message": "Đã bỏ chọn ghế."}


def release_all(db: Session, showtime_id: int, user_id: int) -> dict:
    db.execute(
        delete(SeatHold).where(
            SeatHold.showtime_id == showtime_id, SeatHold.user_id == user_id
        )
    )
    db.commit()
    return {"ok": True, "message": "Đã bỏ tất cả ghế đang chọn."}


def heartbeat(db: Session, showtime_id: int, seat_ids: list[int], user_id: int) -> dict:
    expires = utcnow() + timedelta(seconds=settings.hold_ttl_seconds)
    q = select(SeatHold).where(
        SeatHold.showtime_id == showtime_id,
        SeatHold.user_id == user_id,
    )
    if seat_ids:
        q = q.where(SeatHold.seat_id.in_(seat_ids))
    holds = db.scalars(q).all()
    for hold in holds:
        hold.expires_at = expires
    db.commit()
    return {"ok": True, "message": "Đã gia hạn giữ ghế."}
