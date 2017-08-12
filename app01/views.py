# _*_ coding: utf-8 _*_

from django.shortcuts import render
from django.db.models import Q

from app01.models import Host

import ansible.runner

# Create your views here.

def asset(request):
    info = Host.objects.all()
    return render(request, 'asset.html', {'info': info})

def search(request):
    keyword = request.POST['search']
    info = Host.objects.filter(
        Q(ip__icontains=keyword)|Q(hostname__icontains=keyword)|
	Q(os__icontains=keyword)|Q(cpu_model__icontains=keyword)|
	Q(mem__icontains=keyword)|Q(cpu__icontains=keyword)|
	Q(disk__icontains=keyword)
    )
    return render(request, 'asset.html', {'info': info})

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

    Host.objects.filter(ip=ip).update(hostname=hostname, os=os, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
    info = Host.objects.all()
    if not 'failed' in data:
        get_result = 'success'
    return render(request, 'asset.html', {'get_result': get_result, 'info': info}) 


def getAll(request):
    disk = ''

    runner = ansible.runner.Runner(
        module_name='setup', pattern='all', forks='10'
    )
    data = runner.run()
    Host.objects.all().delete()

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
	Host.objects.create(ip=ip, hostname=hostname, os=os, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
	info = Host.objects.all()
    return render(request, 'index.html', {'info': info})
