import json
import time

from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

from django.contrib.auth.decorators import (
    login_required,
)

from django.db import transaction

from django.http import (
    JsonResponse,
    StreamingHttpResponse,
)

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.utils import timezone

from django.views.decorators.http import (
    require_POST,
)


from .forms import RegisterForm

from .models import (
    Movie,
    Seat,
    Showtime,
    Ticket,
)

from .background_context import (
    get_movie_assets,
    get_movie_cover_url,
)

from .seat_live_state import (
    bump_version,
    get_snapshot,
    held_by_other,
    hold_seat,
    refresh_user_holds,
    release_seat,
    release_user_holds,
)


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# ============================================================
# MOVIE LIST
# ============================================================

def movie_list(request):

    movies = list(
        Movie.objects.all()
    )


    for movie in movies:

        movie.cover_image = (
            get_movie_cover_url(
                movie
            )
        )


    return render(

        request,

        "movie_list.html",

        {
            "movies":
                movies
        }

    )


# ============================================================
# MOVIE DETAIL
# ============================================================

def movie_detail(
    request,
    movie_id
):

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )


    showtimes = (

        Showtime.objects
        .filter(
            movie=movie,
            start_time__gte=
                timezone.now()
        )
        .order_by(
            "start_time"
        )

    )


    assets = get_movie_assets(
        movie
    )


    context = {

        "movie":
            movie,

        "movie_cover":
            assets["poster"],

        "showtimes":
            showtimes,

    }


    if assets["videos"]:

        context[
            "background_playlist"
        ] = assets["videos"]


    return render(

        request,

        "movie_detail.html",

        context

    )


# ============================================================
# SCHEDULE
# ============================================================

def schedule(request):

    showtimes = (

        Showtime.objects
        .filter(
            start_time__gte=
                timezone.now()
        )
        .select_related(
            "movie",
            "room"
        )
        .order_by(
            "start_time"
        )

    )


    return render(

        request,

        "schedule.html",

        {
            "showtimes":
                showtimes
        }

    )


# ============================================================
# REGISTER
# ============================================================

