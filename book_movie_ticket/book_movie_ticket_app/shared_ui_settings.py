import json
import threading
from datetime import datetime

from django.conf import settings


# ==================================================
# FILE SETTING CHUNG
# ==================================================

SETTINGS_FILE = (
    settings.BASE_DIR
    / "shared_ui_settings.json"
)


# ==================================================
# FILE LOG BACKGROUND
# ==================================================

LOG_FOLDER = (
    settings.BASE_DIR
    / "logs"
)

BACKGROUND_LOG_FILE = (
    LOG_FOLDER
    / "background.log"
)


VALID_BACKGROUND_MODES = {
    "cover",
    "contain",
    "fill",
}


DEFAULT_SETTINGS = {
    "background_mode": "contain",
    "version": 1,
}


_file_lock = threading.Lock()
_log_lock = threading.Lock()


# ==================================================
# READ SETTING
# ==================================================

def _read_without_lock():

    if not SETTINGS_FILE.exists():

        return DEFAULT_SETTINGS.copy()


    try:

        data = json.loads(
            SETTINGS_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
    ):

        return DEFAULT_SETTINGS.copy()


    mode = data.get(
        "background_mode",
        "contain"
    )


    if mode not in VALID_BACKGROUND_MODES:

        mode = "contain"


    try:

        version = int(
            data.get(
                "version",
                1
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        version = 1


    return {
        "background_mode":
            mode,

        "version":
            version,
    }


# ==================================================
# GET SETTING
# ==================================================

def get_shared_ui_settings():

    with _file_lock:

        return _read_without_lock()


# ==================================================
# SET BACKGROUND MODE
# ==================================================

def set_shared_background_mode(
    mode
):

    mode = str(
        mode
    ).strip().lower()


    if mode not in VALID_BACKGROUND_MODES:

        raise ValueError(
            "Background mode không hợp lệ."
        )


    with _file_lock:

        current = (
            _read_without_lock()
        )


        previous_mode = (
            current[
                "background_mode"
            ]
        )


        if (
            previous_mode
            !=
            mode
        ):

            current[
                "background_mode"
            ] = mode


            current[
                "version"
            ] += 1


        temp_file = (
            SETTINGS_FILE
            .with_suffix(
                ".tmp"
            )
        )


        temp_file.write_text(

            json.dumps(

                current,

                ensure_ascii=False,

                indent=2,

            ),

            encoding="utf-8",

        )


        temp_file.replace(
            SETTINGS_FILE
        )


        return {
            **current,

            "previous_mode":
                previous_mode,
        }


# ==================================================
# WRITE BACKGROUND LOG
# ==================================================

def write_background_log(
    username,
    old_mode,
    new_mode
):

    if old_mode == new_mode:

        return


    LOG_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


    now = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


    message = (
        f"[{now}] "
        f"Admin '{username}' "
        f"changed background: "
        f"{old_mode.upper()} "
        f"-> "
        f"{new_mode.upper()}"
    )


    with _log_lock:

        with BACKGROUND_LOG_FILE.open(
            "a",
            encoding="utf-8"
        ) as log_file:

            log_file.write(
                message + "\n"
            )
