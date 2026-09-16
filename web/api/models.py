from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100), default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")
    holds: Mapped[list["SeatHold"]] = relationship(back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    genre: Mapped[str] = mapped_column(String(100))
    duration: Mapped[int] = mapped_column(Integer)
    director: Mapped[str] = mapped_column(String(100))
    release_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text, default="")
    poster_url: Mapped[str] = mapped_column(String(500), default="")

    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="movie")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(Integer, default=20)

    seats: Mapped[list["Seat"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="room")


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("room_id", "number", name="uq_room_seat"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    number: Mapped[int] = mapped_column(Integer)

    room: Mapped["Room"] = relationship(back_populates="seats")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="seat")
    holds: Mapped[list["SeatHold"]] = relationship(back_populates="seat")


class Showtime(Base):
    __tablename__ = "showtimes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    movie: Mapped["Movie"] = relationship(back_populates="showtimes")
    room: Mapped["Room"] = relationship(back_populates="showtimes")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="showtime")
    holds: Mapped[list["SeatHold"]] = relationship(back_populates="showtime")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("showtime_id", "seat_id", name="uq_showtime_seat"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    showtime_id: Mapped[int] = mapped_column(
        ForeignKey("showtimes.id", ondelete="CASCADE")
    )
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id", ondelete="CASCADE"))
    ticket_type: Mapped[str] = mapped_column(String(10))  # Adult | Child
    price: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="tickets")
    showtime: Mapped["Showtime"] = relationship(back_populates="tickets")
    seat: Mapped["Seat"] = relationship(back_populates="tickets")


class SeatHold(Base):
    """Temporary seat reservation while a user is selecting seats."""

    __tablename__ = "seat_holds"
    __table_args__ = (
        UniqueConstraint("showtime_id", "seat_id", name="uq_hold_showtime_seat"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    showtime_id: Mapped[int] = mapped_column(
        ForeignKey("showtimes.id", ondelete="CASCADE"), index=True
    )
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    showtime: Mapped["Showtime"] = relationship(back_populates="holds")
    seat: Mapped["Seat"] = relationship(back_populates="holds")
    user: Mapped["User"] = relationship(back_populates="holds")
