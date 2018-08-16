#-*- coding:utf-8 -*-
import requests


# srcImgPath='',desImgPath='',weight=210,height=210
def thumbImgs():
    url = 'http://127.0.0.1:5000/image/thumbImgs'
    data = {'srcImgPath': 'static/image',
            'desImgPath': 'static/image/',
            'weight': 210,
            'height': 210}
    res = requests.post(url,data)
    print res.text

def copyDir():
    url = 'http://10.75.13.114:5000/image/copyDir'
    data = {'srcPath': 'static/image',
            'desPath': 'static/image2/'}
    res = requests.post(url,data)
    print res.text


def getStrValue():
    url = 'http://10.75.13.114:5000/redis/getStr'
    data = {'shenqingh': '1111',
            'documentType': '2222'}
    res = requests.post(url,data)
    print res.text


def singleImg():
    url = 'http://127.0.0.1:5000/upload/singleImg'
    files = {"file": open("static/image/abc.jpg", "rb")}
    data = {'filename':'haha.jpg','filepath':'static/image2'}
    r = requests.post(url, data=data, files=files)
    print r.text


def updateStrValue():
    url = 'http://10.75.13.114:5000/redis/updateStr'
    data = {'shenqingh': '1111',
            'documentType': '2222',
            'value':'guofh'}
    res = requests.post(url, data)
    print res.text


if __name__=='__main__':
    # thumbImgs()
    # copyDir()
    # getStrValue()
    # singleImg()
    updateStrValue()