from django.urls import path

from . import views
from . import ui_settings_views
from . import ticket_actions


urlpatterns = [

    # ========================================================
    # WEBSITE
    # ========================================================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "phim/",
        views.movie_list,
        name="movie_list"
    ),

    path(
        "phim/<int:movie_id>/",
        views.movie_detail,
        name="movie_detail"
    ),

    path(
        "lich-chieu/",
        views.schedule,
        name="schedule"
    ),

    path(
        "dang-ky/",
        views.register_view,
        name="register"
    ),

    path(
        "dang-nhap/",
        views.login_view,
        name="login"
    ),

    path(
        "dang-xuat/",
        views.logout_view,
        name="logout"
    ),

    path(
        "dat-ve/<int:showtime_id>/",
        views.book_ticket,
        name="book_ticket"
    ),

    path(
        "ve-cua-toi/",
        views.my_tickets,
        name="my_tickets"
    ),


    # ========================================================
    # HỦY VÉ
    # ========================================================

    path(
        "ve-cua-toi/huy/<int:ticket_id>/",
        ticket_actions.cancel_ticket,
        name="cancel_ticket"
    ),


    # ========================================================
    # LIVE SEATS
    # ========================================================

    path(
        "api/suat-chieu/<int:showtime_id>/ghe/action/",
        views.seat_live_action,
        name="seat_live_action"
    ),

    path(
        "api/suat-chieu/<int:showtime_id>/ghe/stream/",
        views.seat_live_stream,
        name="seat_live_stream"
    ),


    # ========================================================
    # SHARED UI SETTINGS
    # ========================================================

    path(
        "api/ui-settings/",
        ui_settings_views.get_ui_settings,
        name="ui_settings"
    ),

    path(
        "api/background-mode/",
        ui_settings_views.set_background_mode,
        name="set_background_mode"
    ),

]
