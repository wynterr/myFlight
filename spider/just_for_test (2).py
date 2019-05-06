# -*- coding: utf-8 -*-
# @Author: 毅梅傲雪
# @Date:   2019-04-22 19:09:39
# @Last Modified by:   毅梅傲雪
# @Last Modified time: 2019-04-22 19:18:35
import requests
import json
a = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 
'Accept-Encoding': 'gzip, deflate', 
'Accept': '*/*', 
'Connection': 'keep-alive', 
'Host': 'www.variflight.com', 
'DNT': '1', 
'X-Requested-With': 'XMLHttpRequest', 
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7', 
'Refer': 'http://www.variflight.com/flight/fnum/CA911.html?AE71649A58c77&fdate=20190422', 
'Cookie': 'PHPSESSID=qpd8g8g11g3v22bvspqmj9rnl6;'}
p = requests.get("http://www.variflight.com/flight/List/checkAuthCode?AE71649A58c77&authCode=%s"%"wmes",headers=a)
print(p.request.headers)
print(json.loads(p.text,encoding="utf-8"))
