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
from .n2o import n2o
from .headers import *
from .__init__ import *

class RES(object):
    def __init__(self,code,message,data):
        """
        code 请参考调用处的说明
        """
        self.code = code
        self.message = message
        self.data = data
        self.value = dict(code=code,message=message,data=data)
    def __repr__(self):
        return "code:%s, message:%s, data:%s"%(self.code,self.message,self.data)
    __str__ = __repr__


class Spider(object):
    def __init__(self):
        # --- 日志配置 ---#
        self.logger = logging.getLogger("Spider")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            logfile = logging.FileHandler(LOG_PATH+"spider_run_log.log")
            console = logging.StreamHandler()
            file_formatter = logging.Formatter(
                '[%(levelname)-8s] %(asctime)s %(filename)s[line:%(lineno)d](%(funcName)s) %(message)s')
            console_formatter = logging.Formatter(
                '[%(levelname)-8s]%(filename)s[line:%(lineno)d](%(funcName)s) %(message)s')
            logfile.setFormatter(file_formatter)
            console.setFormatter(console_formatter)
            # 可以通过下边两行修改日志和控制台输出的日志级别
            logfile.setLevel(logging.INFO)
            console.setLevel(logging.DEBUG)
            self.logger.addHandler(logfile)
            self.logger.addHandler(console)
        self.remove_superfluous_handlers()

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
        requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
        self.session.keep_alive = False
        # --- 线程交互数据结构 ---#
        self.local_imgs = os.listdir(ORI_IMG_PATH)
        try:
            with open("local_img_rec_results.pkl", 'rb') as f:
                self.local_img_rec_results = pickle.load(f)
        except FileNotFoundError:
            with open("local_img_rec_results.pkl", 'wb') as f:
                pickle.dump({}, f)
                self.local_img_rec_results = {}
        except EOFError:
            self.local_img_rec_results = {}
        self.img_503_error_total = 0
        self.rec_module = rec_pic.Rec_pic()
        self.img_down_mission_queue = Queue()
        # 多线程获取图片的任务队列，队列中每一个元素是一个元组，元组内容即为 _get_img 函数的参数
        self.img_rec_mission_queue = Queue()
        # 图片识别任务的队列，队列元素是一个元组，结构为(img_path，img_type)
        self.img_rec_result_dic = {"init_key":"init_value"}
        # 识别结果，字典结构为{原图片path：识别结果,...}
        # 此字典必须得有一个初始值！！！
        self.down_img_thread_list = []
        self.img_down_mission_assign_finished = False

    def remove_superfluous_handlers(self):
        if len(self.logger.handlers) > 2:
            print("remove_superfluous_handlers!")
            had = []
            for item in self.logger.handlers:
                if type(item) not in had:
                    had.append(type(item))
                else:
                    self.logger.removeHandler(item)

    def _start_get_imgs(self):
        self.logger.debug("[A]获取图片线程启动！")
        self.rec_module.init_args()
        threading.Thread(target = self.rec_module.run,
                         args = (self.img_rec_mission_queue, self.img_rec_result_dic)).start()
        while not self.img_down_mission_assign_finished:
            # 不能以任务队列是否为空来判断，因为这个线程刚开始时主线程还来不及往任务队列里下发图片
            # 后边那个值只有在图片任务全部进入队列后队列再次为空后才被修改为True
            if threading.activeCount() > 50 or self.img_down_mission_queue.empty():
                time.sleep(0.2)
            else:
                mission = self.img_down_mission_queue.get()
                t = threading.Thread(target = self._get_img, args = (mission,))
                t.start()
                self.down_img_thread_list.append(t)

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

    def _update_local_img_rec_results(self):
        p = self.img_rec_result_dic.copy()
        if p:
            with open("local_img_rec_results.pkl", 'rb+') as f:
                ori = pickle.load(f)
                f.seek(0)
                ori.update(p)
                pickle.dump(ori, f)

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
        """
        :param cur_fail_times: 内部递归使用，调用该函数时不应设置该项值
        :param code_check_info: 内部递归使用，调用该函数时不应设置该项值
        :return: 返回 RES 类, code有 5 个值：
        -2 表示代码结构可能有问题
        -1 表示无法获取页面，即 data 项为 None
        0 表示无验证码且页面没有明确信息表示没有查找到相应航班，
        1 表示有验证码但最后获取到了航班信息
        2 表示页面明确信息提示没有查找到相应航班
        """
        try:
            ori_html = self.session.get(query_url, headers = headers, timeout = 5)
        except Exception as e:
            self.logger.error("获取 url 为 %s 时出现错误，已返回空字典，错误原因为 %s" % (query_url, e))
            return RES(-1,"获取url出错",None)
        if ori_html.status_code != 200:
            self.logger.error("获取到的 url 为 %s 的网页响应状态码有误：%s" % (query_url, ori_html.status_code))
            return RES(-1,"网页响应状态码有误",None)
        if '抱歉，没有找到您输入的航班信息' in ori_html.text:
            code_show_info = re.search(r"\('.authCodeBox'\).(.{4})\(\)", ori_html.text)
            # 正常访问的话这一项是空的，需要输入验证码时这一项的值为 "show"，输入验证码正确时这一项的值为 "hide"
            if not code_show_info or code_show_info.group(1) == "hide":
                # 说明是真的没有这趟航班.
                return RES(2,"没有查找到相应的航班",None)
            elif code_show_info.group(1) == "show":
                # 说明需要输入验证码
                if code_check_info and not code_check_info[0]:
                    # 说明验证码输入错误，需进行退款
                    self.auth_rec_module.refund(code_check_info[1])
                    self.logger.error("上一次验证码输入错误，已发起退款")
                self.logger.warning("有验证码出现，查询结果获取失败！%s" % query_url)
                if cur_fail_times < 3:
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
                        return RES(-1,"验证码识别出现问题",None)
                else:
                    self.logger.critical("多次尝试验证码获取网页失败！不再进行尝试！")
                    return RES(-1,"多次尝试验证码获取网页失败",None)
            else:
                self.logger.critical("code_show_info 信息错误:%s！url:%s,请检查代码结构！"%(code_show_info,query_url))
                return RES(-2,"code_show_info 信息错误",None)
        if cur_fail_times > 0:
            return RES(1,"有验证码出现！",ori_html)
        else:
            return RES(0,"ok",ori_html)

    def _get_img(self, arg_tuple):
        # 获取图片，并把图片推进图片识别队列
        # 参数有四个，使用时请严格按照以下顺序：imgurl, img_path, rec_it, img_type
        # 正常情况下不返回结果，只更新self.img_rec_result_dic字典
        imgurl = arg_tuple[0]
        img_path = arg_tuple[1]
        rec_it = arg_tuple[2]
        img_type = arg_tuple[3]
        img_name = re.search(r"/([^/]+\.png)", img_path).group(1)
        if img_name not in self.local_imgs or img_type == 32:
            # 本地没有这张图片
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
                self.logger.warning("图片路径为: %s" % img_path)
                self.logger.warning("图片 url 为：%s" % imgurl)
                self.logger.warning("获取到的内容为：%s" % img.text)
                self.img_rec_result_dic.update({img_path: '--'})
        if rec_it:
            # 若识别
            result = self.local_img_rec_results.get(img_path)
            if result not in (None, '--') and img_type != 32:
                self.img_rec_result_dic.update({img_path: result})
                return
            else:
                self.img_rec_mission_queue.put((img_path, img_type))

    def _wait_thread(self, fun_type=1):
        self.logger.debug("[%d]页面解析完成，等待图片下载任务下发完成..." % fun_type)
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

    def init_args(self):
        self.headers = Headers()
        self.session = requests.session()
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize = 30))
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize = 30))
        self.local_imgs = os.listdir(ORI_IMG_PATH)
        self.img_503_error_total = 0
        self.img_rec_result_dic.clear()
        self.img_rec_result_dic.update({"init_key":"init_value"})
        self.down_img_thread_list.clear()
        self.img_down_mission_assign_finished = False

    def _get_base_info(self, query_url, with_img):
        """
        :param query_url:
        :param with_img: 默认为 True，表示获取图片信息
        :return: 返回 RES 对象，code 有 3 种，
        0 表示一切正常
        1 表示正确返回了结果但过程中有验证码出现
        11 表示正确返回了结果但有些图片出现了 503 错误
        2 表示查找航班无结果
        -1 表示由于种种原因无法获取正确结果
        """
        # ------ 准备工作 -----#
        flight_infos = []
        query_date = re.search(r"fdate=(\d{8})",query_url).group(1)
        ori_html = self._get_page(query_url, self.headers.get_headers(1))
        if ori_html.code == 2:
            return RES(2,"没有查找到航班！",flight_infos)
        elif ori_html.code in (-2,-1):
            return RES(-1,"无法获取页面",flight_infos)
        #---- 开工 ----#
        query_result = re.findall(r'<li style="position: relative;">.+?</li>', ori_html.data.text, re.S)
        # 各个航班信息的html代码块文本组成的列表，每个元素是一个航班的代码块
        if not query_result:
            self.logger.critical("获取到的航班列表为空但没有提示信息，似乎拿到的网页不对？？？")
            self.logger.warning(ori_html.data.text)
            return RES(-1,"网页信息似乎有误",flight_infos)
        # 是否颠倒图片
        reverse_info = re.search(r"b\((\d,\d)\);", ori_html.data.text).group(1)
        reverse_pic = True if reverse_info == "2,1" else False
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
            shared_flight = sub_html.xpath('//li[@style="position: relative;"]/a[@class="list_share"]/@title')
            try:
                shared_flight = re.search(r"[A-Za-z0-9]+",shared_flight[0]).group(0) if shared_flight else '--'
            except AttributeError:
                shared_flight = "--"
            dep_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@dplan')[0]
            local_dep_date_plan = sub_html.xpath(
                '//div[@class="li_com"]/span[@class="w150" and contains(@dplan,":")]/em/text()')
            local_dep_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][1]/em/text()')
            dep_airp_name = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][2]/text()')[0]
            arri_time_plan = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"]/@aplan')[0]
            local_arri_date_plan = sub_html.xpath(
                '//div[@class="li_com"]/span[@class="w150" and contains(@aplan,":")]/em/text()')
            local_arri_date_act = sub_html.xpath('//div[@class="li_com"]/span[@class="w150 randEle"][2]/em/text()')
            arri_airp_name = sub_html.xpath('//div[@class="li_com"]/span[@class="w150"][4]/text()')[0]
            flight_status = sub_html.xpath('//div[@class="li_com"]/span[contains(@class,"_cor")]/text()')[0]
            # 航班状态，目前已遇到的状态有起飞、到达、取消、提前取消、催促登机、登机结束、正在登机、延误预警、延误
            ontime_rate = '--'
            dep_time_act = '--'
            arri_time_act = '--'
            # ---- 再获取图片信息 ---- #
            if with_img:
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
                g = ["--"]*3
                for sub_index,item in enumerate(("dep_time_act","arri_time_act","ontime_rate")):
                    item_path = ORI_IMG_PATH+"%s_%s_%s-%s_%s.png" % (
                        item, flight_code, dep_airp_code, arri_airp_code, query_date)
                    item_url = eval("%s_imgurl"%item)
                    if item_url:
                        g[sub_index] = item_path
                        img_type = sub_index//2 + 1
                        self.img_down_mission_queue.put((item_url, item_path, True, img_type))
                dep_time_act, arri_time_act, ontime_rate = g
            flight_infos.append(dict(flight_code = flight_code,
                                     flight_date = query_date,
                                     dep_airp_code = dep_airp_code,
                                     arri_airp_code = arri_airp_code,
                                     corp_name = corp_name,
                                     shared_flight = shared_flight,
                                     dep_airp_name = dep_airp_name,
                                     dep_time_plan = dep_time_plan,
                                     dep_time_act = dep_time_act,
                                     local_dep_date_plan = local_dep_date_plan[0] if local_dep_date_plan else '--',
                                     local_dep_date_act = local_dep_date_act[0] if local_dep_date_act else '--',
                                     arri_airp_name = arri_airp_name,
                                     arri_time_plan = arri_time_plan,
                                     arri_time_act = arri_time_act,
                                     local_arri_date_plan = local_arri_date_plan[0] if local_arri_date_plan else '--',
                                     local_arri_date_act = local_arri_date_act[0] if local_arri_date_act else '--',
                                     ontime_rate = ontime_rate,
                                     flight_status = flight_status
                                     ))
        # ---- 获取识别结果 ---- #
        if with_img:
            self._wait_thread()
            threading.Thread(target = self._update_local_img_rec_results).start()
            for flight_info in flight_infos:
                for item in ('dep_time_act', 'arri_time_act', 'ontime_rate'):
                    if flight_info[item] != '--':
                        try:
                            flight_info[item] = self.img_rec_result_dic[flight_info[item]]
                        except KeyError:
                            self.logger.critical("获取图片结果失败！,图片路径为：%s" % flight_info[item])
                            flight_info[item] = '--'
                if flight_info["ontime_rate"] != "--":
                    flight_info["ontime_rate"] = float(flight_info["ontime_rate"][:-1])*0.01
            self.img_rec_result_dic.clear()
        code = ori_html.code
        if self.img_503_error_total > 0:
            code = 11
        return RES(code,"ok",flight_infos)

    def _get_detailed_info(self, query_url, with_img):
        """
        :param query_url: 本次查询的 url
        :param with_img:
        :return: 返回 RES 类，code 有 3 种，
        0 表示一切正常
        1 表示正确返回了结果但有验证码出现
        2 表示查找航班无结果
        -1 表示无法返回正确结果
        """
        #---- 准备工作 ----#
        tem = re.search(r"([A-Z]{3})-([A-Z]{3})-([A-Z0-9]+)\..+?fdate=(\d{8})", query_url)
        dep_airp_code, arri_airp_code, flight_code, query_date = tem.group(1), tem.group(2), tem.group(3), tem.group(4)
        ori_html = self._get_page(query_url, self.headers.get_headers(1))
        if ori_html.code in (-1,-2):
            return RES(-1,"无法获取页面",{})
        elif ori_html.code == 2:
            return RES(2,"查找航班无结果",{})
        if "IP blocked" in ori_html.data.text:
            self.logger.critical("获取详细信息时直接被封ip！%s" % ori_html.data.text)
            return RES(-1,"获取详细信息时直接被封ip！",{})
        # ---- 先获取文本信息 ---- #
        html = etree.HTML(ori_html.data.text)
        try:
            corp_name_and_flight_code = html.xpath('//div[@class="tit"]/span/b/text()')[0].strip()
        except AttributeError:
            self.logger.warning("似乎拿到的网页不对？？？")
            return RES(-1,"似乎拿到的网页不对",{})
        corp_name = corp_name_and_flight_code.replace(flight_code, "").strip()
        flight_status = html.xpath('//div[@class="tit"]/div[@class="state"]/div/text()')[0]
        shared_flight = re.search(r">实际承运(.+?)<",ori_html.data.text)
        shared_flight = shared_flight.group(1) if shared_flight else "--"
        dep_city, arri_city = html.xpath(
            '//div[@class="flyProc"]/div[@id="p_box"]/div[@class="cir_l curr" or @class = "cir_r"]/span/text()')
        flight_distance, flight_dur_time = html.xpath(
            '//div[@class="flyProc"]/div[@id="p_box"]/div[@class="p_ti"]/span/text()')
        try:
            flight_distance = int(re.search(r"\d+",flight_distance).group(0))
        except (AttributeError,ValueError):
            flight_distance = "--"
        plane_type = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="mileage"]/span/text()')[0]
        plane_age = html.xpath('//div[@class="flyProc"]/div[@class="p_info"]/ul/li[@class="time"]/span/text()')[0]
        try:
            plane_age = float(plane_age[:-1])
        except ValueError:
            plane_age = "--"
        delay_time_tip = html.xpath('//div[@class="flyProc"]//li[@class="age"]/span/text()')
        delay_time_tip = delay_time_tip[0] if delay_time_tip else '--'
        pre_flight = html.xpath('//div[@class="old_state"]/text()')[0]
        ave_ontime_rate = '--'
        # ---- 历史平均准点率 ---- #
        if with_img:
            threading.Thread(target = self._start_get_imgs).start()
            self.img_down_mission_assign_finished = False
            ave_ontime_rate_imgurl = self.base_url+html.xpath('//div[@class="flyProc"]//li[@class="per"]//img/@src')[
                0].strip()
            ave_ontime_rate_imgpath = ORI_IMG_PATH+"ave_ontime_rate_%s_%s-%s_%s.png" % (flight_code, dep_airp_code, arri_airp_code, query_date)
            self.img_down_mission_queue.put((ave_ontime_rate_imgurl, ave_ontime_rate_imgpath, True, 31))
            ave_ontime_rate = ave_ontime_rate_imgpath
        # ---- 机场信息 ---- #
        # 航班涉及到的机场数量，有经停时为 3 ，无经停时为 2
        involved_airp_total = len(html.xpath('//div[contains(@class,"fly_mian")]'))

        # ----  图片对应信息  ---- #
        order1 = json.loads('[%s]' % re.search(r"func\('rand_ul_dep', (\d,\d,\d)\);", ori_html.data.text).group(1))
        order2 = json.loads('[%s]' % re.search(r"func\('rand_ul_arr', (\d,\d,\d)\);", ori_html.data.text).group(1))
        order3 = json.loads('[%s]' % re.search(r"midFunc\((\d,\d,\d,\d,\d,\d)\);", ori_html.data.text).group(1)) if involved_airp_total == 3 else None

        # ----  获取机场信息  ---- #
        airp_weathers = html.xpath('//div[contains(@class,"fly_mian")]/ul/li[@class="weather"]/p/text()')
        li_class_list = ['time', 'inspect', 'entrance']
        # 出发机场
        dep_airp_name = html.xpath('//div[@class="fly_mian"][position()=1]/div[@class="f_title f_title_a"]/h2/@title')[0]
        d_item_imgurl_inorder = [None, None, None]
        d_item_values = ["--"]*10   # 对应 key_names 里边的键值
        d_item_name_inorder = [None, "值机柜台", "登机口"]
        d_item_name_inorder[0] = html.xpath('//div[@class="fly_mian"][position()=1]/ul/li[@class="time"]/p[@class="gray_t"]/text()')[0]
        d_item_keynames = ["dep_time_pred","local_dep_date_plan","checkin_counter","dep_gate","dep_airp_weather","dep_airp_pm25","dep_airp_flow","dep_time_plan","dep_time_act", "local_dep_date_act"]
        if d_item_name_inorder[0] == "实际起飞":
            d_item_keynames[:2], d_item_keynames[-2:] = d_item_keynames[-2:], d_item_keynames[:2]
        d_item_values[-3] = html.xpath('//div[@class="tit"]/span/input[@id="depTime"]/@value')[0] # 计划出发时间
        c = html.xpath('//div[@class="fly_mian"][position()=1]/ul/li[@class="time"]/p[@class="com"]/em/text()')[0].strip() # 当地时间
        d_item_values[1] = c if c else "--"
        for i in range(3):
            url = html.xpath('//div[@class="fly_mian"][position()=1]/ul/li[@class="%s"]/p[@class="com rand_p"]/img/@src'%li_class_list[i%3])
            url = self.base_url + url[0] if url else None
            d_item_imgurl_inorder[order1[i]-1] = url
        # 到达机场
        arri_airp_name = html.xpath('//div[@class="fly_mian"][position()=last()]/div[@class="f_title f_title_c"]/h2/@title')[0]
        a_item_imgurl_inorder = [None, None, None]
        a_item_values = ["--"] * 10
        a_item_name_inorder = [None, "行李转盘", "到达口"]
        a_item_name_inorder[0] = html.xpath('//div[@class="fly_mian"][position()=last()]/ul/li[@class="time"]/p[@class="gray_t"]/text()')[0]
        a_item_keynames = ["arri_time_pred","local_arri_date_plan","lug_turn","arri_gate","arri_airp_weather","arri_airp_pm25","arri_airp_flow","arri_time_plan","arri_time_act","local_arri_date_act"]
        if a_item_name_inorder[0] == "实际到达":
            a_item_keynames[:2], a_item_keynames[-2:] = a_item_keynames[-2:], a_item_keynames[:2]
        a_item_values[-3] = html.xpath('//div[@class="tit"]/span/input[@id="arrTime"]/@value')[0] # 计划到达时间
        c = html.xpath('//div[@class="fly_mian"][position()=last()]/ul/li[@class="time"]/p[@class="com"]/em/text()')[0].strip() # 当地时间
        a_item_values[1] = c if c else "--"
        for i in range(3):
            url = html.xpath('//div[@class="fly_mian"][position()=last()]/ul/li[@class="%s"]/p[@class="com rand_p"]/img/@src'%li_class_list[i%3])
            url = self.base_url + url[0] if url else None
            a_item_imgurl_inorder[order2[i]-1] = url
        # 经停机场
        mid_airp_name = "--"
        m_item_values = ["--"] * 17
        m_item_keynames = ["mid_airp_arri_time_pred","local_mid_airp_arri_date_plan","mid_airp_lug_turn","mid_airp_arri_gate","mid_airp_dep_time_pred","local_mid_airp_dep_date_plan","mid_airp_checkin_counter","mid_airp_dep_gate","mid_airp_weather","mid_airp_pm25","mid_airp_flow","mid_airp_dep_time_plan","mid_airp_arri_time_plan","mid_airp_dep_time_act","local_mid_airp_dep_date_act","mid_airp_arri_time_act","local_mid_airp_arri_date_act"]
        if involved_airp_total == 3:
            mid_airp_name = html.xpath('//div[@class="fly_mian rand_mid_div"]/div[@class="f_title f_title_b"]/h2/@title')[0]
            m_item_imgurl_inorder = [None, None, None, None, None, None]
            m_item_name_inorder = [None, "行李转盘", "到达口", None, "值机柜台", "登机口"]
            m_item_name_inorder[0] = html.xpath('//div[@class="fly_mian rand_mid_div"]/ul[position()=1]/li[@class="time"]/p[@class="gray_t"]/text()')[0]
            m_item_name_inorder[3] = html.xpath('//div[@class="fly_mian rand_mid_div"]/ul[position()=2]/li[@class="time"]/p[@class="gray_t"]/text()')[0]
            if m_item_name_inorder[0] == "实际到达":
                m_item_keynames[:2], m_item_keynames[-2:] = m_item_keynames[-2:], m_item_keynames[:2]
            if m_item_name_inorder[3] == "实际起飞":
                m_item_keynames[4:6], m_item_keynames[-4:-2] = m_item_keynames[-4:-2], m_item_keynames[4:6]
            c1 =  html.xpath('//div[@class="fly_mian rand_mid_div"]/ul[position()=1]/li[@class="time"]/p[@class="com"]/em/text()')
            c2 =  html.xpath('//div[@class="fly_mian rand_mid_div"]/ul[position()=2]/li[@class="time"]/p[@class="com"]/em/text()')
            m_item_values[1] = c1[0] if c1 else "--"
            m_item_values[5] = c2[0] if c2 else "--"
            for i in range(6):
                url = html.xpath('//div[@class="fly_mian rand_mid_div"]/ul[position()=%d]/li[@class="%s"]/p[@class="com rand_p"]/img/@src'%(i//3+1,li_class_list[i%3]))
                url = self.base_url + url[0] if url else None
                m_item_imgurl_inorder[order3[i]-1] = url

        k = (("d",3),("m",6),("a",3)) if involved_airp_total == 3 else (("d",3),("a",3))
        indexs = {"d":(0,2,3),"m":(0,2,3,4,6,7),"a":(0,2,3)}
        # ---- 往图片任务队列中推送任务 ---- #
        for index,airp in enumerate(k):
            airp = airp[0]
            h = eval("%s_item_values"%airp)
            if with_img:
                for seq,pos in enumerate(indexs[airp]):
                    url = eval("%s_item_imgurl_inorder"%airp)[seq]
                    if url:
                        img_path = ORI_IMG_PATH + "%s_%s_%s-%s_%s.png"%(eval("%s_item_keynames"%airp)[pos],flight_code,dep_airp_code,arri_airp_code,query_date)
                        if "time" in eval("%s_item_keynames"%airp)[pos]:
                            self.img_down_mission_queue.put((url,img_path,True,32))
                        else:
                            self.img_down_mission_queue.put((url,img_path,True,33))
                        h[pos] = img_path
                    else:
                        h[pos] = "--"
            wea_start_at = indexs[airp][-1] + 1
            if datetime.date.today().__str__().replace("-","") > query_date:
                h[wea_start_at:wea_start_at+3] = ["--",'--','--']
            else:
                tem = airp_weathers[3*index:3*index+3]
                tem[0] = tem[0].replace("\t","")
                try:
                    tem[1] = int(tem[1][6:])
                except (IndexError,ValueError):
                    tem[1] = '--'
                h[wea_start_at:wea_start_at+3] = tem
        #---- 获取识别结果 ----#
        if with_img:
            self._wait_thread(2)
            # 获取图片内容
            threading.Thread(target = self._update_local_img_rec_results).start()
            ave_ontime_rate = self.img_rec_result_dic.get(ave_ontime_rate)
            if not ave_ontime_rate:
                ave_ontime_rate = '--'
            else:
                try:
                    ave_ontime_rate = float(ave_ontime_rate[:-1]) * 0.01
                except ValueError:
                    ave_ontime_rate = "--"
            for airp,num in k:
                h = eval("%s_item_values"%airp)
                for i in indexs[airp]:
                    if h[i] != "--":
                        try:
                            h[i] = self.img_rec_result_dic.pop(h[i])
                        except KeyError:
                            self.logger.critical("获取图片结果失败！,图片路径为：%s" % h[i])
                            myPrint(self.img_rec_result_dic)
            self.img_rec_result_dic.clear()

        to_return = dict(flight_code = flight_code,
                    flight_date = query_date,
                    dep_airp_code = dep_airp_code,
                    arri_airp_code = arri_airp_code,
                    corp_name = corp_name,
                    shared_flight = shared_flight,
                    dep_city = dep_city,
                    arri_city = arri_city,
                    flight_status = flight_status,
                    flight_distance = flight_distance,
                    flight_dur_time = flight_dur_time,
                    plane_type = plane_type,
                    plane_age = plane_age,
                    ave_ontime_rate = ave_ontime_rate,
                    delay_time_tip = delay_time_tip,
                    pre_flight = pre_flight,
                    dep_airp_name = dep_airp_name,
                    arri_airp_name = arri_airp_name,
                    mid_airp_name = mid_airp_name)
        for airp in ("d","m","a"):
            dic = dict(zip(eval("%s_item_keynames"%airp),eval("%s_item_values"%airp)))
            to_return.update(dic)
        return RES(ori_html.code,"ok!",to_return)

    def get_detailed_info(self, *args, with_img=True, return_type=0):
        """
        :param args: 若为一个参数，则该参数是给定的 url,
            若按航班号查询，共需要四个参数，第一、第二个分别为出发机场代码，目的地机场代码，第三个是航班号，第四个是日期
        :param with_img:
        :param return_type: 0 表示返回旧的数据格式的数据信息，1 表示只返回新的格式的数据信息，2 表示返回完整信息
        :return: 返回旧的格式数据
        """
        self.logger.info("查询详细信息，查询条件：%s" % (args,))
        self.init_args()
        query_url = self.detailed_info_baseurl % (args[0].upper(), args[1].upper(), args[2], args[3]) if len(args) > 1 else args[0]
        if 'fdate' not in query_url:
            query_url += '&fdate=%s' % str(datetime.date.today()).replace('-', '')
        p = self._get_detailed_info(query_url,with_img)
        if not p.code == 0:
            self.logger.info("查询条件：%s, 查询信息：code:%d,message:%s"%((args,),p.code,p.message))
        if return_type == 0:
            return n2o(p.data,2)
        elif return_type == 1:
            return p.data
        else:
            return p

    def get_base_info(self, *args, with_img=True, return_type=0):
        """
        :param args:
        开发时可以直接按 url 查询，直接传入 url 即可
        若按航班号查询，args的格式应为(flightcode, query_date)
        若按路线查询，args的格式应为(depart_air_code, arrive_air_code, query_date)
        :param with_img:
        :param return_type: 0 表示返回旧的数据格式的数据信息，1 表示只返回新的格式的数据信息，2 表示返回完整信息
        :return:
        """
        self.init_args()
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
        if 'fdate' not in query_url:
            query_url += '&fdate=%s' % str(datetime.date.today()).replace('-', '')
        self.logger.info("查询基本信息，查询条件：%s" % (args,))
        p = self._get_base_info(query_url,with_img)
        if not p.code == 0:
            self.logger.info("查询条件：%s, 查询信息：code:%d, message:%s"%((args,),p.code,p.message))
        if return_type == 0:
            return n2o(p.data,1)
        elif return_type == 1:
            return p.data
        else:
            return p

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
        if "抱歉，此类查询已达当日上限" in ori_html.data.text:
            self.logger.error("[3]抱歉，此类查询已达当日上限!")
            return dict()
        html = etree.HTML(ori_html.data.text)
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

    def get_all(self,flight_code,flight_date):
        query_url = self.query_by_flightcode_baseurl % (flight_code, flight_date)
        page = self._get_page(query_url,self.headers.get_headers(1))
        if not page.code in (0,1):
            return []
        infos = re.findall(r"href=\"/schedule/([A-Z]{3})-([A-Z]{3})-([A-Z0-9]+?)\.html",page.data.text)
        to_return = []
        for a,b,c in infos:
            detail = self.get_detailed_info(a, b, c, flight_date,return_type=1)
            to_return.append(detail)
            myPrint(to_return)
        return to_return


if __name__ == '__main__':
    pass
    start = time.time()
    pp = Spider().get_base_info("PEK",'SHA', '20190602', with_img=True,return_type = 0)
    myPrint(pp)
    print("总用时:",time.time()-start)
    # myPrint(Spider().get_base_info("BJS",'SHH', '20190519', with_img=True,return_type = 2))
    # myPrint(Spider().get_base_info('111','20190602', with_img = True))
    # myPrint(Spider().get_base_info('CZ3147', '20190520', with_img = True))
    # myPrint(Spider().get_all('3147', '20190517'))
    # myPrint(Spider().get_all('ca1234', '20190602'))
    # myPrint(Spider().get_detailed_info("http://www.variflight.com/schedule/YIN-PEK-CA1234.html?AE71649A58c77&fdate=20190602"))
    # myPrint(Spider().get_detailed_info("BHY", "PEK", "CZ3147", '20190525',with_img = True,return_type=1))
    # myPrint(Spider().get_detailed_info('PEK','ARN','CA911','20190512',with_img=False))
    # myPrint(Spider().get_confort_info('http://happiness.variflight.com/search/airline?date=2019-04-04&dep=PEK&arr=CTU&type=1'))
    # myPrint(Spider().get_confort_info('CZ3147', 'PEK', 'SHA', '2019-04-23'))


