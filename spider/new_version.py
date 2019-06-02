# -*- coding: utf-8 -*-
# @Date    : 2019-03-28 12:00:11
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
import requests
import re
import json
from .myPrint import myPrint
from lxml import etree
class Spider():
    def __init__(self):
        self.base_url = "http://www.variglight.com"
        self.query_by_route_baseurl = "http://www.variflight.com/flight/%s-%s.html?AE71649A58c77&fdate=%s"
        # 按路线查询航班信息的基本url，前两个 %s 是出发地和到达地的机场代码，分别为三个字母，最后一个是日期，格式为八位纯数字
        self.query_by_flightcode_baseurl = "http://www.variflight.com/flight/fnum/%s.html?AE71649A58c77&fdate=%s"
        # 按航班号查询航班信息的基本url，前一个%s是航班号，后一个是日期
        self.detailed_info_baseurl = "http://www.variflight.com/schedule/%s-%s-%s.html?AE71649A58c77=&fdate=%s"
        # 详细信息的基本url，第一、第二个%s分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        self.headers = self.__process_headers('''
        Host: www.variflight.com
        Connection: keep-alive
        Upgrade-Insecure-Requests: 1
        DNT: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
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
        if isinstance(html,requests.models.Response):
            html = html.text
        for item in html:
            try:
                print(item,end = '')
            except UnicodeEncodeError:
                print('\n----------------------- error here! -----------------------------')
        print()
    def search(self,*args):
        '''
        若按航班号查询，args的格式应为(flightcode, query_date)
        若按路线查询，args的格式应为(depart_air_code, arrive_air_code, query_date)
        '''
        if len(args) == 3:
            quert_url = self.query_by_route_baseurl%(args[0],args[1],args[2])
        elif len(args) == 2:
            quert_url = self.query_by_flightcode_baseurl%(args[0],args[1])
        else:
            raise ValueError("输入的参数有误！")
        flight_infos = []
        html = requests.get(quert_url,headers = self.headers)
        print("获取到网页！")
        # self.__print_html(html)
        query_result = re.search(r'<div class="fly_list">(.+?)</div>',html.text,re.S).group(0)
        query_result = re.findall(r'<li style="position: relative;">.+?</li>',html.text,re.S)
        # 各个航班信息的html代码块文本组成的列表
        for flight_info in query_result:
            # self.__print_html(item)
            # print('-------------------------------------------------------')
            html = etree.HTML(flight_info)
            img_urls = html.xpath('//div[@class="li_com"]/span/img/@src')
            # print(len(img_urls),img_urls)
            # 完整信息是四张图，至少两张图，顺序依次为 航空公司图标、准点率、实际起飞时间、实际降落时间
            dep_time_act_img_url = img_urls[1] if len(img_urls)==3 else None
            arri_time_act_img_rl = img_urls[2] if len(img_urls)==4 else None
            corp_name,flight_code = html.xpath('//div[@class="li_com"]/span/b/a/@title')
            # print(corp_name,flight_code)
            # 航空公司名称和航班号
            time_and_place_info= html.xpath('//div[@class="li_com"]/span[@class="w150"]/text()')
            time_and_place_info = list(map(lambda x:x.strip(),time_and_place_info))
            # print(len(time_and_place_info),time_and_place_info)
            # 共六项，只有四项有用，依次为计划起飞时间、计划起飞地点、计划到达时间、计划到达地点
            flight_status = html.xpath('//div[@class="li_com"]/span[@class="w150 blu_cor" or @class="w150 gre_cor" or @class="w150 red_cor" or @class="w150 bla_cor"]/text()')[0]
            # print(flight_status) 
            # 只有一项，即为航班状态，目前已遇到的状态有起飞、到达、取消、催促登机、登机结束、正在登机、延误预警
            flight_detailed_info_url = html.xpath('//li[@style="position: relative;"]/a[@class="searchlist_innerli"]/@href')
            shared_fligt = html.xpath('//li[@style="position: relative;"]/a[@class="list_share"]/@title')
            # print(flight_detailed_info_url,shared_fligt)
            # 有些航班是共享的，具体百度吧
            flight_infos.append(dict(
                flight_detailed_info_url=flight_detailed_info_url,
                corp_img_url=img_urls[0],
                corp_name=corp_name,
                flight_code=flight_code,
                shared_fligt=shared_fligt,
                dep_time_plan=time_and_place_info[0],
                dep_time_act_img_url=dep_time_act_img_url,
                dep_airp=time_and_place_info[1],
                arri_time_plan=time_and_place_info[2],
                arri_time_act_img_rl=arri_time_act_img_rl,
                arri_airp=time_and_place_info[3],
                ontime_rate_img_url=img_urls[-1],
                flight_status=flight_status
                ))
        return flight_infos
    def get_detailed_info(self,*args):
        quert_url = self.detailed_info_baseurl%(args[0],args[1],args[2],args[3])
        html = requests.get(quert_url,headers = self.headers)
        html = etree.HTML(html.text)
        flight_distance,flight_dur_time = html.xpath('//div[@class="flyProc"]/div[@id="p_box"]/div[@class="p_ti"]/span/text()')
        # print(flight_distance,flight_dur_time)
        plane_type = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="mileage"]/span/text()')[0]
        # print(plane_type)
        plane_age = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="time"]/span/text()')[0]
        # print(plane_age)
        pre_fligt = html.xpath('//div[@class="old_state"]/text()')[0]
        # print(pre_fligt)

        # 下面两段代码结构完全一致，只不过一个是出发机场的，一个是目的地机场的
        # 第一段代码
        dep_airp_weather = html.xpath('//div[@class="fly_mian"]/ul/li[@class="weather"]/p/text()')[0:3]
        arri_airp_weather = html.xpath('//div[@class="fly_mian"]/ul/li[@class="weather"]/p/text()')[3:]
        dep_airp_weather_iconurl,arri_airp_weather_iconurl = html.xpath('//div[@class="fly_mian"]/ul/li[@class="weather"]/img/@src')
        dep_time_estimated_iconurl = html.xpath('//div[@class="fly_mian"]/ul/li[@class="time"]/p[@class="com rand_p"]/img/@src')
        if not dep_time_estimated_iconurl:
            dep_time_estimated_iconurl = html.xpath('//div[@class="fly_mian"]/ul/li[@class="time"]/p[@class="com rand_p"]/text()')
        print(dep_time_estimated_iconurl)
        if not arri_time_estimated_iconurl:
            arri_time_estimated_iconurl = html.xpath('//div[@class="fly_mian"][2]/ul/li[@class="time"]/p[@class="com rand_p"]/text()')
        checkin_counter_imgurl,luggage_turntable_imgurl = html.xpath('//div[@class="fly_mian"]/ul/li[@class="inspect"]/p[@class="com rand_p"]/img/@src')
        if not checkin_counter_imgurl:
            checkin_counter_imgurl = html.xpath('//div[@class="fly_mian"]/ul/li[@class="inspect"]/p[@class="com rand_p"]/text()')
        if not luggage_turntable_imgurl:
            luggage_turntable_imgurl = html.xpath('//div[@class="fly_mian"][2]/ul/li[@class="inspect"]/p[@class="com rand_p"]/text()')
        boarding_gate,arri_gate = html.xpath('//div[@class="fly_mian"]/ul/li[@class="entrance"]/p[@class="com rand_p"]/img/@src')
        if not boarding_gate:
            boarding_gate = html.xpath('//div[@class="fly_mian"]/ul/li[@class="entrance"]/p[@class="com rand_p"]/text()')
        if not arri_gate:
            arri_gate = html.xpath('//div[@class="fly_mian"][2]/ul/li[@class="entrance"]/p[@class="com rand_p"]/text()')
        return dict(
            flight_distance = flight_distance,
            flight_dur_time = flight_dur_time,
            plane_type = plane_type,
            plane_age = plane_age,
            pre_fligt = pre_fligt,
            dep_airp_weather = dep_airp_weather,
            dep_airp_weather_iconurl = dep_airp_weather_iconurl,
            dep_time_estimated_iconurl = dep_time_estimated_iconurl,
            checkin_counter_imgurl = checkin_counter_imgurl,
            boarding_gate = boarding_gate,
            arri_airp_weather = arri_airp_weather,
            arri_airp_weather_iconurl = arri_airp_weather_iconurl,
            arri_time_estimated_iconurl = arri_time_estimated_iconurl,
            luggage_turntable_imgurl=luggage_turntable_imgurl,
            arri_gate=arri_gate
            )
if __name__ == '__main__':
    # myPrint(Spider().search('CAN','SHA','20190328'))
    # myPrint(Spider().search('3U2018','20190328'))
    myPrint(Spider().get_detailed_info('HAK','LLF','3U2018','20190328'))
