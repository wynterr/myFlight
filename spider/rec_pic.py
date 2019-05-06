# -*- coding: utf-8 -*-
# @Author: 毅梅傲雪
# @Date:   2019-04-18 12:01:01
# @Last Modified by:   毅梅傲雪
# @Last Modified time: 2019-05-05 00:09:44
import os
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

'''
通过好长时间的测试，初步判断：
出发、到达实际时间的图片像素大小为： 50x28
准点率的图片像素大小为： 63x28

详细信息中，时间图片的像素大小为 80x40
其他信息的像素图片大小为 280x40 或者 80x40
'''
# 详细信息里的百分率图片不打算用百度识别了，用本地识别
'''
一次识别失败就不要对同一张图片进行尝试多次尝试了，结果不会有什么改进的
典型识别失败案例:
2,3    -->  23
A      -->  NULL
18:18  -->  8:18
2      -->  NULL
G5     -->  null
15     -->  null
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
                '[%(levelname)-8s] %(asctime)s %(filename)s[line:%(lineno)d] %(message)s')
            console_formatter = logging.Formatter(
                '[%(levelname)-8s]%(filename)s[line:%(lineno)d] %(message)s')
            logfile.setFormatter(file_formatter)
            console.setFormatter(console_formatter)
            logfile.setLevel(logging.INFO)
            console.setLevel(logging.WARNING)
            self.logger.addHandler(logfile)
            self.logger.addHandler(console)

    def inform_pic_finished(self):
        self.new_img_will_come = False

    def rec_auth_code(self, img_path):
        with open(img_path, "rb") as f:
            return self.aipOcr.basicGeneral(f.read(), {"language_type": "ENG"})

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
        target.save(img_path[:-4]+"new_"+img_path[-4:])
        return target

    def local_rec(self, item, use_baidu=True):
        # 实际上是每张图片用百度和本地进行双重识别，懒得改函数名了
        # 只有第 3 类图片才能用本函数，每次识别一张
        if use_baidu:
            threading.Thread(target = self.local_rec, args = (item, False)).start()
            path, result = self.in_rec([item], 3)
            try:
                result = result["words_result"][0]["words"]
            except IndexError:
                result = None
        else:
            result = pytesseract.image_to_string(Image.open(item))
        if not result:
            self.logger.warning("识别图片 %s 结果为空，尝试本地 double 识别..." % item)
            result = pytesseract.image_to_string(self.double(item))
            result = result.replace(" ", "")
            if len(result) != 2 or result[0] != result[1]:
                self.logger.error("本地 double 识别图片 %s 失败，识别结果：%s" % (item, result))
                result = "--"
            else:
                result = result[0]
        if use_baidu:
            self.local_rec_result.update({item: result})
        else:
            while not self.local_rec_result.get(item):
                # print("等待百度识别完成")
                time.sleep(0.1)
            p = self.local_rec_result.get(item)
            if len(result) > len(p):
                self.logger.info("本地结果更优！")
                self.local_rec_result.update({item: result})
        return self.local_rec_result

    @staticmethod
    def combine(img_path_list, img_type):
        # 拼接指定数目的图片
        # 返回拼接图片的路径
        img_open_list = [Image.open(x) for x in img_path_list]
        img_total = len(img_open_list)
        img_col = 1
        if img_type == 1:
            # 基础信息里的图片尽量排列方正
            img_col = int(pow(img_total, 0.5))
        elif img_type == 2:
            img_col = int(pow(img_total, 0.5))
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

    def check(self, combined_img_path, img_total, result, img_type):
        # 检验识别结果是否正确，正确则返回修正后的结果
        if not result:
            return False
        if img_type in (1, 2):
            # 基础信息里的图片尽量排列方正
            img_col = int(pow(img_total, 0.5))
        else:
            img_col = 1
        img_row = ceil(img_total / img_col)
        result = result["words_result"]
        row_img_num = []
        for i in range(img_row):
            row_img_num.append(img_col)
        row_img_num[-1] = img_total-(img_row-1) * img_col
        to_return = []
        if img_type == 1:
            # 说明这是基础信息里的实际时间图片
            # 这种图片识别结果的判读以每行结果中的数字的数目是否正确为依据，每个时间应有 4 个数字
            for index, item in enumerate(result):
                item = item["words"].replace(":", "")
                if len(item) != 4 * row_img_num[index]:
                    self.logger.info("check函数判断识别结果有误！图片类型：%d，图片路径：%s，错误原因：漏识别数字，错误行：%s，识别结果行原文：%s" % (
                        img_type, combined_img_path, item, result))
                    return False
                for i in range(row_img_num[index]):
                    # print("imgcol",item)
                    to_return.append("%s:%s" % (item[i * 4:i * 4+2], item[i * 4+2:i * 4+4]))
            return to_return
        elif img_type == 2:
            """
            说明这是基础信息里的准点率图片
            这种图片由于有 0% 和 100% 这种数字的出现，不能简单地以每个数字的位数来判断
            判断方法如下：
            逐行判断，对每行识别结果，先把 0% 替换为 0000%，再用 % split，然后过滤空字符串
            然后对每个元素内容进行判断，凡是元素中出现100的，都把100变成1000（不考虑会出现00.xx%这种数字）
            再去掉每个元素中的 . ，
            然后对元素长度进行判断若位数等于 4 的倍数则每 4 位拆开，否则即认定为是识别漏掉了数字，返回False
            最后对每行的元素个数进行判断，若等于 img_col，则认定为本行合格，否则认定不合格，返回False
            """
            for index, rec_row in enumerate(result):
                rec_row = rec_row["words"].replace("%0%", "0000%")
                rec_row = filter(bool, rec_row.split("%"))
                revised_rec_row = []
                for item in rec_row:
                    item = item.replace("100", "1000")
                    item = item.replace(".", "")
                    if not len(item) % 4 == 0:
                        self.logger.info("图片类型：%d，图片路径：%s，错误原因：分片长度不是4的倍数，错误行：%s，识别结果行原文：%s" % (
                            img_type, combined_img_path, list(rec_row), result))
                        return False
                    else:
                        for i in range(len(item) // 4):
                            tem = item[i * 4:i * 4+4]
                            if tem == "1000":
                                revised_rec_row.append("100%")
                            elif tem == "0000":
                                revised_rec_row.append("0%")
                            else:
                                revised_rec_row.append("%s.%s%%" % (tem[i * 4:i * 4+2], tem[i * 4+2:i * 4+4]))
                if len(revised_rec_row) != row_img_num[index]:
                    self.logger.info("图片类型：%d，图片路径：%s，错误原因：行四位数字组合不满足应有数目，错误行：%s，识别结果行原文：%s" % (
                        img_type, combined_img_path, list(rec_row), result))
                    return False
                to_return.extend(revised_rec_row)
            return to_return
        else:
            # 其他图片
            if not len(result) == img_total:
                self.logger.info(
                    "check函数判断识别结果有误！图片类型：%d，图片路径：%s，错误原因：识别结果行数不匹配，识别结果行原文：%s" % (img_type, combined_img_path, result))
                return False
            for rec_row in result:
                if len(rec_row.values()) != 1:
                    self.logger.info(
                        "识别警告！图片类型：%d，图片路径：%s，警告内容：同一行有多个识别结果，已合并处理！识别结果行原文：%s" % (img_type, combined_img_path, result))
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
        self.logger.debug("识别图片：%s" % combined_img_path)
        in_rec_max_retry_times = 5
        cur_error_times = 0
        with open(combined_img_path, 'rb') as f:
            a = time.time()
            img_content = f.read()
        result = self.aipOcr.basicGeneral(img_content)
        while result.get("error_code") and cur_error_times < in_rec_max_retry_times:
            cur_error_times += 1
            self.logger.info("百度返回结果：%s" % result)
            self.logger.info("进行第 %d 次提交..." % (cur_error_times+1))
            result = self.aipOcr.basicGeneral(img_content)
        if not result.get("error_code"):
            self.logger.debug("本次提交识别用时 %.3f s" % (time.time()-a))  # self.logger.debug("识别原始结果：")  # myPrint(result)
        else:
            self.logger.error("%s 5 次提交均返回错误码，已放弃提交！"%combined_img_path)
            return combined_img_path, {}
        return combined_img_path, result

    def rec(self, img_path_list, img_type, dic=None):
        # 识别并检验识别结果，
        if img_type == 3:
            t_list = []
            for item in img_path_list:
                t = threading.Thread(target = self.local_rec, args = (item,))
                t.start()
                t_list.append(t)
            for t in t_list:
                t.join()
            if dic:
                dic.update(self.local_rec_result)
            return self.local_rec_result
        start = time.time()
        combined_img_path, rec_result = self.in_rec(img_path_list, img_type)
        check_result = self.check(combined_img_path, len(img_path_list), rec_result, img_type)
        error_times = 0
        max_retry_times = 5 if img_type in (1, 2) else 3
        while not check_result and error_times <= max_retry_times:
            error_times += 1
            self.logger.warning("识别结果检测为无效，图片路径为 %s，正在进行第 %d 次识别..." % (combined_img_path, error_times+1))
            sub_start = time.time()
            random.shuffle(img_path_list)
            combined_img_path, rec_result = self.in_rec(img_path_list, img_type)
            self.logger.debug("本次识别完毕，用时 %.3f s，正在检查识别准确度..." % (time.time()-sub_start))
            check_result = self.check(combined_img_path, len(img_path_list), rec_result, img_type)
        if check_result:
            if error_times > 0:
                self.logger.warning("图片 %s 第 %d 次识别成功！" % (combined_img_path, error_times+1))
            self.logger.debug("识别成功！总用时 %.3f s" % (time.time()-start))
            if len(check_result) != len(img_path_list):
                self.logger.critical("识别结果认定为有效但与图片数目不相符！请检查代码！！！")
                print("check_result is :")
                myPrint(check_result)
                print('img_path_list is', img_path_list)
                myPrint(img_path_list)
            to_return = dict(zip(img_path_list, check_result))
            if dic:
                dic.update(to_return)
            return to_return
        else:
            self.logger.error("当前图片列表识别失败！！！，图片类型：%d, 最后一组组合图片为：%s" % (img_type, combined_img_path))
            return dict.fromkeys(img_path_list, '--')

    def test(self, img_type=None, img_total=None, test_times=1):
        # 测试用！！！
        # 随机选择同一大小的一批随机数量的图片，拼接后送到百度进行测试
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
            if "商标" not in item and item[-4:] == ".png":
                p = Image.open(ORI_IMG_PATH+item)
                # print(p.size)
                if p.size in img_size:
                    picked_img_path_list.append(ORI_IMG_PATH+item)
        self.logger.debug("共找到符合条件的图片 %d 张" % len(picked_img_path_list))
        for i in range(test_times):
            test_img_path_list = []
            if not img_total:
                img_total = random.randint(1, 15)
            while len(test_img_path_list) < img_total:
                test_img_path_list.append(random.choice(picked_img_path_list))
            self.logger.debug("本次测试图片张数： %d, 图片类型：%s" % (len(test_img_path_list), img_type))
            myPrint(self.rec(test_img_path_list, img_type))
            print("-------------------------第 %d 次测试完毕！------------------------" % (i+1))

    def run(self, mission_queue, result_dic):
        type1_img_list = []
        type2_img_list = []
        type3_img_list = []
        while self.new_img_will_come or not mission_queue.empty():
            if mission_queue.empty():
                time.sleep(0.1)
            else:
                mission = mission_queue.get()
                if mission[1] == 1:
                    type1_img_list.append(mission[0])
                elif mission[1] == 2:
                    type2_img_list.append(mission[0])
                else:
                    type3_img_list.append(mission[0])

                if len(type1_img_list) > 20:
                    self.logger.debug("推送任务！任务图片类型：1")
                    t = threading.Thread(target = self.rec, args = (type1_img_list, 1, result_dic))
                    t.start()
                    self.rec_img_thread_list.append(t)
                    type1_img_list = []
                if len(type2_img_list) > 20:
                    self.logger.debug("推送任务！任务图片类型：2")
                    t = threading.Thread(target = self.rec, args = (type2_img_list, 2, result_dic))
                    t.start()
                    self.rec_img_thread_list.append(t)
                    type2_img_list = []
                if len(type3_img_list) > 0:
                    self.logger.debug("推送任务！任务图片类型：3")
                    t = threading.Thread(target = self.rec, args = (type3_img_list, 3, result_dic))
                    t.start()
                    self.rec_img_thread_list.append(t)
                    type3_img_list = []
        if type1_img_list:
            self.logger.debug("推送残余任务！任务图片类型：1，")
            t = threading.Thread(target = self.rec, args = (type1_img_list, 1, result_dic))
            t.start()
            self.rec_img_thread_list.append(t)
        if type2_img_list:
            self.logger.debug("推送残余任务！任务图片类型：2，")
            t = threading.Thread(target = self.rec, args = (type2_img_list, 2, result_dic))
            t.start()
            self.rec_img_thread_list.append(t)
        if type3_img_list:
            self.logger.debug("推送残余任务！任务图片类型：3，")
            t = threading.Thread(target = self.rec, args = (type3_img_list, 3, result_dic))
            t.start()
            self.rec_img_thread_list.append(t)
        self.logger.debug("识别任务下发完毕，等待识别完成！")
        for t in self.rec_img_thread_list:
            t.join()
        self.rec_finished = True


if __name__ == '__main__':
    r = Rec_pic()
    r.test(3, random.randint(1, 6), test_times = 10)  