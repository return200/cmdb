#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import sys
import subprocess

def do(action, pwd):
    #if action==None:
    #    return u'action 缺少参数:(set, get)'
    #else:
    try:
        script = sys.path[0]+'/other/pwd'
        #print script
        cmd = ' '.join([script, action, pwd])
        # print 'cmd', cmd
        run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, error) = run.communicate()
        # print output, error
        if error == '':
            return output
    except Exception as e:
        return 'error'

if __name__ == '__main__':
    print 'Only Run By Import'
