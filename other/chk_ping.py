#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import sys
import subprocess
import time
import datetime
import ansible

# def do(ip):
    # status = None
    # print u'step：检查是 %s 否已经认证' % ip
    # runner = ansible.runner.Runner(
        # module_name='ping', pattern=ip
    # )
    # data = runner.run()

    # print data
    # local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # update_time = datetime.datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')

    # for (host, result) in data['contacted'].items():
        # if not 'failed' in result:
            # status = 'success'
        # else:
            # status = 'failed'

    # for (host, result) in data['dark'].items():
        # status = 'failed: '+result['msg']

        
        
    # if len(data['contacted'].items())==0 and len(data['dark'].items())==0
    # # print '\n--------------------\ncheck_ping:'
    # # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # print u'\t结果：%s' % (status)
    
    # if status=='success':
        # return 'unneed'
    # else:
        # return 'need'


def do(ip, username, debug):
    script = sys.path[0]+'/other/chk_ping.sh'
    cmd = ' '.join([script, username, ip])

    if os.path.isfile(script):
        print u'step: 检查 %s@%s 是否已经认证' % (username, ip)
        run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = run.communicate()
        #print '\n--------------------\ndelasset:\n'
        # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if debug=='enabled':
            print '      [DEBUG] chk_ping.sh: output: %s' % (output)
            print '      [DEBUG] chk_ping.sh: error: %s' % (err)
        if 'elcome' in output:
            print '      结果：已认证'
            return 'unneed'
        elif 'ogin' in output:
            print '      结果：已认证'
            return 'unneed'
        else:
            print '      结果：待认证'
            return 'need'
    else:
        print '      结果：chk_ping.sh Not Found'
        return 'chk_ping.sh Not Found'

if __name__ == '__main__':
    print 'Only Run By Import'
