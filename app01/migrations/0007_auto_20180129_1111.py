# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-01-29 11:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_auto_20180126_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='pwd_root',
            field=models.CharField(max_length=100, verbose_name='root\u767b\u5f55\u5bc6\u7801'),
        ),
        migrations.AlterField(
            model_name='host',
            name='pwd_user',
            field=models.CharField(max_length=100, verbose_name='\u666e\u901a\u7528\u6237\u767b\u5f55\u5bc6\u7801'),
        ),
    ]