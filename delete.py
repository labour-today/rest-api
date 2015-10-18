from server.models import Labourer, Contractor, Job
from django.contrib.auth.models import User
from push_notifications.models import GCMDevice

User.objects.all().delete()
Labourer.objects.all().delete()
Contractor.objects.all().delete()
Job.objects.all().delete()
GCMDevice.objects.all().delete()
