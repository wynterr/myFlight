from spider.spider import Spider
from spider.myPrint import myPrint
spd = Spider().get_base_info("PEK",'SHA', '20190603')
myPrint(spd)