#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import sys
import subprocess

def chk(ip, username, password):
    script = sys.path[0]+'/other/chk_ping.sh'
    cmd = ' '.join([script, username, ip, password])

    if os.path.isfile(script):
        print u'step: 检查是否已经认证'
        run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = run.communicate()
        #print '\n--------------------\ndelasset:\n'
        #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #print 'chk_ping.sh: output: %s ,err:%s' % (output,err)
        if 'elcome' in output:
            return 'unneed'
        elif 'ogin' in output:
            return 'unneed'
        else:
            return 'need'
    else:
        return 'chk_ping.sh Not Found'

if __name__ == '__main__':
    print 'Only Run By Import'
