#-*- coding:utf-8 -*-
import glob,shutil
from utils import utils,redisUtils
import os
from config import thumbSizeList
import appLogic
import json
import redis
import traceback
import sys

reload(sys)
sys.setdefaultencoding('utf8')

pool = redis.ConnectionPool(host='10.75.13.114', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=pool)

localLibPath = '/data/storage/localLibs/'

#情况一：
def handleLocalLib(case):
    '''
    case的key包含shenqingh,documentType,submitDate,fid,zipFileName
    添加本地的原始压缩包到正确位置并解析，最后保存到redis
    :return:
    '''
    if case.has_key('shenqingh') and case.has_key('wenjianlx') and case.has_key('submitDate') \
        and case.has_key('fid') and case.has_key('zipFileName'):
        shenqingh = case['shenqingh']
        documentType = case['wenjianlx']
        submitDate = case['submitDate']
        fid = case['fid']
        zipFileName = case['zipFileName']
    else:
        print "failed,not Shenqingh or wenjianlx or submitDate or fid or zipFileName!"
        return
    #1.获取原始目录，并判断原始目录下是否包含该压缩包或其他文件，若包含则打印并退出
    originDir = utils.getOriginBasePath(shenqingh,documentType,submitDate,fid)
    files = glob.glob(originDir)
    if len(files) > 0:
        print "failed,origin path exist other files, Path: " + originDir
    else:
        try:
            #2.复制原始包到原始目录，解压，生成缩略图，复制当前目录
            originPath = utils.createOriginDir(shenqingh,documentType,submitDate,fid)
            srcZipFile = localLibPath + zipFileName
            desZipFile = originPath + '/' + zipFileName
            if not os.path.isfile(srcZipFile):
                print "failed,local zip not exists, zip file: " + zipFileName
            else:
                success = handleZip(case,srcZipFile,originPath,desZipFile)
                if success == 0:
                    print "failed, zip handle failed!"
                    appLogic.deleteAll(case)
                    return
                # 4.解析xml文件为json结构
                originJson, currentJson, noticePath = appLogic.parseXmlToJson(case)
                if len(originJson) == 0 or len(currentJson) == 0:
                    appLogic.deleteAll(case)
                    print 'failed, parse xml failed and delete all,origin path: ' + originPath
                    return
                # 原始结构添加公告图
                originJson['notice'] = noticePath
                # 将原始数据保存到redis
                originKey = utils.getKey(shenqingh, documentType, 'origin')
                originValueStr = json.dumps(originJson, ensure_ascii=False, encoding='utf-8')
                success = redisUtils.setHashField(client, originKey, fid, originValueStr)
                if success == 0:
                    appLogic.deleteAll(case)
                    print 'failed, redis set failed and delete all,origin path: ' + originPath
                    return
                # 组合当前版json =>生成原始时同时生成当前版
                # 获取以前的当前版json
                currentKey = utils.getKey(shenqingh, documentType, '')
                oldCurrent = redisUtils.getStrValue(client, currentKey)
                if oldCurrent == 0:
                    appLogic.deleteAll(case)
                    print 'failed, redis get failed and delete all,origin path: ' + originPath
                    return
                if oldCurrent is None:
                    context = {}
                    context['pid'] = shenqingh + '_' + documentType
                    context['notice'] = noticePath
                    lastVersion = []
                    lastVersion.append(currentJson)
                    context['lastVersion'] = lastVersion
                    contextStr = json.dumps(context, ensure_ascii=False, encoding='utf-8')
                else:
                    oldCurrentDict = json.loads(oldCurrent)
                    if noticePath != '':
                        oldCurrentDict['notice'] = noticePath
                    oldCurrentData = oldCurrentDict['lastVersion']
                    oldCurrentData.append(currentJson)
                    contextStr = json.dumps(oldCurrentDict, ensure_ascii=False, encoding='utf-8')
                success = redisUtils.setStrValue(client, currentKey, contextStr)
                if success == 0:
                    appLogic.deleteAll(case)
                    return
        except Exception as e:
            appLogic.deleteAll(case)
            print traceback.format_exc()
            return
        print "success!"


def handleZip(case,srcZipFile,desDir,desZipFile):
    '''
    复制原始包到原始目录，解压，生成缩略图，复制当前目录
    :return:
    '''
    shutil.copyfile(srcZipFile, desZipFile)
    utils.unzip(desZipFile, desDir)
    # 验证xml文件是否唯一
    files = glob.glob(desDir + '/*.xml')
    if len(files) != 1:
        print 'failed,xml files != 1,delete originDir!,originDir: ' + desDir
        shutil.rmtree(desDir)
        return 0
    # 3.删除压缩包
    # 4.将原始目录中的图片生成缩略图到原图同一文件夹下
    for thumb in thumbSizeList:
        appLogic.thrumbImgs(desDir, desDir, thumb[0], thumb[1])
    #5.复制原始目录到当前版目录下
    modifyPath = utils.createModifyDir(case['shenqingh'], case['wenjianlx'], case['submitDate'], case['fid'])
    appLogic.copyDir(desDir, modifyPath)
    return 1



if __name__=='__main__':
    case1 = {
        "shenqingh":"2017301303877",
        "wenjianlx":"130001",
        "submitDate":"20170418",
        "fid":"DA000127288410",
        "zipFileName":"427897536.zip"
    }
    case2 = {
        "shenqingh": "2017301420936",
        "wenjianlx": "130001",
        "submitDate": "20170425",
        "fid": "DA000127816602",
        "zipFileName": "429120611.zip"
    }
    handleLocalLib(case1)
    handleLocalLib(case2)