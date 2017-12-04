#!/usr/bin/env python
# -*- coding: utf8 -*-

def create_file(request, ip, username, flag, info):
    host_file = '/etc/ansible/hosts_cmdb'
    item = '%s ansible_ssh_user=%s\n' % (ip, username)
    print item
    f = file(host_file, 'a+')

    if flag == 0 and info == '成功':
        f.truncate()    #清空文件
        f.writelines(item)
        f.close()
    elif flag == 0 and info != '成功':
	f.truncate()    #清空文件
	f.close()
    elif flag ==1 and info == '成功':
        f.writelines(item)
        f.close()

    print u'%s 添加到 %s' % (ip, host_file)
    print '-------------------'

if __name__ == '__main__':
    print 'Only Run By import'
