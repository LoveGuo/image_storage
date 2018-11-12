#-*-coding:utf-8-*-
from suds.client import Client
import logging
import requests,json

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("migrate2.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
#迁移文件中给定条件的数据

def getFTP(fid,version=1):
    '''
    :param fid:
    :param version:
    :return: 若存在则返回ftp路径；若不存在，则返回None
    '''
    wsdlUrl = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
    client = Client(wsdlUrl)
    ftp = client.service.RetrieveFile(fid,version)
    return ftp


def fileToList():
    reqs = []
    with open('data2.txt','r') as f:
        lines = f.readlines()
        for line in lines:
            req = {}
            cases = []
            case = {}
            lineList = line.strip().split('\t')
            ftp = getFTP(lineList[1])
            if ftp is None:
                logger.info("ftp is None:" + str(line))
                print "ftp is None: " + str(line)
                continue
            logger.info("fid: " + lineList[1] + 'ftp: ' + ftp)
            case['shenqingh'] = lineList[0]
            case['wenjianlx'] = '130001'
            case['fid'] = lineList[1]
            case['submitDate'] = lineList[2]
            case['url'] = ftp
            cases.append(case)
            req['cases'] = cases
            reqs.append(req)
    logger.info("读取数据长度：" + str(len(reqs)))
    return reqs


def save(case):
    url = 'http://10.75.13.114:5000/upload'
    headers = {'Content-Type': 'application/json'}
    originRes = requests.post(url=url, headers=headers, data=json.dumps(case))
    originText = json.loads(originRes.text)
    if originText['status'] == 1:
        return 1
    else:
        logger.info("execute fail: " + str(case))
        return 0


def main():
    count = 0
    data = fileToList()
    for case in data:
        result = save(case)
        if result == 1:
            count = count + 1
            if count % 50 == 0:
                print '已经入库数据：' + str(count)
        else:
            print "failed: " + str(case)
    print str(count)
    logger.info("success num: " + str(count))


if __name__=='__main__':
    main()
    # print getFTP('GD000134335243')