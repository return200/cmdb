#!/usr/bin/env python
# -*- coding: utf8 -*-

import os,sys
import subprocess

from other import hosts_file, chk_ping

#执行ssh
def do_ssh(request, ip, username, password, flag):
    info = ''
    script = sys.path[0]+'/other/auto_ssh.sh'
    if os.path.isfile(script):
        chk_info = chk_ping.chk(request, ip, username, password)
        print chk_info
        if chk_info == 'need':
            cmd=' '.join([script, username, ip, password])
            #print 'do_ssh cmd:%s' % (cmd)
            run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = run.communicate()
            print 'output: %s ,err:%s' % (output,err)
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
