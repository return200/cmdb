#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import subprocess
import time
import chk_ping

def do(username, ip, pwd, debug):
    try: 
        res = chk_ping.do(ip, 'root', debug)
        if res=='unneed':
            cmd = "ssh root@%s -C 'echo %s | passwd --stdin %s'" % (ip, pwd, username)
            print u'step：开始更新密码'
            run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, error) = run.communicate()
            # print 'output:', output, 'error:', error
            if u'成功' in output:
                info = 'success'
            elif 'uccess' in output:
                info = 'success'
            else:
                info = 'failed'
        else:
            info = 'failed'
            print u'step：未认证，无法更新密码'
    except Exception as e:
        print e
        info = 'failed'
    
    return info

if __name__ == '__main__':
    print 'Only Run By Import'