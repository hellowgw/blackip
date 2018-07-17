#!/usr/local/venv/py36/bin/python
# -*- coding: UTF-8 -*-

from pyinotify import WatchManager, Notifier, ProcessEvent, IN_MODIFY, IN_MOVE_SELF
import subprocess
import redis
import IPy
import sys


class LogEvent(ProcessEvent):
    def is_ip(self, ipaddr):
        '''
        判断取出的值是否为标准的ip地址
        :param ipaddr:
        :return: True or False
        '''
        try:
            IPy.IP(ipaddr).version()
            return True
        except ValueError:
            return False

    def push_redis(self, ip):
        r = redis.Redis(host='127.0.0.1', port=6379)
        if not r.exists(ip):
            # 定义频道并发送消息
            r.publish('blackip', ip)
            r.setex(ip, 'ok', 3)

    def process_IN_MODIFY(self, event):
        ret = subprocess.Popen(['tail', '-1', event.path], stdout=subprocess.PIPE).stdout
        # ret。read（）的返回值是个bytes类型的数据，必须通过decode()处理成str，否则split()会报错
        line = ret.read().decode()
        try:
            info_list = line.strip().split(' ')
            ip = info_list[13].split(',')[0]
            if info_list[2] == '[error]' and self.is_ip(ip):
                self.push_redis(ip)
        except IndexError:
            pass

    def process_IN_MOVE_SELF(self, event):
        sys.exit(0)


logfile = '/data/logs/nginx/error.log'
mask = IN_MODIFY | IN_MOVE_SELF
wm = WatchManager()
wm.add_watch(logfile, mask)

notifier = Notifier(wm, LogEvent())
notifier.loop()

