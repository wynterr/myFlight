# -*- coding: utf-8 -*-
import os
import time
import random
import re
import json
import requests
import random
import threading
import logging
import pickle
import pytesseract
import datetime
from aip import AipOcr  
from fake_useragent import UserAgent
from math import ceil
from PIL import Image
from aip import AipOcr  
from PIL import Image
from queue import Queue
from PIL import Image
from lxml import etree
from .myPrint import myPrint

LOG_PATH = "./spider/log/"
AIRP_DATA_PKLS = "./spider/airp_data_pkls/"
ORI_IMG_PATH = "./spider/img_file/"
COMBINED_IMG_PATH = "./spider/combined_imgs/"
AUTH_CODE_IMG_PATH = "./spider/auth_code_imgs/"