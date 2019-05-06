# -*- coding: utf-8 -*-
# @Date    : 2019-03-28 12:00:11
import os
import time
import requests
import threading
import logging
import pickle
import pytesseract
import datetime
from . import rec_pic
from . import rec_auth_code
from queue import Queue
from PIL import Image
from lxml import etree
from .myPrint import myPrint
from .headers import *
from .__init__ import *


class Spider(object):
    def __init__(self):
        # --- 日志配置 ---#
        self.logger = logging.getLogger("Spider")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            logfile = logging.FileHandler(LOG_PATH+"spider_run_log.log")
            console = logging.StreamHandler()
            file_formatter = logging.Formatter(
                '%(asctime)s %(filename)s [line:%(lineno)-3d]%(levelname)s %(message)s')
            console_formatter = logging.Formatter('%(filename)s[line:%(lineno)-3d]%(levelname)-8s %(message)s')
            logfile.setFormatter(file_formatter)
            console.setFormatter(console_formatter)
            # 可以通过下边两行修改日志和控制台输出的日志级别
            logfile.setLevel(logging.WARNING)
            console.setLevel(logging.DEBUG)
            self.logger.addHandler(logfile)
            self.logger.addHandler(console)

        # --- 基本url写入 ---#
        self.base_url = "http://www.variflight.com"
        self.query_by_route_baseurl = "http://www.variflight.com/flight/%s-%s.html?AE71649A58c77&fdate=%s"
        # 按路线查询航班信息的基本url，前两个 %s 是出发地和到达地的机场代码，分别为三个字母，最后一个是日期，格式为八位纯数字
        self.query_by_flightcode_baseurl = "http://www.variflight.com/flight/fnum/%s.html?AE71649A58c77&fdate=%s"
        # 按航班号查询航班信息的基本url，前一个%s是航班号，后一个是日期，格式为八位纯数字
        self.detailed_info_baseurl = "http://www.variflight.com/schedule/%s-%s-%s.html?AE71649A58c77=&fdate=%s"
        # 详细信息的基本url，第一、第二个%s分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期，格式为八位纯数字
        self.comfort_info_baseurl = "http://happiness.variflight.com/info/detail?fnum=%s&dep=%s&arr=%s&date=%s&type=1"
        # 共 5 个参数，由于最后一个是舱位标志，使用时只需要提供前四个参数即可
        # 第一个参数为航班代码，第二个为出发地机场代码，第三个为目的地机场代码，第四个为日期，格式示例为：2019-03-29    

        # --- 网络连接相关配置 ---#
        self.headers = Headers()
        self.session = requests.session()
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize = 30))
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize = 30))
        # --- 线程交互数据结构 ---#
        self.local_imgs = os.listdir(ORI_IMG_PATH)
        try:
            with open("local_img_rec_results.pkl", 'rb') as f:
                self.local_img_rec_results = pickle.load(f)
        except FileNotFoundError:
            with open("local_img_rec_results.pkl", 'wb') as f:
                pickle.dump({}, f)
                self.local_img_rec_results = {}
        self.img_503_error_total = 0
        self.rec_module = rec_pic.Rec_pic()
        self.img_down_mission_queue = Queue()
        # 多线程获取图片的任务队列，队列中每一个元素是一个元组，元组内容即为 _get_img 函数的参数
        self.img_rec_mission_queue = Queue()
        # 图片识别任务的队列，队列元素是一个元组，结构为(img_path，img_type)
        self.img_rec_result_dic = dict(init_key = "init_value")
        # 识别结果的任务队列，队列中每个元素是一个元组，结构为(原图片path，识别结果)
        self.down_img_thread_list = []
        self.img_down_mission_assign_finished = False

    def _start_get_imgs(self):
        self.logger.debug("[A]获取图片线程启动！")
        threading.Thread(target = self.rec_module.run,
                         args = (self.img_rec_mission_queue, self.img_rec_result_dic)).start()
        while not self.img_down_mission_assign_finished:
            if threading.activeCount() > 20 or self.img_down_mission_queue.empty():
                time.sleep(0.2)
            else:
                mission = self.img_down_mission_queue.get()
                t = threading.Thread(target = self._get_img, args = (mission,))
                t.start()
                self.down_img_thread_list.append(t)

    def _update_local_img_rec_results(self, dic):
        self.local_img_rec_results.update(dic)
        with open("local_img_rec_results.pkl", 'wb') as f:
            pickle.dump(self.local_img_rec_results, f)

    @staticmethod
    def __print_html(html):
        # 由于网页中经常含有某些特殊字符，无法用print显示，所以定义这个函数
        if isinstance(html, requests.models.Response):
            html = html.text
        for item in html:
            try:
                print(item, end = '')
            except UnicodeEncodeError:
                print('\n----------------------- error here! -----------------------------')
        print()

    @staticmethod
    def __strip_blanks(s):
        # 去除列表 s 中元素两端的空白字符
        if isinstance(s, list):
            return list(map(lambda x: x.strip(), s))
        elif isinstance(s, str):
            return s.strip()

    def _rec_auth_code(self, text):
        html = etree.HTML(text)
        auth_code_url = self.base_url+html.xpath("//div[@class='authCodeBox']//img/@src")[0]
        try:
            auth_code_img = self.session.get(auth_code_url)
        except Exception as e:
            self.logger.critical("获取验证码图片失败，失败原因：%s" % e)
            return
        if auth_code_img.status_code != 200 or auth_code_img.headers['Content-Type'] != 'image/png':
            self.logger.critical("获取验证码返回状态码错误或返回内容不是图片！！")
            return None
        img_name = "auth_code_%s.png" % str(datetime.datetime.now()).replace(":", "-")
        img_path = AUTH_CODE_IMG_PATH+img_name
        with open(img_path, 'wb') as f:
            f.write(auth_code_img.content)
        p = self.auth_rec_module.rec(img_path)
        self.logger.info("识别验证码：%s, 识别结果为：%s" % (img_path, p))
        return p

    def _get_page(self, query_url, headers, cur_fail_times=0, code_check_info=None):
        try:
            ori_html = self.session.get(query_url, headers = headers, timeout = 5)
        except Exception as e:
            self.logger.error("获取 url 为 %s 时出现错误，已返回空字典，错误原因为 %s" % (query_url, e))
            return None
        if ori_html.status_code != 200:
            self.logger.error("获取到的 url 为 %s 的网页响应状态码有误：%s" % (query_url, ori_html.status_code))
            return None
        if '抱歉，没有找到您输入的航班信息' in ori_html.text:
            code_show_info = re.search(r"\('.authCodeBox'\).(.{4})\(\)", ori_html.text)
            # 正常访问的话这一项是空的，需要输入验证码时这一项的值为 "show"，输入验证码正确时这一项的值为 "hide"
            if not code_show_info or code_show_info.group(1) == "hide":
                # 说明是真的没有这趟航班.
                self.logger.warning("没有查找到相应的航班，查询url：%s" % query_url)
                return None
            elif code_show_info.group(1) == "show":
                # 说明需要输入验证码
                if code_check_info and not code_check_info[0]:
                    # 说明验证码输入错误，需进行退款
                    self.auth_rec_module.refund(code_check_info[1])
                    self.logger.critical("上一次验证码输入错误，已发起退款")
                self.logger.warning("有验证码出现，查询结果获取失败！%s" % query_url)
                if cur_fail_times < 2:
                    self.logger.warning("当前页面失败次数：%d, 正在尝试输入验证码获取网页" % (cur_fail_times+1))
                    if cur_fail_times == 0:
                        self.auth_code_query_url = query_url
                        self.auth_rec_module = rec_auth_code.Rec_auth_code(self.logger)

                    auth_headers = self.headers.get_headers(3)
                    self.session.headers.update(auth_headers)
                    self.session.headers.update({"Refer": self.auth_code_query_url})
                    auth_code = self._rec_auth_code(ori_html.text)
                    cur_query_url = self.auth_code_query_url+"&authCode=%s" % auth_code["result"]
                    if auth_code:
                        p = self.session.get(
                            "http://www.variflight.com/flight/List/checkAuthCode?AE71649A58c77&authCode=%s" % auth_code[
                                "result"])
                        auth_check_result = json.loads(p.text, encoding = "utf-8")
                        self.logger.info("验证码提交结果：%s" % str(auth_check_result))
                        return self._get_page(cur_query_url, headers, cur_fail_times+1,
                                              (auth_check_result["code"], auth_code["request_id"]))
                    else:
                        self.logger.critical("验证码识别出现问题！无法继续获取网页！")
                        return None
                else:
                    self.logger.critical("多次尝试验证码获取网页失败！不再进行尝试！")
                    return None
            else:
                self.logger.critical("code_show_info 信息错误！请检查代码结构！")
                return None
        return ori_html

    def _get_img(self, arg_tuple):
        # 参数有四个，使用时请严格按照以下顺序：imgurl, img_path, rec_it, img_type
        # 正常情况下不返回结果，只更新self.img_rec_result_dic字典
        imgurl = arg_tuple[0]
        img_path = arg_tuple[1]
        rec_it = arg_tuple[2]
        img_type = arg_tuple[3]
        img_name = re.search(r"/([^/]+\.png)", img_path).group(1)
        if img_name not in self.local_imgs:
            # 本地没有这张图片或不使用本地图片
            try:
                img = self.session.get(imgurl)
            except Exception as e:
                self.logger.warning("获取图片失败: %s" % e)
                self.img_rec_result_dic.update({img_path: '--'})
                return
            if img.status_code != 200:
                if img.status_code == 503:
                    if self.img_503_error_total == 0:
                        self.lock = threading.Lock()
                    if self.lock.acquire():
                        self.img_503_error_total += 1
                        self.lock.release()
                else:
                    self.logger.warning("图片返回状态码有误，返回状态码: %s" % img.status_code)
                self.img_rec_result_dic.update({img_path: '--'})
                return
            elif img.headers['Content-Type'] == 'image/png':
                with open(img_path, 'wb') as f:
                    f.write(img.content)
            else:
                self.logger.warning("响应头表示这不是一个图片文件！")
                self.logger.warning("图片标题为: %s" % img_path)
                self.logger.warning("图片 url 为：%s" % imgurl)
                self.logger.warning("获取到的内容为：%s" % img.text)
                self.img_rec_result_dic.update({img_path: '--'})
        if rec_it:
            # 若识别
            result = self.local_img_rec_results.get(img_path)
            if result not in (None, '--'):
                self.img_rec_result_dic.update({img_path: result})
                return
            elif img_type != 4:
                self.img_rec_mission_queue.put((img_path, img_type))
            else:
                result = pytesseract.image_to_string(Image.open(img_path))
                self.img_rec_result_dic.update({img_path: result})

    def _wait_thread(self, fun_type=1):
        self.logger.debug("[%d]处理完成，等待图片下载任务下发完成..." % fun_type)
        while not self.img_down_mission_queue.empty():
            time.sleep(0.1)
        self.img_down_mission_assign_finished = True
        self.logger.debug("[%d]图片下载任务下发完成，等待图片下载完成..." % fun_type)
        for t in self.down_img_thread_list:
            t.join()
        self.rec_module.inform_pic_finished()
        self.logger.debug("[%d]图片下载完成！等待图片识别完成..." % fun_type)
        if self.img_503_error_total:
            self.logger.warning("本次查询共有 %d 张图片出现503错误" % self.img_503_error_total)
        while not self.rec_module.rec_finished:
            time.sleep(0.1)
        self.logger.debug("[%d]图片识别完成！结果马上呈现！" % fun_type)
        return

    def get_base_info(self, *args, with_img=True):
        """
        获取航班的基本信息
        开发时可以直接按 url 查询，直接传入 url 即可
        若按航班号查询，args的格式应为(flightcode, query_date)
        若按路线查询，args的格式应为(depart_air_code, arrive_air_code, query_date)
        """
        # ------ 构造并完善url ------ #
        global dep_time_act, ontime_rate, arri_time_act
        headers = self.headers.get_headers(1)
        if len(args) == 1:
            # 给定 url 查询，主要是调试时用
            query_url = args[0]
        elif len(args) == 2:
            # 按航班号查询
            query_url = self.query_by_flightcode_baseurl % (args[0], args[1])
        elif len(args) == 3:
            # 按路线查询
            query_url = self.query_by_route_baseurl % (args[0], args[1], args[2])
        else:
            self.logger.error("输入的参数有误，函数已报错！")
            raise ValueError("输入的参数有误！")
        query_date = query_url[-8:] if 'fdate' in query_url else str(datetime.date.today())
        if 'fdate' not in query_url:
            query_url += '&fdate=%s' % str(datetime.date.today()).replace('-', '')
        # ------ 准备工作 -----#
        flight_infos = []
        ori_html = self._get_page(query_url, headers)
        if not ori_html:
            self.logger.warning("查询基本信息，查询条件：%s，共查询到 %d 趟航班！" % (args,len(flight_infos)))
            return flight_infos
        # 是否颠倒图片
        reverse_info = re.search(r"b\((\d,\d)\);", ori_html.text).group(1)
        reverse_pic = True if reverse_info == "2,1" else False
        try:
            query_result = re.findall(r'<li style="position: relative;">.+?</li>', ori_html.text,
                                      re.S)  # query_result = re.search(r'<div class="fly_list">(.+?)</div>',ori_html.text,re.S).group(0)
        except AttributeError:
            self.logger.warning("似乎拿到的网页不对？？？")
            # print(self.__print_html(ori_html.text))
            self.img_down_mission_assign_finished = True
            self.logger.warning("查询基本信息，查询条件：%s，共查询到 %d 趟航班！" % (args,len(flight_infos)))
            return flight_infos
        # 各个航班信息的html代码块文本组成的列表，每个元素是一个航班的代码块
        if with_img:
            threading.Thread(target = self._start_get_imgs).start()
        for index, flight_info in enumerate(query_result):
            sub_html = etree.HTML(flight_info)
            # ---- 先获取文本信息 ---- #
            flight_detailed_info_url = self.base_url+sub_html.xpath(
                '//li[@style="position: relative;"]/a[@class="searchlist_innerli"]/@href')[0]
            tem = re.search(r'([A-Z]{3})-([A-Z]{3})', flight_detailed_info_url)
            dep_airp_code, arri_airp_code = tem.group(1), tem.group(2)
            corp_name, flight_code = sub_html.xpath('//div[@class="li_com"]/span/b/a/@title')
            shared_fligt = sub_html.xpath('//li[@style="position: relative;"]/a[@class="list_share"]/@title')
            shared_fligt = shared_fligt[0] if shared_fligt else '--'
            dep_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@dplan')[0]
            local_dep_date_plan = sub_html.xpath(
                '//div[@class="li_com"]/span[@class="w150" and contains(@dplan,":")]/em/text()')
            local_dep_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][1]/em/text()')
            dep_airp = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][2]/text()')[0]
            arri_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@aplan')[0]
            local_arri_date_plan = sub_html.xpath(
                '//div[@class="li_com"]/span[@class="w150" and contains(@aplan,":")]/em/text()')
            local_arri_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][2]/em/text()')
            arri_airp = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][4]/text()')[0]
            flight_status = sub_html.xpath('//div[@class="li_com"]/span[contains(@class,"_cor")]/text()')[0]
            # 航班状态，目前已遇到的状态有起飞、到达、取消、提前取消、催促登机、登机结束、正在登机、延误预警、延误
            if with_img:
                # ---- 再获取图片信息 ---- #
                # corp_imgurl=sub_html.xpath('//div[@class="li_com"]/span[@class="w260"]/img/@src')[0]
                dep_time_act_imgurl = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][1]/img/@src')
                dep_time_act_imgurl = self.base_url+dep_time_act_imgurl[0] if dep_time_act_imgurl else None
                arri_time_act_imgurl = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][2]/img/@src')
                arri_time_act_imgurl = self.base_url+arri_time_act_imgurl[0] if arri_time_act_imgurl else None
                ontime_rate_imgurl = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/img/@src')
                ontime_rate_imgurl = self.base_url+ontime_rate_imgurl[0] if ontime_rate_imgurl else None

                # ----- 重新对应图片 ----- #
                if reverse_pic:
                    arri_time_act_imgurl, dep_time_act_imgurl = dep_time_act_imgurl, arri_time_act_imgurl

                # ----- 往图片任务队列里推送图片 ------ #
                # 准点率
                ontime_rate_imgpath = ORI_IMG_PATH+"ontime_rate_%s_%s-%s_%s.png" % (
                    flight_code, dep_airp_code, arri_airp_code, query_date)
                ontime_rate = '--'
                if ontime_rate_imgurl:
                    self.img_down_mission_queue.put((ontime_rate_imgurl, ontime_rate_imgpath, True, 2))
                    ontime_rate = ontime_rate_imgpath
                # 实际起飞时间
                dep_time_act_imgpath = ORI_IMG_PATH+"dep_time_act_%s_%s-%s_%s.png" % (
                    flight_code, dep_airp_code, arri_airp_code, query_date)
                dep_time_act = '--'
                if dep_time_act_imgurl:
                    self.img_down_mission_queue.put((dep_time_act_imgurl, dep_time_act_imgpath, True, 1))
                    dep_time_act = dep_time_act_imgpath

                # 实际到达时间
                arri_time_act_imgpath = ORI_IMG_PATH+"arri_time_act_%s_%s-%s_%s.png" % (
                    flight_code, dep_airp_code, arri_airp_code, query_date)
                arri_time_act = '--'
                if arri_time_act_imgurl:
                    self.img_down_mission_queue.put((arri_time_act_imgurl, arri_time_act_imgpath, True, 1))
                    arri_time_act = arri_time_act_imgpath
            flight_infos.append(dict(flight_detailed_info_url = flight_detailed_info_url, corp_name = corp_name,
                                     flight_code = flight_code, shared_fligt = shared_fligt,
                                     dep_time_plan = dep_time_plan, dep_time_act = dep_time_act if with_img else '--',
                                     local_dep_date_plan = local_dep_date_plan[0] if local_dep_date_plan else '--',
                                     local_dep_date_act = local_dep_date_act[0] if local_dep_date_act else '--',
                                     dep_airp = dep_airp, dep_airp_code = dep_airp_code,
                                     arri_time_plan = arri_time_plan,
                                     arri_time_act = arri_time_act if with_img else '--',
                                     local_arri_date_plan = local_arri_date_plan[0] if local_arri_date_plan else '--',
                                     local_arri_date_act = local_arri_date_act[0] if local_arri_date_act else '--',
                                     arri_airp = arri_airp, arri_airp_code = arri_airp_code,
                                     ontime_rate = ontime_rate if with_img else '--', flight_status = flight_status))
        if with_img:
            self._wait_thread()
            threading.Thread(target = self._update_local_img_rec_results, args = (self.img_rec_result_dic,)).start()
            for flight_info in flight_infos:
                for item in ('dep_time_act', 'arri_time_act', 'ontime_rate'):
                    if flight_info[item] != '--':
                        try:
                            flight_info[item] = self.img_rec_result_dic.pop(flight_info[item])
                        except KeyError:
                            self.logger.critical("获取图片结果失败！,图片路径为：%s" % flight_info[item])
                            flight_info[item] = '--'  # myPrint(self.img_rec_result_dic)
            self.img_rec_result_dic.clear()
        self.logger.warning("查询基本信息，查询条件：%s，共查询到 %d 趟航班！" % (args,len(flight_infos)))
        return flight_infos

    def get_detailed_info(self, *args, with_img=True):
        # 查询详细信息，
        # 若为一个参数，则该参数是给定的 url
        # 若按航班号查询，共需要四个参数，第一、第二个分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        query_url = self.detailed_info_baseurl % (args[0], args[1], args[2], args[3]) if len(args) > 1 else args[0]
        query_date = query_url[-8:] if 'fdate' in query_url else str(datetime.date.today())
        if 'fdate' not in query_url:
            query_url += '&fdate=%s' % str(datetime.date.today()).replace('-', '')
        self.logger.warning("查询详细信息，查询条件：%s" % (args,))
        tem = re.search(r'([A-Z]{3})-([A-Z]{3})', query_url)
        dep_airp_code, arri_airp_code = tem.group(1), tem.group(2)
        airp_datas = {}
        ori_html = self._get_page(query_url, self.headers.get_headers(1))
        if not ori_html:
            return {}
        html = etree.HTML(ori_html.text)
        if "IP blocked" in ori_html.text:
            self.logger.critical("获取详细信息时直接被封ip！%s" % ori_html.text)
            return {}
        # ---- 先获取文本信息 ---- #
        try:
            corp_name_and_flight_code = html.xpath('//div[@class="tit"]/span/b/text()')[0].strip()
        except AttributeError:
            self.logger.warning("似乎拿到的网页不对？？？")
            return airp_datas
        flight_code = re.findall(r"[A-Z0-9]+", corp_name_and_flight_code)[0]
        corp_name = corp_name_and_flight_code.replace(flight_code, "").strip()
        flight_status = html.xpath('//div[@class="tit"]/div[@class="state"]/div/text()')[0]
        dep_city, arri_city = html.xpath(
            '//div[@class="flyProc"]/div[@id="p_box"]/div[@class="cir_l curr" or @class = "cir_r"]/span/text()')
        flight_distance, flight_dur_time = html.xpath(
            '//div[@class="flyProc"]/div[@id="p_box"]/div[@class="p_ti"]/span/text()')
        plane_type = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="mileage"]/span/text()')[0]
        plane_age = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="time"]/span/text()')[0]
        delay_time_tip = html.xpath('//div[@class="flyProc"]//li[@class="age"]/span/text()')
        delay_time_tip = delay_time_tip[0] if delay_time_tip else '--'
        pre_fligt = html.xpath('//div[@class="old_state"]/text()')[0]
        ave_ontime_rate = '--'
        # ---- 历史平均准点率 ---- #
        if with_img:
            threading.Thread(target = self._start_get_imgs).start()
            ave_ontime_rate_imgurl = self.base_url+html.xpath('//div[@class="flyProc"]//li[@class="per"]//img/@src')[
                0].strip()
            ave_ontime_rate_imgpath = ORI_IMG_PATH+"ave_ontime_rate_%s_%s-%s_%s.png" % (flight_code, dep_airp_code, arri_airp_code, query_date)
            self.img_down_mission_queue.put((ave_ontime_rate_imgurl, ave_ontime_rate_imgpath, True, 4))
            ave_ontime_rate = ave_ontime_rate_imgpath
        # ----------------------------------以下为机场信息---------------------------------------- #
        # 航班涉及到的城市数量，包括起飞地、到达地和经停地（目前只遇到过一个经停地的情况，多个经停地的情况待测试）
        involved_airp_total = len(html.xpath('//div[contains(@class,"fly_mian")]'))
        # 航班涉及到的机场
        involved_airps = html.xpath('//div[contains(@class,"fly_mian")]/div[contains(@class,"f_title")]/h2/text()')
        involved_airps = list(filter(bool, self.__strip_blanks(involved_airps)))
        # 机场天气
        airp_weathers = html.xpath('//div[contains(@class,"fly_mian")]/ul/li[@class="weather"]/p/text()')
        # print(self._get_img(self.base_url+html.xpath('//div[contains(@class,"fly_mian")][1]/ul[1]/li[@class="time"]/p[2]/img/@src')[0].strip(),session,'test'))

        # ----  图片对应信息  ---- #
        order1 = json.loads('[%s]' % re.search(r"func\('rand_ul_dep', (\d,\d,\d)\);", ori_html.text).group(1))
        order2 = json.loads('[%s]' % re.search(r"func\('rand_ul_arr', (\d,\d,\d)\);", ori_html.text).group(1))
        if involved_airp_total == 3:
            order3 = json.loads('[%s]' % re.search(r"midFunc\((\d,\d,\d,\d,\d,\d)\);", ori_html.text).group(1))
        order_list = (order1, order2) if involved_airp_total == 2 else (order1, order3, order2)

        # ----  获取机场信息  ---- #
        blank_data_pos = []
        for i in range(involved_airp_total):
            airp_datas.update({involved_airps[i]: {}})
            airp_data_rows = len(
                html.xpath('//div[contains(@class,"fly_mian")][%d]/ul[contains(@class,"f_common")]' % (i+1)))
            # print("第 %d 行共有 %d 子行数据"%(i+1,airp_data_rows))
            for sub_i in range(airp_data_rows):
                li_class_list = ['time', 'inspect', 'entrance']
                for j in range(3):
                    # 共三列数据
                    item_name = html.xpath(
                        '//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[@class="gray_t"]/text()' % (
                            i+1, sub_i+1, li_class_list[j]))[0]
                    item_data_img_url = html.xpath(
                        '//div[contains(@class,"fly_mian")][%d]/ul[%d]/li[@class="%s"]/p[@class="com rand_p"]/img/@src' % (
                            i+1, sub_i+1, li_class_list[j]))
                    expected_pos = order_list[i][sub_i * 3+j]
                    if with_img:
                        if item_data_img_url:
                            item_data_img_url = self.base_url+item_data_img_url[0].strip()
                            item_data_img_path = ORI_IMG_PATH+'%s_%s-%s_%s_%d%d.png' % (
                                flight_code, dep_airp_code, arri_airp_code, query_date, i+1, expected_pos)
                            self.img_down_mission_queue.put((item_data_img_url, item_data_img_path, True, 3))
                        else:
                            blank_data_pos.append("%d%d" % (i+1, expected_pos))
                    airp_datas[involved_airps[i]][item_name] = ORI_IMG_PATH+'%s_%s-%s_%s_%d%d.png' % (
                        flight_code, dep_airp_code, arri_airp_code, query_date, i+1, sub_i*3+j+1) if with_img else '--'
        # ---- 对本来就是空的项目的内容设置为'--' ---- #
        if with_img:
            for airp_name, airp_data in airp_datas.items():
                for item_name, item_data in airp_data.items():
                    if item_data[-6:-4] in blank_data_pos:
                        airp_datas[airp_name][item_name] = '--'
        # 对应天气
        for index, airp_name in enumerate(involved_airps):
            airp_datas[airp_name]['weather'] = airp_weathers[3 * index:3 * index+3]
        # 等待图片
        if with_img:
            self._wait_thread(2)
            # 获取图片内容
            threading.Thread(target = self._update_local_img_rec_results, args = (self.img_rec_result_dic,)).start()
            ave_ontime_rate = self.img_rec_result_dic.get(ave_ontime_rate)
            if not ave_ontime_rate:
                ave_ontime_rate = '--'
            for airp_name, airp_data in airp_datas.items():
                for item_name, item_data in airp_data.items():
                    if item_data != '--' and item_name != 'weather':
                        try:
                            airp_datas[airp_name][item_name] = self.img_rec_result_dic.pop(item_data)
                        except KeyError:
                            self.logger.critical("获取图片结果失败！,图片路径为：%s" % item_data)
                            airp_datas[airp_name][item_name] = '--'
                            myPrint(self.img_rec_result_dic)
            self.img_rec_result_dic.clear()
        return dict(corp_name_and_flight_code = corp_name_and_flight_code, corp_name = corp_name,
                    flight_code = flight_code, flight_status = flight_status, dep_city = dep_city,
                    arri_city = arri_city, flight_distance = flight_distance, flight_dur_time = flight_dur_time,
                    plane_type = plane_type, plane_age = plane_age,
                    ave_ontime_rate = ave_ontime_rate, delay_time_tip = delay_time_tip,
                    pre_fligt = pre_fligt, airp_datas = airp_datas)

    def get_confort_info(self, *args):
        # 获取舒适度信息，网站限定，查询太频繁会拿不到数据
        # 若给定 url，则只需传入一个参数
        # 若按航班号查询，需提供四个参数，第一个参数为航班代码，第二个为出发地机场代码，第三个为目的地机场代码，第四个为日期，格式示例为：2019-03-29
        url = self.comfort_info_baseurl % (args[0], args[1], args[2], args[3]) if len(args) > 1 else args[0]
        try:
            ori_html = self.session.get(url, headers = self.headers.get_headers(2), timeout = 5)
        except Exception as e:
            self.logger.error("[3]网页获取出现错误！")
            self.logger.error("[3]网页 url：%s" % url)
            self.logger.error("[3]错误原因：%s" % e)
            return {}
        print("[3]获取到网页")
        if ori_html.status_code != 200:
            self.logger.error("[3]网页返回状态码有误：%s" % ori_html.status_code)
            return {}
        if "抱歉，此类查询已达当日上限" in ori_html.text:
            self.logger.error("[3]抱歉，此类查询已达当日上限!")
            return dict()
        html = etree.HTML(ori_html.text)
        sub_info1 = self.__strip_blanks(html.xpath('//div[@class="basic"]//h1/span/text()'))
        # print(sub_info1)
        corp_name, flight_code, flight_date, flight_weeknum = sub_info1
        sub_info2 = self.__strip_blanks(
            html.xpath('//div[@class="mid fl"]//p[@class="rate" or @class="one" or @class="two"]/text()'))
        ave_ontime_rate, flight_distance, flight_dur_time = sub_info2
        # print(sub_info2)
        sub_info3 = self.__strip_blanks(
            html.xpath('//div[@class="circle lefCircle" or @class="circle rigCircle"]/p/text()'))
        # print(sub_info3)
        dep_ave_delay_time, arri_ave_delay_time = sub_info3[0:3:2]

        # --- 舱位信息获取 --- #
        cabin_names = html.xpath('//div[@class="service"]//div[@class="top"]//a/text()')
        # print(cabin_names)
        cabin_infos = dict()
        for i, item in enumerate(cabin_names):
            cabin_infos[item] = {}
            cabin_infos[item]['cabin_marks'] = self.__strip_blanks(
                html.xpath('//div[@class="basic"]//div[@class="scoreList"]//span[%d]/text()' % (i+1)))[0]
            cabin_infos[item]['cabin_equipments'] = self.__strip_blanks(html.xpath(
                '//div[@class="service"]//div[@class="mid clearfix cur" or @class="mid clearfix"][%d]//div[@class="devList"]/ul[1]/li/@title' % (
                        i+1)))
            # print(cabin_equipments)
            cabin_infos[item]['seat_info'] = self.__strip_blanks(html.xpath(
                '//div[@class="service"]//div[@class="mid clearfix cur" or @class="mid clearfix"][%d]//div[@class="devList"]/ul[2]/li/span/text()' % (
                        i+1)))
            # 包含三项内容，分别为座椅角度、座椅宽度、座椅间距 
            # print(seat_info)
            cabin_infos[item]['evaluate_stars'] = len(html.xpath(
                '//div[@class="service-standard"]/p[%d]/i[@class="iconfont icon-Star blue"]' % (
                        i+1)))  # print(evaluate_stars1,evaluate_stars2,evaluate_stars3)

        return dict(corp_name = corp_name, flight_code = flight_code, flight_date = flight_date,
                    flight_weeknum = flight_weeknum, ave_ontime_rate = ave_ontime_rate,
                    flight_distance = flight_distance, flight_dur_time = flight_dur_time,
                    dep_ave_delay_time = dep_ave_delay_time, arri_ave_delay_time = arri_ave_delay_time,
                    cabin_infos = cabin_infos)


if __name__ == '__main__':
    pass
    # myPrint(Spider().get_base_info('BJS', "SHH", '20190504', with_img=True))
    # myPrint(Spider().get_base_info('CA911', '20190505', with_img = True))
    # myPrint(Spider().get_base_info('CA911', '20190424', with_img = True))
    # myPrint(Spider().get_base_info('PEK','SHA','20190422',with_img=True))
    # myPrint(Spider().get_base_info('CA1234','20190415',with_img=True))
    # myPrint(Spider().get_detailed_info("http://www.variflight.com/schedule/PEK-ARN-CA911.html?AE71649A58c77="))
    # myPrint(Spider().get_detailed_info("BHY", "PEK", "CZ3147", '20190504'))
    # myPrint(Spider().get_detailed_info('BHY','PEK','CA911','20190421',with_img=True))
    # myPrint(Spider().get_confort_info('http://happiness.variflight.com/search/airline?date=2019-04-04&dep=PEK&arr=CTU&type=1'))
    # myPrint(Spider().get_confort_info('CZ3147', 'PEK', 'SHA', '2019-04-23'))
