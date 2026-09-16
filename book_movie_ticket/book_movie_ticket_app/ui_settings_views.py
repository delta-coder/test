from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)

from django.http import JsonResponse

from django.views.decorators.http import (
    require_GET,
    require_POST,
)


from .shared_ui_settings import (
    get_shared_ui_settings,
    set_shared_background_mode,
    write_background_log,
)


# ==================================================
# GET SHARED UI SETTINGS
# ==================================================

@require_GET
def get_ui_settings(request):

    data = (
        get_shared_ui_settings()
    )

    return JsonResponse(
        data
    )


# ==================================================
# ADMIN SET BACKGROUND MODE
# ==================================================

@require_POST
@login_required
@user_passes_test(
    lambda user:
        user.is_staff
)
def set_background_mode(request):

    mode = request.POST.get(
        "mode",
        ""
    )


    try:

        data = (
            set_shared_background_mode(
                mode
            )
        )


    except ValueError as error:

        return JsonResponse(

            {
                "ok":
                    False,

                "error":
                    str(error),
            },

            status=400,

        )


    # ==================================================
    # GHI LOG RIÊNG
    # Chỉ ghi khi mode thực sự thay đổi
    # ==================================================

    write_background_log(

        username=
            request.user.username,

        old_mode=
            data["previous_mode"],

        new_mode=
            data["background_mode"],

    )


    return JsonResponse(

        {
            "ok":
                True,

            "background_mode":
                data[
                    "background_mode"
                ],

            "version":
                data[
                    "version"
                ],
        }

    )