def register_view(request):

    if request.method == "POST":

        form = RegisterForm(
            request.POST
        )


        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            return redirect(
                "home"
            )

    else:

        form = RegisterForm()


    return render(

        request,

        "register.html",

        {
            "form":
                form
        }

    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    error = ""


    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )


        user = authenticate(

            request,

            username=username,

            password=password,

        )


        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "home"
            )


        error = (
            "Sai tên đăng nhập "
            "hoặc mật khẩu."
        )


    return render(

        request,

        "login.html",

        {
            "error":
                error
        }

    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    return redirect(
        "home"
    )


# ============================================================
# BOOK TICKET
# ============================================================

@login_required
def book_ticket(
    request,
    showtime_id
):

    showtime = get_object_or_404(

        Showtime,

        id=showtime_id,

    )


    seats = (

        Seat.objects
        .filter(
            room=showtime.room
        )
        .order_by(
            "number"
        )

    )


    booked_seat_ids = list(

        Ticket.objects
        .filter(
            showtime=showtime
        )
        .values_list(
            "seat_id",
            flat=True
        )

    )


    if request.method == "POST":

        seat_ids = (
            request.POST.getlist(
                "seats"
            )
        )


        ticket_type = (
            request.POST.get(
                "ticket_type",
                "Adult"
            )
        )


        if not seat_ids:

            messages.error(

                request,

                "Bạn chưa chọn ghế."

            )


        else:

            price = (

                100000

                if ticket_type
                == "Adult"

                else 50000

            )


            success_count = 0

            unavailable_count = 0


            # ====================================================
            # Transaction giúp gom thao tác kiểm tra + tạo vé.
            # ====================================================

            with transaction.atomic():

                for seat_id in seat_ids:

                    seat = get_object_or_404(

                        Seat,

                        id=seat_id,

                        room=showtime.room,

                    )


                    # Người khác đang giữ ghế.
                    if held_by_other(

                        showtime.id,

                        seat.id,

                        request.user.id,

                    ):

                        unavailable_count += 1

                        continue


                    # Ghế đã được đặt.
                    exists = (

                        Ticket.objects
                        .filter(
                            showtime=showtime,
                            seat=seat
                        )
                        .exists()

                    )


                    if exists:

                        unavailable_count += 1

                        continue


                    Ticket.objects.create(

                        user=
                            request.user,

                        showtime=
                            showtime,

                        seat=
                            seat,

                        ticket_type=
                            ticket_type,

                        price=
                            price,

                    )


                    success_count += 1


            # ====================================================
            # BỎ HOLD SAU KHI ĐẶT
            # ====================================================

            release_user_holds(

                showtime.id,

                request.user.id,

                seat_ids,

            )


            # Báo cho các browser đang xem cùng suất chiếu.
            bump_version()


            if success_count > 0:

                if unavailable_count:

                    messages.warning(

                        request,

                        (
                            f"Đã đặt thành công "
                            f"{success_count} ghế. "
                            f"{unavailable_count} ghế "
                            f"vừa được người khác chọn/đặt."
                        )

                    )

                else:

                    messages.success(

                        request,

                        (
                            f"Đặt vé thành công "
                            f"{success_count} ghế."
                        )

                    )


                return redirect(
                    "my_tickets"
                )


            messages.error(

                request,

                (
                    "Các ghế bạn chọn "
                    "không còn khả dụng."
                )

            )


            booked_seat_ids = list(

                Ticket.objects
                .filter(
                    showtime=showtime
                )
                .values_list(
                    "seat_id",
                    flat=True
                )

            )


    assets = get_movie_assets(
        showtime.movie
    )


    context = {

        "showtime":
            showtime,

        "seats":
            seats,

        "booked_seat_ids":
            booked_seat_ids,

    }


    if assets["videos"]:

        context[
            "background_playlist"
        ] = assets["videos"]


    return render(

        request,

        "book_ticket.html",

        context

    )


# ============================================================
# LIVE SEAT ACTION
# ============================================================

@login_required
@require_POST
def seat_live_action(
    request,
    showtime_id
):

    showtime = get_object_or_404(

        Showtime,

        id=showtime_id,

    )


    action = request.POST.get(
        "action",
        ""
    )


    # ========================================================
    # HEARTBEAT
    # ========================================================

    if action == "heartbeat":

        seat_ids = (
            request.POST.getlist(
                "seat_ids"
            )
        )


        refresh_user_holds(

            showtime.id,

            request.user.id,

            seat_ids,

        )


        return JsonResponse(
            {
                "ok": True
            }
        )


    # ========================================================
    # RELEASE ALL
    # ========================================================

    if action == "release_all":

        release_user_holds(

            showtime.id,

            request.user.id,

        )


        return JsonResponse(
            {
                "ok": True
            }
        )


    # ========================================================
    # SINGLE SEAT
    # ========================================================

    seat_id = request.POST.get(
        "seat_id"
    )


    if not seat_id:

        return JsonResponse(

            {
                "ok":
                    False,

                "error":
                    "Thiếu seat_id.",
            },

            status=400,

        )


    seat = get_object_or_404(

        Seat,

        id=seat_id,

        room=showtime.room,

    )


    # ========================================================
    # RELEASE
    # ========================================================

    if action == "release":

        release_seat(

            showtime.id,

            seat.id,

            request.user.id,

        )


        return JsonResponse(

            {
                "ok":
                    True,

                "state":
                    "released",
            }

        )


    # ========================================================
    # HOLD
    # ========================================================

    if action == "hold":

        # Đã bán rồi.
        if Ticket.objects.filter(

            showtime=showtime,

            seat=seat,

        ).exists():

            return JsonResponse(

                {
                    "ok":
                        False,

                    "state":
                        "booked",

                    "error":
                        "Ghế đã được đặt.",
                },

                status=409,

            )


        success = hold_seat(

            showtime.id,

            seat.id,

            request.user.id,

            request.user.username,

        )


        if not success:

            return JsonResponse(

                {
                    "ok":
                        False,

                    "state":
                        "held",

                    "error":
                        "Ghế đang được người khác chọn.",
                },

                status=409,

            )


        return JsonResponse(

            {
                "ok":
                    True,

                "state":
                    "mine",
            }

        )


    return JsonResponse(

        {
            "ok":
                False,

            "error":
                "Action không hợp lệ.",
        },

        status=400,

    )


# ============================================================
# LIVE SEAT STREAM
#
# Server-Sent Events.
# Browser không cần refresh.
# ============================================================

@login_required
def seat_live_stream(
    request,
    showtime_id
):

    showtime = get_object_or_404(

        Showtime,

        id=showtime_id,

    )


    user_id = request.user.id


    def event_stream():

        last_version = None

        last_keep_alive = time.time()


        while True:

            try:

                snapshot = get_snapshot(

                    showtime.id,

                    user_id,

                )


                version = (
                    snapshot[
                        "version"
                    ]
                )


                # ================================================
                # Chỉ query vé khi trạng thái live thay đổi.
                # ================================================

                if version != last_version:

                    booked = list(

                        Ticket.objects
                        .filter(
                            showtime=showtime
                        )
                        .values_list(
                            "seat_id",
                            flat=True
                        )

                    )


                    payload = {

                        "version":
                            version,

                        "booked":
                            booked,

                        "mine":
                            snapshot[
                                "mine"
                            ],

                        "held":
                            snapshot[
                                "others"
                            ],

                    }


                    yield (

                        "data: "
                        +
                        json.dumps(
                            payload
                        )
                        +
                        "\n\n"

                    )


                    last_version = (
                        version
                    )

                    last_keep_alive = (
                        time.time()
                    )


                else:

                    # Giữ connection sống.
                    if (
                        time.time()
                        -
                        last_keep_alive
                        >=
                        12
                    ):

                        yield (
                            ": keep-alive\n\n"
                        )

                        last_keep_alive = (
                            time.time()
                        )


                # Check nhanh để tạo cảm giác realtime.
                time.sleep(
                    0.55
                )


            except GeneratorExit:

                break


            except Exception:

                # Nếu kết nối DB/file tạm thời lỗi,
                # chờ rồi thử lại.
                time.sleep(
                    1
                )


    response = StreamingHttpResponse(

        event_stream(),

        content_type=
            "text/event-stream",

    )


    response[
        "Cache-Control"
    ] = "no-cache"


    response[
        "X-Accel-Buffering"
    ] = "no"


    return response


# ============================================================
# MY TICKETS
# ============================================================

@login_required
def my_tickets(request):

    tickets = (

        Ticket.objects
        .filter(
            user=request.user
        )
        .select_related(
            "showtime__movie",
            "showtime__room",
            "seat"
        )
        .order_by(
            "-showtime__start_time"
        )

    )


    return render(

        request,

        "my_tickets.html",

        {
            "tickets":
                tickets
        }

    )
