#-*- coding:utf-8 -*-
import requests
import json

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#模拟上传图片
def saveSingleImg():
    files = {"file": open("static/image/abc.jpg", "rb")}
    data = {"filepath": "/home/dell/copy3/abc.jpg"}
    r = requests.post("http://10.75.13.114:5000/upload/singleImg", data=data, files=files)
    print r


def saveImgs():
    files = {"file": open("static/image/test.zip", "rb")}
    data = {"filepath": "/home/dell/copy4/test.zip"}
    r = requests.post("http://10.75.13.114:5000/saveImgs", data=data, files=files)
    print r


def hello():
    r = requests.get("http://10.75.13.114:5000/test",data=None)
    print r


# srcImgPath='',desImgPath='',weight=210,height=210
def thumbImgs():
    url = 'http://127.0.0.1:5000/image/thumbImgs'
    data = {'srcImgPath': 'static/image/abc.jpg',
            'desImgPath': 'static/image/',
            'weight': 20,
            'height': 20}
    res = requests.post(url, data)


#test
def getOriginImgs():
    url = 'http://10.75.13.114:5000/getOriginImgs'
    data = {
        'shenqingh': "201830064781X",
        'wenjianlx': '130001'
    }
    res = requests.post(url,data)
    result = json.loads(res.text)

    print result


def loaddata():
    url = 'http://10.75.13.114:5000/getCurrentData'
    data = {
        'shenqingh': "2017301021508",
        'wenjianlx': '130001'
    }
    res = requests.post(url, data)
    cur = res.text
    print cur


if __name__=="__main__":
    # hello()
    # upload()
    # saveSingleImg()
    # saveImgs()
    # savecreate()
    # getOriginImgs()
    loaddata()