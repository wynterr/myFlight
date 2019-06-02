# -*- coding: utf-8 -*-
import requests
from lxml import etree
class Chinaatm(object):
    """docstring for Chinaatm"""
    def __init__(self):
        super(Chinaatm, self).__init__()
        self.url = 'http://www.chinaatm.com.cn/Notice.aspx'
    def get_page(self,page_index=1):
        data = {
        '__EVENTTARGET': 'AspNetPager2',
        # '__EVENTARGUMENT': '4',
        # '__VIEWSTATE': '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',
        # '__VIEWSTATEGENERATOR': '970C11B2',
        # '__EVENTVALIDATION': '/wEWAgLF9ZjuBgLbuOStB5ip6YIzlNepk6cI7Y7lGRscyKgN',
        # 'search': '搜索',
        'AspNetPager2_input': str(page_index)
        }
        headers = {
        'Host': 'www.chinaatm.com.cn',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Origin': 'http://www.chinaatm.com.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'http://www.chinaatm.com.cn/Notice.aspx',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7'
        }
        p = requests.post(self.url,headers=headers,data=data)
        return p.text

    @staticmethod
    def __strip_blanks(s):
        # 去除列表 s 中元素两端的空白字符
        if isinstance(s, list):
            return list(map(lambda x: x.strip(), s))
        elif isinstance(s, str):
            return s.strip()

    @staticmethod
    def parse_page(ori_html):
        html = etree.HTML(ori_html)
        notice_time = html.xpath("//td/li/span[@class='li_tit_wz_n'][position()=2]/text()")
        notice_time = list(map(lambda x: x.strip(), notice_time))
        notice = html.xpath("//td/li/span[@class='li_tit_time_n']/text()")
        notice = list(map(lambda x: x.strip(), notice))
        notice_dic = {}
        for item in notice:
            item = item.split("：", 1)
            notice_dic.update({item[0]:item[1]})
        # map(lambda x,y: , )
        print(notice_dic)
        return notice_dic
if __name__ == '__main__':
    c = Chinaatm()
    c.parse_page(c.get_page())
