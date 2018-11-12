#-*- coding:utf-8 -*-
from config import logger
import traceback

def getStrValue(client,key):
    if key == '' or key is None:
        return False
    try:
        value = client.get(key)
    except Exception as e:
        logger.info("get redis value exception:" + traceback.format_exc())
        return False
    return value

def setStrValue(client,key,value):
    logger.info("redis set operate:" + key + ',value: ' + value)
    if key.strip() == '' or key is None or value.strip() == '' or value is None:
        return False
    try:
        client.set(key,value)
    except Exception as e:
        logger.info("set str exception:" + traceback.format_exc())
        return False
    return True

def getListValues(client,key):
    return client.lrange(key,0,-1)

#以LPUSH的方式进行添加数据
def addListValue(client,key,value):
    logger.info("redis set operate:" + key)
    client.lpush(key,value)

def setHashField(client,key,field,value):
    logger.info("redis set operate:" + key + ' ,field: ' + field)
    if key == '' or key is None or field == '' or field is None or value == '' or value is None:
        return False
    try:
        client.hset(key,field,value)
    except Exception as e:
        logger.info("set hash exception: " + traceback.format_exc())
        return False
    return True

def getHashField(client,key,field):
    logger.info('redis: get hash field')
    return client.hget(key,field)


#hgetall
def getHashValues(client,key):
    return client.hgetall(key)

def deleteKey(client,key):
    client.delete(key)

