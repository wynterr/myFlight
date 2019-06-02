# -*- coding: utf-8 -*-
# @Author: 毅梅傲雪
# @Date:   2019-04-18 12:01:01
# @Last Modified by:   毅梅傲雪
# @Last Modified time: 2019-05-06 18:59:30
import os
import re
import time
import random
import threading
import logging
import pytesseract
import datetime
from math import ceil
from aip import AipOcr
from PIL import Image
from .myPrint import myPrint
from .__init__ import *
from .my_ocr import my_ocr

'''
图片大小：
出发、到达实际时间的图片像素大小为： 50x28
准点率的图片像素大小为： 63x28
详细信息中，时间图片的像素大小为 80x40
其他信息的像素图片大小为 280x40 或者 80x40

图片类型：
1. 基本信息里的出发、到达实际时间
2. 基本信息里的准点率的图片
3. 泛指所有 3x 类图片
31. 详细信息里的准点率图片
32. 详细信息里的时间图片
33. 详细信息里的其他图片
'''


class Rec_pic(object):
    def __init__(self):
        super(Rec_pic, self).__init__()
        # ---- ocr初始化 ----#    
        APP_ID = '15943518'
        API_KEY = 'T2icUbUcTgiv6GGUucZvbyMv'
        SECRET_KEY = 'ir5gXsiLtFZ4VGEZ5kq87EEyBFkpRxyk'
        self.aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

        # ---- 参数初始化 ----#
        self.new_img_will_come = True
        self.rec_finished = False
        self.rec_img_thread_list = []
        self.local_rec_result = {}
        # ---- 日志设置 ----#
        self.logger = logging.getLogger("Rec_pic")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            logfile = logging.FileHandler(LOG_PATH+"rec_run_log.log")
            console = logging.StreamHandler()
            file_formatter = logging.Formatter(
                '[%(levelname)-8s] %(asctime)s %(filename)s[line:%(lineno)d](%(funcName)s) %(message)s')
            console_formatter = logging.Formatter(
                '[%(levelname)-8s]%(filename)s[line:%(lineno)d](%(funcName)s) %(message)s')
            logfile.setFormatter(file_formatter)
            console.setFormatter(console_formatter)
            logfile.setLevel(logging.INFO)
            console.setLevel(logging.WARNING)
            self.logger.addHandler(logfile)
            self.logger.addHandler(console)
        self.remove_superfluous_handlers()

    def remove_superfluous_handlers(self):
        if len(self.logger.handlers) > 2:
            print("remove_superfluous_handlers!")
            had = []
            for item in self.logger.handlers:
                if type(item) not in had:
                    had.append(type(item))
                else:
                    self.logger.removeHandler(item)

    def inform_pic_finished(self):
        self.new_img_will_come = False

    def init_args(self):
        self.new_img_will_come = True
        self.rec_finished = False
        self.rec_img_thread_list.clear()
        self.local_rec_result.clear()
        
    @staticmethod
    def double(img_path):
        # 对于无法识别的单字符图片，将字符区域复制，命名为 new_+原名 并保存
        img = Image.open(img_path)
        width = img.size[0]
        height = img.size[1]
        # print(help(Image.new))
        target = Image.new('RGB', (width+20, height), color = "white")
        valid_area = img.crop((width / 2-20, 0, width / 2+20, height))
        pos_tuple = (int(width / 2+10), 0)
        target.paste(img, (0, 0))
        target.paste(valid_area, pos_tuple)
        target.save(img_path[:-4]+"_new"+img_path[-4:])
        return target

    def local_rec(self, item, img_type, use_baidu=True):
        """
        实际上是专门识别第 3 类图片，每次识别一张，懒得改函数名了
        对于 31、32 类图片，对每个识别结果进行判断，判断正确再选用
        对于 33 类图片，择优规则暂定为优先使用百度识别结果，本地识别结果更长时采用本地结果
        不返回结果，只更新字典 self.local_rec_result
        """
        if use_baidu:
            # use_baidu 保证为每个item创建字典键值，识别失败或结果验证失败时值为 "--"
            path, result = self.in_rec([item], 3)
            try:
                result = result["words_result"][0]["words"]
            except (IndexError,KeyError):
                result = ""
            if not result:
                self.logger.warning("百度识别图片 %s 结果为空，尝试本地 double 识别..." % item)
                result = pytesseract.image_to_string(self.double(item))
                result = result.replace(" ", "")
                if len(result) != 2 or result[0] != result[1]:
                    self.logger.error("本地 double 识别图片 %s 失败！识别结果：%s" % (item, result))
                    self.local_rec_result.update({item: "--"})
                else:
                    self.logger.warning("本地 double 识别图片 %s 成功！识别结果：%s" % (item, result[0]))
                    self.local_rec_result.update({item: result[0]})
            else:
                if img_type in (31,32):
                    result = self.check(item,1,result,img_type)
                    if not result:
                        result = "--"
                self.local_rec_result.update({item: result})
        else:
            # 这个分支起辅助作用，对字典中结果为 "--" 的项进行本地尝试修正，对 33 类图片进行择优录用
            result = pytesseract.image_to_string(Image.open(item))
            if not result:
                self.logger.warning("本地识别图片 %s 结果为空！识别结果：%s" % (item, result))
                return 
            else:
                if img_type in (31,32):
                    result = self.check(item,1,result,img_type)
                    if not result:
                        return 
                while not self.local_rec_result.get(item):
                    time.sleep(0.1)
                p = self.local_rec_result.get(item)
                # print("baidu:%-10s, local:%s"%(p,result))
                if p == "--":
                    self.logger.info("图片 %s 本地结果更优！百度：%s，本地: %s"%(item,p,result))
                    self.local_rec_result.update({item: result})
                if img_type == 33 and len(result) > len(p):
                    self.logger.info("图片 %s 本地结果更优！百度：%s，本地: %s"%(item,p,result))
                    self.local_rec_result.update({item: result})

    def rec_3(self, item, img_type):
        # 每张图片使用本地和百度双重识别
        t1 = threading.Thread(target = self.local_rec, args = (item, img_type, True))
        t1.start()
        t2 = threading.Thread(target = self.local_rec, args = (item, img_type, False))
        t2.start()
        t1.join()
        t2.join()
        return self.local_rec_result

    @staticmethod
    def combine(img_path_list, img_type):
        # 拼接列表中的图片
        # 返回拼接图片的路径
        img_open_list = [Image.open(x) for x in img_path_list]
        img_total = len(img_open_list)
        if img_type in (1,2):
            # 基础信息里的图片尽量排列方正
            img_col = int(pow(img_total, 0.5))
        else:
            img_col = 1
        img_row = ceil(img_total / img_col)
        img_size = img_open_list[0].size
        img_height = img_size[1]
        img_width = img_size[0]
        if img_type in (1, 2):
            target = Image.new('RGB', (16+(img_width+15) * img_col, 16+(img_height+8) * img_row), color = "white")
        else:
            target = Image.new('RGB', (16+280, 16+48 * img_row), color = "white")
        for index, img in enumerate(img_open_list):
            if img_type in (1, 2):
                pos_tuple = (16+index % img_col * (img_width+15), 8+index // img_col * (img_height+8))
            else:
                pos_tuple = (16, 8+index // img_col * (img_height+8))
            target.paste(img, pos_tuple)  # print("位置：",pos_tuple)
        img_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")+'.jpg'
        img_path = COMBINED_IMG_PATH+img_name
        target.save(img_path)
        return img_path

    def check(self, img_path, img_total, result, img_type):
        # 检验识别结果是否正确，正确则返回修正后的结果
        if not result:
            return False
        
        if img_type == 1:
            """
            说明这是基础信息里的实际时间图片
            先把各行结果合并为一个字符串，去掉 : ，留下纯数字
            然后对识别结果长度进行判断，若位数不是 4 的倍数则认定为是识别漏掉了数字，返回False
            最后对四位数字的元素个数进行判断，若等于 img_total，则认定为本行合格，否则认定不合格，返回False
            合格则重新格式化数字并返回列表
            """
            result = result["words_result"]
            rec_result = ""
            for rec_row in result:
                rec_result += rec_row["words"]
            rec_result = rec_result.replace(":","")
            if not len(rec_result) % 4 == 0:
                self.logger.warning("识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果总长度不是4的倍数，处理后的识别结果：%s，识别结果行原文：%s" % (
                    img_type, img_path, rec_result, result))
                return False
            else:
                revised_rec_result = []
                for i in range(len(rec_result) // 4):
                    tem = rec_result[i*4:i*4 + 4]
                    revised_rec_result.append("%s:%s" % (tem[:2], tem[2:]))
                if len(revised_rec_result) != img_total:
                    self.logger.warning("识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果数目与图片数目不相符，修订后的识别结果：%s，识别结果行原文：%s" % (
                    img_type, img_path, revised_rec_result, result))
                    return False
                return revised_rec_result
        elif img_type == 2:
            """
            说明这是基础信息里的准点率图片
            这种图片由于有 0% 和 100% 这种数字的出现，不能简单地以每个数字的位数来判断
            判断方法如下：
            先把各行识别结果合并成一个字符串，
            再进行替换，%0% 替换为 %0000%，%100%替换成 %1000%，去掉 . 和 %，留下纯数字
            然后对识别结果长度进行判断，若位数不是 4 的倍数则认定为是识别漏掉了数字，返回False
            最后对四位数字的元素个数进行判断，若等于 img_total，则认定为本行合格，否则认定不合格，返回False
            合格则重新格式化数字并返回列表
            """
            result = result["words_result"]
            rec_result = ""
            for rec_row in result:
                rec_result += rec_row["words"]
            rec_result = "%"+rec_result
            # 考虑到可能有开头是 "0%" 的情况，需要在开头就加一个 "%"
            rec_result = rec_result.replace("%0%", "%0000%")
            rec_result = rec_result.replace("%0%", "%0000%")
            # 写两行是为了解决两个 0% 连一块儿的情况，如 "0%0%65.32%"，三个连一块儿的话。。，就重新排序吧
            rec_result = rec_result.replace("%100%","%1000%")
            rec_result = rec_result.replace("%100%","%1000%")
            rec_result = rec_result.replace(".", "")
            rec_result = rec_result.replace("%","")
            if not len(rec_result) % 4 == 0:
                self.logger.warning("识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果总长度不是4的倍数，处理后的识别结果：%s，识别结果行原文：%s" % (
                    img_type, img_path, rec_result, result))
                return False
            else:
                revised_rec_result = []
                for i in range(len(rec_result) // 4):
                    tem = rec_result[i*4:i*4 + 4]
                    if tem == "1000":
                        revised_rec_result.append("100%")
                    elif tem == "0000":
                        revised_rec_result.append("0%")
                    else:
                        revised_rec_result.append("%s.%s%%" % (tem[:2], tem[2:]))
                if len(revised_rec_result) != img_total:
                    self.logger.warning("识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果数目与图片总数不符，修订后的识别结果：%s，识别结果行原文：%s" % (
                    img_type, img_path, revised_rec_result, result))
                    return False
                return revised_rec_result
        elif img_type in (31,32):
            # 详细信息里的准点率或时间图片，这种图片单张识别，result即为识别结果
            p = re.search(r"\d\d\.\d\d%",result) if img_type == 31 else re.search(r"\d\d:\d\d",result)
            if p:
                return result
            else:
                if img_type == 31 and (result == "0%" or result == "100%"):
                    return result
                self.logger.warning(
                    "识别结果有误！图片类型：%d，图片路径：%s，识别结果行原文：%s，正在尝试修复..." % (img_type, img_path, result))
                revised_rec_result = ""
                for let in result:
                    if let.isdigit():
                        revised_rec_result += let
                if len(revised_rec_result) == 4:
                    a = revised_rec_result[:2]
                    b = revised_rec_result[2:]
                    to_return = "%s.%s%%"%(a,b) if img_type == 31 else "%s:%s"%(a,b)
                    self.logger.warning("修复成功！修复结果：%s"%to_return)
                    return to_return
                else:
                    self.logger.error("修复失败！")
                    return False
        else:
            # 适用于合并识别 33 类图片的情况，暂时没用
            result = result["words_result"]
            to_return = []
            if not len(result) == img_total:
                self.logger.warning(
                    "识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果行数不匹配，识别结果行原文：%s" % (img_type, img_path, result))
                return False
            for rec_row in result:
                if len(rec_row.values()) != 1:
                    self.logger.info(
                        "识别警告！图片类型：%d，图片路径：%s，警告内容：同一行有多个识别结果，已合并处理！识别结果行原文：%s" % (img_type, img_path, result))
                    to_return.append("".join(rec_row.values()))
                else:
                    for item in rec_row.values():
                        to_return.append(item)
            return to_return

    def in_rec(self, img_path_list, img_type):
        # 只识别，不检验识别结果是否正确
        if len(img_path_list) == 1:
            combined_img_path = img_path_list[0]
        else:
            combined_img_path = self.combine(img_path_list, img_type)
        self.logger.debug("开始识别图片：%s" % combined_img_path)
        in_rec_max_retry_times = 5
        cur_error_times = 0
        with open(combined_img_path, 'rb') as f:
            a = time.time()
            img_content = f.read()
        try:
            result = self.aipOcr.basicGeneral(img_content)
        except requests.exceptions:
            self.logger.warning("提交百度过程中出现网络连接错误！")
            result = {"error_code":999}
        while result.get("error_code") and cur_error_times < in_rec_max_retry_times:
            cur_error_times += 1
            self.logger.info("百度返回结果：%s" % result)
            self.logger.info("进行第 %d 次提交..." % (cur_error_times+1))
            time.sleep(random.randint(5,15)*0.1)
            result = self.aipOcr.basicGeneral(img_content)
        if not result.get("error_code"):
            self.logger.info("本次提交识别用时 %.3f s" % (time.time()-a))
            return combined_img_path, result
        else:
            self.logger.error("图片 %s 6 次提交均返回错误码，已放弃提交！"%combined_img_path)
            return combined_img_path, {}

    def rec(self, img_path_list, img_type, dic=None):
        # 识别并检验识别结果，若识别结果有误，则进行若干次重试
        if img_type in (3,31,32,33):
            t_list = []
            for item in img_path_list:
                t = threading.Thread(target = self.rec_3, args = (item,img_type))
                t.start()
                t_list.append(t)
            for t in t_list:
                t.join()
            for key,value in self.local_rec_result.items():
                if value == "--":
                    self.logger.error("3 类图片 %s 最终识别失败！"%key)
            if dic:
                dic.update(self.local_rec_result)
            return self.local_rec_result
        start = time.time()
        combined_img_path, rec_result = self.in_rec(img_path_list, img_type)
        self.logger.info("本次识别完毕，识别用时 %.3f s，正在检查识别准确度..." % (time.time()-start))
        check_result = self.check(combined_img_path, len(img_path_list), rec_result, img_type)
        error_times = 0
        max_retry_times = 5 if img_type in (1, 2) else 3
        while not check_result and error_times <= max_retry_times:
            error_times += 1
            self.logger.warning("识别结果错误！图片路径为 %s，正在进行第 %d 次识别..." % (combined_img_path, error_times+1))
            sub_start = time.time()
            random.shuffle(img_path_list)
            combined_img_path, rec_result = self.in_rec(img_path_list, img_type)
            self.logger.info("本次识别完毕，识别用时 %.3f s，正在检查识别准确度..." % (time.time()-sub_start))
            check_result = self.check(combined_img_path, len(img_path_list), rec_result, img_type)
        if check_result:
            if error_times > 0:
                self.logger.info("图片 %s 第 %d 次识别成功！识别+判断总用时 %.3f s" % (combined_img_path, error_times+1, time.time()-start))
            else:
                self.logger.info("图片 %s 识别成功！识别+判断总用时 %.3f s" % (combined_img_path, time.time()-start))
            to_return = dict(zip(img_path_list, check_result))
            if len(to_return) != len(img_path_list):
                self.logger.critical("识别结果数量与图片数量不相符 %d vs %d ！请检查代码！"%(len(to_return), len(img_path_list)))
                self.logger.critical("%s"%img_path_list)
                self.logger.critical("%s"%to_return)
            if dic:
                dic.update(to_return)
            return to_return
        else:
            self.logger.error("当前图片列表识别失败！，图片类型：%d, 最后一张组合图片为：%s" % (img_type, combined_img_path))
            to_return = dict.fromkeys(img_path_list, '--')
            if dic:
                dic.update(to_return)
            return to_return

    @staticmethod
    def my_ocr_rec(img_path,img_type,dic=None):
        res = my_ocr.My_rec().rec(img_path,img_type)
        if dic is not None:
            dic.update({img_path:res})
        return res

    def test(self, img_type=None, img_total=None, test_times=1):
        # 测试用！！！
        # 随机选择同一大小的一批随机数量的图片，拼接后送到百度进行测试
        # 测试无法区分31 32 33类图片
        if not img_type:
            img_type = random.choice((1, 2, 3))
        picked_img_path_list = []
        if img_type == 1:
            img_size = ((50, 28),)
        elif img_type == 2:
            img_size = ((63, 28),)
        else:
            img_size = ((280, 40), (80, 40))
        for item in os.listdir(ORI_IMG_PATH):
            if item[-4:] == ".png":
                p = Image.open(ORI_IMG_PATH+item)
                if p.size in img_size:
                    picked_img_path_list.append(ORI_IMG_PATH+item)
        self.logger.debug("共找到符合条件的图片 %d 张" % len(picked_img_path_list))
        for i in range(test_times):
            if not img_total:
                if img_type in (1,2):
                    img_total = random.randint(1, 25)
                else:
                    img_total = random.randint(1,6)
            try:
                test_img_path_list = random.sample(picked_img_path_list,img_total)
            except ValueError:
                self.logger.warning("可用图片数不足测试所需数量！")
                test_img_path_list = picked_img_path_list
            self.logger.debug("本次测试图片张数： %d, 图片类型：%s" % (len(test_img_path_list), img_type))
            self.logger.info("测试结果：")
            myPrint(self.rec(test_img_path_list, img_type))
            self.init_args()
            print("-------------------------第 %d 次测试完毕！------------------------" % (i+1))

    def run(self, mission_queue, result_dic):
        self.init_args()
        def push(img_path_list,img_type,remnants=False,dic = result_dic):
            """
            1、2 类图片数量多，格式固定，所以多张图片拼接后送交识别
            3x 类图片数量少且格式不固定，逐张识别
            """
            if img_type in (1,2):
                if len(img_path_list) < 20 and not remnants:
                    return
            if img_path_list:
                if remnants:
                    self.logger.debug("推送残余任务！任务图片类型：%d"%img_type)
                else:
                    self.logger.debug("推送任务！任务图片类型：%d"%img_type)
                tt = threading.Thread(target = self.rec, args = (img_path_list[:], img_type, dic))
                tt.start()
                self.rec_img_thread_list.append(tt)
                img_path_list.clear()

        type1_img_list = []
        type2_img_list = []
        while self.new_img_will_come or not mission_queue.empty():
            if mission_queue.empty():
                time.sleep(0.1)
            else:
                mission = mission_queue.get()
                if OCR_TYPE == 1:
                    if mission[1] == 1:
                        type1_img_list.append(mission[0])
                    elif mission[1] == 2:
                        type2_img_list.append(mission[0])
                    else:
                        push([mission[0]],mission[1])
                    push(type1_img_list,1)
                    push(type2_img_list,2)
                elif OCR_TYPE == 2:
                    if mission[0] != 33:
                        ttt = threading.Thread(target = self.my_ocr_rec, args = (mission[0], mission[1], result_dic))
                        ttt.start()
                        self.rec_img_thread_list.append(ttt)
                    else:
                        push([mission[0]],mission[1])
        if OCR_TYPE == 1:
            push(type1_img_list,1,remnants=True)
            push(type2_img_list,2,remnants=True)
        for t in self.rec_img_thread_list:
            t.join()
        self.rec_finished = True


if __name__ == '__main__':
    r = Rec_pic()
    # r.test(1,20,test_times=8)