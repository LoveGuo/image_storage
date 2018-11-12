# -*- coding:utf-8 -*-
import redis

pool = redis.ConnectionPool(host='10.50.167.111', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)

def vaildConnect():
    v1 = client.get('k1')
    print v1



if __name__=='__main__':
    vaildConnect()