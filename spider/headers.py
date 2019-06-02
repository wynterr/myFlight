# -*- coding: utf-8 -*-
import re
import json
import random
from fake_useragent import UserAgent


class Headers(object):
    """专门为spider提供headers的类"""
    def __init__(self):
        self.ua = UserAgent().random
        self.ip1 = '%s.%s.%s.%s'%(random.randint(0, 255),random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))
        self.ip2 = '%s.%s.%s.%s'%(random.randint(200, 255),random.randint(200, 255),random.randint(200, 255),random.randint(200, 255))
        self.ip3 = "%s,%s"%(self.ip1,self.ip2)
        # 获取基本信息和详细信息时的headers，
        self.headers1_default = {
            "X-Forwarded-For":self.ip1,
            'Host': 'www.variflight.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'User-Agent': self.ua,
            'DNT': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        }

        # 获取舒适度信息时的headers
        self.headers2_default = self.headers1_default.copy()
        self.headers2_default.update(Host='happiness.variflight.com')

        # 获取图片时的headers
        self.headers4_default = {
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'www.variflight.com',
            'User-Agent': self.ua
        }

        self.headers3_default = {
            'Host': 'www.variflight.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        }

    @staticmethod
    def __process_headers(s):
        def sub_fun_for_key(x):
            return '\n"%s":' % x

        def sub_fun_for_value(x):
            return ':"%s",\n' % x.strip()
        tem1 = re.sub(r"\n *?([\w-]+?):", lambda x: sub_fun_for_key(x.group(1)), s)
        # print("替换完键：\n",tem1.__repr__())
        tem2 = re.sub(r":(.*?)\n", lambda x: sub_fun_for_value((x.group(1))), tem1)
        # print("替换完值：\n",tem2)
        return json.loads("{%s}" % tem2.strip()[:-1])

    def get_headers(self, get_type: int):
        if get_type == 1:
            headers = self.headers1_default
        elif get_type == 2:
            headers = self.headers2_default
        else:
            headers = self.headers3_default
        return headers
