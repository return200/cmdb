# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-01-16 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20171206_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='pwd',
            field=models.CharField(default='aaaaaaaaaaaaa', max_length=50, verbose_name='\u767b\u5f55\u5bc6\u7801'),
            preserve_default=False,
        ),
    ]
