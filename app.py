#-*- coding:utf-8 -*-

'''
外观存储接口
'''
from flask import Flask
import redis
import logging

#logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

#app
app = Flask(__name__)
#redis
# pool = redis.ConnectionPool(host='10.75.13.114',port=6379,decode_responses=True)
# r = redis.Redis(connection_pool=pool)

@app.route("/")
def hello():
    logger.info('hello')
    return "Hello World!"



def uploadCase():
    pass



if __name__ == '__main__':
    app.run(host='localhost',port=5000,debug=True)