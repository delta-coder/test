import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


# ============================================================
# DJANGO SETUP
# ============================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "book_movie_ticket.settings"
)

import django

django.setup()


from django.conf import settings
from django.utils.text import slugify

from book_movie_ticket_app.models import Movie

from book_movie_ticket_app.background_context import (
    create_movie_background_folders,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(
    settings.BASE_DIR
)

TOKEN_FILE = (
    BASE_DIR
    / ".tmdb_read_token"
)

MEDIA_FILE = (
    BASE_DIR
    / "movie_media_sources.json"
)


TMDB_API_ROOT = (
    "https://api.themoviedb.org/3"
)

TMDB_IMAGE_ROOT = (
    "https://image.tmdb.org/t/p/w780"
)


# ============================================================
# TOKEN
# ============================================================

def get_token():

    env_token = (
        os.environ
        .get(
            "TMDB_READ_TOKEN",
            ""
        )
        .strip()
    )


    if env_token:

        return env_token


    if TOKEN_FILE.exists():

        try:

            token = (
                TOKEN_FILE
                .read_text(
                    encoding="utf-8"
                )
                .strip()
            )

        except OSError:

            token = ""


        if token:

            return token


    print()
    print(
        "=================================================="
    )
    print(
        "     CINEMA BOOKING - TMDB FIRST TIME SETUP"
    )
    print(
        "=================================================="
    )
    print()
    print(
        "Paste TMDB API Read Access Token."
    )
    print(
        "Token chi duoc luu local tai:"
    )
    print(
        f"  {TOKEN_FILE}"
    )
    print()


    try:

        token = getpass.getpass(
            "TMDB Read Access Token: "
        ).strip()

    except Exception:

        token = input(
            "TMDB Read Access Token: "
        ).strip()


    if not token:

        print()
        print(
            "[ERROR] Token dang trong."
        )

        raise SystemExit(
            1
        )


    TOKEN_FILE.write_text(
        token,
        encoding="utf-8"
    )


    return token


# ============================================================
# HTTP
# ============================================================

def api_get(
    token,
    endpoint,
    params=None
):

    params = params or {}


    query = urllib.parse.urlencode(
        params
    )


    url = (
        TMDB_API_ROOT
        +
        endpoint
    )


    if query:

        url += "?" + query


    request = urllib.request.Request(

        url,

        headers={
            "Authorization":
                "Bearer "
                +
                token,

            "accept":
                "application/json",

            "User-Agent":
                "CinemaBookingStudentProject/1.0",
        },

    )


    with urllib.request.urlopen(
        request,
        timeout=25
    ) as response:

        return json.loads(
            response.read()
            .decode(
                "utf-8"
            )
        )


def download_file(
    url,
    destination
):

    request = urllib.request.Request(

        url,

        headers={
            "User-Agent":
                "CinemaBookingStudentProject/1.0"
        },

    )


    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        data = response.read()


    temp = destination.with_suffix(
        destination.suffix
        +
        ".tmp"
    )


    temp.write_bytes(
        data
    )


    temp.replace(
        destination
    )


# ============================================================
# LOAD CURRENT MEDIA FILE
# ============================================================

def load_media_file():

    if not MEDIA_FILE.exists():

        return {}


    try:

        data = json.loads(
            MEDIA_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
    ):

        return {}


    if not isinstance(
        data,
        dict
    ):

        return {}


    return data


# ============================================================
# SEARCH MOVIE
# ============================================================

def find_tmdb_movie(
    token,
    movie
):

    params = {

        "query":
            movie.title,

        "include_adult":
            "false",

        "language":
            "en-US",

    }


    release_date = getattr(
        movie,
        "release_date",
        None
    )


    if release_date:

        try:

            params[
                "primary_release_year"
            ] = release_date.year

        except Exception:

            pass


    data = api_get(

        token,

        "/search/movie",

        params,

    )


    results = (
        data.get(
            "results",
            []
        )
    )


    if not results:

        return None


    return results[0]


# ============================================================
# GET DETAILS + VIDEOS
# ============================================================

def get_movie_details(
    token,
    tmdb_id
):

    return api_get(

        token,

        f"/movie/{tmdb_id}",

        {
            "append_to_response":
                "videos",

            "language":
                "en-US",
        },

    )


# ============================================================
# PICK TRAILER
# ============================================================

def pick_youtube_trailer(
    details
):

    videos = (
        details
        .get(
            "videos",
            {}
        )
        .get(
            "results",
            []
        )
    )


    youtube_videos = [

        video

        for video in videos

        if (
            video.get(
                "site"
            )
            ==
            "YouTube"

            and

            video.get(
                "key"
            )
        )

    ]


    if not youtube_videos:

        return None


    def score(video):

        points = 0


        if video.get(
            "official"
        ):

            points += 100


        video_type = (
            str(
                video.get(
                    "type",
                    ""
                )
            )
            .lower()
        )


        if video_type == "trailer":

            points += 50


        elif video_type == "teaser":

            points += 20


        name = (
            str(
                video.get(
                    "name",
                    ""
                )
            )
            .lower()
        )


        if "official trailer" in name:

            points += 40


        elif "trailer" in name:

            points += 20


        if "final trailer" in name:

            points += 5


        return points


    youtube_videos.sort(

        key=score,

        reverse=True,

    )


    return youtube_videos[0]


# ============================================================
# SYNC ONE MOVIE
# ============================================================

def sync_movie(
    token,
    movie,
    media_data
):

    print()
    print(
        "--------------------------------------------------"
    )
    print(
        f"[MOVIE] {movie.title}"
    )


    found = find_tmdb_movie(
        token,
        movie
    )


    if not found:

        print(
            "  [NOT FOUND] TMDB"
        )

        return False


    tmdb_id = found[
        "id"
    ]


    print(
        f"  TMDB ID: {tmdb_id}"
    )


    details = get_movie_details(
        token,
        tmdb_id
    )


    folders = (
        create_movie_background_folders(
            movie
        )
    )


    # ========================================================
    # POSTER
    # ========================================================

    poster_path = (
        details.get(
            "poster_path"
        )
        or
        found.get(
            "poster_path"
        )
    )


    poster_downloaded = False


    if poster_path:

        poster_url = (
            TMDB_IMAGE_ROOT
            +
            poster_path
        )


        poster_file = (
            folders[
                "images"
            ]
            /
            "poster.jpg"
        )


        try:

            download_file(
                poster_url,
                poster_file
            )


            poster_downloaded = True


            print(
                f"  [POSTER] {poster_file}"
            )


        except Exception as error:

            print(
                "  [POSTER ERROR]",
                error
            )


    else:

        poster_url = ""


    # ========================================================
    # YOUTUBE TRAILER
    # ========================================================

    trailer = pick_youtube_trailer(
        details
    )


    youtube_id = ""


    if trailer:

        youtube_id = str(
            trailer[
                "key"
            ]
        )


        print(
            "  [TRAILER] "
            +
            trailer.get(
                "name",
                "YouTube"
            )
        )


        print(
            "            https://www.youtube.com/watch?v="
            +
            youtube_id
        )


    else:

        print(
            "  [TRAILER] Khong tim thay YouTube trailer."
        )


    # ========================================================
    # SAVE
    # ========================================================

    movie_key = slugify(
        movie.title
    )


    media_data[
        movie_key
    ] = {

        "title":
            movie.title,

        "tmdb_id":
            tmdb_id,

        "tmdb_title":
            details.get(
                "title",
                found.get(
                    "title",
                    ""
                )
            ),

        "poster_url":
            poster_url,

        "poster_local":
            poster_downloaded,

        "youtube_id":
            youtube_id,

        "youtube_url":
            (
                "https://www.youtube.com/watch?v="
                +
                youtube_id

                if youtube_id

                else ""
            ),

        "synced_at":
            datetime.now()
            .isoformat(
                timespec="seconds"
            ),

    }


    return True


# ============================================================
# MAIN
# ============================================================

def main():

    token = get_token()


    movies = list(

        Movie.objects
        .all()
        .order_by(
            "id"
        )

    )


    if not movies:

        print()
        print(
            "[INFO] Database chua co Movie."
        )

        return


    media_data = (
        load_media_file()
    )


    print()
    print(
        "=================================================="
    )
    print(
        "        CINEMA BOOKING - AUTO MEDIA SYNC"
    )
    print(
        "=================================================="
    )

    print()
    print(
        f"Movies in database: {len(movies)}"
    )


    ok = 0
    failed = 0


    for movie in movies:

        try:

            success = sync_movie(
                token,
                movie,
                media_data
            )


            if success:

                ok += 1

            else:

                failed += 1


            # Save after every movie,
            # so interruption does not lose previous progress.
            MEDIA_FILE.write_text(

                json.dumps(
                    media_data,
                    ensure_ascii=False,
                    indent=2,
                ),

                encoding="utf-8",

            )


        except urllib.error.HTTPError as error:

            failed += 1


            print()
            print(
                f"[HTTP ERROR] {movie.title}: "
                f"{error.code}"
            )


            if error.code in {
                401,
                403,
            }:

                print()
                print(
                    "TMDB token co the khong dung."
                )

                print(
                    "Xoa file:"
                )

                print(
                    f"  {TOKEN_FILE}"
                )

                print(
                    "roi chay lai."
                )

                break


        except Exception as error:

            failed += 1

            print(
                f"[ERROR] {movie.title}: {error}"
            )


    print()
    print(
        "=================================================="
    )
    print(
        "                    DONE"
    )
    print(
        "=================================================="
    )

    print()
    print(
        f"Synced: {ok}"
    )

    print(
        f"Failed: {failed}"
    )

    print()
    print(
        "Poster da duoc dua vao images/poster.jpg."
    )

    print(
        "Trailer YouTube da duoc luu trong:"
    )

    print(
        f"  {MEDIA_FILE}"
    )

    print()


if __name__ == "__main__":

    main()
