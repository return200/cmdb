# _*_ coding: utf-8 _*_

from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import time, datetime
import os
import xlrd

from app01.models import Asset, Host
from other import hosts_ssh, hosts_file

import ansible.runner

# Create your views here.

def asset(request):
    all_info = Asset.objects.all()
    count = Asset.objects.all().count()
    insert_time = Asset.objects.order_by('-update_time')[:1]

    if insert_time:
        for update_time in insert_time:
            update_time = update_time.update_time 
#            print update_time
    else:
        update_time = u'未更新'

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    # Provide Paginator with the request object for complete querystring generation
    p = Paginator(all_info, 10, request=request)
    info = p.page(page)

    return render(request, 'asset.html', {'info': info, 'count': count, 'update_time': update_time})

def search(request):
    keyword = request.POST['search']
    search_info = Asset.objects.filter(
        Q(ip__icontains=keyword)|Q(hostname__icontains=keyword)|
        Q(os__icontains=keyword)|Q(cpu_model__icontains=keyword)|
        Q(mem__icontains=keyword)|Q(cpu__icontains=keyword)|
        Q(disk__icontains=keyword)
    )
    print "search_info %s" % type(search_info)

    count = search_info.count()

    insert_time = Asset.objects.order_by('-update_time')[:1]
    if insert_time:
        for update_time in insert_time:
            update_time = update_time.update_time
#            print update_time
    else:
        update_time = u'未更新'

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    # Provide Paginator with the request object for complete querystring generation
    p = Paginator(search_info, 10, request=request)
    info = p.page(page)


    return render(request, 'asset.html', {'info': info, 'count': count, 'update_time': update_time})

