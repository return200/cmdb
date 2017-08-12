# _*_ encoding: utf-8 _*_

from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Host(models.Model):
    ip = models.CharField(max_length=50, verbose_name=u'IP地址')
    hostname = models.CharField(max_length=20, verbose_name=u'主机名')
    os = models.CharField(max_length=50, verbose_name=u'操作系统')
    cpu_model = models.CharField(max_length=50, verbose_name=u'CPU型号')
    cpu = models.CharField(max_length=50, verbose_name=u'CPU')
    mem = models.CharField(max_length=50, verbose_name=u'内存')
    disk = models.CharField(max_length=50, verbose_name=u'硬盘')
