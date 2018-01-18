# _*_ coding: utf-8 _*_

import time
import datetime
import os
import sys
import xlrd
import xlwt
import random

from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from app01.models import Asset, Host
from other import hosts_ssh, hosts_file, chk_ip, crypt, update_pwd, transfer
from other.export import HostResource

import ansible.runner

# Create your views here.

@login_required
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

@login_required
def search_asset(request):
    keyword = request.GET['search']
    search_info = Asset.objects.filter(
        Q(ip_pub__icontains=keyword)|Q(hostname__icontains=keyword)|
        Q(os__icontains=keyword)|Q(cpu_model__icontains=keyword)|
        Q(mem__icontains=keyword)|Q(cpu__icontains=keyword)|
        Q(disk__icontains=keyword)
    )

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

@login_required
def getOne(request):
    get_result = None
    update_time = None
    ip_pub = None
    system = None
    
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        runner = ansible.runner.Runner(
            module_name='setup', pattern=ip_pub, host_list='/etc/ansible/hosts_cmdb'
        )
        data = runner.run()

        if data['dark'] == {} and data['contacted'] == {}:
            status = u'未更新'
        else:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')

        for (host, result) in data['contacted'].items():
            if not 'failed' in result:
                #ip = data['contacted'][host]['ansible_facts']['ansible_default_ipv4']['address']
                #if chk_ip.do(ip) == 'matched':
                #    ip_pub = ip
                hostname = data['contacted'][host]['ansible_facts']['ansible_hostname']
                if 'ansible_lsb' in data['contacted'][host]['ansible_facts'].keys():
                    system = data['contacted'][host]['ansible_facts']['ansible_lsb']['description']
                elif 'ansible_distribution' in data['contacted'][host]['ansible_facts'].keys():
                    distribution = data['contacted'][host]['ansible_facts']['ansible_distribution']
                    distribution_major = data['contacted'][host]['ansible_facts']['ansible_distribution_version']
                    system = ' '.join([distribution, distribution_major])
                cpu_core = data['contacted'][host]['ansible_facts']['ansible_processor_cores']
                #单颗的核数
                cpu_thread = data['contacted'][host]['ansible_facts']['ansible_processor_threads_per_core']
                #单核的线程数
                cpu_count = data['contacted'][host]['ansible_facts']['ansible_processor_count']
                #颗数
                cpu = "%s核%s线程 x %s" %(cpu_core, cpu_thread, cpu_count)
                cpu_model = data['contacted'][host]['ansible_facts']['ansible_processor'][-1]
                mem = data['contacted'][host]['ansible_facts']['ansible_memtotal_mb']
                device = data['contacted'][host]['ansible_facts']['ansible_devices'].keys()
                for partation in device:
                    if data['contacted'][host]['ansible_facts']['ansible_devices'][partation]['removable'] == '0':
                        disk = data['contacted'][host]['ansible_facts']['ansible_devices'][partation]['size']
            
                print '\n--------------------\ngetOne:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
                
                Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
                status = 'success'
                print status
                
            elif 'failed' in result:
                hostname = 'N/A'
                system = 'N/A'
                cpu_core = 'N/A'
                cpu_thread = 'N/A'
                cpu_count = 'N/A'
                cpu = 'N/A'
                cpu_model = 'N/A'
                mem = 'N/A'
                disk = 'N/A'
        
                Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
                print '\n--------------------\ngetOne:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(ip_pub, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
                status = 'failed: '+result['msg']
                print status

        for (host, result) in data['dark'].items():
            hostname = 'N/A'
            system = 'N/A'
            cpu_core = 'N/A'
            cpu_thread = 'N/A'
            cpu_count = 'N/A'
            cpu = 'N/A'
            cpu_model = 'N/A'
            mem = 'N/A'
            disk = 'N/A'
        
            Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
            print '\n--------------------\ngetOne:'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
            print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
            status = 'failed: '+result['msg']
            print status

    return HttpResponse(status)

