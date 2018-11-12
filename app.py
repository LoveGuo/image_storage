#-*- coding:utf-8 -*-
import base64
import json
import os
import redis,shutil
import sys
import traceback
from flask import Flask, request, jsonify, make_response
import appLogic
from config import logger, thumbSizeList
from utils import redisUtils, utils
from utils.parseUtils import getVersionPath
import migrateLogic
from utils import ImagePathUtils
import time
from utils import oracleUtils
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

#redis
redisPool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
client = redis.Redis(connection_pool=redisPool)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        logger.info("InvalidUsage info : " + str(rv))
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/hello")
def hello():
    time.sleep(10)
    return "hello!"


@app.route('/upload',methods=['POST'])
def uploadXMLCase():
    '''
        从ftp服务器下载zip压缩包,解压到原始文件夹，
        将文件夹中的图片生成缩略图
        解析xml为originJson,currentJson,
        将生成的json保存到redis中
        公告图以最后一个fid为准
    :return:
    '''
    #1.获取ftp列表json
    jsonData = request.get_json()
    logger.info("upload: " + str(jsonData))
    if jsonData is None:
        logger.info("获取参数错误："  + str(jsonData))
        return jsonify({'status': 0})
    if 'cases' in jsonData.keys():
        cases = jsonData['cases']
    for case in cases:
        if appLogic.validCase(case) == 0:
            return jsonify({'status': 0})
        currentDir,zipDir,zipFile = appLogic.getZipFilePath(case)
        if os.path.isfile(zipFile):
            logger.info("文件已经存在，跳过")
            continue
        try:
            shenqingh = case['shenqingh']
            documentType = case['wenjianlx']
            fid = case['fid']
            #2.从ftp服务器下载zip到origin,并解压到origin文件夹下 #下载、解压、缩略图、复制
            flag = appLogic.ftpDownload(case)
            if flag == 0:
                appLogic.deleteAll(case)
                logger.info('申请号：' +shenqingh + ' ,文件类型： ' + documentType + ' ,fid: ' + fid + ' : download Failed!')
                return jsonify({'status': 0})
            #4.解析xml文件为json结构
            originJson,currentJson,noticePath = appLogic.parseXmlToJson(case)
            if len(originJson) == 0 or len(currentJson) == 0:
                appLogic.deleteAll(case)
                logger.info('申请号：' + shenqingh + ' ,文件类型： ' + documentType + ' ,fid: ' + fid + ' : xml parse exception!')
                return jsonify({'status': 0})
            # 原始结构添加公告图
            originJson['notice'] = noticePath
            # 将原始数据保存到redis
            originKey = utils.getKey(shenqingh, documentType, 'origin')
            originValueStr = json.dumps(originJson, ensure_ascii=False, encoding='utf-8')
            success = redisUtils.setHashField(client,originKey,fid,originValueStr)
            if success == 0:
                appLogic.deleteAll(case)
                return jsonify({'status': 0})
            #组合当前版json =>生成原始时同时生成当前版
            #获取以前的当前版json
            currentKey = utils.getKey(shenqingh,documentType,'')
            oldCurrent = redisUtils.getStrValue(client,currentKey)
            if oldCurrent == 0:
                appLogic.deleteAll(case)
                return jsonify({'status': 0})
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
            success = redisUtils.setStrValue(client,currentKey,contextStr)
            if success == 0:
                appLogic.deleteAll(case)
                return jsonify({'status': 0})
        except Exception as e:
            appLogic.deleteAll(case)
            logger.info('申请号：' + shenqingh + ' ,文件类型： ' + documentType + ' ,fid: ' + fid + ' : exception!')
            logger.info(traceback.format_exc())
            return jsonify({'status': 0})
    return jsonify({'status': 1})


