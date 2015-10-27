# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labourer',
            name='available',
            field=models.CharField(default=None, max_length=50, null=True, blank=True),
        ),
    ]
