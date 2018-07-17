#!/usr/local/venv/py36/bin/python
# -*- coding: UTF-8 -*-

import redis
import subprocess
import time
import json
from urllib import request


logfile = 'ip.log'
API = "http://ip.taobao.com/service/getIpInfo.php?ip="


def write_log(ipaddr):
    with open(logfile, 'a') as f:
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(time_str)
        f.write('\n')
        url = API + ipaddr
        # 访问淘宝的API 获取IP属地
        jsondata = json.loads(request.urlopen(url).read())
        if jsondata['code'] == '1':
            ip_info = '{0}，{1} 无信息'.format(Count, IPaddr)
        else:
            ip_info = '{0}, 所属城市：{1}, 运营商：{2}'.format(ipaddr, jsondata['data']['city'], jsondata['data']['isp'])
        f.write(ip_info)
        f.write('\n')
        f.write('######\n\n')


r = redis.Redis(host='127.0.0.1', port=6379)
sub = r.pubsub()
# 定义要监听的频道
sub.subscribe('blackip')
while True:
    # 数据格式是bytes格式的  [b'message', b'blackip', b'123.123.87.153']
    msg = sub.parse_response()
    if msg[0].decode() == 'message':
        write_log(msg[2].decode())
