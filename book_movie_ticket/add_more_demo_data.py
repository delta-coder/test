import os
from datetime import timedelta

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "book_movie_ticket.settings"
)

import django

django.setup()


from django.utils import timezone

from book_movie_ticket_app.models import (
    Movie,
    Room,
    Seat,
    Showtime,
)


# ============================================================
# HELPER
# ============================================================

def has_field(model, field_name):

    return any(
        field.name == field_name
        for field in model._meta.get_fields()
    )


def create_movie(data):

    defaults = {}

    for key, value in data.items():

        if (
            key != "title"
            and
            has_field(Movie, key)
        ):

            defaults[key] = value


    movie, created = (
        Movie.objects.update_or_create(

            title=data["title"],

            defaults=defaults,

        )
    )


    if created:

        print(
            f"[MOVIE] Created: {movie.title}"
        )

    else:

        print(
            f"[MOVIE] Updated: {movie.title}"
        )


    return movie


# ============================================================
# MOVIES
#
# 12 PHIM MỚI
# + 3 PHIM CŨ
# = KHOẢNG 15 PHIM
# = 3 HÀNG x 5 PHIM
# ============================================================

print()
print("================================================")
print("        CINEMA BOOKING - ADD MORE MOVIES")
print("================================================")
print()


inception = create_movie(
    {
        "title":
            "Inception",

        "genre":
            "Khoa học viễn tưởng, Hành động",

        "duration":
            148,

        "director":
            "Christopher Nolan",

        "release_date":
            "2010-07-16",

        "description":
            (
                "Một chuyên gia xâm nhập vào giấc mơ "
                "nhận nhiệm vụ cấy một ý tưởng vào "
                "tâm trí của mục tiêu."
            ),
    }
)


spiderman = create_movie(
    {
        "title":
            "Spider-Man: No Way Home",

        "genre":
            "Hành động, Phiêu lưu",

        "duration":
            148,

        "director":
            "Jon Watts",

        "release_date":
            "2021-12-17",

        "description":
            (
                "Peter Parker phải đối mặt với "
                "những hậu quả sau khi danh tính "
                "Spider-Man bị tiết lộ."
            ),
    }
)


your_name = create_movie(
    {
        "title":
            "Your Name",

        "genre":
            "Hoạt hình, Tình cảm",

        "duration":
            106,

        "director":
            "Makoto Shinkai",

        "release_date":
            "2016-08-26",

        "description":
            (
                "Hai học sinh xa lạ bất ngờ hoán đổi "
                "cơ thể và tạo nên một mối liên kết "
                "vượt qua không gian và thời gian."
            ),
    }
)


dark_knight = create_movie(
    {
        "title":
            "The Dark Knight",

        "genre":
            "Hành động, Tội phạm",

        "duration":
            152,

        "director":
            "Christopher Nolan",

        "release_date":
            "2008-07-18",

        "description":
            (
                "Batman phải đối đầu với Joker khi "
                "Gotham rơi vào một làn sóng hỗn loạn."
            ),
    }
)


frozen2 = create_movie(
    {
        "title":
            "Frozen II",

        "genre":
            "Hoạt hình, Phiêu lưu",

        "duration":
            103,

        "director":
            "Chris Buck, Jennifer Lee",

        "release_date":
            "2019-11-22",

        "description":
            (
                "Elsa và Anna bắt đầu hành trình "
                "khám phá nguồn gốc sức mạnh của Elsa."
            ),
    }
)


oppenheimer = create_movie(
    {
        "title":
            "Oppenheimer",

        "genre":
            "Tiểu sử, Chính kịch",

        "duration":
            180,

        "director":
            "Christopher Nolan",

        "release_date":
            "2023-07-21",

        "description":
            (
                "Câu chuyện về nhà vật lý J. Robert "
                "Oppenheimer và dự án phát triển "
                "bom nguyên tử."
            ),
    }
)


dune2 = create_movie(
    {
        "title":
            "Dune: Part Two",

        "genre":
            "Khoa học viễn tưởng, Phiêu lưu",

        "duration":
            166,

        "director":
            "Denis Villeneuve",

        "release_date":
            "2024-03-01",

        "description":
            (
                "Paul Atreides tiếp tục hành trình "
                "cùng người Fremen trên hành tinh Arrakis."
            ),
    }
)


avatar2 = create_movie(
    {
        "title":
            "Avatar: The Way of Water",

        "genre":
            "Khoa học viễn tưởng, Phiêu lưu",

        "duration":
            192,

        "director":
            "James Cameron",

        "release_date":
            "2022-12-16",

        "description":
            (
                "Gia đình Sully phải tìm nơi trú ẩn "
                "và khám phá những vùng biển mới "
                "trên Pandora."
            ),
    }
)


godzilla = create_movie(
    {
        "title":
            "Godzilla x Kong",

        "genre":
            "Hành động, Quái vật",

        "duration":
            115,

        "director":
            "Adam Wingard",

        "release_date":
            "2024-03-29",

        "description":
            (
                "Godzilla và Kong phải đối đầu "
                "với một mối đe dọa mới có thể "
                "thay đổi thế giới."
            ),
    }
)


