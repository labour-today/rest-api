# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('push_notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contractor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=50)),
                ('phone_number', models.CharField(default=None, max_length=12, null=True, blank=True)),
                ('customer_id', models.CharField(default=None, max_length=10000, null=True, blank=True)),
                ('device', models.ForeignKey(default=None, to='push_notifications.GCMDevice')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_code', models.CharField(max_length=50)),
                ('job_address', models.CharField(max_length=200)),
                ('job_description', models.CharField(max_length=500)),
                ('start_time', models.CharField(max_length=50)),
                ('start_date', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('province', models.CharField(max_length=20)),
                ('wage', models.CharField(max_length=10)),
                ('expired', models.CharField(max_length=5)),
                ('duration', models.CharField(max_length=50)),
                ('contractor', models.ForeignKey(to='server.Contractor')),
            ],
        ),
        migrations.CreateModel(
            name='Labourer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(default=None, max_length=200, null=True, blank=True)),
                ('sin', models.CharField(default=None, max_length=9, null=True, blank=True)),
                ('phone_number', models.CharField(max_length=12)),
                ('rating', models.CharField(default=None, max_length=10, null=True, blank=True)),
                ('carpentry', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('concrete_forming', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('general_labour', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('dry_walling', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('painting', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('landscaping', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('machine_operating', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('roofing', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('brick_laying', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('electrical', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('plumbing', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('available', models.CharField(default=None, max_length=50, null=True, blank=True)),
                ('hat', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('vest', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('tool', models.CharField(default=0, max_length=3, null=True, blank=True)),
                ('device', models.ForeignKey(default=None, to='push_notifications.GCMDevice')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='labourer',
            field=models.ManyToManyField(related_name='job', to='server.Labourer'),
        ),
    ]
