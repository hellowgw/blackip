#!/usr/local/venv/py36/bin/python
# -*- coding: UTF-8 -*-

import redis
import subprocess

r = redis.Redis(host='127.0.0.1', port=6379)
sub=r.pubsub()
# 定义要监听的频道
sub.subscribe('blackip')
while True:
    # 数据格式是bytes格式的  [b'message', b'blackip', b'123.123.87.153']
    msg = sub.parse_response()
    if msg[0].decode() == 'message':
        subprocess.call(['/sbin/iptables -A BLACK-LIST -s {0} -j DROP'.format(msg[2].decode())], shell=True)
