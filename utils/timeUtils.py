#-*- coding:utf-8 -*-
import time

def getCurrentYMD():
    return time.strftime("%Y-%m-%d",time.localtime(time.time()))


def getCurrentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))