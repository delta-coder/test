from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, movies, showtimes, tickets
from .config import get_settings
from .db import init_db, engine
from . import models  # noqa: F401
from sqlalchemy.orm import Session
import os

settings = get_settings()

app = FastAPI(
    title="Cinema Booking API",
    description="Cinema booking system API for Vercel deployment",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_db()

    # Create demo data if tables are empty
    from .auth import get_password_hash
    from .models import User, Movie, Room, Seat, Showtime
    from datetime import datetime, timedelta

    db = Session(engine)
    try:
        # Create or update admin user
        admin_user = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin_user:
            admin_user = User(
                username=settings.admin_username,
                email=settings.admin_email,
                name="Admin User",
                is_admin=True,
                password_hash=get_password_hash(settings.admin_password)
            )
            db.add(admin_user)
        else:
            # Sync password so admin/123 works immediately
            admin_user.password_hash = get_password_hash(settings.admin_password)
        db.commit()
        db.refresh(admin_user)


        # Real movie dataset matching local assets in /images/movies/
        real_movies = [
            {
                "title": "Avengers: Endgame",
                "genre": "Hành động, Phiêu lưu, Khoa học viễn tưởng",
                "duration": 181,
                "director": "Anthony Russo, Joe Russo",
                "release_date": datetime(2019, 4, 26).date(),
                "description": "Sau những sự kiện tàn khốc của Infinity War, các Avengers còn lại tập hợp lần cuối để đảo ngược những gì Thanos đã gây ra và cứu lấy vũ trụ.",
                "poster_url": "/images/movies/avengers.jpg"
            },
            {
                "title": "Interstellar",
                "genre": "Khoa học viễn tưởng, Phiêu lưu, Tâm lý",
                "duration": 169,
                "director": "Christopher Nolan",
                "release_date": datetime(2014, 11, 7).date(),
                "description": "Một nhóm nhà thám hiểm dũng cảm xuyên qua lỗ sâu không gian để tìm kiếm hành tinh sinh sống mới nhằm cứu lấy tương lai nhân loại.",
                "poster_url": "/images/movies/interstellar.jpg"
            },
            {
                "title": "Doraemon: Nobita và bản giao hưởng Địa Cầu",
                "genre": "Hoạt hình, Phiêu lưu, Gia đình",
                "duration": 110,
                "director": "Kazuaki Imai",
                "release_date": datetime(2024, 5, 24).date(),
                "description": "Doraemon, Nobita cùng nhóm bạn bước vào cuộc phiêu lưu âm nhạc kỳ diệu để cứu lấy Địa Cầu khỏi nguy cơ bị xóa sổ giai điệu.",
                "poster_url": "/images/movies/doraemon.jpg"
            },
            {
                "title": "Inception",
                "genre": "Khoa học viễn tưởng, Hành động",
                "duration": 148,
                "director": "Christopher Nolan",
                "release_date": datetime(2010, 7, 16).date(),
                "description": "Một chuyên gia trộm cắp thông tin qua tiềm thức trong mơ được giao nhiệm vụ tưởng chừng bất khả thi: cấy một ý tưởng vào tâm trí của mục tiêu.",
                "poster_url": "/images/movies/inception.jpg"
            },
            {
                "title": "Spider-Man: Brand New Day",
                "genre": "Hành động, Phiêu lưu, Viễn tưởng",
                "duration": 148,
                "director": "Jon Watts",
                "release_date": datetime(2026, 7, 27).date(),
                "description": "Peter Parker cô độc chật vật bảo vệ New York trước kẻ thù tâm linh bí ẩn, trong khi siêu năng lực bị biến đổi nguy hiểm do áp lực từ việc cả thế giới quên mất danh tính của cậu.",
                "poster_url": "/images/movies/spider-man.jpg"
            },
            {
                "title": "Your Name (Kimi no Na wa)",
                "genre": "Hoạt hình, Lãng mạn, Kỳ ảo",
                "duration": 106,
                "director": "Makoto Shinkai",
                "release_date": datetime(2016, 8, 26).date(),
                "description": "Hai học sinh xa lạ bất ngờ hoán đổi cơ thể và tạo nên một sợi dây liên kết vượt qua cả không gian, thời gian và định mệnh.",
                "poster_url": "/images/movies/your-name.webp"
            },
            {
                "title": "The Dark Knight",
                "genre": "Hành động, Tội phạm, Giật gân",
                "duration": 152,
                "director": "Christopher Nolan",
                "release_date": datetime(2008, 7, 18).date(),
                "description": "Batman cùng Trung úy Gordon và Công tố viên Harvey Dent phải đối đầu với Joker - kẻ mang đến sự hỗn loạn tột cùng cho thành phố Gotham.",
                "poster_url": "/images/movies/the-dark-knight.webp"
            },
            {
                "title": "Frozen II",
                "genre": "Hoạt hình, Phiêu lưu, Âm nhạc",
                "duration": 103,
                "director": "Chris Buck, Jennifer Lee",
                "release_date": datetime(2019, 11, 22).date(),
                "description": "Nữ hoàng băng giá Elsa cùng em gái Anna và các bạn dấn thân vào khu rừng ma thuật để khám phá nguồn gốc sức mạnh tiềm ẩn của cô.",
                "poster_url": "/images/movies/frozen-ii.png"
            },
            {
                "title": "Oppenheimer",
                "genre": "Tiểu sử, Chính kịch, Lịch sử",
                "duration": 180,
                "director": "Christopher Nolan",
                "release_date": datetime(2023, 7, 21).date(),
                "description": "Kiệt tác điện ảnh đoạt giải Oscar về nhà vật lý J. Robert Oppenheimer - cha đẻ của bom nguyên tử và Dự án Manhattan chấn động lịch sử.",
                "poster_url": "/images/movies/oppenheimer.png"
            },
            {
                "title": "Dune: Part Two",
                "genre": "Khoa học viễn tưởng, Phiêu lưu, Sử thi",
                "duration": 166,
                "director": "Denis Villeneuve",
                "release_date": datetime(2024, 3, 1).date(),
                "description": "Paul Atreides hợp lực cùng Chani và người Fremen trên hành tinh sa mạc Arrakis để báo thù những kẻ đã hủy diệt gia tộc của mình.",
                "poster_url": "/images/movies/dune.png"
            },
            {
                "title": "Avatar: The Way of Water",
                "genre": "Khoa học viễn tưởng, Phiêu lưu, Hành động",
                "duration": 192,
                "director": "James Cameron",
                "release_date": datetime(2022, 12, 16).date(),
                "description": "Jake Sully và Neytiri cùng các con phải rời bỏ quê hương và tìm nơi ẩn náu tại các bộ tộc sống dưới đại dương xanh thẳm của hành tinh Pandora.",
                "poster_url": "/images/movies/avatar.png"
            },
            {
                "title": "Godzilla x Kong: The New Empire",
                "genre": "Hành động, Quái vật, Viễn tưởng",
                "duration": 115,
                "director": "Adam Wingard",
                "release_date": datetime(2024, 3, 29).date(),
                "description": "Hai siêu quái thú hùng mạnh Godzilla và Kong buộc phải liên minh để đối đầu với mối đe dọa khổng lồ trỗi dậy từ lòng Trái Đất Rỗng.",
                "poster_url": "/images/movies/godzilla-x-kong.png"
            },
            {
                "title": "Suzume (Khóa chặt cửa nào)",
                "genre": "Hoạt hình, Phiêu lưu, Kỳ ảo",
                "duration": 122,
                "director": "Makoto Shinkai",
                "release_date": datetime(2022, 11, 11).date(),
                "description": "Nữ sinh 17 tuổi Suzume cùng chàng trai bí ẩn Souta dấn thân vào hành trình đóng lại những cánh cửa bí ẩn đang mang thảm họa đến khắp Nhật Bản.",
                "poster_url": "/images/movies/suzume.png"
            },
            {
                "title": "Spirited Away (Vùng đất linh hồn)",
                "genre": "Hoạt hình, Kỳ ảo, Gia đình",
                "duration": 125,
                "director": "Hayao Miyazaki",
                "release_date": datetime(2001, 7, 20).date(),
                "description": "Kiệt tác Ghibli kể về cô bé Chihiro lạc vào thế giới thần linh kỳ bí và dũng cảm vượt qua thử thách để cứu lấy cha mẹ.",
                "poster_url": "/images/movies/spirited-away.png"
            },
            {
                "title": "Guardians of the Galaxy Vol. 3",
                "genre": "Hành động, Khoa học viễn tưởng, Hài",
                "duration": 150,
                "director": "James Gunn",
                "release_date": datetime(2023, 5, 5).date(),
                "description": "Biệt đội Vệ binh Dải Ngân hà bước vào nhiệm vụ đầy cảm xúc để bảo vệ Rocket và khẳng định tình bạn gắn bó qua bao gian nan.",
                "poster_url": "/images/movies/guardians-of-the-galaxy-vol-3.png"
            }
        ]

        # Authentic cinema rooms
        real_rooms = [
            {"name": "Phòng 1 - IMAX Laser", "capacity": 24},
            {"name": "Phòng 2 - Dolby Atmos", "capacity": 20},
            {"name": "Phòng 3 - Gold Class VIP", "capacity": 16},
            {"name": "Phòng 4 - Tiêu chuẩn", "capacity": 24},
            {"name": "Phòng 5 - 3D Cinema", "capacity": 20}
        ]

        # Check if database needs refreshing (fewer than 15 movies or placeholder URLs)
        existing_movies = db.query(Movie).all()
        has_placeholder = any("placeholder.com" in (m.poster_url or "") for m in existing_movies)

        if len(existing_movies) < len(real_movies) or has_placeholder:
            # Clean old showtimes, tickets, holds, and movies for a fresh sync
            from .models import Ticket, SeatHold
            db.query(Ticket).delete()
            db.query(SeatHold).delete()
            db.query(Showtime).delete()
            db.query(Seat).delete()
            db.query(Room).delete()
            db.query(Movie).delete()
            db.commit()

            # Seed 15 authentic movies
            for m_data in real_movies:
                db.add(Movie(**m_data))
            db.commit()

            # Seed 5 rooms
            for r_data in real_rooms:
                db.add(Room(**r_data))
            db.commit()

            # Seed seats for each room
            rooms = db.query(Room).all()
            for room in rooms:
                for seat_num in range(1, room.capacity + 1):
                    db.add(Seat(number=seat_num, room_id=room.id))
            db.commit()

            # Seed rich showtimes across today and next 4 days
            movies = db.query(Movie).all()
            now_dt = datetime.now()
            # Slot schedule: times of day
            daily_slots = [
                (9, 30),
                (12, 15),
                (15, 0),
                (17, 45),
                (20, 15),
                (22, 45)
            ]

            showtime_count = 0
            for day_offset in range(5):
                slot_date = now_dt.date() + timedelta(days=day_offset)
                for slot_idx, (hour, minute) in enumerate(daily_slots):
                    # Rotate movies and rooms for variety
                    movie = movies[(day_offset * 3 + slot_idx) % len(movies)]
                    room = rooms[slot_idx % len(rooms)]
                    st_time = datetime(slot_date.year, slot_date.month, slot_date.day, hour, minute)
                    
                    db.add(Showtime(
                        movie_id=movie.id,
                        room_id=room.id,
                        start_time=st_time
                    ))
                    showtime_count += 1
            db.commit()
            print(f"[Seed] Successfully initialized {len(movies)} movies, {len(rooms)} rooms, and {showtime_count} showtimes.")

    except Exception as e:
        print(f"Error during startup: {e}")
        db.rollback()
    finally:
        db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

# Create api_router with prefix /api (matches app.js API_BASE='/api')
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(movies.router)
api_router.include_router(showtimes.router)
api_router.include_router(tickets.router)
app.include_router(api_router)

# Also include at root for direct calls or Vercel route rewrites
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(showtimes.router)
app.include_router(tickets.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


# Mount public directory for static files and frontend UI
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")