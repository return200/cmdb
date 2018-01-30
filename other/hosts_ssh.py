#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import os,sys
import subprocess

from other import hosts_file, chk_ping, transfer

#执行ssh
def do_ssh(ip, username, password, debug, host_list, flag):
    info = ''
    script = sys.path[0]+'/other/auto_ssh.sh'
    if os.path.isfile(script):
        # chk_info = chk_ping.chk(ip, username, password)
        chk_info = chk_ping.do(ip, username, debug)
        # print '\n--------------------\nchk_ping:'
        # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # print '检测%s，认证用户：%s，结果：%s' % (ip, username, chk_info)
        if chk_info == 'need':
            password = transfer.do(password)
            cmd=' '.join([script, username, ip, password])
            print u'step：开始认证'
            if debug=='enabled':
                print u'      [DEBUG] do_ssh cmd:%s' % (cmd)
            run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = run.communicate()
            if debug=='enabled':
                print u'      [DEBUG] output：', output
                print u'      [DEBUG] error：', err
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

            # print u'      结果：', info
            
        elif chk_info == 'unneed':
            info = '成功'
        # else:
            # info = 'chk_ping.sh Not Found'
            
            # print u'      结果：', info
    else:
        info = 'auto_ssh.sh Not Found'
        
    # print u'      结果：', info

    hosts_file.create_file(ip, username, flag, host_list, info)
    
    return info

if __name__ == '__main__':
    print 'Only Run By import'
