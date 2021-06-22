import os

from django.core.files.base import ContentFile
from django.db import models
from authentication.models import BandProfile,UserProfile
from django.utils.timezone import now
from datetime import date, time
from io import BytesIO
from PIL import Image

# Create your models here.


class Band(models.Model):
    pass


class EventMode(models.Model):
    band = models.ForeignKey(BandProfile, on_delete=models.CASCADE, null=True, default=None)
    event_mode_name = models.CharField(max_length=300,null=True,blank=True)

    def __str__(self):
        return self.event_mode_name



class Event(models.Model):
    def upload_location(instance, filename):
        return "event_images/%s/%s" % (instance.event_name, filename)

    event_mode = models.ForeignKey(EventMode, on_delete=models.SET_NULL, null=True, default=None)
    event_name = models.CharField(max_length=300,null=True,blank=True)
    band = models.ForeignKey(BandProfile,on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    event_type = models.CharField(max_length=100,null=True,blank=True)
    event_date = models.DateField(default=date.today)
    event_start = models.TextField()
    event_end = models.TextField()
    event_label = models.CharField(max_length=15,null=True,blank=True)
    event_content = models.TextField(null=True,blank=True)
    is_freeze = models.BooleanField(default=False)
    event_cover = models.ImageField(null=True, blank=True, upload_to=upload_location, default='event_images/default.jpg')
    event_price = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.event_name

    def save(self, *args, **kwargs):
        if self.event_cover:
            im = Image.open(self.event_cover)
            im = im.convert('RGB')
            # create a BytesIO object
            im_io = BytesIO()
            # save image to BytesIO object
            im.save(im_io, 'JPEG', quality=20)
            temp_name = os.path.split(self.event_cover.name)[1]
            self.event_cover.save(temp_name, content=ContentFile(im_io.getvalue()), save=False)
            super().save(*args, **kwargs)


class Enrollment(models.Model):
    ticket_number = models.CharField(max_length=100,default="Text here",null=True)
    event = models.ForeignKey(Event,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True)
    is_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.ticket_number


class Ticket(models.Model):
    ticket_number = models.CharField(max_length=100, null=True)
    isValid = models.BooleanField(default=True)
    isIssued = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.ticket_number + "  issued: " + str(self.isIssued)






