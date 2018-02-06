# _*_ coding: utf-8 _*_

# 清除 inventory 文件中重复的条目

import subprocess

def do(filename, debug):
    old_filename = filename
    new_filename = filename+'.new'
    
    if debug=='enabled':
        print u'      [DEBUG] 旧文件：%s，新文件：%s' % (old_filename, new_filename)
    
    cmd = 'cat %s |sort |uniq > %s; \mv %s %s' % (old_filename, new_filename, new_filename, old_filename)
    
    if debug=='enabled':
        print u'      [DEBUG] 清理 inventory 重复条目的命令：', cmd
    
    info = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, error) = run.communicate()
    if debug=='enabled':
        print u'      [DEBUG] 命令执行结果：output：', output
        print u'      [DEBUG] 命令执行结果：error：', error
    
    return output, error
    