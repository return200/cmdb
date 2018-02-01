# _*_ coding: utf-8 _*_

import time, datetime

from app01.models import Asset

import ansible.runner

def do(each, host_list, debug):
    # time.sleep(2)
    runner = ansible.runner.Runner(
        module_name='setup', pattern=each, forks='1', host_list=host_list
        )
    data = runner.run()
    print u'      收集 %s' % (each)
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
            if debug=='enabled':
                print u"      [DEBUG] %s 的主机名：%s，操作系统：%s ，CPU：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
            print u'      %s 存入资产信息表' % host
            # if not Asset.objects.filter(ip_pub=host):
                # Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=str(mem)+' MB', disk=disk)
            # else:
                # Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=str(mem)+' MB', disk=disk, update_time=update_time)
            return host, hostname, system, cpu, cpu_model, str(mem)+' MB', disk, update_time
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

            # if not Asset.objects.filter(ip_pub=host):
                # Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
            # else:
                # Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
            if debug=='enabled':
                print u"      [DEBUG] %s 的主机名：%s，操作系统：%s，CPU型号：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
            return host, hostname, system, cpu, cpu_model, str(mem)+' MB', disk, update_time
            
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
 
        # if not Asset.objects.filter(ip_pub=host):
            # Asset.objects.create(ip_pub=host, hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk)
        # else:
            # Asset.objects.filter(ip_pub=host).update(hostname=hostname, os=system, cpu=cpu, cpu_model=cpu_model, mem=mem, disk=disk, update_time=update_time)
        if debug=='enabled':
            print u"      [DEBUG] %s 的主机名：%s，操作系统：%s，CPU型号：%s，%s核%s线程x%s，内存：%s MB，磁盘：%s" %(host, hostname, system, cpu_model, cpu_core, cpu_thread, cpu_count, mem, disk)
        return host, hostname, system, cpu, cpu_model, str(mem)+' MB', disk, update_time
        
    # insert_time = Asset.objects.order_by('-update_time')[:1]

    # if insert_time:
        # for update_time in insert_time:
            # update_time = update_time.update_time 
# #            print update_time
    # else:
        # update_time = u'未更新'
        
    # return update_time