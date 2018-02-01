# _*_ coding: utf-8 _*_

import time
import datetime
import os
import sys
import xlrd
import xlwt
import random
import ConfigParser

from multiprocessing import Pool
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from app01.models import Asset, Host
from other import hosts_ssh, hosts_file, chk_ip, crypt, update_pwd, transfer, getall, templateAdd
from other.export import HostResource, AssetResource

import ansible.runner

# Create your views here.

try:
    global debug, password_length, host_list, max_processes
    config = ConfigParser.ConfigParser()
    config.read('%s/conf/cmdb.conf' % sys.path[0]) 
    debug = config.get('base', 'debug')
    max_processes = config.get('base', 'max_processes')
    password_length = config.get('base', 'password_length')
    host_list = config.get('base', 'host_list')
    if debug=='enabled':
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print '!!!!!!!!! DEBUG MODE ON !!!!!!!!!'
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    elif debug=='disabled':
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print '!!!!!!!! DEBUG MODE OFF !!!!!!!!!'
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    else:
        raise Exception('debug 选项错误[ enabled | disabled ]')
except Exception as e:
    print u'\033[31m！！！cmdb.conf 读取失败！！！\033[0m'
    print '\033[31m%s\033[0m\n' % e

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
        print '\n--------------------\ngetOne:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'收集资产信息'
        print u'step：收集', ip_pub
        runner = ansible.runner.Runner(
            module_name='setup', pattern=ip_pub, host_list=host_list
        )
        data = runner.run()
        
        if debug=='enabled':
            print u'      [DEBUG] ', data
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
            
                print u"      主机名：%s，操作系统：%s，CPU型号：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
                
                Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=str(mem)+' MB', disk=disk, update_time=update_time)
                status = 'success'
                
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
                print u"      主机名：%s，操作系统：%s，CPU型号：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
                status = 'failed: '+result['msg']

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
        
            Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system,
                                                    cpu=cpu, cpu_model=cpu_model,
                                                    mem=mem, disk=disk, update_time=update_time)
            print u"      主机名：%s，操作系统：%s，CPU型号：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
            status = 'failed: '+result['msg']
            
        if status=='success':
            print u'收集结果：\033[32m成功\033[0m\n'
        else:
            print u'收集结果：\033[31m失败：%s\033[0m\n' % status


    return HttpResponse(status)

    
@login_required
def getAll(request):
    disk = None
    system = None
    update_time = None
    global done
    done = 0
    
    def save(x):
        if not Asset.objects.filter(ip_pub=x[0]):
            Asset.objects.create(ip_pub=x[0], hostname=x[1], os=x[2], cpu=x[3], cpu_model=x[4], mem=x[5], disk=x[6])
        else:
            Asset.objects.filter(ip_pub=x[0]).update(hostname=x[1], os=x[2], cpu=x[3], cpu_model=x[4], mem=x[5], disk=x[6], update_time=x[7])
    
    if os.path.isfile(host_list): 
        if request.method == 'POST':
            print '\n--------------------\ngetAll:'
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'批量收集资产信息'
            print u'step：清空资产列表'
            try:
                Asset.objects.all().delete()
            except Exception as e:
                update_time = e
                return HttpResponse(update_time)
            print u'step：读取 inventory 列表：%s' % host_list
            with open(host_list, 'r+') as f:
                global all_host
                all_host = f.readlines()
            
            # print u'顺序执行开始', time.strftime('%H:%M:%S', time.localtime())
            # before = time.time()
            # print u'step：开始批量收集'
            # for each in all_host:
                # # res.append(do(each))
                # each = each.split(' ')[0]
                # getall.do(each, host_list, count)
                # count+=1
            # # for line in res:
                # # print line
            # print u'顺序执行结束', time.strftime('%H:%M:%S', time.localtime())
            # after = time.time()
            # use = after-before
            # print u'耗时 ', use
            
            # count = 001
            print u'step：开始批量收集'
            if debug=='enabled':
                print u'      [DEBUG] 并发执行开始 %s，进程数：%s' % (time.strftime('%H:%M:%S', time.localtime()), max_processes)
                before = time.time()
            pool = Pool(processes=int(max_processes))
            for each in all_host:
                each = each.split(' ')[0]
                pool.apply_async(getall.do, args=(each, host_list, debug), callback=save)
                done+=1
                # time.sleep(2)
            pool.close()
            pool.join()
            
            if debug=='enabled':
                print u'      [DEBUG] 并发执行结束', time.strftime('%H:%M:%S', time.localtime())
                after = time.time()
                use = after-before
                print u'      [DEBUG] 耗时 ', use
            
            print u'------批量收集完成------\n'
            
            insert_time = Asset.objects.order_by('-update_time')[:1]

            if insert_time:
                for update_time in insert_time:
                    update_time = update_time.update_time 
        #            print update_time
            else:
                update_time = u'未更新'
                
            return HttpResponse(update_time)
            

