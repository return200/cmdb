#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import subprocess
import time
import chk_ping

def do(username, ip, pwd):
    try: 
        res = chk_ping.chk(ip, username, pwd)
        if res=='unneed':
            cmd = "ssh %s@%s -C 'echo %s | passwd --stdin %s'" % (username, ip, pwd, username)
            print u'step：已经认证，开始更新密码'
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