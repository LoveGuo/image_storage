#-*- coding:utf-8 -*-
import appLogic,json
from xml.dom import minidom
from config import logger
def xmlParse():
    # case = {
     #    "shenqingh":"201830064781X",
     #    "wenjianlx":"130001",
     #    "fid":"GD000157639932",
     #    "url":"ftp://efsftp_w:123456@10.1.10.229:21/20180719/13/494306658.zip",
     #    "urltype":"0",
     #    "submitDate":"20180202"
	# }
    # submitDate = case['submitDate']
    # fid = case['fid']
    xmldoc = minidom.parse('static/abc.xml')
    itemlist = xmldoc.getElementsByTagName('picture')
    # originJson['date'] = submitDate
    # originJson['fid'] = fid
    originJson = {}
    data = []
    noticePath = ''
    flag = True  # 若找到公示图则为False
    for item in itemlist:
        child = {}
        child['ori_name'] = item.attributes['origin_name'].value.encode('utf-8')
        child['path'] = '/' + item.attributes['picture_no'].value + '.jpg'
        child['imgUpdateNum'] = 0
        keys = appLogic.extractWord(item.attributes['origin_name'].value)
        child['name'] = keys[-1]
        child['rotateDesc'] = {}
        # 2.解析xml to json
        appLogic.toOriginJson(data, keys, child)
        # 3.处理公示图
        if flag:
            flag, flag2 = appLogic.getNoticePath(keys[-1])
            if flag2:
                noticePath = child['path']
    originJson['data'] = data
    logger.info(data)


if __name__=='__main__':
    xmlParse()