@app.route('/getCurrentData',methods=['POST'])
def getCurrentData():

    '''
    第一次最上面公告
    获取pid:origin ，pid 对应的json进行组装成新的json。
    将最新版和授权版进行返回
    :param shenqingh:
    :param documentType:
    :return: 组装后的json
    '''
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    if shenqingh is None or documentType is None:
        raise InvalidUsage("shenqingh or documentType is None", status_code=401)
    #1.获取整体json
    key = utils.getKey(shenqingh,documentType)
    value = redisUtils.getStrValue(client,key)
    context = {}
    context['lastVersion'] = []
    if value is not None and value != 0:
        valueDict = json.loads(value)
        #路径添加前缀
        context['lastVersion'] = valueDict['lastVersion']
        ImagePathUtils.currentPreffixHandle(context,'addPrefix')
    result = json.dumps(context, ensure_ascii=False, encoding='utf-8')
    return result,{'Content-Type': 'application/json'}


@app.route('/image/load',methods=['POST'])
def loadData():

    '''
    第一次最上面公告
    获取pid:origin ，pid 对应的json进行组装成新的json。
    将最新版和授权版进行返回
    :param shenqingh:
    :param documentType:
    :return: 组装后的json
    '''

    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    if shenqingh is None or documentType is None:
        raise InvalidUsage("shenqingh or documentType is None", status_code=401)
    #1.获取当前版json
    key = utils.getKey(shenqingh,documentType)
    value = redisUtils.getStrValue(client,key)
    resultJson = {}
    if value is not None and value != 0:
        resultJson = json.loads(value)
        ImagePathUtils.currentPreffixHandle(resultJson,'addPrefix')
    authKey = utils.getKey(shenqingh,documentType,'auth')
    #2.获取授权版
    authValue = redisUtils.getStrValue(client,authKey)
    if authValue is not None and authValue != 0:
        authJson = json.loads(authValue)
        ImagePathUtils.authPreffixHandle(authJson,'addPrefix')
        resultJson['authVersion'] = authJson
    result = json.dumps(resultJson, ensure_ascii=False, encoding='utf-8')
    response = make_response(result)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/image/modify',methods=['POST'])
