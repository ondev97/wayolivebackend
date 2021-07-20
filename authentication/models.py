import os

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import AbstractUser
from io import BytesIO
from PIL import Image


# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    username = models.CharField(max_length=30,unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=80,unique=True)
    phone_no = models.CharField(max_length=15,null=True,blank=True, unique=True)
    is_band = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


class BandProfile(models.Model):
    def upload_location(instance, filename):
        return "band_images/%s/%s" % (instance.user.username, filename)

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    band_description = models.TextField(null=True,blank=True)
    band_image = models.ImageField(null=True,blank=True, upload_to=upload_location, default='user_images/default.jpg')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.band_image:
            im = Image.open(self.band_image)
            im = im.convert('RGB')
            # create a BytesIO object
            im_io = BytesIO()
            # save image to BytesIO object
            im.save(im_io, 'JPEG', quality=20)
            temp_name = os.path.split(self.band_image.name)[1]
            self.band_image.save(temp_name, content=ContentFile(im_io.getvalue()), save=False)
            super().save(*args, **kwargs)


class UserProfile(models.Model):
    def upload_location(instance, filename):
        return "user_images/%s/%s" % (instance.user.username, filename)


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_description = models.TextField(null=True,blank=True)
    user_image = models.ImageField(null=True,blank=True, upload_to=upload_location, default='user_images/default.jpg')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.user_image:
            im = Image.open(self.user_image)
            im = im.convert('RGB')
            # create a BytesIO object
            im_io = BytesIO()
            # save image to BytesIO object
            im.save(im_io, 'JPEG', quality=20)
            temp_name = os.path.split(self.user_image.name)[1]
            self.user_image.save(temp_name, content=ContentFile(im_io.getvalue()), save=False)
            super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def createprofile(sender, instance, created, **kwargs):
    print("///////", created)
    if instance.is_band:
        BandProfile.objects.get_or_create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def saveprofile(sender, instance, **kwargs):
    print('Saved')
    if instance.is_band:
        instance.bandprofile.save()
    else:
        print("status",instance.is_superuser)
        UserProfile.objects.get_or_create(user=instance)


class Phone(models.Model):
    mobile = models.CharField(max_length=15, default="0000000000")
    otp = models.CharField(max_length=6, default="100001")

    def __str__(self):
        return str(self.mobile)






