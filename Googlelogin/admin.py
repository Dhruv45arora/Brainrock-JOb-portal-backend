from django.contrib import admin
from .models import CustomUser  # import your user model

admin.site.register(CustomUser)  # register it
