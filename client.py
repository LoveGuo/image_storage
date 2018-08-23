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
    # 2017301167196 sqh
    #
    # 130001 documentType
    #
    # GD000126680358 fid
    url = 'http://10.75.13.114:5000/getOriginImgs'
    data = {
        'shenqingh': "2017301167196",
        'wenjianlx': '130001',
        'fid':'DA000126680358'
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


def uploadAuthImgs():
    url = 'http://10.75.13.114:5000/uploadAuthImgs'
    headers = {'Content-Type': 'application/json'}
    data1 = {
        "shenqingh":"2015304108218",
        "wenjianlx":"130001",
        "fid":"GY000003031250",
        "url":"ftp://efsftp_w:go123456@10.1.10.111:21/20180814/10/351393022.zip",
        "urltype":"0",
        "submitDate":"2018-08-17 16:16:59"
    }
    res = requests.post(url=url,headers=headers,data=json.dumps(data1))
    cur = res.text
    print cur


if __name__=="__main__":
    # hello()
    # upload()
    # saveSingleImg()
    # saveImgs()
    # savecreate()
    getOriginImgs()
    # loaddata()
    # uploadAuthImgs()