@login_required
def getAll(request):
    disk = None
    system = None
    update_time = None
    if os.path.isfile('/etc/ansible/hosts_cmdb'): 
        if request.method == 'POST':
            runner = ansible.runner.Runner(
                module_name='setup', pattern='all', forks='10', host_list='/etc/ansible/hosts_cmdb'
            )
            data = runner.run()
    
            Asset.objects.all().delete()
    
            print '\n--------------------\ngetAll:'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
            for (host, result) in data['contacted'].items():
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
                
                if not 'failed' in result:
                   # ip = data['contacted'][host]['ansible_facts']['ansible_default_ipv4']['address']
                   # if chk_ip.do(ip) == 'matched':
                   #     ip = ip
                    hostname = data['contacted'][host]['ansible_facts']['ansible_hostname']
                    if 'ansible_lsb' in data['contacted'][host]['ansible_facts'].keys():
                        system = data['contacted'][host]['ansible_facts']['ansible_lsb']['description']
                    elif 'ansible_distribution' in data['contacted'][host]['ansible_facts'].keys():
                        distribution = data['contacted'][host]['ansible_facts']['ansible_distribution']
                        distribution_major = data['contacted'][host]['ansible_facts']['ansible_distribution_version']
                        system = ' '.join([distribution, distribution_major])
                    cpu_core = data['contacted'][host]['ansible_facts']['ansible_processor_cores']
                    #单颗的核数
                    cpu_thread = data['contacted'][host]['ansible_facts']['ansible_processor_threads_per_core']
                    #单核的线程数
                    cpu_count = data['contacted'][host]['ansible_facts']['ansible_processor_count']
                    #颗数
                    cpu = "%s核%s线程 x %s" %(cpu_core, cpu_thread, cpu_count)
                    cpu_model = data['contacted'][host]['ansible_facts']['ansible_processor'][-1]
                    mem = data['contacted'][host]['ansible_facts']['ansible_memtotal_mb']
                    device = data['contacted'][host]['ansible_facts']['ansible_devices'].keys()
                    for partation in device:
                        if data['contacted'][host]['ansible_facts']['ansible_devices'][partation]['removable'] == '0':
                            disk = data['contacted'][host]['ansible_facts']['ansible_devices'][partation]['size']
                    print u"地址为%s的主机名为%s，操作系统为%s ，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
                    if not Asset.objects.filter(ip_pub=host):
                        Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
                    else:
                        Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
    
            for (host, result) in data['contacted'].items():
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
    
                if 'failed' in result:
                    hostname = 'N/A'
                    system = 'N/A'
                    cpu_core = 'N/A'
                    cpu_thread = 'N/A'
                    cpu_count = 'N/A'
                    cpu = 'N/A'
                    cpu_model = 'N/A'
                    mem = 'N/A'
                    disk = 'N/A'
    
                    if not Asset.objects.filter(ip_pub=host):
                        Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
                    else:
                        Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
                    print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
    
            for (host, result) in data['dark'].items():
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
    
                hostname = 'N/A'
                system = 'N/A'
                cpu_core = 'N/A'
                cpu_thread = 'N/A'
                cpu_count = 'N/A'
                cpu = 'N/A'
                cpu_model = 'N/A'
                mem = 'N/A'
                disk = 'N/A'
         
                if not Asset.objects.filter(ip_pub=host):
                    Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
                else:
                    Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
                print u"地址为%s的主机名为%s，操作系统为%s，CPU型号：%s，%s核%s线程x%s，内存%sMB，磁盘%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
    
            insert_time = Asset.objects.order_by('-update_time')[:1]
    
            if insert_time:
                for update_time in insert_time:
                    update_time = update_time.update_time 
        #            print update_time
            else:
                update_time = u'未更新'

        return HttpResponse(update_time)
    else:
        update_time = u'未更新'

        return HttpResponse(update_time)

@login_required
def delasset(request):
    status = None
    content = None
    filename = '/etc/ansible/hosts_cmdb'
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        print ip_pub
        username = Host.objects.filter(ip_pub=ip_pub)
        for user in username:
            content = '%s ansible_ssh_user=%s' % (ip_pub, user.username)
        Asset.objects.filter(ip_pub=ip_pub).delete()
        Host.objects.filter(ip_pub=ip_pub).delete()
        if not Asset.objects.filter(ip_pub=ip_pub):
            os.system("sed -i '/"+content+"/d' "+filename)
            status = "success"
        else:
            status = "failed"
        print '\n--------------------\ndelasset:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
        print '删除%s，结果:%s' %(content, status)

    return HttpResponse(status) 

@login_required
def host(request):
    all_info = Host.objects.all()

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(all_info, 10, request=request)
    info = p.page(page)

    return render(request, 'host.html', {'info': info})

