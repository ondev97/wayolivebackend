from django.db import models
from authentication.models import BandProfile,UserProfile

# Create your models here.


class Band(models.Model):
    pass


class Concert(models.Model):
    band = models.ForeignKey(BandProfile, on_delete=models.CASCADE, null=True, default=None)
    concert_name = models.CharField(max_length=300,null=True,blank=True)
    price = models.CharField(max_length=10,null=True,blank=True)
    concert_description = models.TextField(null=True,blank=True)
    concert_image = models.ImageField(null=True,blank=True)
    hours = models.CharField(max_length=10,null=True,blank=True)

    def __str__(self):
        return self.concert_name


class Event(models.Model):
    concert = models.ForeignKey(Concert,on_delete=models.CASCADE,null=True,default=None)
    event_name = models.CharField(max_length=300,null=True,blank=True)
    messages = models.TextField(null=True,blank=True)
    links = models.URLField(null=True,blank=True)
    event_mode = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.event_name


class Enrollment(models.Model):
    ticket_number = models.CharField(max_length=100,default="Text here",null=True)
    concert = models.ForeignKey(Concert,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True)
    is_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.ticket_number


class Ticket(models.Model):
    ticket_number = models.CharField(max_length=100, null=True)
    isValid = models.BooleanField(default=True)
    isIssued = models.BooleanField(default=False)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.ticket_number + "  issued: " + str(self.isIssued)






