# -*- coding: utf-8 -*-
import re
import requests
import spider
import database
import pickle
import time
import random
import threading
from queue import Queue
from datetime import date
from .myPrint import *

class Save2db(object):
    def __init__(self):
        self.url = "http://www.variflight.com/sitemap/flight?AE71649A58c77="
        self.datebase = database.Database()
        self.mission_put_finished = False
        self.mission_queue = Queue()
        self.lock = threading.Lock()
        self.auth_code_appear = False

    def get_all_d2as(self):
        p = requests.get(self.url)
        flight_codes = re.findall(r"href=\"/flight/(.{3})-(.{3})\.html\?AE71649A58c77=",p.text)
        return flight_codes

    def get_and_save_one(self,worker_id=1):
        """
        多线程获取基本信息时的消费者函数
        :param worker_id: 顾名思义
        :return: 不return，只把数据存数据库
        """
        if self.auth_code_appear:
            time.sleep(18*60)
        while not self.mission_put_finished or not self.mission_queue.empty():
            mission = self.mission_queue.get()
            print("工人 %d 执行任务：%s"%(worker_id,mission))
            flight_info = spider.Spider().get_base_info(
                mission[0],mission[1],mission[2],with_img = mission[3],return_type = mission[4])
            if flight_info.code in (0,1,11):
                if self.lock.acquire():
                    self.datebase.add(1,flight_info.data)
                    if len(flight_info.data) > 1:
                        for item in flight_info.data:
                            fly = {"flight_code":item["flight_code"],
                                    "flight_date":item["flight_date"],
                                    "dep_airp_code":item["dep_airp_code"],
                                    "arri_airp_code":item["arri_airp_code"]
                                    }
                            self.datebase.add(2,fly)
                    self.lock.release()
                if flight_info.code == 1:
                    print("\n\n\n\n\n有验证码出现，休息 18 分钟！\n\n\n\n\n")
                    self.auth_code_appear = True
            if flight_info.code in (11,-1):
                self.mission_queue.put(mission)
            print("工人 %d 结束任务：%s"%(worker_id,mission))
            self.mission_queue.task_done()
        print("------工人 %d 结束所有任务！------"%worker_id)

    def save_all_base_info(self,max_ths=50,flight_date=None):
        """
        获取所有航班的基本信息，不包括实际时间和准点率，由于百度限制 qps的原因，with_img 必须为False，否则会出现大面积的图片识别失败
        :param max_ths: 最大线程数
        :param flight_date:
        :return:
        """
        # 获取所有国内航班的信息
        start = time.time()
        for i in range(max_ths):
            threading.Thread(target = self.get_and_save_one,args = (i+1,)).start()
        if not flight_date:
            flight_date = "20190528"#str(date.today()).replace("-","")
        d2as = self.get_all_d2as()
        for dep,arri in d2as:
            if dep in ("PEK","NAY"):
                dep = "BJS"
            elif dep in ("SHA","PVG"):
                dep = "SHH"
            if arri in ("PEK","NAY"):
                arri = "BJS"
            elif arri in ("SHA","PVG"):
                arri = "SHH"
            self.mission_queue.put((dep,arri,flight_date,False,2))
        print("任务入队完毕！")
        self.mission_put_finished = True
        self.mission_queue.join()
        print("queue has joined!!!")
        print("总用时: %.3f s"%(time.time()-start))

    def save_a_detailed_info(self,dep,arri,flight_code,flight_date):
        info = spider.Spider().get_detailed_info(dep,arri,flight_code,flight_date,with_img = True,return_type = 2)
        if info.code in (0,1):
            self.datebase.add(1,info.data)

if __name__ == "__main__":
    Save2db().save_all_base_info()
    Save2db().save_all_base_info(flight_date = "20190529")