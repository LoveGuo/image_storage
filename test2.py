#-*- coding:utf-8 -*-
import glob,redis
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)


if __name__=='__main__':
    key = '2017301167196_130001_o'
    field = 'GD000126680358'
    print client.hget(key, field)