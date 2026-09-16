import os
import shutil

src_base = "d:/cinema_booking_simple/book_movie_ticket/book_movie_ticket_app/static/movie_backgrounds"
dest_base = "d:/cinema_booking_simple/web/public/images/movies"
os.makedirs(dest_base, exist_ok=True)

mapping = {
    "Avengers: Endgame": ("avengers", "avengers.jpg"),
    "Interstellar": ("interstellar", "interstellar.jpg"),
    "Doraemon": ("doraemon", "doraemon.jpg"),
    "Inception": ("inception", "OIP.jpg"),
    "Spider-Man: No Way Home": ("spider-man", "SPIDER-MAN-BRAND-NEW-DAY.jpg"),
    "Your Name": ("your-name", "8GJsy7w7frGquw1cy9jasOGNNI1.webp"),
    "The Dark Knight": ("the-dark-knight", "OIP.webp"),
    "Frozen II": ("frozen-ii", "image.png"),
    "Oppenheimer": ("oppenheimer", "image.png"),
    "Dune: Part Two": ("dune", "image.png"),
    "Avatar: The Way of Water": ("avatar", "image.png"),
    "Godzilla x Kong": ("godzilla-x-kong", "image.png"),
    "Suzume": ("suzume", "image.png"),
    "Spirited Away": ("spirited-away", "image.png"),
    "Guardians of the Galaxy Vol. 3": ("guardians-of-the-galaxy-vol-3", "image.png"),
}

for title, (folder, fname) in mapping.items():
    src = os.path.join(src_base, folder, "images", fname)
    ext = os.path.splitext(fname)[1].lower()
    dest_name = f"{folder}{ext}"
    dest = os.path.join(dest_base, dest_name)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"Copied {title} -> {dest_name}")
    else:
        print(f"WARNING: Not found {src}")

# Copy default.jpg
default_src = os.path.join(src_base, "avengers", "images", "default.jpg")
if os.path.exists(default_src):
    shutil.copy2(default_src, "d:/cinema_booking_simple/web/public/images/default.jpg")
    print("Copied default.jpg")

# Copy background images
bg_src = "d:/cinema_booking_simple/book_movie_ticket/book_movie_ticket_app/static/backgrounds/images"
bg_dest = "d:/cinema_booking_simple/web/public/images/backgrounds"
os.makedirs(bg_dest, exist_ok=True)
if os.path.exists(bg_src):
    for f in os.listdir(bg_src):
        if f.endswith((".jpg", ".png", ".webp")):
            shutil.copy2(os.path.join(bg_src, f), os.path.join(bg_dest, f))
            print(f"Copied background {f}")

print("DONE copying all images!")
