#-*- coding:utf-8 -*-
import glob,redis,json
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)


if __name__=='__main__':
    key = '2017301288241_130001'
    res = client.get(key)
    print json.loads(res)