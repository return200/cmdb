# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-12-06 14:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_auto_20171206_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='ip_prv',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='\u5185\u7f51IP\u5730\u5740'),
        ),
    ]
