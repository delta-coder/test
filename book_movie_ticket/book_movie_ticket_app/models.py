from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver

from .background_context import create_movie_background_folders

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.username


class Movie(models.Model):
    title = models.CharField(max_length=150)
    genre = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    director = models.CharField(max_length=100)
    release_date = models.DateField()
    description = models.TextField()
    poster_url = models.URLField(blank=True)

    @property
    def poster_path(self):
        posters = {
            'Avengers: Endgame': 'images/avengers.jpg',
            'Interstellar': 'images/interstellar.jpg',
            'Doraemon': 'images/doraemon.jpg',
        }
        return posters.get(self.title, 'images/default.jpg')

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.room.name} - Ghế {self.number}'

    class Meta:
        unique_together = ('room', 'number')
        ordering = ['number']


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()

    def __str__(self):
        return f'{self.movie.title} - {self.start_time.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['start_time']


class Ticket(models.Model):
    TICKET_TYPES = [
        ('Adult', 'Người lớn'),
        ('Child', 'Trẻ em'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES)
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.showtime.movie.title} - Ghế {self.seat.number}'

    class Meta:
        unique_together = ('showtime', 'seat')
        ordering = ['-created_at']


@receiver(post_save, sender=Room)
def create_seats(sender, instance, **kwargs):
    current_numbers = set(
        Seat.objects.filter(room=instance).values_list('number', flat=True)
    )

    for number in range(1, instance.capacity + 1):
        if number not in current_numbers:
            Seat.objects.create(room=instance, number=number)

# ==================================================
# TỰ TẠO FOLDER BACKGROUND KHI TẠO / SỬA PHIM
# ==================================================

@receiver(post_save, sender=Movie)
def create_movie_background_directory(
    sender,
    instance,
    **kwargs
):

    create_movie_background_folders(
        instance.title
    )