# -*- coding: utf-8 -*-
# @Date    : 2019-03-28 12:00:11
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
import sys
import re
import json
import requests
import pytesseract
from PIL import Image
from lxml import etree
from myPrint import myPrint
class Spider():
    def __init__(self):
        self.base_url = "http://www.variflight.com"
        self.query_by_route_baseurl = "http://www.variflight.com/flight/%s-%s.html?AE71649A58c77&fdate=%s"
        # 按路线查询航班信息的基本url，前两个 %s 是出发地和到达地的机场代码，分别为三个字母，最后一个是日期，格式为八位纯数字
        self.query_by_flightcode_baseurl = "http://www.variflight.com/flight/fnum/%s.html?AE71649A58c77&fdate=%s"
        # 按航班号查询航班信息的基本url，前一个%s是航班号，后一个是日期
        self.detailed_info_baseurl = "http://www.variflight.com/schedule/%s-%s-%s.html?AE71649A58c77=&fdate=%s"
        # 详细信息的基本url，第一、第二个%s分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        self.comfort_info_baseurl = "http://happiness.variflight.com/info/detail?fnum=%s&dep=%s&arr=%s&date=%s&type=1"
        # 共 5 个参数，由于最后一个是舱位标志，使用时只需要提供前四个参数即可
        # 第一个参数为航班代码，第二个为出发地机场代码，第三个为目的地机场代码，第四个为日期，格式示例为：2019-03-29
        self.headers = self.__process_headers('''
        Host: www.variflight.com
        Connection: keep-alive
        Upgrade-Insecure-Requests: 1
        Cache-Control: max-age=0
        DNT: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
        Cookie:_ga=GA1.2.827246213.1552463842; orderRole=1; _gid=GA1.2.928809635.1553787287; __utma=66649513.827246213.1552463842.1553787338.1553787338.1; __utmz=66649513.1553787338.1.1.utmcsr=co-biz.variflight.com|utmccn=(referral)|utmcmd=referral|utmcct=/Product/default.asp; Clients_IPAddress=undefined%2C%u5317%u4EAC%u5E02; fnumHistory=%5B%7B%22fnum%22%3A%22CZ3147%22%7D%2C%7B%22fnum%22%3A%22CZ300%22%7D%2C%7B%22fnum%22%3A%22HO1252%22%7D%2C%7B%22fnum%22%3A%223U2018%22%7D%2C%7B%22fnum%22%3A%223U2012%22%7D%2C%7B%22fnum%22%3A%223U2013%22%7D%2C%7B%22fnum%22%3A%22AQ1052%22%7D%2C%7B%22fnum%22%3A%223U5137%22%7D%5D; midsalt=5c9e1dbc3a23f;

        ''')
        # Cookie:_ga=GA1.2.322889095.1552466396; citiesHistory=%5B%7B%22depCode%22%3A%22PEK%22%2C%22arrCode%22%3A%22CKG%22%2C%22depCity%22%3A%22%5Cu5317%5Cu4eac%5Cu9996%5Cu90fd%22%2C%22arrCity%22%3A%22%5Cu91cd%5Cu5e86%5Cu6c5f%5Cu5317%22%7D%5D; Hm_lvt_d1f759cd744b691c20c25f874cadc061=1553684104,1553684286,1553873400; fnumHistory=%5B%7B%22fnum%22%3A%22CZ3147%22%7D%5D; PHPSESSID=bgmol4m9310v3vq21qpnjj0973; salt=5c9e39f755c99; Hm_lpvt_d1f759cd744b691c20c25f874cadc061=1553873400        

        self.comfort_info_headers = self.__process_headers(
            '''
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            Accept-Encoding: gzip, deflate
            Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
            Cache-Control: max-age=0
            Connection: keep-alive
            DNT: 1
            Cookie: _ga=GA1.2.827246213.1552463842; _gid=GA1.2.928809635.1553787287; __utma=66649513.827246213.1552463842.1553787338.1553787338.1; __utmz=66649513.1553787338.1.1.utmcsr=co-biz.variflight.com|utmccn=(referral)|utmcmd=referral|utmcct=/Product/default.asp; HAPPINESS_USER_LAST_SEARCH_FLIGHT=3U2018; Hm_lvt_d1f759cd744b691c20c25f874cadc061=1553953959; Hm_lpvt_d1f759cd744b691c20c25f874cadc061=1553953959; Hm_lvt_4b7d84e5b348685ca608145cd1e1f6f0=1553688147,1553859709,1553862333,1553954758; _gat_gtag_UA_131096296_1=1; HAPPINESS_USER_LAST_SEARCH=%7B%22dep%22%3A%22PEK%22%2C%22arr%22%3A%22SHA%22%7D; Hm_lpvt_4b7d84e5b348685ca608145cd1e1f6f0=1553954800
            Host: happiness.variflight.com
            Referer: http://happiness.variflight.com/search/airline?date=2019-03-30&dep=PEK&arr=SHA&type=1
            Upgrade-Insecure-Requests: 1
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
            ''')
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
    def __print_html(self,html):
        # 由于网页中经常含有某些特殊字符，无法用print显示，所以定义这个函数
        if isinstance(html,requests.models.Response):
            html = html.text
        for item in html:
            try:
                print(item,end = '')
            except UnicodeEncodeError:
                print('\n----------------------- error here! -----------------------------')
        print()
    def __strip_blinks(self,s):
        # 去除列表 s 中元素两端的空白字符
        if isinstance(s,list):
            return list(map(lambda x:x.strip(),s))
        elif isinstance(s,str):
            return s.strip()
    def _get_img(self,imgurl,session,img_path,rec_it = True,headers=None):
        # 获取图片，顺便识别图片内容
        # 若识别，则返回图片内容的字符串，若不识别，则返回图片路径
        try:
            img = session.get(imgurl)
        except Exception as e:
            print("获取图片失败！")
            print(e)
            return 
        if sys.getsizeof(img.content) > 500:
            if '.png' not in img_path:
                img_path += '.png'
            with open(img_path,'wb') as f:
                f.write(img.content)
                # print("%s保存成功！"%img_path)
            if rec_it:
                result = pytesseract.image_to_string(Image.open(img_path))
                # print("识别到内容：",result)
                return result
            else:
                return img_path
        else:
            print("获取图片内容有误！")
            print("图片标题为",img_path)
            print("图片 url 为：%s"%imgurl)
            print("获取到的内容为：%s"%img.text)
    def get_base_info(self,*args):
        '''
        获取航班的基本信息
        开发时可以直接按 url 查询，直接传入 url 即可
        若按航班号查询，args的格式应为(flightcode, query_date)
        若按路线查询，args的格式应为(depart_air_code, arrive_air_code, query_date)
        '''
        session = requests.session()
        if len(args) == 1:
            # 给定 url 查询，主要是调试时用
            query_url = args[0]
        elif len(args) == 2:
            # 按航班号查询
            query_url = self.query_by_flightcode_baseurl%(args[0],args[1])
        elif len(args) == 3:
            # 按路线查询
            query_url = self.query_by_route_baseurl%(args[0],args[1],args[2])
        else:
            raise ValueError("输入的参数有误！")
        flight_infos = []
        html = session.get(query_url,headers = self.headers)
        # myPrint(self.headers)
        # self.__print_html(html)
        query_result = re.search(r'<div class="fly_list">(.+?)</div>',html.text,re.S).group(0)
        query_result = re.findall(r'<li style="position: relative;">.+?</li>',html.text,re.S)
        # 各个航班信息的html代码块文本组成的列表，每个元素是一个航班的代码块
        for flight_info in query_result:
            html = etree.HTML(flight_info)
            imgurls = html.xpath('//div[@class="li_com"]/span/img/@src')
            # print(len(imgurls),imgurls)
            # 完整信息是四张图，至少两张图，顺序依次为 航空公司图标、准点率、实际起飞时间、实际降落时间
            corp_name,flight_code = html.xpath('//div[@class="li_com"]/span/b/a/@title')
            # print(corp_name,flight_code)
            # 航空公司名称和航班号
            time_and_place_info= self.__strip_blinks(html.xpath('//div[@class="li_com"]/span[@class="w150"]/text()'))
            # print(len(time_and_place_info),time_and_place_info)
            # 共六项，只有四项有用，依次为计划起飞时间、计划起飞地点、计划到达时间、计划到达地点
            flight_status = html.xpath('//div[@class="li_com"]/span[contains(@class,"_cor")]/text()')[0]
            # print(flight_status) 
            # 只有一项，即为航班状态，目前已遇到的状态有起飞、到达、取消、催促登机、登机结束、正在登机、延误预警
            # flight_detailed_info_url = self.base_url + html.xpath('//li[@style="position: relative;"]/a[@class="searchlist_innerli"]/@href')
            # 这一项暂时没用
            shared_fligt = html.xpath('//li[@style="position: relative;"]/a[@class="list_share"]/@title')
            shared_fligt = shared_fligt[0] if shared_fligt else None
            # print(flight_detailed_info_url,shared_fligt)
            # 有些航班是共享的，不懂的具体百度吧

            corp_imgurl=imgurls[0]
            corp_imgpath = "./img_file/%s商标.png"%corp_name
            dep_time_act_imgurl = self.base_url + imgurls[1] if len(imgurls)>=3 else None
            arri_time_act_imgurl = self.base_url + imgurls[2] if len(imgurls)==4 else None
            ontime_rate_imgurl=self.base_url + imgurls[-1]
            #----- 下面开始获取图片 ------#
            # 由于获取图片的真地址后，需要设置相应的 Cookie 才能拿到图片，所以需要传递 session
            self._get_img(corp_imgurl,session,corp_imgpath,rec_it=False)
            ontime_rate = self._get_img(ontime_rate_imgurl,session,"./img_file/%s_onTimeRate.png"%flight_code)
            # 实际起飞时间
            if dep_time_act_imgurl:
                dep_time_act = self._get_img(dep_time_act_imgurl,session,"./img_file/dep_act_%s_date.png"%flight_code)
            else:
                dep_time_act = None
            if arri_time_act_imgurl:
                arri_time_act = self._get_img(arri_time_act_imgurl,session,"./img_file/arri_act_%s_date.png"%flight_code)
            else:
                arri_time_act = None
            flight_infos.append(dict(
                corp_imgpath=corp_imgpath,
                corp_name=corp_name,
                flight_code=flight_code,
                shared_fligt=shared_fligt,
                dep_time_plan=time_and_place_info[0],
                dep_time_act=dep_time_act,
                dep_airp=time_and_place_info[1],
                arri_time_plan=time_and_place_info[2],
                arri_time_act=arri_time_act,
                arri_airp=time_and_place_info[3],
                ontime_rate=ontime_rate,
                flight_status=flight_status
                ))
        return flight_infos
    def get_detailed_info(self,*args):
        # 查询详细信息，
        # 若为一个参数，则该参数是给定的 url
        # 若按航班号查询，共需要四个参数，第一、第二个分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        query_url = self.detailed_info_baseurl%(args[0],args[1],args[2],args[3]) if len(args)>1 else args[0]
        session = requests.session()
        html = session.get(query_url,headers = self.headers)
        print("获取到网页")
        # self.__print_html(html)
        html = etree.HTML(html.text)
        corp_name_and_flight_code = html.xpath('//div[@class="tit"]/span/b/text()')[0].strip()
        # print(corp_name_and_flight_code)
        flight_status = html.xpath('//div[@class="tit"]/div[@class="state"]/div/text()')[0]
        # print(flight_status)
        dep_city,arri_city = html.xpath('//div[@class="flyProc"]/div[@id="p_box"]/div[@class="cir_l curr" or @class = "cir_r"]/span/text()')
        # print(dep_city,arri_city)
        flight_distance,flight_dur_time = html.xpath('//div[@class="flyProc"]/div[@id="p_box"]/div[@class="p_ti"]/span/text()')
        # print(flight_distance,flight_dur_time)
        plane_type = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="mileage"]/span/text()')[0]
        # print(plane_type)
        plane_age = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="time"]/span/text()')[0]
        # print(plane_age)
        ave_ontime_rate_imgurl = self.base_url + html.xpath('//div[@class="flyProc"]//li[@class="per"]//img/@src')[0].strip()
        ave_ontime_rate = self._get_img(ave_ontime_rate_imgurl,session,"./img_file/%s_ave_ontime_rate"%corp_name_and_flight_code)
        # print(ave_ontime_rate)
        delay_time_tip = html.xpath('//div[@class="flyProc"]//li[@class="age"]/span/text()')
        delay_time_tip = delay_time_tip[0] if delay_time_tip else None
        # print(delay_time_tip)
        pre_fligt = html.xpath('//div[@class="old_state"]/text()')[0]
        # print(pre_fligt)
        #---------------------------------------------------------------------------------------------#
        involved_airp_total = len(html.xpath('//div[contains(@class,"fly_mian")]'))
        # print('involved_airp_total:',involved_airp_total)
        # 航班涉及到的城市数量，包括起飞地、到达地和经停地（目前只遇到过一个经停地的情况，多个经停地的情况待测试）
        involved_airps = html.xpath('//div[contains(@class,"fly_mian")]/div[contains(@class,"f_title")]/h2/text()')
        involved_airps = list(filter(bool,self.__strip_blinks(involved_airps))) 
        # print(involved_airps)
        # 航班涉及到的机场
        involved_times = html.xpath('//div[contains(@class,"fly_mian")]/div[contains(@class,"f_title")]/span/text()')
        involved_times = self.__strip_blinks(involved_times)
        # print(involved_times)
        # 航班涉及到的地点的时间
        airp_weathers = html.xpath('//div[contains(@class,"fly_mian")]/ul/li[@class="weather"]/p/text()')
        airp_weathers_iconurls = html.xpath('//div[contains(@class,"fly_mian")]/ul/li[@class="weather"]/img/@src')
        airp_weathers_iconurls = list(map(lambda x:self.base_url+x,airp_weathers_iconurls))
        # print(airp_weathers)
        for item in airp_weathers_iconurls:
            self._get_img(item,session,"./img_file/%s"%item[item.rindex("/")+1:],rec_it=False)
        # print(airp_weathers_iconurls)
        #-- 以上两个变量所包含的内容的数量应与 involved_airp_total 相等
        #-- 以下变量所包含的内容的数量应比 involved_airp_total 多出经停地的数量，因为每一个经停地都有到达和出发时间，而出发到达地则只有一个时间
        # 每个机场有至少三项数据要拿（网页右边的三列），但各个机场的数据名不同，内容都是图片或空，所以用first_item,second_item,third_item来描述他们，每个变量对应一列
        data_total = len(html.xpath('//ul[contains(@class,"f_common")]'))
        # 所有机场的同一数据项的数目之和，就是网页右边数据的行数
        # print("data total is",data_total)
        # print(self._get_img(self.base_url+html.xpath('//div[contains(@class,"fly_mian")][1]/ul[1]/li[@class="time"]/p[2]/img/@src')[0].strip(),session,'test'))
        airp_datas = []
        for i in range(involved_airp_total):
            airp_datas.append({involved_airps[i]:[]})
            airp_data_rows = len(html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[contains(@class,"f_common")]'%(i+1)))
            # print("第 %d 行共有 %d 子行数据"%(i+1,airp_data_rows))
            for sub_i in range(airp_data_rows):
                airp_datas[i][involved_airps[i]].append({})
                li_class_list = ['time','inspect','entrance']
                for j in range(3): 
                # 共三列数据
                    item_name = html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[@class="gray_t"]/text()'%(i+1,sub_i+1,li_class_list[j]))[0]
                    # print("第 %d 行第 %d 子行第 %d 列数据项名称："%(i+1,sub_i+1,j+1),item_name)
                    item_data_img_url = html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[2]/img/@src'%(i+1,sub_i+1,li_class_list[j]))
                    # print("第 %d 行第 %d 子行第 %d 列图片的xpath内容："%(i+1,sub_i+1,j+1),'//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[2]/img/@src'%(i+1,sub_i+1,li_class_list[j]))
                    # print(item_data_img_url)
                    if not item_data_img_url:
                        # print("第 %d 行第 %d 子行第 %d 列数据无图片链接"%(i+1,sub_i+1,j+1))
                        item_data =  html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[2]/text()'%(i+1,sub_i+1,li_class_list[j]))
                        item_data = item_data[0].strip()
                    else:
                        item_data_img_url = self.base_url + item_data_img_url[0].strip()
                        item_data = self._get_img(item_data_img_url,session,'./img_file/%s_%d%d%d'%(corp_name_and_flight_code,i+1,sub_i+1,j+1))
                        # print("第 %d 行第 %d 子行第 %d 列图片识别结果："%(i+1,sub_i+1,j+1),item_data)
                    airp_datas[i][involved_airps[i]][sub_i][item_name] = item_data
        # myPrint(airp_datas)
        return dict(
            corp_name_and_flight_code=corp_name_and_flight_code,
            flight_status=flight_status,
            dep_city=dep_city,
            arri_city=arri_city,
            flight_distance = flight_distance,
            flight_dur_time = flight_dur_time,
            plane_type = plane_type,
            plane_age = plane_age,
            ave_ontime_rate=ave_ontime_rate,
            delay_time_tip=delay_time_tip,
            pre_fligt = pre_fligt,
            airp_weathers=airp_weathers,
            airp_datas=airp_datas
            )
    def get_confort_info(self,*args):
        # 获取舒适度信息，网站限定，查询太频繁会拿不到数据
        # 若给定 url，则只需传入一个参数
        # 若按航班号查询，需提供四个参数，第一个参数为航班代码，第二个为出发地机场代码，第三个为目的地机场代码，第四个为日期，格式示例为：2019-03-29
        url = self.comfort_info_baseurl%(args[0],args[1],args[2],args[3]) if len(args)>1 else args[0]
        print(url)
        session = requests.session()
        if len(args) > 1:
            html = session.get('http://happiness.variflight.com/search/airline?date=%s&dep=%s&arr=%s&type=1'%(args[3],args[1],args[2]))
        else:
            date = re.search(r'date=([\d-]+)',args[0]).group(1)
            dep = re.search(r'dep=(.{3})',args[0]).group(1)
            arri = re.search(r'arr=(.{3})',args[0]).group(1)
            html = session.get('http://happiness.variflight.com/search/airline?date=%s&dep=%s&arr=%s&type=1'%(date,dep,arri))
        html = session.get(url,headers = self.comfort_info_headers)
        # self.__print_html(html)
        html = etree.HTML(html.text)
        sub_info1 = self.__strip_blinks(html.xpath('//div[@class="basic"]//h1/span/text()'))
        # print(sub_info1)
        corp_name, flight_code, flight_date, flight_weeknum = sub_info1
        comfort_scores = self.__strip_blinks(html.xpath('//div[@class="basic"]//div[@class="scoreList"]/span/text()',))
        # print(comfort_scores)
        sub_info2 = self.__strip_blinks(html.xpath('//div[@class="mid fl"]//p[@class="rate" or @class="one" or @class="two"]/text()'))
        ave_ontime_rate, flight_distance,flight_dur_time = sub_info2
        # print(sub_info2)
        sub_info3 = self.__strip_blinks(html.xpath('//div[@class="circle lefCircle" or @class="circle rigCircle"]/p/text()'))       
        # print(sub_info3)
        dep_ave_delay_time,arri_ave_delay_time = sub_info3[0:3:2]

        #---经停信息获取，目前可获取一级经停信息---#
        cabin_names = html.xpath('//div[@class="service"]//div[@class="top"]//a/text()')
        # print(cabin_names)
        cabin_infos = dict()
        for i,item in enumerate(cabin_names):
            cabin_infos[item] = {}
            cabin_infos[item]['cabin_marks'] = self.__strip_blinks(html.xpath('//div[@class="basic"]//div[@class="scoreList"]//span[%d]/text()'%(i+1)))[0]
            cabin_infos[item]['cabin_equipments'] = self.__strip_blinks(html.xpath('//div[@class="service"]//div[@class="mid clearfix cur" or @class="mid clearfix"][%d]//div[@class="devList"]/ul[1]/li/@title'%(i+1)))
            # print(cabin_equipments)
            cabin_infos[item]['seat_info'] = self.__strip_blinks(html.xpath('//div[@class="service"]//div[@class="mid clearfix cur" or @class="mid clearfix"][%d]//div[@class="devList"]/ul[2]/li/span/text()'%(i+1)))
            # 包含三项内容，分别为座椅角度、座椅宽度、座椅间距 
            # print(seat_info)
            cabin_infos[item]['evaluate_stars'] = len(html.xpath('//div[@class="service-standard"]/p[%d]/i[@class="iconfont icon-Star blue"]'%(i+1)))
            # print(evaluate_stars1,evaluate_stars2,evaluate_stars3)

        return dict(
            corp_name = corp_name,
            flight_code = flight_code,
            flight_date = flight_date,
            flight_weeknum = flight_weeknum,
            ave_ontime_rate = ave_ontime_rate,
            flight_distance = flight_distance,
            flight_dur_time = flight_dur_time,
            dep_ave_delay_time = dep_ave_delay_time,
            arri_ave_delay_time = arri_ave_delay_time,
            cabin_infos = cabin_infos
            )
if __name__ == '__main__':
    # myPrint(Spider().get_base_info('PEK','PVG','20190331'))
    # myPrint(Spider().get_base_info('3U2018','20190328'))
    # myPrint(Spider().get_base_info("http://www.variflight.com/flight/PEK-CAN.html?AE71649A58c77"))
    # myPrint(Spider().get_detailed_info("http://www.variflight.com/schedule/PEK-CTU-AA7139.html?AE71649A58c77=&fdate=20190330"))
    # myPrint(Spider().get_detailed_info('BHY','PEK','CZ3147','20190331'))
    myPrint(Spider().get_confort_info('http://happiness.variflight.com/info/detail?fnum=CZ9075&dep=PEK&arr=SHA&date=2019-04-02&type=2'))
    # myPrint(Spider().get_confort_info('CZ3147','PEK','SHA','2019-03-30'))
