#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# 对密码中的特殊字符进行转义

def do(request, password):
    pattern = {
        '\\': "\\\\",
        ";": "\;",
        "'": "\\'",
        "<": "\<",
        ">": "\>",
        '"': '\\"',
        "|": "\|",
        "(": "\(",
        ")": "\)",
        "&": "\&",
        "!": "\!",
        "`": "\`",
    }
    
    for each in pattern.keys():
        password = password.replace(each, pattern[each])

    return password

if __name__ == '__main__':
    print 'Only Run By Import'
