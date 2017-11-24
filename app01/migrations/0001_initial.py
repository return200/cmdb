# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-11-23 14:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(verbose_name='IP\u5730\u5740')),
                ('hostname', models.CharField(max_length=20, verbose_name='\u4e3b\u673a\u540d')),
                ('os', models.CharField(max_length=50, verbose_name='\u64cd\u4f5c\u7cfb\u7edf')),
                ('cpu_model', models.CharField(max_length=50, verbose_name='CPU\u578b\u53f7')),
                ('cpu', models.CharField(max_length=50, verbose_name='CPU')),
                ('mem', models.CharField(max_length=50, verbose_name='\u5185\u5b58')),
                ('disk', models.CharField(max_length=50, verbose_name='\u786c\u76d8')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
            options={
                'ordering': ['ip'],
                'verbose_name': '\u8d44\u4ea7\u4fe1\u606f\u8868',
                'verbose_name_plural': '\u8d44\u4ea7\u4fe1\u606f\u8868',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(verbose_name='IP\u5730\u5740')),
                ('username', models.CharField(max_length=20, verbose_name='\u7528\u6237\u540d')),
                ('add_time', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u4e0a\u6b21\u68c0\u6d4b\u65f6\u95f4')),
                ('status', models.CharField(max_length=50, verbose_name='\u6dfb\u52a0\u72b6\u6001')),
            ],
            options={
                'ordering': ['ip'],
                'verbose_name': '\u4e3b\u673a\u4fe1\u606f\u8868',
                'verbose_name_plural': '\u4e3b\u673a\u4fe1\u606f\u8868',
            },
        ),
    ]