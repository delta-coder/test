import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


# ============================================================
# CINEMA BOOKING - CONTROLLED DJANGO SERVER
#
# Mục tiêu:
# - Pane giữa chỉ chạy Django.
# - Pane Control bên trái tạo STOP_FILE khi user bấm Ctrl+C.
# - Wrapper nhận STOP_FILE và gửi CTRL_BREAK_EVENT cho Django.
# - Không cần click sang pane server.
# ============================================================


WORKSPACE = Path(__file__).resolve().parent.parent

PROJECT_DIR = (
    WORKSPACE
    / "book_movie_ticket"
)

MANAGE_PY = (
    PROJECT_DIR
    / "manage.py"
)

STOP_FILE = (
    WORKSPACE
    / ".cinema_stop_server"
)

STATUS_FILE = (
    WORKSPACE
    / ".cinema_server_status.json"
)


def remove_if_exists(path):

    try:
        path.unlink()

    except FileNotFoundError:
        pass

    except OSError:
        pass


def write_status(
    running,
    django_pid=None,
):

    data = {
        "running": bool(running),
        "wrapper_pid": os.getpid(),
        "django_pid": django_pid,
        "port": 8000,
    }

    try:

        STATUS_FILE.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

    except OSError:
        pass


def graceful_stop(proc):

    if proc.poll() is not None:

        return


    print()
    print(
        "[CONTROL] Received stop request from Cinema Control."
    )
    print(
        "[CONTROL] Stopping Django gracefully..."
    )
    print()


    # ========================================================
    # Windows:
    # Django được chạy trong process group riêng.
    # Gửi CTRL_BREAK_EVENT tương tự interrupt console.
    # ========================================================

    if os.name == "nt":

        try:

            proc.send_signal(
                signal.CTRL_BREAK_EVENT
            )

            proc.wait(
                timeout=8
            )

            return

        except (
            subprocess.TimeoutExpired,
            OSError,
            ValueError,
        ):

            pass


    # ========================================================
    # POSIX fallback
    # ========================================================

    else:

        try:

            proc.send_signal(
                signal.SIGINT
            )

            proc.wait(
                timeout=8
            )

            return

        except (
            subprocess.TimeoutExpired,
            OSError,
            ValueError,
        ):

            pass


    # ========================================================
    # Fallback mềm hơn force kill
    # ========================================================

    try:

        proc.terminate()

        proc.wait(
            timeout=5
        )

        return

    except (
        subprocess.TimeoutExpired,
        OSError,
    ):

        pass


    # Chỉ dùng kill nếu process thực sự không chịu thoát.
    try:

        proc.kill()

    except OSError:

        pass


def main():

    remove_if_exists(
        STOP_FILE
    )


    print()
    print(
        "============================================="
    )
    print(
        "       CINEMA BOOKING - LAN SERVER"
    )
    print(
        "============================================="
    )
    print()
    print(
        "Server local:"
    )
    print(
        "    http://127.0.0.1:8000/"
    )
    print()
    print(
        "May khac cung Wi-Fi/LAN:"
    )
    print(
        "    http://IP-CUA-MAY-CHU:8000/"
    )
    print()
    print(
        "Tat server tu pane CONTROL:"
    )
    print(
        "    Ctrl + C"
    )
    print()
    print(
        "============================================="
    )
    print()


    command = [
        sys.executable,
        str(MANAGE_PY),
        "runserver",
        "0.0.0.0:8000",
        "--settings=book_movie_ticket.lan_settings",
    ]


    creationflags = 0


    if os.name == "nt":

        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
        )


    proc = subprocess.Popen(

        command,

        cwd=str(
            PROJECT_DIR
        ),

        creationflags=creationflags,

    )


    write_status(
        True,
        proc.pid,
    )


    try:

        while True:

            # Django tự thoát vì lỗi / Ctrl+C tại pane giữa.
            return_code = (
                proc.poll()
            )


            if return_code is not None:

                break


            # Control pane yêu cầu dừng.
            if STOP_FILE.exists():

                remove_if_exists(
                    STOP_FILE
                )

                graceful_stop(
                    proc
                )

                break


            time.sleep(
                0.20
            )


    except KeyboardInterrupt:

        # Vẫn cho phép Ctrl+C trực tiếp ở pane server.
        graceful_stop(
            proc
        )


    finally:

        if proc.poll() is None:

            graceful_stop(
                proc
            )


        write_status(
            False,
            None,
        )


        remove_if_exists(
            STOP_FILE
        )


        print()
        print(
            "============================================="
        )
        print(
            "       CINEMA BOOKING - SERVER STOPPED"
        )
        print(
            "============================================="
        )
        print()


if __name__ == "__main__":

    main()
