#-*- coding:utf-8 -*-
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


#缩略图大小
thumbSize1=(210,210)
thumbSize2=(20,20)
#数组0号为宽，1号为高
thumbSizeList=[[60,60],[90,90],[140,140],[210,210],[450,450],[600,600]]
#图片初始版本号
imgInitialVersion = 0
# 存储路径 .../data/imgs/storage/
basePath = '/wgzstxqy/data/'
# basePath = '/data/imgs/storage/'
ipPort = 'http://10.50.167.111:80'


#当前文件夹名称
modifyDirName = 'a'
originDirName = 'o'
authDirName = 'c'

#入库使用
authPath = '/wgzstxqy/data/auth/'