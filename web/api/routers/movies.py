from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..models import Movie, Showtime
from ..schemas import MovieOut, ShowtimeOut

router = APIRouter(tags=["movies"])


@router.get("/movies", response_model=list[MovieOut])
def list_movies(db: Session = Depends(get_db)):
    return db.scalars(select(Movie).order_by(Movie.title)).all()


@router.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Không tìm thấy phim.")
    return movie


@router.get("/movies/{movie_id}/showtimes", response_model=list[ShowtimeOut])
def movie_showtimes(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Không tìm thấy phim.")
    rows = (
        db.execute(
            select(Showtime)
            .options(joinedload(Showtime.movie), joinedload(Showtime.room))
            .where(Showtime.movie_id == movie_id)
            .order_by(Showtime.start_time)
        )
        .scalars()
        .all()
    )

    result = []
    for st in rows:
        result.append(
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
        )
    return result
