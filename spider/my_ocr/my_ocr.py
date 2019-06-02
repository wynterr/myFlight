# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = '毅梅傲雪'
__mtime__ = '2019/5/22'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""
import os
import time
import random
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from ..__init__ import *


class Pic_divide(object):
    def __init__(self,img_path,img_type=None):
        self.img = Image.open(img_path).convert("L")
        self.img = self.binary()
        self.ori_img = Image.open(img_path)
        self.img_path = img_path
        self.img_name = os.path.split(img_path)[1]
        if img_type is None:
            if self.img.size == (50,28):
                self.img_type = 1
            elif self.img.size == (63,28):
                self.img_type = 2
            elif self.img.size[1] == 40:
                if "ave_ontime_rate" in img_path:
                    self.img_type = 31
                elif "_time_" in img_path:
                    self.img_type = 32
                else:
                    self.img_type = 33
            else:
                raise ValueError("无法识别的图片大小：%s"%(self.img.size,))
        else:
            self.img_type = img_type

    def binary(self,std=180):
        """
        二值化图片
        :param std: 二值化阈值
        :return: 返回二值化后的图片的Image对象
        """
        new = [0] * 256
        for point in range(std,256):
            new[point] = 1
        new = self.img.point(new,'1')
        return new

    def partition(self,ori=False):
        crop_ranges = self.get_dls()
        if ori:
            return [self.ori_img.crop(item[0],0,item[1],self.ori_img.size[1])]

        res = []
        for rg in crop_ranges:
            start_line = None
            end_line = None
            for col in range(rg[0],rg[1]):
                if start_line is not None:
                    break
                for row in range(self.img.size[1]):
                    if self.img.getpixel((col,row)) == 0:
                        for pix_row in (row-1,row,row+1):
                            if self.img.getpixel((col+1,pix_row)) == 0:
                                start_line = col
                                break
            for col in range(rg[1],rg[0],-1):
                if end_line is not None:
                    break
                for row in range(self.img.size[1]):
                    if self.img.getpixel((col,row)) == 0:
                        end_line = col+1
                        break
            if start_line is None:
                start_line = rg[0]
                print("使用原起始分割线")
            if end_line is None:
                end_line = rg[1]
                print("使用原结束分割线")
            res.append(self.img.crop((start_line,0,end_line,self.img.size[1])))
        return res

    def get_dls(self,fixed_dl=True):
        w = self.img.size[0]
        h = self.img.size[1]
        if fixed_dl:
            if self.img_type == 1:
                return [(0,8),(8,17),(22,31),(31,40)]
            elif self.img_type == 2:
                return self.revise_dls([(0,8),(8,17),(22,31),(31,40)])
            elif self.img_type == 31:
                return self.revise_dls([(0,10),(10,22),(27,38),(38,50)])
            elif self.img_type == 32:
                return [(0,13),(13,27),(36,49),(49,65)]
            # 31 和 33 类图片无法固定位置切割

        crop_ranges = []
        in_word = False
        for col in range(w):
            col_is_dl = True
            for row in range(h):
                if self.img.getpixel((col,row)) == 0:
                    if not in_word:
                        crop_ranges.append([max(0,col-1),None])
                        in_word = True
                    for pix_row in (row-1,row,row+1):
                        if self.img.getpixel((col+1,pix_row)) == 0:
                            col_is_dl = False
                            break
                if not col_is_dl:
                    break
            if col_is_dl and in_word:
                crop_ranges[-1][1] = col+1
                in_word = False
        return crop_ranges

    def revise_dls(self,dls,re_revise=False):
        if re_revise:
            dls = dls[:-1]
            for index,rg in enumerate(dls):
                if rg[1] - rg[0] <= 3:
                    dls.pop(index)
                elif rg[1] - rg[0] > 10:
                    dls.pop(index)
            return dls
        #--- 检查是不是 0% ---#
        has_black = False
        for row in range(self.img.size[1]):
            if has_black:
                break
            for col in range(dls[0][0],dls[0][1]+1):
                if self.img.getpixel((col,row)) == 0:
                    has_black = True
                    break
        if not has_black:
            return [(10,20)]
        #--- 检查是不是 100% ---#
        boder_dot = 0
        for col in (dls[-1][0],dls[-1][1]):
            for row in range(self.img.size[1]):
                if self.img.getpixel((col,row)) == 0:
                    for pix_row in (row-1,row,row+1):
                        if self.img.getpixel((col+1,pix_row)) == 0:
                            boder_dot += 1
                            break
        if boder_dot >= 4:
            return self.revise_dls(self.get_dls(fixed_dl = False),re_revise=True)

        return dls



    def show_img(self,show_part=False):
        crop_ranges = self.get_dls()
        plt.figure()
        if not show_part:
            plt.imshow(self.img)
            for rg in crop_ranges:
                plt.axvline(rg[0],color="r")
                plt.axvline(rg[1],color="b")
        else:
            plt.subplot(2,len(crop_ranges),1)
            for index,item in enumerate(self.partition()):
                plt.subplot(2,len(crop_ranges),index+1)
                plt.imshow(item)
            plt.subplot(2,1,2)
            plt.imshow(self.img)
            for rg in crop_ranges:
                plt.axvline(rg[0],color="r")
                plt.axvline(rg[1],color="b")
        plt.show()

    @staticmethod
    def save(img_list):
        for index,img in enumerate(img_list):
            img.save("./sample32/%d.png"%(random.randint(10,255)+index))
            print("saved")

