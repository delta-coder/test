import json
import threading
import time

from django.conf import settings


# ============================================================
# LIVE SEAT STATE
#
# Dùng cho server LAN hiện tại.
# Không cần migration.
#
# Ghế đang được user giữ sẽ tự hết hạn sau 45 giây
# nếu browser biến mất / mất mạng.
# Browser đang mở sẽ heartbeat để gia hạn.
# ============================================================

STATE_FILE = (
    settings.BASE_DIR
    / "live_seat_holds.json"
)

HOLD_SECONDS = 45

_lock = threading.RLock()


def _default_state():

    return {
        "version": 1,
        "holds": {},
    }


def _read_state_without_lock():

    if not STATE_FILE.exists():

        return _default_state()


    try:

        data = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
    ):

        return _default_state()


    if not isinstance(
        data,
        dict
    ):

        return _default_state()


    if not isinstance(
        data.get("holds"),
        dict
    ):

        data["holds"] = {}


    try:

        data["version"] = int(
            data.get(
                "version",
                1
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        data["version"] = 1


    return data


def _write_state_without_lock(
    state
):

    temp_file = (
        STATE_FILE
        .with_suffix(".tmp")
    )

    temp_file.write_text(

        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ),

        encoding="utf-8",

    )

    temp_file.replace(
        STATE_FILE
    )


def _seat_key(
    showtime_id,
    seat_id
):

    return (
        f"{int(showtime_id)}:"
        f"{int(seat_id)}"
    )


def _cleanup_expired_without_lock(
    state
):

    now = time.time()

    expired_keys = []


    for key, hold in list(
        state["holds"].items()
    ):

        try:

            expires_at = float(
                hold.get(
                    "expires_at",
                    0
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            expires_at = 0


        if expires_at <= now:

            expired_keys.append(
                key
            )


    if expired_keys:

        for key in expired_keys:

            state["holds"].pop(
                key,
                None
            )


        state["version"] += 1


    return bool(
        expired_keys
    )


def get_snapshot(
    showtime_id,
    user_id
):

    showtime_id = int(
        showtime_id
    )

    user_id = int(
        user_id
    )


    with _lock:

        state = (
            _read_state_without_lock()
        )

        changed = (
            _cleanup_expired_without_lock(
                state
            )
        )


        mine = []
        others = []


        prefix = (
            f"{showtime_id}:"
        )


        for key, hold in (
            state["holds"].items()
        ):

            if not key.startswith(
                prefix
            ):

                continue


            try:

                seat_id = int(
                    hold["seat_id"]
                )

                owner_id = int(
                    hold["user_id"]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):

                continue


            if owner_id == user_id:

                mine.append(
                    seat_id
                )

            else:

                others.append(
                    seat_id
                )


        if changed:

            _write_state_without_lock(
                state
            )


        return {
            "version":
                state["version"],

            "mine":
                sorted(mine),

            "others":
                sorted(others),
        }


def hold_seat(
    showtime_id,
    seat_id,
    user_id,
    username,
):

    showtime_id = int(
        showtime_id
    )

    seat_id = int(
        seat_id
    )

    user_id = int(
        user_id
    )


    with _lock:

        state = (
            _read_state_without_lock()
        )

        _cleanup_expired_without_lock(
            state
        )


        key = _seat_key(
            showtime_id,
            seat_id
        )


        old_hold = (
            state["holds"].get(
                key
            )
        )


        if old_hold:

            try:

                old_user_id = int(
                    old_hold[
                        "user_id"
                    ]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):

                old_user_id = -1


            if (
                old_user_id
                !=
                user_id
            ):

                _write_state_without_lock(
                    state
                )

                return False


        is_new = (
            old_hold is None
        )


        state["holds"][key] = {

            "showtime_id":
                showtime_id,

            "seat_id":
                seat_id,

            "user_id":
                user_id,

            "username":
                str(username),

            "expires_at":
                time.time()
                +
                HOLD_SECONDS,

        }


        if is_new:

            state["version"] += 1


        _write_state_without_lock(
            state
        )


        return True


def refresh_user_holds(
    showtime_id,
    user_id,
    seat_ids,
):

    showtime_id = int(
        showtime_id
    )

    user_id = int(
        user_id
    )

    seat_ids = {
        int(seat_id)
        for seat_id in seat_ids
    }


    with _lock:

        state = (
            _read_state_without_lock()
        )

        _cleanup_expired_without_lock(
            state
        )

        now = time.time()


        for seat_id in seat_ids:

            key = _seat_key(
                showtime_id,
                seat_id
            )

            hold = (
                state["holds"].get(
                    key
                )
            )


            if not hold:

                continue


            try:

                owner_id = int(
                    hold[
                        "user_id"
                    ]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):

                continue


            if owner_id == user_id:

                hold[
                    "expires_at"
                ] = (
                    now
                    +
                    HOLD_SECONDS
                )


        _write_state_without_lock(
            state
        )


def release_seat(
    showtime_id,
    seat_id,
    user_id,
):

    showtime_id = int(
        showtime_id
    )

    seat_id = int(
        seat_id
    )

    user_id = int(
        user_id
    )


    with _lock:

        state = (
            _read_state_without_lock()
        )

        _cleanup_expired_without_lock(
            state
        )


        key = _seat_key(
            showtime_id,
            seat_id
        )

        hold = (
            state["holds"].get(
                key
            )
        )


        if not hold:

            _write_state_without_lock(
                state
            )

            return


        try:

            owner_id = int(
                hold[
                    "user_id"
                ]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):

            owner_id = -1


        if owner_id == user_id:

            state["holds"].pop(
                key,
                None
            )

            state["version"] += 1


        _write_state_without_lock(
            state
        )


def release_user_holds(
    showtime_id,
    user_id,
    seat_ids=None,
):

    showtime_id = int(
        showtime_id
    )

    user_id = int(
        user_id
    )


    allowed_seats = None


    if seat_ids is not None:

        allowed_seats = {
            int(seat_id)
            for seat_id in seat_ids
        }


    with _lock:

        state = (
            _read_state_without_lock()
        )

        _cleanup_expired_without_lock(
            state
        )


        removed = False


        for key, hold in list(
            state["holds"].items()
        ):

            try:

                hold_showtime = int(
                    hold[
                        "showtime_id"
                    ]
                )

                hold_user = int(
                    hold[
                        "user_id"
                    ]
                )

                hold_seat_id = int(
                    hold[
                        "seat_id"
                    ]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):

                continue


            if (
                hold_showtime
                !=
                showtime_id
            ):

                continue


            if (
                hold_user
                !=
                user_id
            ):

                continue


            if (
                allowed_seats
                is not None
                and
                hold_seat_id
                not in
                allowed_seats
            ):

                continue


            state["holds"].pop(
                key,
                None
            )

            removed = True


        if removed:

            state["version"] += 1


        _write_state_without_lock(
            state
        )


def held_by_other(
    showtime_id,
    seat_id,
    user_id,
):

    snapshot = get_snapshot(
        showtime_id,
        user_id
    )

    return (
        int(seat_id)
        in
        snapshot["others"]
    )


def bump_version():

    with _lock:

        state = (
            _read_state_without_lock()
        )

        _cleanup_expired_without_lock(
            state
        )

        state["version"] += 1

        _write_state_without_lock(
            state
        )
