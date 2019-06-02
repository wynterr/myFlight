# -*- coding: utf-8 -*-
import requests
url = 'http://www.variflight.com/flight/detail/productImg&s=bmNPL09pS3U3UVhFcWlUZkhsd2N6Tis4SkYwPQ==&w=50&h=28&fontSize=13&fontColor=2f3032&background=ffffff?AE71649A58c77='
pic = requests.get(url)
with open ('pic.png','wb') as f:
    f.write(pic.content)
print(pic.status_code)
print(pic.text.__repr__())