def modifyImg():
    '''
    ?结构中图片版本如何更新 直接提交修改图片和修改信息
    ？前端如何维护图片的版本号  ~A
    :return:
    '''
    try:
        shenqingh = request.values.get('shenqingh')
        documentType = request.values.get('wenjianlx')
        pic_name = request.values.get('pic_name')  #img path
        pic_version = request.values.get('pic_version') #img 修改版本
        rotate_desc = request.values.get('rotate_desc')
        if shenqingh is None or documentType is None or pic_name is None or pic_version is None:
            raise InvalidUsage("get params is None", status_code=401)
        try:
            img_str = request.values.get('image_data')
        except Exception as e:
            logger.info(traceback.format_exc())
            raise InvalidUsage('Invalid "img" param, must be a blob string',
                               status_code=431)
        #1.获取图片最新版本号并加1
        date, fid, imgId = appLogic.parsePath(pic_name)
        # 从json获取图片版本号并加一
        key = utils.getKey(shenqingh, documentType)
        value = redisUtils.getStrValue(client,key)
        if value is not None and value != 0:
            value = json.loads(value)
            lastVersionData = value['lastVersion']
            for context in lastVersionData:
                if context['date'] == date and context['fid'] == fid:
                    path, rotateInfo = getVersionPath(context['data'], imgId, pic_version, rotate_desc)
                    redisUtils.setStrValue(client,key,json.dumps(value, ensure_ascii=False, encoding='utf-8'))
                    index1 = path.rfind('.')
                    index2 = path.rfind('~')
                    version = path[index2 + 1:index1]
                    imgdata = base64.b64decode(img_str)
                    file = open(path, 'wb')
                    file.write(imgdata)
                    #生成缩略图
                    logger.info('thrumb path : ' + path)
                    appLogic.thrumbImg(path, thumbSizeList)
                    break
    except Exception as e:
        logger.info(traceback.format_exc())
        raise InvalidUsage('save update image fail ',status_code=432)
    out = {'version':version,"rotateInfo": rotateInfo}
    response = make_response(jsonify(out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/tree/modify',methods=['POST'])
def modifyTree():
    '''将tree保存到当前版'''
    out = {'success':True}
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    jsonData = request.values.get('tree')
    if shenqingh is None or documentType is None or jsonData is None:
        out['success'] = False
        out['message'] = 'params is None'
        raise InvalidUsage('params is None',status_code=401)
    jsonData = json.loads(jsonData)
    ImagePathUtils.currentPreffixHandle(jsonData,'clearPrefix')
    json_str = json.dumps(jsonData,ensure_ascii=False,encoding='utf-8')
    key = utils.getKey(shenqingh,documentType)
    try:
        redisUtils.setStrValue(client,key,json_str)
    except Exception as e:
        out['success'] = False
        out['message'] = 'redis operate exception'
        raise InvalidUsage('redis operate exception',status_code=405)
    response = make_response(jsonify(out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/auth/save',methods=['POST'])
def saveAuthImgs():
    '''
    修改下 保存图片  存储redis
    流程：
    1.获取json，shenqingh,documentType
    2.复制图片到授权目录
    :param authImg_zip: 图片和xml
    :return:
    '''
    out = {'success': True}
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    jsonValue = request.values.get('tree')
    if shenqingh is None or documentType is None or jsonValue is None:
        out['success'] = False
        out['message'] = 'get params exception'
        raise InvalidUsage("get params exception",status_code=401)
    jsonValue = json.loads(jsonValue)
    ImagePathUtils.authPreffixHandle(jsonValue,'clearPrefix')
    authKey = utils.getKey(shenqingh,documentType,'auth')
    authStr = json.dumps(jsonValue, ensure_ascii=False, encoding='utf-8')
    try:
        redisUtils.setStrValue(client,authKey,authStr)
    except Exception as e:
        out['success'] = False
        out['message'] = 'redis operate exception'
        raise InvalidUsage('redis operate exception', status_code=405)
    response = make_response(jsonify(out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/getOriginImgs',methods=['POST'])
def getOriginImgs():
    '''
    获取某个申请号的原始图片或者获取某个申请号的某个fid的原始图片
    :return:
    '''
    resultFailed = json.dumps(None, ensure_ascii=False, encoding='utf-8')
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    if shenqingh is None or documentType is None:
        logger.info("申请号或文件类型获取失败")
        return resultFailed, {'Content-Type': 'application/json'}
    logger.info("获取原始数据接口，申请号：" + shenqingh + " ,文件类型： " + documentType)
    key = utils.getKey(shenqingh,documentType,'origin')
    res = {}
    if 'fid' in request.values:
        fid = request.values.get('fid')
        if fid is None:
            return resultFailed, {'Content-Type': 'application/json'}
        logger.info("fid: " + fid)
        value = redisUtils.getHashField(client,key,fid)
        if value is None:
            return resultFailed, {'Content-Type': 'application/json'}
        valueDic = json.loads(value)
        ImagePathUtils.originPreffixHandle(valueDic,'addPrefix')
        res['origin'] = valueDic
        result = json.dumps(res,ensure_ascii=False, encoding='utf-8')
        return result,{'Content-Type': 'application/json'}
    else:
        valueDict = redisUtils.getHashValues(client,key)
        if valueDict is None:
            return resultFailed, {'Content-Type': 'application/json'}
        contentList = []
        for key in valueDict.keys():
            content = {}
            content['fid'] = key
            v = json.loads(valueDict[key])
            ImagePathUtils.originPreffixHandle(v,'addPrefix')
            content['data'] = v['data']
            content['date'] = v['date']
            content['notice'] = v['notice']
            contentList.append(content)
        res['origin'] = contentList
        result = json.dumps(res,ensure_ascii=False, encoding='utf-8')
    return result, {'Content-Type': 'application/json'}



@app.route('/getAuthImgs',methods=['POST'])
def getAuthImgs():
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('wenjianlx')
    if shenqingh is None or documentType is None:
        raise InvalidUsage('get params exception', status_code=401)
    authKey = utils.getKey(shenqingh,documentType,'auth')
    value = redisUtils.getStrValue(client,authKey)
    res = {}
    res['authVersion'] = ''
    if value is not None and value != 0:
        valueLoad = json.loads(value)
        ImagePathUtils.authPreffixHandle(valueLoad,'addPrefix')
        res['authVersion'] = valueLoad
    result = json.dumps(res,ensure_ascii=False,encoding='utf-8')
    return result, {'Content-Type': 'application/json'}


@app.route('/getThrumbImgs',methods=['POST'])
def getThrumbImgs():
    '''
    :return: 原始版和授权版
    '''
    paramJson = request.get_json()
    if paramJson is None:
        raise InvalidUsage('get params exception', status_code=401)
    result = {}
    for key in paramJson.keys():
        #0申请号、1文献类型
        arr = paramJson[key]
        shenqinghKey = arr[0] + '_' + arr[1]
        context = {}
        context['origin'] = []
        context['authVersion'] = {}
        originKey = utils.getKey(arr[0], arr[1], 'origin')
        originDict = redisUtils.getHashValues(client, originKey)
        for key in originDict.keys():
            fidContext = {}
            fidContext['fid'] = key
            fidData = json.loads(originDict[key])
            ImagePathUtils.originPreffixHandle(fidData,'addPrefix')
            fidContext['data'] = fidData['data']
            # fidContext['date'] = fidData['date']
            context['origin'].append(fidContext)
        authKey = utils.getKey(arr[0],arr[1],'auth')
        authStr = redisUtils.getStrValue(client,authKey)
        if authStr is not None and authStr != 0:
            authJson = json.loads(authStr)
            ImagePathUtils.authPreffixHandle(authJson,'addPrefix')
            context['authVersion'] = authJson
        result[shenqinghKey] = context
    return json.dumps(result, ensure_ascii=False, encoding='utf-8'),{'Content-Type': 'application/json'}


@app.route('/uploadAuthImgs', methods=['POST','GET'])
def uploadAuthImgs():
    '''入库接口{
    "shenqingh":"201830064781X",//申请号
    "wenjianlx":"130001",//文件类型
    "fid":"GD000157639932",//文件id  QIETUBID
    "url":"ftp://efsftp_w:123456@10.1.10.229:21/20180719/13/494306658.zip",  WENJIANLJ
    "urltype":"0",//文件获取方式 0-ftp方式获取
    "submitDate":"TIJIAORQ"
    }
    '''
    case = request.get_json()
    if appLogic.validCase(case) == 0:
        return jsonify({'status': 0})
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    # 下载文件
    flag = migrateLogic.ftpDownload(case)
    logger.info('shenqingh: ' + str(shenqingh) + 'download end!')
    if flag == 0:
        migrateLogic.deleteAuthAll(case)
        logger.info("shenqingh download exception: " + str(case))
        return jsonify({'status': 0})
    try:
        authKey = shenqingh + '_' + documentType + '_a'
        # 解析文件
        dateDict = oracleUtils.getAuthDate(shenqingh)
        authJson = migrateLogic.parseXmlToJson(case, dateDict)
        if len(authJson) == 0:
            migrateLogic.deleteAuthAll(case)
            logger.info('xml parse exception: ' + str(case))
            return jsonify({'status': 0})
        # 删除旧文件
        delSuccess = migrateLogic.deleteAuthDir(client, authKey)
        if delSuccess == 0:
            migrateLogic.deleteAuthAll(case)
            logger.info("delete old auth dir: " + str(case))
            return jsonify({'status': 0})
        # 添加redis
        addRedis = redisUtils.setStrValue(client, authKey, json.dumps(authJson, ensure_ascii=False, encoding='utf-8'))
        if addRedis == 0:
            migrateLogic.deleteAuthAll(case)
            logger.info("set redis exception: " + str(case))
            return jsonify({'status': 0})
    except Exception as e:
        migrateLogic.deleteAuthAll(case)
        logger.info(str(case) + traceback.format_exc())
        return jsonify({"status": 0})
    return jsonify({"status": 1})


if __name__ == '__main__':
    # from werkzeug.contrib.fixers import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    # app.run()
    app.run(host='0.0.0.0',port=5000,debug=True,use_reloader=True,threaded=True)
