from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    username = models.CharField(max_length=30,unique=True)
    email = models.EmailField(max_length=80,unique=True)
    phone_no = models.CharField(max_length=15,null=True,blank=True)
    is_band = models.BooleanField(default=False)


class BandProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    band_description = models.TextField()
    band_image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    user_description = models.TextField()
    user_image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.user.username


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






