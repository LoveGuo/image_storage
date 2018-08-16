#-*- coding:utf-8 -*-
from config import logger

def getStrValue(client,key):
    return client.get(key)

def setStrValue(client,key,value):
    logger.info("redis set operate:" + key)
    client.set(key,value)

def getListValues(client,key):
    return client.lrange(key,0,-1)

#以LPUSH的方式进行添加数据
def addListValue(client,key,value):
    logger.info("redis set operate:" + key)
    client.lpush(key,value)

def setHashField(client,key,field,value):
    logger.info("redis set operate:" + key)
    client.hset(key,field,value)

def getHashField(client,key,field):
    logger.info('redis: get hash field')
    return client.hget(key,field)


#hgetall
def getHashValues(client,key):
    return client.hgetall(key)