@login_required
def getAll_percentage(request):
    percent = {}
    percent['done'] = done
    percent['all_host'] = len(all_host)
    
    # print percent
    
    return JsonResponse(percent, safe=False)
        
        
@login_required
def delasset(request):
    status = None
    content = None
    filename = '/etc/ansible/hosts_cmdb'
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        username = Host.objects.filter(ip_pub=ip_pub)
        print '\n--------------------\ndelasset:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'删除资产 ', ip_pub
        for user in username:
            content = '%s ansible_ssh_user=%s' % (ip_pub, user.username)
        print u'step：删除资产信息'
        Asset.objects.filter(ip_pub=ip_pub).delete()
        print u'step：删除主机信息'
        Host.objects.filter(ip_pub=ip_pub).delete()
        if not Asset.objects.filter(ip_pub=ip_pub):
            info = os.system("sed -i '/"+content+"/d' "+filename)
            print u'step：删除对应 inventory 条目'
            if debug=='enabled':
                print u"      [DEBUG] 执行 sed -i '/%s/d' %s 的结果：%s" % (content, filename, info)
            status = "success"
        else:
            status = "failed"
        
        if status=="success":
            print u'删除结果\033[32m成功\033[0m\n'
        else:
            print u'删除结果\033[31m失败\033[0m\n'
        
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
    global num
    num = 1
    filename = sys.path[0]+'/upload/template.xls'
    
    def save(x):
        if not Host.objects.filter(ip_pub=x[0]):
            Host.objects.create(ip_pub=x[0],
                                ip_prv=x[1],
                                username=x[2],
                                pwd_root=x[3],
                                pwd_user=x[4],
                                status=x[5])
        else:
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
            Host.objects.filter(ip_pub=x[0]).update(username=x[2],
                                                        pwd_root=x[3],
                                                        pwd_user=x[4],
                                                        status=x[5],
                                                        update_time=update_time)
    
    if request.method == 'POST':
        while count>0:
            if os.path.isfile(filename):
                data = xlrd.open_workbook(filename)
                table = data.sheets()[0]
                global nrows
                nrows = table.nrows
                print '\n--------------------\ntemplate_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'模版添加主机'
                print u'step：开始批量添加'
                if debug=='enabled':
                    print u'      [DEBUG] 并发执行开始 %s，进程数：%s' % (time.strftime('%H:%M:%S', time.localtime()), max_processes)
                    before = time.time()
                    
                pool = Pool(processes=int(max_processes))
                
                for i in range(1, nrows):
                    pool.apply_async(templateAdd.do, args=(i, filename, debug, host_list, flag), callback=save)
                    # time.sleep(2)
                    flag = 1
                    num+=1
                pool.close()
                pool.join()
                status = 'success'
                if debug=='enabled':
                    print u'      [DEBUG] 并发执行结束', time.strftime('%H:%M:%S', time.localtime())
                    after = time.time()
                    use = after-before
                    print u'      [DEBUG] 耗时 ', use
                print u'------添加完成------\n'
                os.remove(filename)
                break
            else:
                print '\n--------------------\ntemplate_add:'
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'模版添加'
                print u'未发现上传的模版文件，剩余重试次数：%s' % count
                count-=1
                time.sleep(1)
                status = u'未发现上传的模版文件!'

    return HttpResponse(status)

# def template_add(request):
    # flag = 0
    # count = 5
    # num = 001
    # filename = sys.path[0]+'/upload/template.xls'
    
    # if request.method == 'POST':
        # while count>0:
            # if os.path.isfile(filename):
                # data = xlrd.open_workbook(filename)
                # table = data.sheets()[0]
                # nrows = table.nrows
                # print '\n--------------------\ntemplate_add:'
                # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'模版添加主机'
                # print u'step：开始批量添加'
                
                # for i in range(1, nrows):
                    # # data = xlrd.open_workbook(filename)
                    # # table = data.sheets()[0]
                    # # nrows = table.nrows
                    # ip_pub = table.row_values(i)[0]
                    # ip_prv = table.row_values(i)[1]
                    # username = table.row_values(i)[2]   # 认证用户
                    # password = table.row_values(i)[3]   # 认证密码
                    # password_user = table.row_values(i)[4]  # 普通用户密码
                    # print '[%03d] 开始添加 %s' % (num, ip_pub)
                    # pwd_root_encrypt = crypt.do('set', password, debug)
                    # pwd_user_encrypt = crypt.do('set', password_user, debug)
                    
                    # info = hosts_ssh.do_ssh(ip_pub, username, password, debug, host_list, flag)
                    
                    # if info==u'成功':
                        # print '添加结果：\033[32m%s\033[0m' % (info)
                    # else:
                        # print '添加结果：\033[31m%s\033[0m' % (info)
                    
                    # if not Host.objects.filter(ip_pub=ip_pub):
                        # Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username,
                                            # pwd_root=pwd_root_encrypt, pwd_user=pwd_user_encrypt, status=info)
                    # else:
                        # local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        # update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
                        # Host.objects.filter(ip_pub=ip_pub).update(username=username,
                                                                    # pwd_root=pwd_root_encrypt,
                                                                    # pwd_user=pwd_user_encrypt,
                                                                    # status=info,
                                                                    # update_time=update_time)
                    # flag = 1
                    # num+=1
                # status = 'success'
                # print u'------添加完成------\n'
                # os.remove(filename)
                # break
            # else:
                # print '\n--------------------\ntemplate_add:'
                # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'模版添加'
                # print u'未发现上传的模版文件，剩余重试次数：%s' % count
                # count-=1
                # time.sleep(1)
                # status = u'未发现上传的模版文件!'

    # return HttpResponse(status)
    
    
