#-*- coding:utf-8 -*-
import json,traceback
from ftplib import FTP
import redis
from PIL import Image

pool = redis.ConnectionPool(host='127.0.0.1',port=6379,decode_responses=True)
client = redis.Redis(connection_pool=pool)
# client = redis.StrictRedis(host='127.0.0.1',port=6379,decode_responses=True)

def getValues():
    content = {
        "notice": "http://10.75.13.114/a.jpg",
        "data": [
            {
                "name": "组件1",
                "children": [
                    {
                        "name": "主视图",
                        "date": "20180209",
                        "ori_name": "组件1主视图",
                        "path": "http://10.75.13.114/a.jpg",
                    },
                    {
                        "name": "侧视图",
                        "date": "20180209",
                        "ori_name": "组件1侧视图",
                        "path": "http://10.75.13.114/b.jpg",
                    }
                ]
            }
        ]

    }
    content = json.dumps(content,ensure_ascii=False,encoding='utf-8')
    print content.replace('\"','\'')
    # print type(content)
    client.set('201830064781X_130001_a',content)


def get():
    values = client.get('201830064781X_130001_a')
    # value = client.get('201830064781X_130001_a')
    print values
    print type(values)
    valueLoad = json.loads(values)
    auth = valueLoad['authVersion']
    auth = json.dumps(auth, ensure_ascii=False,encoding='utf-8')
    print auth
    print type(auth)

#"ftp://efsftp_w:123456@10.1.10.230:21/20180807/11/148353870.zip",
#ftp://efsftp_w:go123456@10.1.10.108:21/20180807/11/137922504.zip
def ftpTest():
    try:
        user = 'efsftp_w'
        passwd = 'go123456'
        host = '10.1.10.108'
        port = '21'
        ftp = FTP()
        ftp.set_debuglevel(2)
        # 1.下载
        ftp.connect(host, int(port))
        ftp.login(user, passwd)
        fileHandler = open('static/abc.zip', 'wb').write
        print ftp.pwd()
        ftp.retrbinary('RETR 20180807/11/137922504.zip', fileHandler)
        ftp.set_debuglevel(0)
        ftp.quit()
    except Exception as e:
        print traceback.format_exc()

def thrumbTest():
    filePath = 'static/abc~1.jpg'
    size = (50, 50)
    saveImgPath = filePath.replace('.', '_' + str(50) + '_' + str(50) + '.')
    im = Image.open(filePath)
    im.thumbnail(size)
    im.save(saveImgPath)


if __name__=="__main__":
    # getValues()
    # get()
    # ftpTest()
    thrumbTest()