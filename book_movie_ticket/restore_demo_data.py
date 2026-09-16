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


# ============================================================
# MOVIE
# ============================================================

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
# THÊM 5 PHIM
# ============================================================

print()
print("==============================================")
print("           ADD MORE CINEMA DATA")
print("==============================================")
print()


inception = create_movie(
    {
        "title": "Inception",

        "genre":
            "Khoa học viễn tưởng",

        "duration":
            148,

        "director":
            "Christopher Nolan",

        "release_date":
            "2010-07-16",

        "description":
            (
                "Một chuyên gia đánh cắp bí mật "
                "thông qua giấc mơ nhận nhiệm vụ "
                "cấy một ý tưởng vào tâm trí mục tiêu."
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
                "những hậu quả khi danh tính "
                "Spider-Man của mình bị tiết lộ."
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
                "Hai học sinh xa lạ bí ẩn hoán đổi "
                "cơ thể và dần tạo nên một mối liên "
                "kết vượt qua không gian và thời gian."
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
                "Batman phải đối đầu với Joker, "
                "một kẻ tội phạm khiến Gotham "
                "rơi vào hỗn loạn."
            ),
    }
)


frozen = create_movie(
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
                "Elsa, Anna và những người bạn "
                "bắt đầu hành trình tìm hiểu nguồn "
                "gốc sức mạnh của Elsa."
            ),
    }
)


# ============================================================
# ROOM
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
            f"[ROOM] Exists: {name}"
        )


    return room


print()
print("--------------- ROOMS ----------------")


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
# SEATS
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
        f"[SEAT] {room.name}: {total} ghế"
    )


print()
print("--------------- SEATS ----------------")


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
# SHOWTIMES
# ============================================================

print()
print("------------- SHOWTIMES --------------")


tomorrow = (
    timezone.now()
    +
    timedelta(days=1)
)


day_after = (
    timezone.now()
    +
    timedelta(days=2)
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

    # ========================================================
    # INCEPTION
    # ========================================================

    (
        inception,
        room3,
        make_time(
            tomorrow,
            10,
            30
        )
    ),

    (
        inception,
        room4,
        make_time(
            day_after,
            20,
            0
        )
    ),


    # ========================================================
    # SPIDER-MAN
    # ========================================================

    (
        spiderman,
        room4,
        make_time(
            tomorrow,
            13,
            30
        )
    ),

    (
        spiderman,
        room5,
        make_time(
            day_after,
            18,
            30
        )
    ),


    # ========================================================
    # YOUR NAME
    # ========================================================

    (
        your_name,
        room5,
        make_time(
            tomorrow,
            9,
            0
        )
    ),

    (
        your_name,
        room3,
        make_time(
            day_after,
            16,
            30
        )
    ),


    # ========================================================
    # THE DARK KNIGHT
    # ========================================================

    (
        dark_knight,
        room3,
        make_time(
            tomorrow,
            19,
            0
        )
    ),

    (
        dark_knight,
        room4,
        make_time(
            day_after,
            21,
            0
        )
    ),


    # ========================================================
    # FROZEN II
    # ========================================================

    (
        frozen,
        room5,
        make_time(
            tomorrow,
            15,
            0
        )
    ),

    (
        frozen,
        room3,
        make_time(
            day_after,
            11,
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
            f"{movie.title} | "
            f"{room.name} | "
            f"{start_time.strftime('%d/%m/%Y %H:%M')}"
        )

    else:

        print(
            "[SHOWTIME] Exists: "
            f"{movie.title}"
        )


# ============================================================
# RESULT
# ============================================================

print()
print("==============================================")
print("               COMPLETE")
print("==============================================")

print(
    f"Tổng phim: "
    f"{Movie.objects.count()}"
)

print(
    f"Tổng phòng: "
    f"{Room.objects.count()}"
)

print(
    f"Tổng ghế: "
    f"{Seat.objects.count()}"
)

print(
    f"Tổng suất chiếu: "
    f"{Showtime.objects.count()}"
)

print()