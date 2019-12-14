# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2019/12/9 19:30
# @Author  : Fangyang
# @Software: PyCharm

import secrets
import base64
import hashlib

if __name__ == '__main__':
    a = secrets.token_bytes(16)
    b = base64.urlsafe_b64encode(a)
    c = str(b, encoding='utf-8')
    salt = base64.b64encode(c.encode('utf-8'))

    sk = hashlib.pbkdf2_hmac(
        hash_name='sha1',
        password='12345'.encode('utf-8'),
        salt=salt,
        iterations=10000,
        dklen=64
    )
    print(1)


