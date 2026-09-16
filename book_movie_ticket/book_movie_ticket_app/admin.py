from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Movie, Room, Seat, Showtime, Ticket


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Movie)
admin.site.register(Room)
admin.site.register(Seat)
admin.site.register(Showtime)
admin.site.register(Ticket)
