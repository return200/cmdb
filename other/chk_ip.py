#!/usr/bin/env python
#_*_ coding: utf-8 _*_
#
#检测是否是私有IP

import re

def do(request, ip):
    pattern={
        '10': '10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
        '172': '172\.(1[6-9]|2[0-9]|31)\.[0-9]{1,3}\.[0-9]{1,3}',
        '192': '192\.168\.[0-9]{1,3}\.[0-9]{1,3}'
    }
    
    for each in pattern.keys():
        if re.match(pattern[each], ip):
            info = 'matched'
            break
        else:
            info = None
    
    return info
    
if __name__ == '__main__':
    print 'Only Run By Import'
