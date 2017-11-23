# _*_ encoding: utf-8 _*_

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import datetime, time

# Create your models here.

class Asset(models.Model):
    ip = models.GenericIPAddressField(max_length=50, verbose_name=u'IP地址')
    hostname = models.CharField(max_length=20, verbose_name=u'主机名')
    os = models.CharField(max_length=50, verbose_name=u'操作系统')
    cpu_model = models.CharField(max_length=50, verbose_name=u'CPU型号')
    cpu = models.CharField(max_length=50, verbose_name=u'CPU')
    mem = models.CharField(max_length=50, verbose_name=u'内存')
    disk = models.CharField(max_length=50, verbose_name=u'硬盘')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
 
    class Meta:
        verbose_name = u"资产信息表"
	verbose_name_plural = verbose_name
	ordering = ['ip']
    
    def __unicode__(self):
        return self.ip

class Host(models.Model):
    pass
