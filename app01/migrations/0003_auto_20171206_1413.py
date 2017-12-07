# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-12-06 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_auto_20171206_0947'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['ip_pub'], 'verbose_name': '\u8d44\u4ea7\u4fe1\u606f\u8868', 'verbose_name_plural': '\u8d44\u4ea7\u4fe1\u606f\u8868'},
        ),
        migrations.RemoveField(
            model_name='asset',
            name='ip',
        ),
        migrations.AddField(
            model_name='asset',
            name='ip_pub',
            field=models.GenericIPAddressField(default='1.1.1.1', verbose_name='\u5916\u7f51IP\u5730\u5740'),
            preserve_default=False,
        ),
    ]