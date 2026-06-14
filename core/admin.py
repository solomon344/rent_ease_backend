from django.contrib import admin
from core.models import (Property, Booking, Amenties, PropertyMedia, Profile)

# Register your models here.
admin.site.register(Property)
admin.site.register(Booking)
admin.site.register(Amenties)
admin.site.register(PropertyMedia)
admin.site.register(Profile)