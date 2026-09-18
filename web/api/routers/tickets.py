from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..deps import get_current_user
from ..models import Showtime, Ticket, User
from ..schemas import MessageOut, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _utcnow_naive() -> datetime:
    """Thời gian UTC hiện tại không có tzinfo (để so sánh với SQLite naive datetime)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _normalize_naive(dt: datetime) -> datetime:
    """Loại bỏ tzinfo nếu có, để so sánh đồng nhất với SQLite naive datetime."""
    if dt is None:
        return dt
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def _calc_seat_code(seat_num: int, room_capacity: int) -> str:
    """Tính mã ghế (A1, B3, ...) từ số ghế và dung lượng phòng."""
    if seat_num <= 0:
        return "?"
    cols = 6
    if room_capacity <= 16:
        cols = 4
    elif room_capacity <= 20:
        cols = 5
    row_letter = chr(65 + (seat_num - 1) // cols)
    col_num = ((seat_num - 1) % cols) + 1
    return f"{row_letter}{col_num}"


@router.get("", response_model=list[TicketOut])
@router.get("/", response_model=list[TicketOut], include_in_schema=False)
def list_my_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retrieve all tickets booked by the currently authenticated user."""
    tickets = (
        db.execute(
            select(Ticket)
            .options(
                joinedload(Ticket.showtime).joinedload(Showtime.movie),
                joinedload(Ticket.showtime).joinedload(Showtime.room),
                joinedload(Ticket.seat),
            )
            .where(Ticket.user_id == user.id)
            .order_by(Ticket.created_at.desc())
        )
        .scalars()
        .all()
    )

    result = []
    for t in tickets:
        st = t.showtime
        seat_num = t.seat.number if t.seat else 0
        room_capacity = st.room.capacity if (st and st.room) else 24
        seat_code = _calc_seat_code(seat_num, room_capacity)

        result.append(
            TicketOut(
                id=t.id,
                ticket_type=t.ticket_type,
                price=t.price,
                created_at=t.created_at,
                seat_number=seat_num,
                seat_code=seat_code,
                movie_title=st.movie.title if (st and st.movie) else "N/A",
                room_name=st.room.name if (st and st.room) else "N/A",
                start_time=st.start_time if st else datetime.now(timezone.utc),
                showtime_id=t.showtime_id,
            )
        )
    return result


@router.delete("/{ticket_id}", response_model=MessageOut)
def cancel_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cancel a booked ticket if the showtime has not yet started."""
    ticket = db.execute(
        select(Ticket)
        .options(
            joinedload(Ticket.showtime).joinedload(Showtime.movie),
            joinedload(Ticket.seat),
        )
        .where(Ticket.id == ticket_id, Ticket.user_id == user.id)
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy vé hoặc bạn không có quyền hủy vé này.",
        )

    # BUG-3 FIX: So sánh với naive UTC datetime (SQLite không lưu timezone)
    now = _utcnow_naive()
    st = ticket.showtime
    if st and st.start_time:
        st_time = _normalize_naive(st.start_time)
        if st_time <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hủy vé vì suất chiếu đã bắt đầu hoặc đã kết thúc.",
            )

    movie_title = st.movie.title if (st and st.movie) else "phim"
    seat_number = ticket.seat.number if ticket.seat else ""

    db.delete(ticket)
    db.commit()

    return MessageOut(
        ok=True,
        message=f"Đã hủy vé {movie_title} - ghế {seat_number}. Ghế đã được mở lại cho người khác.",
    )
