from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Concert)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Enrollment)