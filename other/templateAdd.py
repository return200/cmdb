# _*_ coding: utf-8 _*_

import xlrd

from other import crypt, hosts_ssh

def do(i, filename, debug, host_list, flag):
    if debug=='enabled':
        print u'      [DEBUG] 添加第 %s 个主机，上传文件名：%s，debug：%s，inventory文件：%s，flag：%s' % (i, filename, debug, host_list, flag)
    # return num, debug, host_list, flag
    data = xlrd.open_workbook(filename)
    table = data.sheets()[0]
    ip_pub = table.row_values(i)[0]
    ip_prv = table.row_values(i)[1]
    username = table.row_values(i)[2]   # 认证用户
    password = table.row_values(i)[3]   # 认证密码
    password_user = table.row_values(i)[4]  # 普通用户密码
    print '      开始添加 %s' % (ip_pub)
    pwd_root_encrypt = crypt.do('set', password, debug)
    pwd_user_encrypt = crypt.do('set', password_user, debug)
    
    info = hosts_ssh.do_ssh(ip_pub, username, password, debug, host_list, flag)
    
    if info==u'成功':
        status = u'添加成功'
        print '添加结果：\033[32m%s\033[0m' % (info)
    else:
        status = info
        print '添加结果：\033[31m%s\033[0m' % (info)
        
    return ip_pub, ip_prv, username, pwd_root_encrypt, pwd_user_encrypt, status
    