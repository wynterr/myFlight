# -*- coding: utf-8 -*-
# @Date    : 2019-03-28 12:00:11
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
import sys
import re
import time
import json
import requests
import pytesseract
import random
import threading
from queue import Queue
from PIL import Image
from lxml import etree
from .headers import Headers
from .myPrint import myPrint
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
        self.headers = Headers()
        self.session = requests.session()
        self.headers2 = self.headers.get_headers(3)
        self.img_mission_queue = Queue()
        # 多线程获取图片的任务队列，队列中每一个元素是一个元组，元组内容即为 _get_img 函数的参数
        self.img_result_dict = dict()
        self.down_img_thread_list = []
        self.stop_get_imgs = False
    def _start_get_imgs(self,max_try_times=5):
        print("[A]爬取图片线程启动！")
        while not self.stop_get_imgs:
            if threading.activeCount() > 250 or self.img_mission_queue.empty():
                time.sleep(0.2)
            else:
                mission = self.img_mission_queue.get()
                t=threading.Thread(target=self._get_img,args=(mission,))
                t.start()
                self.down_img_thread_list.append(t)
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
    def _get_img(self,arg_tuple):
        # 获取图片，顺便识别图片内容
        # 参数最多只能有四个，至少两个，使用时请严格按照以下顺序：imgurl, img_path, rec_it, headers
        # 返回一个字典，若识别，则返回{img_path:识别结果}，若不识别，则返回{img_path:None}
        imgurl = arg_tuple[0]
        img_path = arg_tuple[1]
        rec_it = True if len(arg_tuple)==2 else arg_tuple[2]
        headers = None if len(arg_tuple)<4 else arg_tuple[3]
        try:
            img = self.session.get(imgurl)
        except Exception as e:
            print("获取图片失败！")
            print(e)
            self.img_result_dict.update({img_path:None})
            return 
        if sys.getsizeof(img.content) > 450:
            if '.png' not in img_path:
                img_path += '.png'
            with open(img_path,'wb') as f:
                f.write(img.content)
                # print("[i]%s保存成功！"%img_path)
            if rec_it:
                result = pytesseract.image_to_string(Image.open(img_path))
                # print("识别到内容：",result)
                self.img_result_dict.update({img_path:result})
            else:
                self.img_result_dict.update({img_path:img_path})
        else:
            print("获取图片内容有误！")
            print("图片标题为",img_path)
            print("图片 url 为：%s"%imgurl)
            print("获取到的内容为：%s"%img.text)
            self.img_result_dict.update({img_path:None})
    def _get_img_result(self,img_path):
        pass
    def get_base_info(self,*args):
        '''
        获取航班的基本信息
        开发时可以直接按 url 查询，直接传入 url 即可
        若按航班号查询，args的格式应为(flightcode, query_date)
        若按路线查询，args的格式应为(depart_air_code, arrive_air_code, query_date)
        '''
        img_get_thread = threading.Thread(target=self._start_get_imgs)
        img_get_thread.start()
        self.stop_get_imgs = False
        headers = self.headers.get_headers(1)
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

        query_date = args[-1] if len(args)>1 else 'rand_'+str(ramdom.randint(1,99))
        # 如果是按url查询则日期为随机数
        flight_infos = []
        try:
            ori_html = self.session.get(query_url,headers = headers,timeout = 5)
        except Exception as e:
            print("[1]网页获取出现错误！")
            print("[1]网页 url：",query_url)
            print("[1]错误原因：",e)
            return flight_infos
        print("[1]获取到网页！")
        # myPrint(headers)
        # self.__print_html(ori_html.text)
        if ori_html.status_code != 200:
            print("[1]网页返回状态码有误：",ori_html.status_code)
            return flight_infos
        html = etree.HTML(ori_html.text)
        p = html.xpath('//div[@class="fly_main"]//img[contains(@src,"404")]')
        if p:
            print("[1]抱歉，没有查找到您需要的航班！")
            print(ori_html.text)
            return flight_infos
        query_result = re.search(r'<div class="fly_list">(.+?)</div>',ori_html.text,re.S).group(0)
        query_result = re.findall(r'<li style="position: relative;">.+?</li>',ori_html.text,re.S)
        # 各个航班信息的html代码块文本组成的列表，每个元素是一个航班的代码块
        for index,flight_info in enumerate(query_result):
            sub_html = etree.HTML(flight_info)

            #---- 先获取文本信息 ----#
            flight_detailed_info_url = self.base_url + sub_html.xpath('//li[@style="position: relative;"]/a[@class="searchlist_innerli"]/@href')[0]
            corp_name,flight_code = sub_html.xpath('//div[@class="li_com"]/span/b/a/@title')
            # print(corp_name,flight_code)
            shared_fligt = sub_html.xpath('//li[@style="position: relative;"]/a[@class="list_share"]/@title')
            shared_fligt = shared_fligt[0] if shared_fligt else None
            # print(flight_detailed_info_url,shared_fligt)
            dep_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@dplan')[0]
            local_dep_date_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150" and contains(@dplan,":")]/em/text()')
            local_dep_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][1]/em/text()')
            dep_airp = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][2]/text()')[0]
            # print(dep_time_plan,local_dep_date_plan,local_dep_date_act,dep_airp)
            arri_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@aplan')[0]
            local_arri_date_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150" and contains(@aplan,":")]/em/text()')
            local_arri_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][2]/em/text()')
            arri_airp = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][4]/text()')[0]
            # print(arri_time_plan,local_arri_date_plan,local_arri_date_act,arri_airp)
            flight_status = sub_html.xpath('//div[@class="li_com"]/span[contains(@class,"_cor")]/text()')[0]
            # 只有一项，即为航班状态，目前已遇到的状态有起飞、到达、取消、催促登机、登机结束、正在登机、延误预警

            #---- 再获取图片信息 ----#
            corp_imgurl=sub_html.xpath('//div[@class="li_com"]/span[@class="w260"]/img/@src')[0]
            # print(corp_imgurl)
            corp_imgpath = "./spider/img_file/%s商标.png"%corp_name
            dep_time_act_imgurl = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][1]/img/@src')
            dep_time_act_imgurl = self.base_url + dep_time_act_imgurl[0] if dep_time_act_imgurl else None
            # print(dep_time_act_imgurl)
            arri_time_act_imgurl = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][2]/img/@src')
            arri_time_act_imgurl = self.base_url + arri_time_act_imgurl[0] if arri_time_act_imgurl else None
            # print(arri_time_act_imgurl)
            ontime_rate_imgurl=sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/img/@src')
            ontime_rate_imgurl = self.base_url + ontime_rate_imgurl[0] if ontime_rate_imgurl else None
            # print(ontime_rate_imgurl)

            #----- 往图片任务队列里推送图片 ------#
            # 航空公司商标
            self.img_mission_queue.put((corp_imgurl,corp_imgpath,False))
            corp_imgpath = corp_imgpath
            # 准点率
            ontime_rate_imgpath = "./spider/img_file/%s_%s-%s_%s_onTimeRate.png"%(flight_code,dep_airp,arri_airp,query_date)
            if ontime_rate_imgurl:
                self.img_mission_queue.put((ontime_rate_imgurl,ontime_rate_imgpath))
                ontime_rate = ontime_rate_imgpath
            else:
                ontime_rate = '--'
            # 实际起飞时间
            dep_time_act_imgpath = "./spider/img_file/dep_time_act_%s_%s-%s_%s.png"%(flight_code,dep_airp,arri_airp,query_date)
            if dep_time_act_imgurl:
                self.img_mission_queue.put((dep_time_act_imgurl,dep_time_act_imgpath))
                dep_time_act = dep_time_act_imgpath
            else:
                dep_time_act = '--'
            # 实际到达时间
            arri_time_act_imgpath = "./spider/img_file/arri_time_act_%s_%s-%s_%s.png"%(flight_code,dep_airp,arri_airp,query_date)
            if arri_time_act_imgurl:
                self.img_mission_queue.put((arri_time_act_imgurl,arri_time_act_imgpath))
                arri_time_act = arri_time_act_imgpath
            else:
                arri_time_act = '--'
            flight_infos.append(dict(
                flight_detailed_info_url=flight_detailed_info_url,
                corp_imgpath=corp_imgpath,
                corp_name=corp_name,
                flight_code=flight_code,
                shared_fligt=shared_fligt,
                dep_time_plan=dep_time_plan,
                dep_time_act=min(dep_time_act,arri_time_act),
                local_dep_date_plan=local_dep_date_plan[0] if local_dep_date_plan else None,
                local_dep_date_act=local_dep_date_act[0] if local_dep_date_act else None,
                dep_airp=dep_airp,
                arri_time_plan=arri_time_plan,
                arri_time_act=max(dep_time_act,arri_time_act),
                local_arri_date_plan=local_arri_date_plan[0] if local_arri_date_plan else None,
                local_arri_date_act=local_arri_date_act[0] if local_arri_date_act else None,
                arri_airp=arri_airp,
                ontime_rate=ontime_rate,
                flight_status=flight_status
                ))
        print("[1]处理完成，等待图片任务下发完成...")
        while not self.img_mission_queue.empty():
            time.sleep(0.1)
        self.stop_get_imgs = True
        print("[1]图片任务下发完成，等待图片下载识别完成...")
        for t in self.down_img_thread_list:
            t.join()
        for flight_info in flight_infos:
            for item in ('corp_imgpath','dep_time_act','arri_time_act','ontime_rate'):
                if flight_info[item] != '--':
                    try:
                        flight_info[item] = self.img_result_dict.pop(flight_info[item])
                    except KeyError:
                        if item == 'corp_imgpath':
                            pass
                        else:
                            print("[1]获取失败！",flight_info[item])
                            myPrint(self.img_result_dict)
        return flight_infos
    def get_detailed_info(self,*args):
        # 查询详细信息，
        # 若为一个参数，则该参数是给定的 url
        # 若按航班号查询，共需要四个参数，第一、第二个分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        img_get_thread = threading.Thread(target=self._start_get_imgs)
        img_get_thread.start()
        self.stop_get_imgs = False
        query_url = self.detailed_info_baseurl%(args[0],args[1],args[2],args[3]) if len(args)>1 else args[0]
        query_date = query_url[-8:] if 'fdate' in query_url else 'rand_'+str(ramdom.randint(1,99))
        airp_datas = {}
        try:
            ori_html = self.session.get(query_url,headers = self.headers.get_headers(1))
        except Exception as e:
            print("[2]网页获取出现错误！")
            print("[2]网页 url：",query_url)
            print("[2]错误原因：",e)
            return airp_datas
        print("[2]获取到网页")
        if ori_html.status_code != 200:
            print("[2]网页返回状态码有误：",ori_html.status_code)
            return airp_datas
        html = etree.HTML(ori_html.text)
        p = html.xpath('//div[@class="fly_main"]//img[contains(@src,"404")]')
        if p:
            print("[2]抱歉，没有查找到您需要的航班！")
            # self.__print_html(html.text)
            return airp_datas
        # self.__print_html(html)
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
        ave_ontime_rate_imgpath ="./spider/img_file/%s_%s-%s_ave_ontime_rate.png"%(corp_name_and_flight_code,dep_city,arri_city)
        ave_ontime_rate = self.img_mission_queue.put((ave_ontime_rate_imgurl,ave_ontime_rate_imgpath))
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
            self.img_mission_queue.put((item,"./spider/img_file/%s.png"%item[item.rindex("/")+1:],False))
        # print(airp_weathers_iconurls)
        #-- 以上两个变量所包含的内容的数量应与 involved_airp_total 相等
        #-- 以下变量所包含的内容的数量应比 involved_airp_total 多出经停地的数量，因为每一个经停地都有到达和出发时间，而出发到达地则只有一个时间
        data_total = len(html.xpath('//ul[contains(@class,"f_common")]'))
        # 所有机场的同一数据项的数目之和，就是网页右边数据的行数
        # print("data total is",data_total)
        # print(self._get_img(self.base_url+html.xpath('//div[contains(@class,"fly_mian")][1]/ul[1]/li[@class="time"]/p[2]/img/@src')[0].strip(),session,'test'))
        for i in range(involved_airp_total):
            airp_datas.update({involved_airps[i]:{"item_name_list":[],"item_data_list":[]}})
            airp_data_rows = len(html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[contains(@class,"f_common")]'%(i+1)))
            # print("第 %d 行共有 %d 子行数据"%(i+1,airp_data_rows))
            for sub_i in range(airp_data_rows):
                li_class_list = ['time','inspect','entrance']
                for j in range(3): 
                # 共三列数据
                    item_name = html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[@class="gray_t"]/text()'%(i+1,sub_i+1,li_class_list[j]))[0]
                    # print("第 %d 行第 %d 子行第 %d 列数据项名称："%(i+1,sub_i+1,j+1),item_name)
                    item_data_img_url = html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[@class="com rand_p"]/img/@src'%(i+1,sub_i+1,li_class_list[j]))
                    # print("第 %d 行第 %d 子行第 %d 列图片的xpath内容："%(i+1,sub_i+1,j+1),'//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[2]/img/@src'%(i+1,sub_i+1,li_class_list[j]))
                    # print(item_data_img_url)
                    if not item_data_img_url:
                        # print("第 %d 行第 %d 子行第 %d 列数据无图片链接"%(i+1,sub_i+1,j+1))
                        item_data =  html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[2]/text()'%(i+1,sub_i+1,li_class_list[j]))
                        item_data = item_data[0].strip()
                    else:
                        item_data_img_url = self.base_url + item_data_img_url[0].strip()
                        item_data_img_path = './spider/img_file/%s_%s-%s_%s_%d%d%d.png'%(corp_name_and_flight_code,dep_city,arri_city,query_date,i+1,sub_i+1,j+1)
                        self.img_mission_queue.put((item_data_img_url,item_data_img_path))
                        item_data = item_data_img_path
                    airp_datas[involved_airps[i]]['item_name_list'].append(item_name)
                    airp_datas[involved_airps[i]]['item_data_list'].append(item_data)

        # 重新对应图片
        order1 = json.loads('[%s]'%re.search(r"func\('rand_ul_dep', (\d,\d,\d)\);",ori_html.text).group(1))
        order2 = json.loads('[%s]'%re.search(r"func\('rand_ul_arr', (\d,\d,\d)\);",ori_html.text).group(1))
        if involved_airp_total == 3:
            order3 = json.loads('[%s]'%re.search(r"midFunc\((\d,\d,\d,\d,\d,\d)\);",ori_html.text).group(1))
        order_list = (order1,order2) if involved_airp_total==2 else (order1,order3,order2)
        for airp_index,airp_name in enumerate(involved_airps):
            item_total = len(airp_datas[airp_name]['item_name_list'])
            new_list = [None for i in range(item_total)]
            for i in range(item_total):
                new_list[order_list[airp_index][i]-1] = airp_datas[airp_name]["item_data_list"][i]
            airp_datas[airp_name] = dict(zip(airp_datas[airp_name]['item_name_list'],new_list))

        # 对应天气
        for index,airp_name in enumerate(involved_airps):
            airp_datas[airp_name]['weather'] = airp_weathers[3*index:3*index+3]
        print('[2]处理完成，等待图片任务下发完成...')
        while not self.img_mission_queue.empty():
            time.sleep(0.1)
        self.stop_get_imgs = True
        print('[2]图片任务下发完成，等待图片获取识别完成...')
        for t in self.down_img_thread_list:
            t.join()
        # 获取图片内容
        for airp_name,airp_data in airp_datas.items():
            for item_name,item_data in airp_data.items():
                if item_data != '--' and ('预计' in item_name or '实际' in item_name):
                    try:
                        airp_datas[airp_name][item_name] = self.img_result_dict[item_data]
                    except KeyError:
                        print('[2]获取失败！',item_data)
                        myPrint(self.img_result_dict)
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
            airp_datas=airp_datas
            )
    def get_confort_info(self,*args):
        # 获取舒适度信息，网站限定，查询太频繁会拿不到数据
        # 若给定 url，则只需传入一个参数
        # 若按航班号查询，需提供四个参数，第一个参数为航班代码，第二个为出发地机场代码，第三个为目的地机场代码，第四个为日期，格式示例为：2019-03-29
        url = self.comfort_info_baseurl%(args[0],args[1],args[2],args[3]) if len(args)>1 else args[0]
        if len(args) > 1:
            html = self.session.get('http://happiness.variflight.com/search/airline?date=%s&dep=%s&arr=%s&type=1'%(args[3],args[1],args[2]))
        else:
            date = re.search(r'date=([\d-]+)',args[0]).group(1)
            dep = re.search(r'dep=(.{3})',args[0]).group(1)
            arri = re.search(r'arr=(.{3})',args[0]).group(1)
            html = self.session.get('http://happiness.variflight.com/search/airline?date=%s&dep=%s&arr=%s&type=1'%(date,dep,arri))
        try:
            ori_html = self.session.get(url,headers = self.headers.get_headers(2),timeout=5)
        except Exception as e:
            print("[3]网页获取出现错误！")
            print("[3]网页 url：",query_url)
            print("[3]错误原因：",e)
            return airp_datas
        print("[3]获取到网页")
        if ori_html.status_code != 200:
            print("[3]网页返回状态码有误：",ori_html.status_code)
            return airp_datas
        html = etree.HTML(html.text)
        p = html.xpath('//div[@class="not-found"]')
        if p:
            print("[3]抱歉，此类查询已达当日上限!")
            self.__print_html(ori_html.text)
            return dict()
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
    #myPrint(Spider().get_base_info('SHA','PEK','20190405'))
    # myPrint(Spider().get_base_info('CA911','20190329'))
    # myPrint(Spider().get_base_info("http://www.variflight.com/flight/PEK-CAN.html?AE71649A58c77"))
    url1="http://www.variflight.com/schedule/BHY-CSX-CZ3147.html?AE71649A58c77=&fdate=20190402"
    myPrint(Spider().get_detailed_info(url1))
    # myPrint(Spider().get_detailed_info('http://www.variflight.com/schedule/BHY-CSX-CZ3147.html?AE71649A58c77=&fdate=20190331'))
    # myPrint(Spider().get_detailed_info('BHY','PEK','CZ3147','20190331'))
    # myPrint(Spider().get_confort_info('http://happiness.variflight.com/search/airline?date=2019-04-04&dep=PEK&arr=CTU&type=1'))
    # myPrint(Spider().get_confort_info('CZ3147','PEK','SHA','2019-03-30'))