@login_required
def template_add_percentage(request):
    percent = {}
    percent['done'] = num
    percent['all_host'] = nrows
    
    # print percent
    
    return JsonResponse(percent, safe=False)    

@login_required
def manual_add(request):
    info = ''
    if request.method == 'POST':
        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
        print '\n--------------------\nmanual_add:'
        print local_time, u'手动添加'
        ip_pub = request.POST['ip_pub']
        ip_prv = request.POST['ip_prv']
        username = request.POST['authuser']
        password = request.POST['passw0rd']
        password_user = request.POST['passw0rd1']
        print u'step：手动添加 %s' % ip_pub
        pwd_root_encrypt = crypt.do('set', password, debug)
        pwd_user_encrypt = crypt.do('set', password_user, debug)
        
        if Host.objects.filter(ip_pub=ip_pub):
            info = u'该IP已存在'
            Host.objects.filter(ip_pub=ip_pub).update(update_time=update_time) 
            print '添加结果:\033[31m%s\033[0m\n' % (info)
            return render(request, 'host.html', {'status_warning': info})
        else:
            info = hosts_ssh.do_ssh(ip_pub, username, password, debug, host_list, flag=1)
            if info == '成功':
                Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username,
                                    pwd_root=pwd_root_encrypt, pwd_user=pwd_user_encrypt, status=info)
                print '添加结果:\033[32m%s\033[0m\n' %(info)
                return render(request, 'host.html', {'status_success': info})
            else:
                #Host.objects.create(ip_pub=ip_pub, ip_prv=ip_prv, username=username, status=info)
                print '添加结果:\033[31m%s\033[0m\n' %(info)
                return render(request, 'host.html', {'status_warning': info})
        
    else:
        return HttpResponseRedirect('/host/')

@login_required
def delhost(request):
    status = None
    filename = host_list
    if request.method == 'POST':
        ip_pub = request.POST['ip_pub']
        username = request.POST['username']
        content = '%s ansible_ssh_user=%s' % (ip_pub, username)
        
        print '\n--------------------\ndelhost:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'删除主机'
        print u'step：删除%s' %(ip_pub)
        
        Host.objects.filter(ip_pub=ip_pub).delete()
        Asset.objects.filter(ip_pub=ip_pub).delete()
        if not Host.objects.filter(ip_pub=ip_pub):
            print u'step：从 inventory 中删除 %s' %(content)
            info = os.system("sed -i '/"+content+"/d' "+filename)
            if debug=='enabled':
                print '      [DEBUG] sed -i "/%s/d" %s 命令返回值：%s' % (content, filename, info)
            if info==0:
                status = "success"
            else:
                status = "failed"
        else:
            status = "failed"
        if status=='success':
            print u'删除结果：\033[32m%s\033[0m\n' %(status)
        else:
            print u'删除结果：\033[31m%s\033[0m\n' %(status)

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
        print '\n--------------------\ncheck_host:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'检测主机状态'
        print u'step：检测%s' % ip_pub
        runner = ansible.runner.Runner(
            module_name='ping', pattern=ip_pub, host_list=host_list
        )
        data = runner.run()
        if debug=='enabled':
            print u'      [DEBUG] ', data

        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')

        for (host, result) in data['contacted'].items():
            if not 'failed' in result:
                status = 'success'
            else:
                status = 'failed'

        for (host, result) in data['dark'].items():
            status = 'failed: '+result['msg']
            
        if len(data['contacted'].items())==0 and len(data['dark'].items())==0:
            status = u'failed: '+u'检查 inventory 中是否包含 %s' % ip_pub
        if status=='success':
            print u'检测结果：\033[32m%s\033[0m\n' % (u'成功')
        else:
            print u'检测结果：\033[31m失败，%s\033[0m\n' % (status)

    return HttpResponse(status)

