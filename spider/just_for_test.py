#-*-coding:utf-8-*-
# coding:utf-8
import sys, os
from PIL import Image, ImageDraw
import random
# 二值数组
t2val = {}
def twoValue(image, G):
    for y in range(0, image.size[1]):
        for x in range(0, image.size[0]):
            g = image.getpixel((x, y))
            if g > G:
                t2val[(x, y)] = 1
            else:
                t2val[(x, y)] = 0
# 根据一个点A的RGB值，与周围的8个点的RBG值比较，设定一个值N（0 <N <8），当A的RGB值与周围8个点的RGB相等数小于N时，此点为噪点
# G: Integer 图像二值化阀值
# N: Integer 降噪率 0 <N <8
# Z: Integer 降噪次数
# 输出
#  0：降噪成功
#  1：降噪失败
def clearNoise(image, N, Z):
    for i in range(0, Z):
        t2val[(0, 0)] = 1
        t2val[(image.size[0] - 1, image.size[1] - 1)] = 1
        for x in range(1, image.size[0] - 1):
            for y in range(1, image.size[1] - 1):
                nearDots = 0
                L = t2val[(x, y)]
                if L == t2val[(x - 1, y - 1)]:
                    nearDots += 1
                if L == t2val[(x - 1, y)]:
                    nearDots += 1
                if L == t2val[(x - 1, y + 1)]:
                    nearDots += 1
                if L == t2val[(x, y - 1)]:
                    nearDots += 1
                if L == t2val[(x, y + 1)]:
                    nearDots += 1
                if L == t2val[(x + 1, y - 1)]:
                    nearDots += 1
                if L == t2val[(x + 1, y)]:
                    nearDots += 1
                if L == t2val[(x + 1, y + 1)]:
                    nearDots += 1
                if nearDots < N:
                    t2val[(x, y)] = 1

def saveImage(filename, size):
    image = Image.new("1", size)
    draw = ImageDraw.Draw(image)

    for x in range(0, size[0]):
        for y in range(0, size[1]):
            draw.point((x, y), t2val[(x, y)])

    image.save(filename)

from aip import AipOcr 
import pytesseract
APP_ID = '15943518'  
API_KEY = 'T2icUbUcTgiv6GGUucZvbyMv'  
SECRET_KEY = 'ir5gXsiLtFZ4VGEZ5kq87EEyBFkpRxyk'
ocr = AipOcr(APP_ID,API_KEY,SECRET_KEY)  
base_path = "./auth_code_imgs/"
imgs = os.listdir(base_path)
for i in range(20):
    path = base_path+random.choice(imgs)
    image = Image.open(path)
    image = image.convert('L')
    twoValue(image, 150)
    path1 = base_path+"test%d1.jpg"%i
    # saveImage(path1, image.size)
    clearNoise(image, 3, 1)
    path1 = base_path+"test%d2.jpg"%i
    saveImage(path1, image.size)
    with open(path1,"rb") as f:
        print(path1,pytesseract.image_to_string(Image.open(path1)))
        print(path1,ocr.basicGeneral(f.read(),{"language_type":"ENG"}),sep="\n")
        print("-----------------------------------------------")