@login_required
def download_template(request):
    filename = sys.path[0]+'/media/template.xls'
    if os.path.isfile(filename):
        f = open(filename)
        data = f.read()
        f.close()
        response = HttpResponse(data) 
        response['Content-Disposition'] = 'attachment; filename=%s' % 'template.xls'
        return response
    else:
        return render(request, 'host.html', {'error': u'模版文件不存在！'})

@login_required
def upload(request):
    path = sys.path[0]+'/upload'
    if request.method == "POST":
        myFile =request.FILES.get("templateFile", None)
        destination = open(os.path.join(path, myFile.name), 'wb+')

        for chunk in myFile.chunks():
            destination.write(chunk) 
        destination.close() 

        if not os.path.isfile(path+'/template.xls'):
            return render(request, 'host.html',{'upload_info': u'模版文件上传失败！'})
        else:
            return render(request, 'host.html',{'upload_info': u'success'})

    return HttpResponseRedirect('/host/')

@login_required
def template_add(request):
    flag = 0
    count = 5
    filename = sys.path[0]+'/upload/template.xls'
    if request.method == 'POST':
        while count>0:
            if os.path.isfile(filename):
                data = xlrd.open_workbook(filename)
                table = data.sheets()[0]
                nrows = table.nrows
                print '\n--------------------\ntemplate_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                for i in range(1, nrows):
                    ip_pub = table.row_values(i)[0]
                    ip_prv = table.row_values(i)[1]
                    username = table.row_values(i)[2]
                    password = table.row_values(i)[3]
                    info = hosts_ssh.do_ssh(request, ip_pub, username, password, flag)
                    print '模版添加%s，认证用户：%s，结果：%s' %(ip_pub, username, info)
                    if not Host.objects.filter(ip_pub=ip_pub):
                        Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username, status=info)
                    else:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
                        Host.objects.filter(ip_pub=ip_pub).update(username=username, status=info, update_time=update_time) 
                    flag = 1
                status = u'添加完成'
                print status
                os.remove(filename)
                break
            else:
                print '\n--------------------\ntemplate_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                print u'未发现上传的模版文件，剩余重试次数：%s' % count
                count-=1
                time.sleep(1)
                status = u'未发现上传的模版文件!'

    return HttpResponse(status)

@login_required
def manual_add(request):
    info = ''
    if request.method == 'POST':
        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
        ip_pub = request.POST['ip_pub']
        ip_prv = request.POST['ip_prv']
        username = request.POST['authuser']
        password = request.POST['passw0rd']
        pwd_encrypt = crypt.do('set', password)
        
        if Host.objects.filter(ip_pub=ip_pub):
            info = u'该IP已存在'
            Host.objects.filter(ip_pub=ip_pub).update(update_time=update_time)
            print '\n--------------------\nmanual_add:'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
            print '手动添加%s，用户名：%s，结果:%s' %(ip_pub, username, info)
            return render(request, 'host.html', {'status_warning': info})
        else:
            info = hosts_ssh.do_ssh(request, ip_pub, username, password, flag=1)
            if info == '成功':
                Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username, pwd=pwd_encrypt, status=info)    
                print '\n--------------------\nmanual_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                print '手动添加%s，用户名：%s，结果:%s' %(ip_pub, username, info)
                return render(request, 'host.html', {'status_success': info})
            else:
                #Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username, status=info)
                print '\n--------------------\nmanual_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                print '手动添加%s，用户名：%s，结果:%s' %(ip_pub, username, info)
                return render(request, 'host.html', {'status_warning': info})
        
    else:
        return HttpResponseRedirect('/host/')

@login_required
def delhost(request):
    status = None
    filename = '/etc/ansible/hosts_cmdb'
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        username = request.POST['username']
        content = '%s ansible_ssh_user=%s' % (ip_pub, username)

        Host.objects.filter(ip_pub=ip_pub).delete()
        Asset.objects.filter(ip_pub=ip_pub).delete()
        if not Host.objects.filter(ip_pub=ip_pub):
            os.system("sed -i '/"+content+"/d' "+filename)
            status = "success"
        else:
            status = "failed"
        print '\n--------------------\ndelhost:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
        print '删除%s，结果:%s' %(content, status)

    return HttpResponse(status)
    
