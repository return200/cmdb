#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import os,sys
import subprocess

from other import hosts_file, chk_ping, transfer

#执行ssh
def do_ssh(request, ip, username, password, flag):
    info = ''
    script = sys.path[0]+'/other/auto_ssh.sh'
    if os.path.isfile(script):
        chk_info = chk_ping.chk(ip, username, password)
        print '\n--------------------\nchk_ping:'
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '检测%s，认证用户：%s，结果：%s' % (ip, username, chk_info)
        if chk_info == 'need':
            password = transfer.do(password)
            cmd=' '.join([script, username, ip, password])
            #print 'do_ssh cmd:%s' % (cmd)
            run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = run.communicate()
            print 'output', output, 'error', err
            if 'Permission denied' in output:
                info = '用户名或密码错误'
            elif 'Connection refused' in output:
                info = '用户名或密码错误'
            elif 'No route to host' in output:
                info =  '主机不可达'
            elif 'cannot create' in output:
                info = '家目录权限错误'
            elif 'Now try logging into' in output:
                info = '成功'
            elif '/usr/bin/expect' in err:
                info = '未安装 expect 包'
            else:
                info = '未知错误'
        elif chk_info == 'unneed':
            info = '成功'
        else:
            info = 'chk_ping.sh Not Found'
    else:
        info = 'auto_ssh.sh Not Found'

    hosts_file.create_file(request, ip, username, flag, info)
    
    return info

if __name__ == '__main__':
    print 'Only Run By import'