class My_rec(object):
    def __init__(self):
        self.sample_mat = {
            1:[],
            31:[],
            32:[]
        }
        for img_type in (1,31,32):
            for i in range(10):
                img = Image.open("./my_ocr/sample%d/%d.png"%(img_type,i))
                data = np.matrix(img.getdata(),dtype="float")/255
                self.sample_mat[img_type].append(np.reshape(data,(img.size[1],img.size[0])))
        self.sample_mat[2] = self.sample_mat[1]

    @staticmethod
    def get_contact_ratio(a,b,offset=0):
        """
        :param a:np.matrix，列数小于 b
        :param b:
        :param offset:
        :return:float
        """
        if a.shape[1] > b.shape[1]:
            a,b = b,a
        total = 0
        contacted = 0
        w = a.shape[1]
        h = a.shape[0]
        for i in range(h):
            for j in range(w):
                if offset + j >= b.shape[1]:
                    break
                if offset + j < 0:
                    pass
                else:
                    if a[i,j] or b[i,offset+j]:
                        total += 1
                    if a[i,j] and b[i,offset+j]:
                        contacted += 1
        return contacted/total

    def get_max_contact_ratio(self,a,b):
        ratio = self.get_contact_ratio(a,b)
        delda = abs(a.shape[1]-b.shape[1])
        for i in range(0,delda+1):
            cur = self.get_contact_ratio(a,b,i)
            if cur > ratio:
                ratio = cur
        return ratio

    def _rec(self,img_path,img_type):
        # start = time.time()
        imgs = Pic_divide(img_path,img_type).partition()
        res = []
        for sub_img in imgs:
            data = np.matrix(sub_img.getdata(),dtype="float")/255
            sub_img_array = np.reshape(data,(sub_img.size[1],sub_img.size[0]))
            ratio_list = [self.get_max_contact_ratio(item,sub_img_array) for item in self.sample_mat[img_type]]
            res.append(ratio_list.index(max(ratio_list)))
        # print("识别用时:",time.time()-start)
        return res

    def rec(self,img_path,img_type):
        raw = self._rec(img_path,img_type)
        if img_type == 1 or img_type == 32:
            return "%d%d:%d%d"%(raw[0],raw[1],raw[2],raw[3])
        elif img_type == 2 or img_type == 31:
            if len(raw) == 4:
                return "%d%d.%d%d%%"%(raw[0],raw[1],raw[2],raw[3])
            elif raw == [1,0,0]:
                return "100%"
            elif len(raw) == 3:
                return "%d.%d%d%%"%(raw[0],raw[1],raw[2])
            elif len(raw) == 1:
                return "0%"
            else:
                return "--"
        else:
            return "--"


class Pic_mark(Pic_divide):
    def __init__(self,img_path,img_type):
        super(Pic_mark,self).__init__(img_path,img_type)


if __name__ == '__main__':
    pass
    i = 1
    # ocr = My_rec()
    for file in os.listdir("../img_file"):
        if '.png' in file:
            # "ontime_rate_FM9106_PEK-SHA_20190601.png"
            # "ave_ontime_rate_MF8178_PEK-SHA_20190522.png"
            pic = Pic_divide(os.path.join("../img_file",file))
            print(My_rec().rec(os.path.join("../img_file",file),pic.img_type))
            pic.show_img(show_part = True)
            if pic.img_type == 256:
                # pics = pic.partition(ori=False)
                # pic.save(pics)
                # start = time.time()
                # o = ocr.OCR().test_all(pics)
                # print(o,time.time()-start)
                # prediction = My_rec().rec(os.path.join("../img_file", file),pic.img_type)
                # print("prediction:",prediction,time.time()-start)
                pic.show_img(show_part = True)
                # i += 1
                # break