from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(EventMode)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Enrollment)
admin.site.register(AudienceDataForm)
admin.site.register(Payment)