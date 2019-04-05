# -*- coding: utf-8 -*-
from fake_useragent import UserAgent
import requests
class Headers(object):
    """专门为spider提供headers的类"""
    def __init__(self):
        self.ua = UserAgent(verify_ssl=False).random
        # 共三个 headers ，第一个是获取基本信息和详细信息时的headers，第二个是获取舒适度信息时的headers，第三个是获取图片时的headers
        self.headers1_default = {
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

        self.headers2_default = self.headers1_default.copy()
        self.headers2_default.update(Host='happiness.variflight.com')

        self.headers3_default = {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.variflight.com',
        'User-Agent':self.ua
        }
        # 'Cookie':'_ga=GA1.2.322889095.1552466396; citiesHistory=%5B%7B%22depCode%22%3A%22PEK%22%2C%22arrCode%22%3A%22CKG%22%2C%22depCity%22%3A%22%5Cu5317%5Cu4eac%5Cu9996%5Cu90fd%22%2C%22arrCity%22%3A%22%5Cu91cd%5Cu5e86%5Cu6c5f%5Cu5317%22%7D%5D; Hm_lvt_d1f759cd744b691c20c25f874cadc061=1553684104,1553684286,1553873400; fnumHistory=%5B%7B%22fnum%22%3A%22CZ3147%22%7D%5D; PHPSESSID=bgmol4m9310v3vq21qpnjj0973; salt=5c9e39f755c99; Hm_lpvt_d1f759cd744b691c20c25f874cadc061=1553873400'
    def __process_headers(self,s):
        def sub_fun_for_key(x):
            return '\n"%s":'%x
        def sub_fun_for_value(x):
            return ':"%s",\n'%x.strip()
        tem1 = re.sub(r"\n *?([\w-]+?):",lambda x:sub_fun_for_key(x.group(1)),s)
        # print("替换完键：\n",tem1.__repr__())
        tem2 =  re.sub(r":(.*?)\n",lambda x:sub_fun_for_value((x.group(1))),tem1)
        # print("替换完值：\n",tem2)
        return json.loads("{%s}"%tem2.strip()[:-1])
    def get_headers(self,type:int,cookie:requests.cookies.RequestsCookieJar=None,ua:dict=None,refer:str=None):
        if type == 1:
            headers = self.headers1_default
        elif type==2:
            headers = self.headers2_default
        else :
            headers = self.headers3_default
        if cookie:
            headers.update(Cookie=cookie)
        if ua:
            headers.update({'User-Agent':ua})
        if refer:
            headers.update(Refer=refer)
        return headers