suzume = create_movie(
    {
        "title":
            "Suzume",

        "genre":
            "Hoạt hình, Phiêu lưu",

        "duration":
            122,

        "director":
            "Makoto Shinkai",

        "release_date":
            "2022-11-11",

        "description":
            (
                "Suzume bắt đầu hành trình đóng lại "
                "những cánh cửa bí ẩn đang gây ra "
                "thảm họa trên khắp Nhật Bản."
            ),
    }
)


spirited_away = create_movie(
    {
        "title":
            "Spirited Away",

        "genre":
            "Hoạt hình, Fantasy",

        "duration":
            125,

        "director":
            "Hayao Miyazaki",

        "release_date":
            "2001-07-20",

        "description":
            (
                "Một cô bé bước vào thế giới linh hồn "
                "và phải tìm cách giải cứu cha mẹ."
            ),
    }
)


guardians3 = create_movie(
    {
        "title":
            "Guardians of the Galaxy Vol. 3",

        "genre":
            "Hành động, Khoa học viễn tưởng",

        "duration":
            150,

        "director":
            "James Gunn",

        "release_date":
            "2023-05-05",

        "description":
            (
                "Nhóm Guardians bắt đầu một nhiệm vụ "
                "mới nhằm bảo vệ Rocket và những "
                "người bạn của mình."
            ),
    }
)


# ============================================================
# LẤY / TẠO 5 PHÒNG
# ============================================================

def create_room(
    name,
    capacity
):

    defaults = {}


    if has_field(
        Room,
        "capacity"
    ):

        defaults[
            "capacity"
        ] = capacity


    room, created = (
        Room.objects.update_or_create(

            name=name,

            defaults=defaults,

        )
    )


    if created:

        print(
            f"[ROOM] Created: {name}"
        )

    else:

        print(
            f"[ROOM] Ready: {name}"
        )


    return room


print()
print("---------------- ROOMS ----------------")


room1 = create_room(
    "Phòng 1",
    16
)

room2 = create_room(
    "Phòng 2",
    12
)

room3 = create_room(
    "Phòng 3",
    20
)

room4 = create_room(
    "Phòng 4",
    24
)

room5 = create_room(
    "Phòng 5",
    16
)


# ============================================================
# GHẾ
# ============================================================

def create_seats(
    room,
    total
):

    for number in range(
        1,
        total + 1
    ):

        Seat.objects.get_or_create(

            room=room,

            number=number,

        )


    print(
        f"[SEAT] {room.name}: {total}"
    )


print()
print("---------------- SEATS ----------------")


create_seats(
    room1,
    16
)

create_seats(
    room2,
    12
)

create_seats(
    room3,
    20
)

create_seats(
    room4,
    24
)

create_seats(
    room5,
    16
)


# ============================================================
# SHOWTIME
# ============================================================

print()
print("-------------- SHOWTIMES --------------")


day1 = (
    timezone.now()
    +
    timedelta(days=1)
)

day2 = (
    timezone.now()
    +
    timedelta(days=2)
)

day3 = (
    timezone.now()
    +
    timedelta(days=3)
)


def make_time(
    base,
    hour,
    minute=0
):

    return base.replace(

        hour=hour,

        minute=minute,

        second=0,

        microsecond=0,

    )


showtime_data = [

    (
        inception,
        room1,
        make_time(
            day1,
            10,
            0
        )
    ),

    (
        spiderman,
        room2,
        make_time(
            day1,
            12,
            30
        )
    ),

    (
        your_name,
        room3,
        make_time(
            day1,
            14,
            0
        )
    ),

    (
        dark_knight,
        room4,
        make_time(
            day1,
            17,
            0
        )
    ),

    (
        frozen2,
        room5,
        make_time(
            day1,
            19,
            30
        )
    ),


    (
        oppenheimer,
        room1,
        make_time(
            day2,
            9,
            0
        )
    ),

    (
        dune2,
        room2,
        make_time(
            day2,
            11,
            30
        )
    ),

    (
        avatar2,
        room3,
        make_time(
            day2,
            14,
            30
        )
    ),

    (
        godzilla,
        room4,
        make_time(
            day2,
            18,
            0
        )
    ),

    (
        suzume,
        room5,
        make_time(
            day2,
            20,
            30
        )
    ),


    (
        spirited_away,
        room2,
        make_time(
            day3,
            10,
            0
        )
    ),

    (
        guardians3,
        room4,
        make_time(
            day3,
            19,
            0
        )
    ),

]


for (
    movie,
    room,
    start_time
) in showtime_data:


    showtime, created = (
        Showtime.objects.get_or_create(

            movie=movie,

            room=room,

            start_time=start_time,

        )
    )


    if created:

        print(

            "[SHOWTIME] "

            +
            movie.title

            +
            " | "

            +
            room.name

            +
            " | "

            +
            start_time.strftime(
                "%d/%m/%Y %H:%M"
            )

        )

    else:

        print(
            f"[SHOWTIME] Exists: {movie.title}"
        )


# ============================================================
# RESULT
# ============================================================

print()
print("================================================")
print("                    DONE")
print("================================================")
print()

print(
    "Tổng số phim:",
    Movie.objects.count()
)

print(
    "Tổng số phòng:",
    Room.objects.count()
)

print(
    "Tổng số ghế:",
    Seat.objects.count()
)

print(
    "Tổng suất chiếu:",
    Showtime.objects.count()
)

print()
print(
    "Có thể chạy lại file này nhiều lần, "
    "không nhân đôi phim/phòng/ghế."
)
print()