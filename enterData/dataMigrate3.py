#-*-coding:utf-8-*-
import logging
import redis

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("migrate2.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
#迁移文件中给定条件的数据

'''
    旧id拷贝到新id：复制redis数据
'''

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)

def setHashField(client,key,field,value):
    logger.info("redis set operate:" + key)
    client.hset(key,field,value)

def getHashField(client,key,field):
    logger.info('redis: get hash field')
    return client.hget(key,field)

def getStrValue(client,key):
    return client.get(key)

def setStrValue(client,key,value):
    logger.info("redis set operate:" + key)
    client.set(key,value)

#2010301373242	AB000000000001684028	20100323    |2017302487168 DA000132413212	20170616
def getData():
    oldKey = '2010301373242_130001_o'
    oldField = 'AB000000000001684028'
    newKey = '2017302487168_130001_o'
    newField = 'DA000132413212'
    value = getHashField(client,oldKey,oldField)
    setHashField(client,newKey,newField,value)
    print('end1!')
    oK = '2010301373242_130001'
    nk = '2017302487168_130001'
    strValue = getStrValue(client,oK)
    setStrValue(client,nk,strValue)
    print('end2!')






if __name__=='__main__':
    getData()