from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..deps import get_current_user, get_current_user_optional
from ..models import Showtime, Ticket, User, Seat
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


def _utcnow() -> datetime:
    """Trả về thời gian hiện tại UTC (naive) để so sánh với DB."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/showtimes", response_model=list[ShowtimeOut])
def list_showtimes(db: Session = Depends(get_db)):
    # Lọc các suất chiếu từ 4 giờ trước đến tương lai (cho phép xem suất chiếu đang diễn ra)
    # Dùng naive datetime để so sánh với SQLite (không lưu timezone)
    now = _utcnow() - timedelta(hours=4)
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

    # Kiểm tra suất chiếu chưa kết thúc
    now_naive = _utcnow()
    st_time = st.start_time
    if hasattr(st_time, 'tzinfo') and st_time.tzinfo is not None:
        st_time = st_time.replace(tzinfo=None)
    if st_time <= now_naive:
        raise HTTPException(
            status_code=400,
            detail="Không thể đặt vé cho suất chiếu đã kết thúc."
        )

    purge_expired_holds(db, showtime_id)
    price = PRICES[payload.ticket_type]
    created: list[Ticket] = []

    for seat_id in payload.seat_ids:
        # Kiểm tra ghế đã có vé chưa
        existing = db.scalar(
            select(Ticket.id).where(
                Ticket.showtime_id == showtime_id, Ticket.seat_id == seat_id
            )
        )
        if existing:
            raise HTTPException(
                status_code=409, detail=f"Ghế {seat_id} đã được đặt."
            )

        # BUG-2 FIX: Chỉ kiểm tra ghế bị người KHÁC hold (không phải của user hiện tại)
        snap = get_seat_snapshot(db, showtime_id, user.id)
        # snap["held"] = ghế người khác đang giữ, snap["mine"] = ghế user đang giữ
        if seat_id in snap["held"]:
            raise HTTPException(
                status_code=409, detail=f"Ghế {seat_id} đang được người khác chọn."
            )
        # Ghế phải thuộc về user (đang hold) hoặc là ghế trống
        # Nếu ghế không phải của user và không trong held → ghế trống → cho phép
        if seat_id not in snap["mine"] and seat_id not in snap["booked"]:
            # Ghế trống, có thể book trực tiếp (không cần hold trước)
            pass

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
    # Giải phóng tất cả holds của user cho showtime này sau khi đặt vé
    release_all(db, showtime_id, user.id)
    db.commit()

    for t in created:
        db.refresh(t)
        # Load quan hệ seat để lấy seat number
        if not t.seat:
            t.seat = db.get(Seat, t.seat_id)

    result = []
    for t in created:
        seat_num = t.seat.number if t.seat else 0
        # Tính seat_code: phòng chiếu thường có 5-6 cột
        room_capacity = st.room.capacity if st.room else 24
        cols = 6
        if room_capacity <= 16:
            cols = 4
        elif room_capacity <= 20:
            cols = 5
        row_letter = chr(65 + (seat_num - 1) // cols)
        col_num = ((seat_num - 1) % cols) + 1
        seat_code = f"{row_letter}{col_num}"

        result.append(
            TicketOut(
                id=t.id,
                ticket_type=t.ticket_type,
                price=t.price,
                created_at=t.created_at,
                seat_number=seat_num,
                seat_code=seat_code,
                movie_title=st.movie.title if st.movie else "N/A",
                room_name=st.room.name if st.room else "N/A",
                start_time=st.start_time,
                showtime_id=st.id,
            )
        )
    return result
