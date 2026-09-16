from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    name: str = ""
    age: int | None = None
    is_admin: bool = False

    model_config = {"from_attributes": True}


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str = ""
    age: int | None = None


class LoginIn(BaseModel):
    username: str
    password: str


class MovieOut(BaseModel):
    id: int
    title: str
    genre: str
    duration: int
    director: str
    release_date: date
    description: str
    poster_url: str = ""

    model_config = {"from_attributes": True}


class MovieIn(BaseModel):
    title: str
    genre: str
    duration: int = Field(gt=0)
    director: str
    release_date: date
    description: str = ""
    poster_url: str = ""


class RoomOut(BaseModel):
    id: int
    name: str
    capacity: int

    model_config = {"from_attributes": True}


class RoomIn(BaseModel):
    name: str
    capacity: int = Field(gt=0, le=200)


class SeatOut(BaseModel):
    id: int
    number: int
    room_id: int

    model_config = {"from_attributes": True}


class ShowtimeOut(BaseModel):
    id: int
    movie_id: int
    room_id: int
    start_time: datetime
    movie_title: str | None = None
    room_name: str | None = None
    movie_poster_url: str | None = None
    movie_duration: int | None = None
    movie_genre: str | None = None

    model_config = {"from_attributes": True}


class ShowtimeIn(BaseModel):
    movie_id: int
    room_id: int
    start_time: datetime


class SeatSnapshot(BaseModel):
    booked: list[int]
    held: list[int]
    mine: list[int]
    seats: list[SeatOut]


class SeatActionIn(BaseModel):
    action: str  # hold | release | release_all | heartbeat
    seat_id: int | None = None
    seat_ids: list[int] = []


class BookIn(BaseModel):
    seat_ids: list[int] = Field(min_length=1)
    ticket_type: str = Field(pattern="^(Adult|Child)$")


class TicketOut(BaseModel):
    id: int
    ticket_type: str
    price: int
    created_at: datetime
    seat_number: int
    movie_title: str
    room_name: str
    start_time: datetime
    showtime_id: int

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    ok: bool = True
    message: str = ""
