#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from import_export import resources
from app01.models import Host

class HostResource(resources.ModelResource):

    class Meta:
        model = Host
        fields = ('ip_pub', 'ip_prv', 'pwd_root', 'pwd_user')