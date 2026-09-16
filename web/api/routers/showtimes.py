from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..deps import get_current_user, get_current_user_optional
from ..models import Showtime, Ticket, User
from ..schemas import BookIn, MessageOut, SeatActionIn, SeatSnapshot, ShowtimeOut, TicketOut
from ..seat_service import get_seat_snapshot, purge_expired_holds, release_all, hold_seat, release_seat, heartbeat
from ..auth import decode_access_token

router = APIRouter(tags=["showtimes"])

PRICES = {"Adult": 100000, "Child": 50000}


def _optional_user(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    return db.get(User, int(payload["sub"]))


from datetime import datetime, timedelta, timezone

@router.get("/showtimes", response_model=list[ShowtimeOut])
def list_showtimes(db: Session = Depends(get_db)):
    # Include showtimes starting from earlier today
    now = datetime.now(timezone.utc) - timedelta(hours=4)
    rows = (
        db.execute(
            select(Showtime)
            .options(joinedload(Showtime.movie), joinedload(Showtime.room))
            .where(Showtime.start_time >= now)
            .order_by(Showtime.start_time)
        )
        .scalars()
        .unique()
        .all()
    )
    return [
        ShowtimeOut(
            id=st.id,
            movie_id=st.movie_id,
            room_id=st.room_id,
            start_time=st.start_time,
            movie_title=st.movie.title if st.movie else None,
            room_name=st.room.name if st.room else None,
            movie_poster_url=st.movie.poster_url if st.movie else None,
            movie_duration=st.movie.duration if st.movie else None,
            movie_genre=st.movie.genre if st.movie else None,
        )
        for st in rows
    ]


@router.get("/showtimes/{showtime_id}", response_model=ShowtimeOut)
def get_showtime(showtime_id: int, db: Session = Depends(get_db)):
    st = db.execute(
        select(Showtime)
        .options(joinedload(Showtime.movie), joinedload(Showtime.room))
        .where(Showtime.id == showtime_id)
    ).scalar_one_or_none()
    if not st:
        raise HTTPException(status_code=404, detail="Không tìm thấy suất chiếu.")
    return ShowtimeOut(
        id=st.id,
        movie_id=st.movie_id,
        room_id=st.room_id,
        start_time=st.start_time,
        movie_title=st.movie.title if st.movie else None,
        room_name=st.room.name if st.room else None,
        movie_poster_url=st.movie.poster_url if st.movie else None,
        movie_duration=st.movie.duration if st.movie else None,
        movie_genre=st.movie.genre if st.movie else None,
    )


import asyncio
import json
from fastapi.responses import StreamingResponse


@router.get("/showtimes/{showtime_id}/seats", response_model=SeatSnapshot)
def seat_snapshot(showtime_id: int, db: Session = Depends(get_db), user: User | None = Depends(get_current_user_optional)):
    return get_seat_snapshot(db, showtime_id, user.id if user else None)


@router.get("/showtimes/{showtime_id}/stream")
async def showtime_stream(
    showtime_id: int,
    user: User | None = Depends(get_current_user_optional),
):
    """Server-Sent Events endpoint streaming real-time seat availability."""
    async def event_generator():
        try:
            # Yield updates every 2 seconds for active connections (safe for Vercel 10s limit)
            for _ in range(4):
                from ..db import SessionLocal
                with SessionLocal() as db:
                    snap = get_seat_snapshot(db, showtime_id, user.id if user else None)
                    data = {
                        "booked": snap["booked"],
                        "held": snap["held"],
                        "mine": snap["mine"],
                    }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(2)

        except (asyncio.CancelledError, GeneratorExit):
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )



@router.post("/showtimes/{showtime_id}/seat-action", response_model=MessageOut)
def seat_action(
    showtime_id: int,
    payload: SeatActionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    action = payload.action
    seat_id = payload.seat_id
    seat_ids = payload.seat_ids

    if action == "hold":
        result = hold_seat(db, showtime_id, seat_id, user.id)
        return {"ok": result["ok"], "message": result["message"]}
    elif action == "release":
        result = release_seat(db, showtime_id, seat_id, user.id)
        return {"ok": result["ok"], "message": result["message"]}
    elif action == "release_all":
        result = release_all(db, showtime_id, user.id)
        return {"ok": result["ok"], "message": result["message"]}
    elif action == "heartbeat":
        heartbeat(db, showtime_id, seat_ids or [], user.id)
        return {"ok": True, "message": "Đã gia hạn giữ ghế."}
    else:
        raise HTTPException(status_code=400, detail="Hành động không xác định.")

@router.post("/showtimes/{showtime_id}/book", response_model=list[TicketOut])
def book_tickets(
    showtime_id: int,
    payload: BookIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    st = db.execute(
        select(Showtime)
        .options(joinedload(Showtime.movie), joinedload(Showtime.room))
        .where(Showtime.id == showtime_id)
    ).scalar_one_or_none()
    if not st:
        raise HTTPException(status_code=404, detail="Không tìm thấy suất chiếu.")

    purge_expired_holds(db, showtime_id)
    price = PRICES[payload.ticket_type]
    created: list[Ticket] = []

    for seat_id in payload.seat_ids:
        existing = db.scalar(
            select(Ticket.id).where(
                Ticket.showtime_id == showtime_id, Ticket.seat_id == seat_id
            )
        )
        if existing:
            raise HTTPException(
                status_code=409, detail=f"Ghế {seat_id} đã được đặt."
            )

        snap = get_seat_snapshot(db, showtime_id, user.id)
        if seat_id in snap["held"]:
            raise HTTPException(
                status_code=409, detail=f"Ghế {seat_id} đang được người khác chọn."
            )

        ticket = Ticket(
            user_id=user.id,
            showtime_id=showtime_id,
            seat_id=seat_id,
            ticket_type=payload.ticket_type,
            price=price,
        )
        db.add(ticket)
        created.append(ticket)

    db.flush()
    release_all(db, showtime_id, user.id)
    db.commit()

    for t in created:
        db.refresh(t)

    result = []
    for t in created:
        result.append(
            TicketOut(
                id=t.id,
                ticket_type=t.ticket_type,
                price=t.price,
                created_at=t.created_at,
                seat_number=t.seat.number,
                movie_title=st.movie.title,
                room_name=st.room.name,
                start_time=st.start_time,
                showtime_id=st.id,
            )
        )
    return result
