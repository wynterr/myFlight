# -*- coding: utf-8 -*-
# @Author: 毅梅傲雪
# @Date:   2019-05-04 22:26:46
# @Last Modified by:   毅梅傲雪
# @Last Modified time: 2019-05-05 00:50:46
import os
import re
import pickle
import datetime
from .__init__ import *


def clear(year=None,month=None,day=None):
    """
    清理指定日期之前的图片、日志
    若不指定日期，则清理全部图片和日志
    """
    #--- 先获取截止时间 ---#
    tem = locals().copy()
    now = datetime.date.today()
    if any(tem.values()):
        for key in tem:
            if not tem[key]:
                tem[key] = eval("now.%s"%key)
        to_time = datetime.date(tem['year'],tem['month'],tem['day']).__str__()
    else:
        to_time = str(now+datetime.timedelta(days=1))
    to_time = to_time.replace("-",'')

    #--- 清理图片 ---#
    for path in (ORI_IMG_PATH,COMBINED_IMG_PATH):
        for item in os.listdir(path):
            file_date = re.search(r"\d{8}",item).group(0)
            if file_date < to_time:
                os.remove(os.path.join(path,item))

    #--- 清理本地识别字典 ---#
    try:
        with open("local_img_rec_results.pkl", 'rb') as f:
            dic = pickle.load(f)
    except FileNotFoundError:
        with open("local_img_rec_results.pkl", 'wb') as f:
            pickle.dump({}, f)
    else:
        new_dic = {}
        for key in dic:
            key_date = re.search(r"\d{8}",item).group(0)
            if key_date >= to_time:
                new_dic[key] = dic[key]
        with open("local_img_rec_results.pkl","wb") as f:
            pickle.dump(new_dic,f)

    #--- 清理日志 ---#
    for file in os.listdir(LOG_PATH):
        new_text = ''
        with open(os.path.join(LOG_PATH,file),'r') as f:
            line = f.readline()
            while line:
                line_date = re.search(r"\d{4}-\d{2}-\d{2}",line).group(0)
                line_date = line_date.replace("-","")
                if line_date >= to_time:
                    new_text += line
                line = f.readline()
        with open(os.path.join(LOG_PATH,file),'w') as f:
            f.write(new_text)


if __name__ == '__main__':
    clear()


        