@login_required
def search_host(request):
    keyword = request.GET['search']
    search_info = Host.objects.filter(
        Q(ip_pub__icontains=keyword)|Q(ip_prv__icontains=keyword)|
        Q(username__icontains=keyword)|Q(status__icontains=keyword)
    )

    count = search_info.count()

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(search_info, 10, request=request)
    info = p.page(page)

    return render(request, 'host.html', {'info': info, })

@login_required
def check_host(request):
    status = None
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        runner = ansible.runner.Runner(
            module_name='ping', pattern=ip_pub, host_list='/etc/ansible/hosts_cmdb'
        )
        data = runner.run()

        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')

        for (host, result) in data['contacted'].items():
            if not 'failed' in result:
                status = 'success'
            else:
                status = 'failed'

        for (host, result) in data['dark'].items():
            status = 'failed: '+result['msg']

        print '\n--------------------\ncheck_host:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
        print '检测%s，结果：%s' % (ip_pub, status)

    return HttpResponse(status)

# 更改资产密码
@login_required
def UpdatePwd(request):
#    1.add sudo permission to normal user eg. usermode wheel user01
#    2.run cmd 'sudo passwd user01' to change password of user01
    ip = request.POST.get('ip', '')
    username = request.POST.get('username', '')
    pwd_generate = "".join(random.sample('1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()',12))
    print u'\n--------------------\nupdate_pwd:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'更新%s的密码:' % (ip)
    pwd_update = update_pwd.do(username, ip, transfer.do(pwd_generate))
    print u'结果：%s' % (pwd_update)
    if pwd_update == 'success':
        print u'step：对密码进行加密存储'
        pwd_crypt = crypt.do('set', transfer.do(pwd_generate))
        # print ip, pwd_generate, pwd_crypt    
        if pwd_crypt=='error':
            status = 'failed'
            print u'存储失败!'
        else:
            status = 'success'
            host_pwd = Host.objects.get(ip_pub=ip)
            host_pwd.pwd = pwd_crypt
            host_pwd.save()
            print u'更新完成!'
    else:
        status = 'failed'

    return HttpResponse(status)



# 导出host的ip、密码
@login_required
def export_host(request):
    global export_host_filename
    status = []
    export_host_filename = sys.path[0]+'/media/'+time.strftime('%Y-%m-%d-%H-%M', time.localtime())+'.xls'
    headers = (u'公网IP', u'内网IP', u'用户名', u'密码')
    print u'\n--------------------\nexport_host:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'导出 host 列表'
    
    try:
        dataset = HostResource().export() 
        workbook = xlwt.Workbook(encoding = 'utf-8')
        worksheet = workbook.add_sheet('sheet01')
        # style = xlwt.XFStyle()
        # font = xlwt.Font()
        # font.name = u'宋体'
        # font.bold = True
        # style.font = font
        
        for i in range(0, len(headers)):
            worksheet.write(0, i, headers[i])
        
        rows = len(dataset)
        line = len(dataset[0])
        row = 1
        
        
        for each in dataset:
            print u'step：获取第%s条信息' % row
            
            for j in range(0, line):
                
                content = each[j]
                if j==3:
                    print u'step：对密码进行解密'
                    content = crypt.do('get', each[j])
                # print 'col', j
                # print 'each[k]', each[j]
                worksheet.write(row, j, content)
            print u'step：写入第%s条信息\n' % row
            row += 1
            
        
        workbook.save(export_host_filename)
        if os.path.isfile(export_host_filename):
            status.append('success')
            status.append(export_host_filename)
        else:
            status.append('failed')
    except Exception as e:
        status.append('failed')
        status.append(e)

    print u'结果：', status
    
    return JsonResponse(status, safe=False)

    
@login_required
def download_host(request):
    print u'\n--------------------\ndownload_host:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'下载 host 列表'
    print u'step：检查文件是否存在'
    if os.path.isfile(export_host_filename):
        print u'step：文件存在，开始解析'
        f = open(export_host_filename)
        data = f.read()
        f.close()
        response = HttpResponse(data) 
        response['Content-Disposition'] = 'attachment; filename=%s' % export_host_filename.split('/')[-1]
        print u'step：解析完成，删除文件'
        os.remove(export_host_filename)
        return response
    else:
        print u'结果：文件不存在！'
        return render(request, 'host.html', {'error': u'文件不存在！'})

    

def loginview(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['passw0rd']
        url = request.POST['next']
        error = u'用户名或密码错误'
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(url or '/')
        else:
            return render(request, 'login.html', {'error': error})

@login_required
def logoutview(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")
