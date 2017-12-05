#!/usr/bin/env python
# -*- coding: utf8 -*-

import time

def create_file(request, ip, username, flag, info):
    host_file = '/etc/ansible/hosts_cmdb'
    item = '%s ansible_ssh_user=%s\n' % (ip, username)
    f = file(host_file, 'a+')

    if flag == 0 and info == '成功':
        f.truncate()
        f.writelines(item)
        f.close()
    elif flag == 0 and info != '成功':
	f.truncate()
	f.close()
    elif flag ==1 and info == '成功':
        f.writelines(item)
        f.close()

    print '\n--------------------\ncreate_file:'
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print '添加 %s 到 %s' % (item, host_file)

if __name__ == '__main__':
    print 'Only Run By import'
