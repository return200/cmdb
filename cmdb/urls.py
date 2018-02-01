# _*_ coding: utf-8 _*_
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
    
    # 后台
    url(r'^adminn/', xadmin.site.urls),
    
    # 更新单个资产
    url(r'^getone/$', views.getOne),
    
    # 更新全部资产
    url(r'^getall/$', views.getAll),
    
    # 资产搜索
    url(r'^search/asset/$', views.search_asset),
    
    # 主机搜索
    url(r'^search/host/$', views.search_host),
    
    # 删除资产
    url(r'^delasset/$', views.delasset),
    
    # 删除主机
    url(r'^delhost/$', views.delhost),
    
    # 菜单“主机列表”
    url(r'^host/$', views.host),
    
    # 下载模版
    url(r'^download/template/$', views.download_template),
    
    # 下载导出的主机列表
    url(r'^download/host/$', views.download_host),
    
    # 下载导出的资产列表
    url(r'^download/asset/$', views.download_asset),
    
    # 上传主机模版
    url(r'^upload/$', views.upload),
    
    # 模版添加主机
    url(r'^addhost/template/$', views.template_add),
    
    # 手动添加主机
    url(r'^addhost/manual/$', views.manual_add),
    
    # 检测主机状态
    url(r'^chkhost/$', views.check_host),
    
    # 更改主机密码
    url(r'^pwd/update/$', views.UpdatePwd),
    
    # 导出主机列表
    url(r'^export/host/$', views.export_host),
    
    # 导出资产列表
    url(r'^export/asset/$', views.export_asset),
    
    # 批量添加资产的进度
    url(r'^percentage/asset/$', views.getAll_percentage),
    
    # 批量添加主机的进度
    url(r'^percentage/host/$', views.template_add_percentage),
    
]
