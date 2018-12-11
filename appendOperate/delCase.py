#-*- coding:utf-8 -*-
import shutil
import logging
import traceback
import redis
'''
根据申请号删除案件和redis信息
'''

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("del.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)

def getBasePath(shenqingh, submitDate):
    '''
    basePath:storage/申请号后4位/申请号(15位,不足前面补0)/文献类型/年/月/日/fid/
    :param shenqingh:
    :param documentType:
    :return:
    '''
    basePath = '/data/storage/'
    sqh_last_4 = shenqingh[-4:]
    sqh_15 = shenqingh
    if len(sqh_15) < 15:
        sqh_15 = '0'*(15-len(sqh_15)) + sqh_15
    return basePath + submitDate[0:4] + '/' + submitDate[4:6] + '/' + submitDate[6:8] + '/' \
           + sqh_last_4 + "/" + sqh_15


def delRedis(shenqingh):
    keyList = [shenqingh + '_130001_o',shenqingh + '_130001_a',shenqingh + '_130001']
    for key in keyList:
        client.delete(key)


def delCases():
    with open('del.txt','r') as f:
        lines = f.readlines()
        for line in lines:
            try:
                line = line.strip()
                arr = line.split('\t')
                path = getBasePath(arr[0],arr[3])
                logger.info("shenqingh: " + arr[0] + ',path: ' + path)
                #删除文件
                shutil.rmtree(path)
                #删除redis信息
                delRedis(arr[0])
            except Exception as e:
                logger.info("line: " + str(line) + str(traceback.format_exc()))




if __name__ == '__main__':
    delCases()
    print "end!"