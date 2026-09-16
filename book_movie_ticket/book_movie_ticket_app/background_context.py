import json
import re
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static
from django.utils.text import slugify


# ============================================================
# PATHS
# ============================================================

APP_STATIC_ROOT = (
    settings.BASE_DIR
    / "book_movie_ticket_app"
    / "static"
)

GLOBAL_BACKGROUND_ROOT = (
    APP_STATIC_ROOT
    / "backgrounds"
)

MOVIE_BACKGROUND_ROOT = (
    APP_STATIC_ROOT
    / "movie_backgrounds"
)

REMOTE_MEDIA_FILE = (
    settings.BASE_DIR
    / "movie_media_sources.json"
)


# ============================================================
# HELPERS
# ============================================================

def natural_sort_key(name):

    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(
            r"(\d+)",
            str(name)
        )
    ]


def normalize_name(text):

    return re.sub(
        r"[^a-z0-9]+",
        "",
        slugify(
            str(text)
        ).lower()
    )


def make_static_url(
    relative_path,
    file_path
):

    try:

        version = (
            file_path.stat().st_mtime_ns
        )

    except OSError:

        version = 0


    return (
        f"{static(relative_path)}"
        f"?v={version}"
    )


def load_remote_media():

    if not REMOTE_MEDIA_FILE.exists():

        return {}


    try:

        data = json.loads(
            REMOTE_MEDIA_FILE.read_text(
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
# RESOLVE MOVIE FOLDER
#
# Hỗ trợ cả folder cũ:
#
# avengers/
# spider-man/
#
# và folder mới:
#
# avengers-endgame/
# spider-man-no-way-home/
# ============================================================

def resolve_movie_folder(
    movie_or_title,
    create=True
):

    title = (
        movie_or_title.title

        if hasattr(
            movie_or_title,
            "title"
        )

        else str(
            movie_or_title
        )
    )


    MOVIE_BACKGROUND_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )


    exact_slug = slugify(
        title
    )


    exact_folder = (
        MOVIE_BACKGROUND_ROOT
        / exact_slug
    )


    if exact_folder.exists():

        return exact_folder


    target_key = normalize_name(
        title
    )


    candidates = []


    for folder in (
        MOVIE_BACKGROUND_ROOT.iterdir()
    ):

        if not folder.is_dir():

            continue


        folder_key = normalize_name(
            folder.name
        )


        if not folder_key:

            continue


        if (
            folder_key in target_key
            or
            target_key in folder_key
        ):

            candidates.append(
                (
                    len(folder_key),
                    folder
                )
            )


    if candidates:

        candidates.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return candidates[0][1]


    if not create:

        return exact_folder


    exact_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return exact_folder


# ============================================================
# AUTO CREATE MOVIE FOLDERS
#
# Giữ compatibility với models.py hiện tại.
# ============================================================

def create_movie_background_folders(
    movie_or_title
):

    movie_folder = resolve_movie_folder(
        movie_or_title,
        create=True
    )


    images_folder = (
        movie_folder
        / "images"
    )


    videos_folder = (
        movie_folder
        / "videos"
    )


    images_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    videos_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return {
        "root":
            movie_folder,

        "images":
            images_folder,

        "videos":
            videos_folder,
    }


# ============================================================
# GLOBAL BACKGROUND PLAYLIST
# ============================================================

def background_playlist(request):

    image_folder = (
        GLOBAL_BACKGROUND_ROOT
        / "images"
    )


    video_folder = (
        GLOBAL_BACKGROUND_ROOT
        / "videos"
    )


    playlist = []


    if not image_folder.exists():

        return {
            "background_playlist":
                playlist
        }


    image_files = [

        file

        for file in image_folder.iterdir()

        if (
            file.is_file()
            and
            file.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            }
        )

    ]


    image_files.sort(
        key=lambda file:
            natural_sort_key(
                file.stem
            )
    )


    video_files = {}


    if video_folder.exists():

        for file in video_folder.iterdir():

            if (
                file.is_file()
                and
                file.suffix.lower()
                == ".mp4"
            ):

                video_files[
                    file.stem.lower()
                ] = file


    for image_file in image_files:

        name = image_file.stem


        video_file = (
            video_files.get(
                name.lower()
            )
        )


        image_url = make_static_url(

            "backgrounds/images/"
            +
            image_file.name,

            image_file

        )


        item = {

            "name":
                name,

            "kind":
                "global",

            "image":
                image_url,

            "video":
                "",

            "youtube":
                "",

        }


        if video_file:

            video_url = make_static_url(

                "backgrounds/videos/"
                +
                video_file.name,

                video_file

            )


            item["video"] = (
                video_url
            )


        playlist.append(
            item
        )


    return {
        "background_playlist":
            playlist
    }


# ============================================================
# GET MOVIE ASSETS
# ============================================================

def get_movie_assets(movie):

    folders = (
        create_movie_background_folders(
            movie
        )
    )


    images_folder = (
        folders[
            "images"
        ]
    )


    videos_folder = (
        folders[
            "videos"
        ]
    )


    # ========================================================
    # POSTER
    # ========================================================

    image_files = [

        file

        for file in images_folder.iterdir()

        if (
            file.is_file()
            and
            file.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            }
        )

    ]


    image_files.sort(

        key=lambda file: (

            0
            if
            file.stem.lower()
            in {
                "poster",
                "cover",
            }
            else
            1,

            natural_sort_key(
                file.name
            )

        )

    )


    poster_url = static(
        "images/default.jpg"
    )


    if image_files:

        poster_file = (
            image_files[0]
        )


        relative_path = (

            "movie_backgrounds/"
            +
            folders[
                "root"
            ].name
            +
            "/images/"
            +
            poster_file.name

        )


        poster_url = make_static_url(

            relative_path,

            poster_file

        )


    # ========================================================
    # LOCAL MP4 TRAILERS
    # ========================================================

    video_files = [

        file

        for file in videos_folder.iterdir()

        if (
            file.is_file()
            and
            file.suffix.lower()
            == ".mp4"
        )

    ]


    video_files.sort(
        key=lambda file:
            natural_sort_key(
                file.name
            )
    )


    playlist = []


    for video_file in video_files:

        relative_path = (

            "movie_backgrounds/"
            +
            folders[
                "root"
            ].name
            +
            "/videos/"
            +
            video_file.name

        )


        playlist.append(
            {
                "name":
                    movie.title,

                "kind":
                    "movie",

                "image":
                    "",

                "video":
                    make_static_url(
                        relative_path,
                        video_file
                    ),

                "youtube":
                    "",
            }
        )


    # ========================================================
    # REMOTE YOUTUBE FALLBACK
    #
    # Chỉ dùng khi không có MP4 local.
    # ========================================================

    if not playlist:

        remote_media = (
            load_remote_media()
        )


        movie_key = slugify(
            movie.title
        )


        media = (
            remote_media.get(
                movie_key,
                {}
            )
        )


        youtube_id = str(
            media.get(
                "youtube_id",
                ""
            )
        ).strip()


        if youtube_id:

            playlist.append(
                {
                    "name":
                        movie.title,

                    "kind":
                        "movie",

                    "image":
                        "",

                    "video":
                        "",

                    "youtube":
                        youtube_id,
                }
            )


    return {

        "poster":
            poster_url,

        "videos":
            playlist,

    }


# ============================================================
# MOVIE CARD POSTER
# ============================================================

def get_movie_cover_url(movie):

    assets = get_movie_assets(
        movie
    )

    return assets[
        "poster"
    ]
