from django.contrib import admin
from .models import Profile, Trip

# Register your models here.
admin.site.register(Trip)
admin.site.register(Profile)