# 更改资产密码
@login_required
def UpdatePwd(request):
#    1.add sudo permission to normal user eg. usermode wheel user01
#    2.run cmd 'sudo passwd user01' to change password of user01
    ip = request.POST.get('ip', '')
    username = request.POST.get('username', '')
    print password_length
    pwd_generate = "".join(random.sample('1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()', int(password_length)))
    print u'\n--------------------\nupdate_pwd:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'更新 %s@%s 的密码:' % (username, ip)
    print u'step：生成 %s %s 用户的新密码' % (ip, username)
    if debug=='enabled':
        print u'      [DEBUG] %s %s 用户的新密码：%s' % (ip, username, pwd_generate)
    pwd_update = update_pwd.do(username, ip, transfer.do(pwd_generate), debug)
    # if pwd_update=='success':
        
    if pwd_update == 'success':
        print u'      结果：\033[32m成功\033[0m'
        print u'step：对密码进行加密存储'
        pwd_crypt = crypt.do('set', pwd_generate, debug)
        if debug=='enabled':
            print u'      [DEBUG] 加密前密码：%s' % (pwd_generate)
            print u'              加密后密码：%s' % (pwd_crypt)
        if pwd_crypt=='error':
            status = 'failed'
            print u'      结果：\033[31m存储失败!\033[0m'
            print u'更新结果：\033[31m失败\033[0m\n'
        else:
            status = 'success'
            host_pwd = Host.objects.get(ip_pub=ip)
            if username=='root':
                host_pwd.pwd_root = pwd_crypt
            else:
                host_pwd.pwd_user = pwd_crypt
            host_pwd.save()
            print u'更新结果：\033[32m成功\033[0m\n'
    else:
        status = 'failed'
        print u'更新结果：\033[31m失败\033[0m\n'

    return HttpResponse(status)



# 导出host的ip、密码
@login_required
def export_host(request):
    global export_host_filename
    status = []
    export_host_filename = sys.path[0]+'/media/'+time.strftime('host-%Y-%m-%d-%H-%M', time.localtime())+'.xls'
    headers = (u'公网IP', u'内网IP', u'root密码', u'wwwuser密码')  # 0,1,3,4
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
                if j==2:
                    print u'step：对 root 密码进行解密'
                    content = crypt.do('get', each[j], debug)
                    if debug=='enabled':
                        print u'      [DEBUG] root 密码解密结果:', content.replace('\n', '')
                elif j==3:
                    print u'step：对普通用户密码进行解密'
                    content = crypt.do('get', each[j], debug)
                    if debug=='enabled':
                        print u'      [DEBUG] 普通用户密码解密结果:', content.replace('\n', '')
                # print 'col', j
                # print 'each[k]', each[j]
                worksheet.write(row, j, content.replace('\n', ''))
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

    print u'导出结果：%s\n' % status
    print u'-----导出完成------\n'
    
    return JsonResponse(status, safe=False)

@login_required
def export_asset(request):
    global export_asset_filename
    status = []
    export_asset_filename = sys.path[0]+'/media/'+time.strftime('asset-%Y-%m-%d-%H-%M', time.localtime())+'.xls'
    headers = (u'IP地址', u'主机名', u'操作系统', u'CPU型号', u'CPU', u'内存', u'硬盘', u'最后更新时间')
    print u'\n--------------------\nexport_asset:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'导出 asset 列表'
    
    try:
        dataset = AssetResource().export() 
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
                # print 'col', j
                # print 'each[k]', each[j]
                worksheet.write(row, j, content.replace('\n', ''))
            print u'step：写入第%s条信息\n' % row
            row += 1
            
        workbook.save(export_asset_filename)
        if os.path.isfile(export_asset_filename):
            status.append('success')
            status.append(export_asset_filename)
        else:
            status.append('failed')
    except Exception as e:
        status.append('failed')
        status.append(e)

    print u'导出结果：%s\n' % status
    print u'-----导出完成------\n'
    
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

@login_required
def download_asset(request):
    print u'\n--------------------\ndownload_asset:' 
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), u'下载 asset 列表'
    print u'step：检查文件是否存在'
    if os.path.isfile(export_asset_filename):
        print u'step：文件存在，开始解析'
        f = open(export_asset_filename)
        data = f.read()
        f.close()
        response = HttpResponse(data) 
        response['Content-Disposition'] = 'attachment; filename=%s' % export_asset_filename.split('/')[-1]
        print u'step：解析完成，删除文件'
        os.remove(export_asset_filename)
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
