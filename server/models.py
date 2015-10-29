from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from push_notifications.models import  GCMDevice

class Labourer(models.Model):
    address = models.CharField(max_length = 200, null = True, blank = True, default = None) # full address
    sin = models.CharField(max_length = 9, null = True, blank = True, default = None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    device = models.ForeignKey('push_notifications.GCMDevice', default = None)
    phone_number = models.CharField(max_length = 12)
    rating = models.CharField(max_length = 10, null = True, blank = True, default = None)    
    # Labourer experience
    carpentry = models.CharField(max_length = 3, null = True, blank = True, default = None)
    concrete_forming = models.CharField(max_length = 3, null = True, blank = True, default = None)
    general_labour = models.CharField(max_length = 2, null = True, blank = True, default = None) 
    # availability
    available = models.CharField(max_length = 50, null = True, blank = True, default = None)


class Contractor(models.Model):
    company_name = models.CharField(max_length = 50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    device = models.ForeignKey('push_notifications.GCMDevice', default = None)
    phone_number = models.CharField(max_length = 12, null = True, blank = True, default = None)
    customer_id = models.CharField(max_length = 100, null = True, blank = True, default = None)

class Job(models.Model):
    job_code = models.CharField(max_length = 50)
    contractor = models.ForeignKey('Contractor')
    labourer = models.ManyToManyField('Labourer', related_name = "job")
    expired = models.CharField(max_length = 5)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user = instance)
