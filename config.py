#-*- coding:utf-8 -*-
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


UPLOAD_FOLDER="static/upload"
ALLOWED_EXTENSIONS=set(["zip","jpg","jpeg","png","gif"])
#缩略图大小
thumbSize1=(210,210)
thumbSize2=(20,20)
#数组0号为宽，1号为高
thumbSizeList=[[90,90],[140,140],[210,210]]
#图片初始版本号
imgInitialVersion = 0
# 存储路径 .../data/imgs/storage/
basePath = '/data/storage/'
# basePath = 'static/image/'
ipPort = 'http://10.75.13.114:50003'

#当前文件夹名称
modifyDirName = 'a'
originDirName = 'o'
authDirName = 'c'