from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Ticket
from .seat_live_state import bump_version


# ============================================================
# HỦY VÉ
#
# - Chỉ user sở hữu vé mới được hủy.
# - Không cho hủy nếu suất chiếu đã bắt đầu.
# - Sau khi xóa vé, bump live version để các browser đang
#   xem cùng suất chiếu cập nhật ghế ngay không cần refresh.
# ============================================================

@login_required
@require_POST
def cancel_ticket(
    request,
    ticket_id
):

    ticket = get_object_or_404(

        Ticket.objects.select_related(
            "showtime__movie",
            "showtime__room",
            "seat",
        ),

        id=ticket_id,

        user=request.user,

    )


    # ========================================================
    # KHÔNG CHO HỦY VÉ ĐÃ / ĐANG CHIẾU
    # ========================================================

    if (
        ticket.showtime.start_time
        <=
        timezone.now()
    ):

        messages.error(

            request,

            (
                "Không thể hủy vé vì suất chiếu "
                "đã bắt đầu hoặc đã kết thúc."
            )

        )

        return redirect(
            "my_tickets"
        )


    # ========================================================
    # LƯU THÔNG TIN TRƯỚC KHI DELETE
    # ========================================================

    movie_title = (
        ticket.showtime.movie.title
    )

    seat_number = (
        ticket.seat.number
    )

    showtime_id = (
        ticket.showtime_id
    )


    # ========================================================
    # DELETE TICKET
    # ========================================================

    ticket.delete()


    # ========================================================
    # BÁO LIVE SYSTEM
    #
    # Mọi browser đang mở sơ đồ ghế sẽ nhận snapshot mới.
    # Ghế vừa hủy sẽ chuyển từ BOOKED -> AVAILABLE.
    # ========================================================

    bump_version()


    messages.success(

        request,

        (
            f"Đã hủy vé {movie_title} "
            f"- ghế {seat_number}. "
            f"Ghế đã được mở lại."
        )

    )


    return redirect(
        "my_tickets"
    )
