"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from app01 import views
import xadmin

urlpatterns = [
    url(r'^$', views.asset),
    url(r'^login/$', views.loginview),
    url(r'^logout/$', views.logoutview),
    url(r'^admin/', xadmin.site.urls),
    url(r'^getone/$', views.getOne),
    url(r'^getall/$', views.getAll),
    url(r'^search/asset/$', views.search_asset),
    url(r'^search/host/$', views.search_host),
    url(r'^delasset/$', views.delasset),
    url(r'^delhost/$', views.delhost),
    url(r'^host/$', views.host),
    url(r'^download/$', views.download),
    url(r'^upload/$', views.upload),
    url(r'^addhost/template/$', views.template_add),
    url(r'^addhost/manual/$', views.manual_add),
    url(r'^chkhost/$', views.check_host),
    
    
    
]
