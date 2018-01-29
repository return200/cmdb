#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import sys
import subprocess
import transfer

def do(action, pwd, debug):
    #if action==None:
    #    return u'action 缺少参数:(set, get)'
    #else:
    pwd = transfer.do(pwd)
    try:
        script = sys.path[0]+'/other/pwd'
        #print script
        cmd = ' '.join([script, action, pwd])
        # print 'cmd', cmd
        run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, error) = run.communicate()
        if debug=='enabled':
            print u'      [DEBUG] %s 密码，output：%s' % (action, output.replace('\n', ''))
            print u'      [DEBUG] %s 密码，error：%s' % (action, error.replace('\n', ''))
        # print output, error
        if error == '':
            return output.replace('\n', '')
    except Exception as e:
        print '\033[31m[ERROR]\033[0m:', e
        return 'error'

if __name__ == '__main__':
    print 'Only Run By Import'
