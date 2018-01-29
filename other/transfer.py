#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# 对密码中的特殊字符进行转义

def do(password):
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
        "$": "\$",
        "\n": "",
    }
    
    for key, value in pattern.items():
        password = password.replace(key, value)

    return password

if __name__ == '__main__':
    print 'Only Run By Import'