def getOne(request, ip):
    get_result = None
    runner = ansible.runner.Runner(
        module_name='setup', pattern=ip,
    )
    data = runner.run()
    hostname = data['contacted'][ip]['ansible_facts']['ansible_hostname']
    os = data['contacted'][ip]['ansible_facts']['ansible_lsb']['description']
    cpu_core = data['contacted'][ip]['ansible_facts']['ansible_processor_cores']
    #单颗的核数
    cpu_thread = data['contacted'][ip]['ansible_facts']['ansible_processor_threads_per_core']
    #单核的线程数
    cpu_count = data['contacted'][ip]['ansible_facts']['ansible_processor_count']
    #颗数
    cpu = "%s核%s线程 x %s" %(cpu_core, cpu_thread, cpu_count)
    cpu_model = data['contacted'][ip]['ansible_facts']['ansible_processor'][-1]
    mem = data['contacted'][ip]['ansible_facts']['ansible_memtotal_mb']
    device = data['contacted'][ip]['ansible_facts']['ansible_devices'].keys()
    for partation in device:
        if data['contacted'][ip]['ansible_facts']['ansible_devices'][partation]['removable'] == '0':
            disk = data['contacted'][ip]['ansible_facts']['ansible_devices'][partation]['size']

    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
    print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(ip, hostname, os, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)

    if not 'failed' in data:
        #get_result = 'success'
	local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
	Asset.objects.filter(ip=ip).update(hostname=hostname, os=os, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
#	print update_time
    return HttpResponse(update_time)


def getAll(request):
    disk = ''

    runner = ansible.runner.Runner(
        module_name='setup', pattern='all', forks='10'
    )
    data = runner.run()
    if not 'failed' in data:
        Asset.objects.all().delete()

    operation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print operation_time

    for each in data['contacted'].keys():
	#ip_all = data['contacted'][each]['ansible_facts']['ansible_all_ipv4_addresses']
	ip = data['contacted'][each]['ansible_facts']['ansible_default_ipv4']['address']
	hostname = data['contacted'][each]['ansible_facts']['ansible_hostname']
	os = data['contacted'][each]['ansible_facts']['ansible_lsb']['description']
	cpu_core = data['contacted'][each]['ansible_facts']['ansible_processor_cores']
	#单颗的核数
	cpu_thread = data['contacted'][each]['ansible_facts']['ansible_processor_threads_per_core']
	#单核的线程数
	cpu_count = data['contacted'][each]['ansible_facts']['ansible_processor_count']
	#颗数
	cpu = "%s核%s线程 x %s" %(cpu_core, cpu_thread, cpu_count)
	cpu_model = data['contacted'][each]['ansible_facts']['ansible_processor'][-1]
	mem = data['contacted'][each]['ansible_facts']['ansible_memtotal_mb']
	device = data['contacted'][each]['ansible_facts']['ansible_devices'].keys()
	for partation in device:
	    if data['contacted'][each]['ansible_facts']['ansible_devices'][partation]['removable'] == '0':
	        disk = data['contacted'][each]['ansible_facts']['ansible_devices'][partation]['size']
	print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(ip, hostname, os, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
	Asset.objects.create(ip=ip, hostname=hostname, os=os, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)

    insert_time = Asset.objects.order_by('-update_time')[:1]

    if insert_time:
        for update_time in insert_time:
            update_time = update_time.update_time 
#            print update_time
    else:
        update_time = u'未更新'
    return HttpResponse(update_time)

def delasset(request):
    status = ''
    ip = request.POST['ip']
    Asset.objects.filter(ip=ip).delete()
    if not Asset.objects.filter(ip=ip):
        status = "success"
    else:
        status = "failed"

    return HttpResponse(status) 

def host(request):
    all_info = Host.objects.all()

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    # Provide Paginator with the request object for complete querystring generation
    p = Paginator(all_info, 10, request=request)
    info = p.page(page)

    return render(request, 'host.html', {'info': info})

def download(request):
    filename = 'media/template.xls'
    if os.path.isfile(filename):
        f =open(filename)
        data = f.read()
        f.close()
        #以下设置项是为了下载任意类型文件
        response = HttpResponse(data) 
        response['Content-Disposition'] = 'attachment; filename=%s' % 'template.xls'
        return response
    else:
        return render(request, 'host.html', {'error': u'模版文件不存在！'})

def upload(request):
    if request.method == "POST":    # 请求方法为POST时，进行处理  
        myFile =request.FILES.get("templateFile", None)    # 获取上传的文件，如果没有文件，则默认为None  
        destination = open(os.path.join("upload",myFile.name), 'wb+')    # 打开特定的文件进行二进制的写操作  

        for chunk in myFile.chunks():      # 分块写入文件  
            destination.write(chunk) 
        destination.close() 

        if not os.path.isfile('upload/template.xls'):
   #     if not myFile: 
            return render(request, 'host.html',{'error': u'模版文件上传失败！'})
    return HttpResponseRedirect('/host/')

def template_add(request):
    count = 5
    filename = 'upload/template.xls'
    while True:
        if os.path.isfile(filename):
            data = xlrd.open_workbook(filename)
            table = data.sheets()[0]
            nrows = table.nrows
            for i in range(1, nrows):
                ip = table.row_values(i)[0]
                username = table.row_values(i)[1]
                password = table.row_values(i)[2]
                info = hosts_ssh.do_ssh(request, ip, username, password)
                print info
                if not Host.objects.filter(ip=ip):
                    Host.objects.create(ip=ip, username=username, status=info)
                else:
                    Host.objects.filter(ip=ip).update(username=username, status=info) 
	    break
	else:
	    count-=1
	    time.sleep(1)
    return HttpResponse('')


def change_pwd(request):
#    1.add sudo permission to normal user eg. usermode wheel user01
#    2.run cmd 'sudo passwd user01' to change password of user01
    pass

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST['username']
	password = request.POST['passw0rd']
        url = request.POST.get['next']
	user = auth.authenticated(username=username, password=password)
	if user is not None and user.is_active:
	    login(request, user)
	    return HttpResponseRedirect(url or '/')
	else:
	    return render(request, 'login.html', {'error': error})

def logoutview(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
