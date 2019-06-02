# -*- coding: utf-8 -*-
import re
import json
import requests
import pickle
from .myPrint import myPrint
from .__init__ import *
"""
"PEK,NAY": "BJS",
"PVG,SHA": "SHH",
XIY: "SIA"
"""


class UpdateAirpData(object):
    """用于更新机场代码数据的类"""
    @staticmethod
    def resubfun(item):
        return '"%s":' % item

    def update_data(self):
        source_data = requests.get(self.source_url)
        print("获取到网页")
        print(source_data.text)
        source_data = re.search(r"[\[\{].+[\]\}]", source_data.text).group(0)
        new_data = json.loads(re.sub(r"(\w+?):", lambda x: self.resubfun(x.group(1)), source_data))
        # 这一步因为要替换的数据较多而比较慢
        exit(0)
        with open(self.filepath, 'wb') as f:
            pickle.dump(new_data, f)
        print("数据更新完成！")


class CountryCodes(UpdateAirpData):
    # 每个国家对应一个代码
    def __init__(self):
        self.filepath = AIRP_DATA_PKLS + 'CountryCodes.pkl'
        self.source_url = "http://www.variflight.com/_newstatic/dest/js/countryCode.js?v=cd7ff69153103daf5ec8a59309dbaf1e"
        with open(self.filepath, 'rb') as f:
            self.CountryCodes = pickle.load(f)
            
    def print_data(self):
        print("--------------CountryCodes----------------")
        myPrint(self.CountryCodes)
        print('------------------------------------------')
        
    def getcountry_name(self, code):
        for country in self.CountryCodes:
            if country["code"] == code:
                return country["country"]
            
    def get_country_code(self, country_name):
        for country in self.CountryCodes:
            if country["country"] == country_name:
                return country["code"]
            
            
class CitiesData(UpdateAirpData):
    # 对应APP上的输入框的选择列表
    # 键值为 (['in', 'inHot', 'out', 'outHot', 'outHotHot'])
    # in 为APP上显示的国内机场的全部列表，inhot为APP上显示的国内热门
    # out 为国外机场的全部数据，数据应该是最全的，outhot 是APP上显示的国外机场的列表，outhothot 是APP上显示的国外热门机场
    def __init__(self):
        self.filepath = AIRP_DATA_PKLS + 'CitiesData.pkl'
        self.source_url = "http://www.variflight.com/_newstatic/dest/js/airportlist.js?v=d5c61d33f11f3aaca776b2cf9e27d563"
        with open(self.filepath, 'rb') as f:
            self.CitiesData = pickle.load(f)
            
    def print_data(self):
        print("--------------CitiesData----------------")
        myPrint(self.CitiesData)
        print(self.CitiesData.keys())
        print('------------------------------------------')
        
    def print_keys(self):
        print(self.CitiesData.keys())


class CitiesinbyAZ(UpdateAirpData):
    # 对应网站输入框的 国内热门 和 A-Z 的候选机场
    # 字典的所有键为：(['inHot', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'W', 'X', 'Y', 'Z'])
    def __init__(self):
        self.filepath = AIRP_DATA_PKLS + "CitiesinbyAZ.pkl"
        self.source_url = "http://www.variflight.com/_newstatic/dest/js/citiesinbyAZ.js?v=7d573df17e320bd942b470f1149766a8"
        with open(self.filepath, 'rb') as f:
            self.CitiesinbyAZ = pickle.load(f)
            
    def print_data(self):
        print("--------------CitiesinbyAZ----------------")
        myPrint(self.CitiesinbyAZ)
        print(self.CitiesinbyAZ.keys())
        print('------------------------------------------')
        
    def print_keys(self):
        print(self.CitiesinbyAZ.keys())
        
        
class Citiesoutbyarea(UpdateAirpData):
    # 字典的所有键值为：(['outhot', 'inhot', 'asia', 'europe', 'america', 'africa', 'oceania'])
    # outhot 对应“国际热门”，inhot 与 CitiesinbyAZ中的 inhot 内容一致，其余为各大洲的候选机场
    def __init__(self):
        self.filepath = AIRP_DATA_PKLS + "Citiesoutbyarea.pkl"
        self.source_url = "http://www.variflight.com/_newstatic/dest/js/citiesoutbyarea.js?v=044d24deb14a6b6880c48f6d3c58446f"
        with open(self.filepath, 'rb') as f:
            self.Citiesoutbyarea = pickle.load(f)
            
    def print_data(self):
        print("--------------Citiesoutbyarea----------------")
        myPrint(self.Citiesoutbyarea)
        print(self.Citiesoutbyarea.keys())
        print('---------------------------------------------')
        
    def print_keys(self):
        print(self.Citiesoutbyarea.keys())


if __name__ == '__main__':
    # CountryCodes().print_data()
    # CitiesData().print_data()
    CitiesinbyAZ().print_data()
    # Citiesoutbyarea().update_data()
