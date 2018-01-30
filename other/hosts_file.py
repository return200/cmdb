#!/usr/bin/env python
# -*- coding: utf8 -*-

import time

def create_file(ip, username, flag, host_list, info):
    # flag=1 手动添加，以及非首次添加
    # flag=0 批量添加，以及首次添加
    
    host_file = host_list
    item = '%s ansible_ssh_user=%s' % (ip, username)
    f = file(host_file, 'a+')

    if flag == 0 and info == '成功':
        print u'step：开始写入 hosts 文件'
        print u'      首次写入，清空 hosts 文件'
        f.truncate()
        print u'      写入 %s 到 %s' % (item, host_file)
        f.writelines(item+'\n')
        f.close()
    elif flag == 0 and info != '成功':
        print u'step：开始写入 hosts 文件'
        print u'      首次添加，清空 hosts 文件'
        f.truncate()
        f.close()
    elif flag ==1 and info == '成功':
        print u'step：开始写入 hosts 文件'
        print u'      写入 %s 到 %s' % (item, host_file)
        f.writelines(item+'\n')
        f.close()

if __name__ == '__main__':
    print 'Only Run By import'
