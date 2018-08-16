#-*- coding:utf-8 -*-

import json
import traceback
import os,shutil
import redis
from flask import Flask, request, jsonify,make_response
# from iptcinfo import IPTCInfo

import appLogic
from config import logger, UPLOAD_FOLDER, ALLOWED_EXTENSIONS,basePath,thumbSize1
from utils import redisUtils
from utils import utils
from utils.parseUtils import parseJson
from utils.timeUtils import getCurrentTime
import ast
from PIL import Image
from cStringIO import StringIO
from utils import utils
import glob

app = Flask(__name__)

#redis
pool = redis.ConnectionPool(host='127.0.0.1',port=6379,decode_responses=True)
client = redis.Redis(connection_pool=pool)

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


@app.route("/test")
def hello():
    return "success"

# @app.route("/uploadJson",methods=['POST'])
# def uploadCase():
#     ''' 此接口暂时不用
#     ? 申请号和文献号传值 和公告图
#     两种方式上传json和xml
#     json方式：
#         1.解析json，并保存图片到原始目录和图片目录
#         2.保存redis
#         3.组合json
#     xml方式：
#
#     1.将zip文件保存到根目录
#     2.解压到o目录
#     3.将解压图片生成缩略图，存放在原图目录
#     4.根据解压的xml，构建json保存到redis中。
#         origin:解析
#         lastVersion:""
#         authVersion:""
#     :param shenqingh: 申请号
#     :param documentType: 文献类型
#     :param caseZip: 案件zip
#     :return:
#     '''
#     out = {"ok":True}
#     # shenqingh = request.values.get('shenqingh')
#     # documentType = request.values.get('documentType')
#     shenqingh = '1234'
#     documentType = '5678'
#     valid = utils.isValid(str(shenqingh),str(documentType))
#     if not valid:
#         raise InvalidUsage("shenqingh or documentType invalid",status_code=410)
#     formDict = request.form.to_dict()
#     logger.info("request forms: " + str(formDict))
#     originPath = utils.getOriginPath(shenqingh,documentType)
#     lastVersionPath = utils.getCaseImgPath(shenqingh,documentType)
#     data = parseJson(request,formDict, originPath, lastVersionPath)
#     #添加origin,添加当前版本，组合originJson
#     originKey = utils.getKey(shenqingh,documentType,'origin')
#     lastVersionKey = utils.getKey(shenqingh,documentType,'')
#     originJson = {}
#     originJson['date'] = getCurrentTime()
#     # originJson['notice']=         # 处理公告图片，上传时公告图片如何传递
#     originJson['data'] = data
#     logger.info(originKey + ' :  ' + str(originJson))
#     redisUtils.addListValue(client,originKey,originJson)
#     lastValue = redisUtils.getStrValue(client,lastVersionKey)
#     #如果pid_value为None，说明是上传新案件，否则为某案件多次上传。
#     lastVersion = appLogic.handler(originJson,lastVersionPath)
#     if lastValue is None:
#         resultJson = {}
#         resultJson['pid'] = lastVersionKey
#         # resultJson['notice'] = ''  # 处理公告图片，上传时公告图片如何传递
#         resultJson['lastVersion'] = lastVersion
#         logger.info(lastVersionKey + '  :  ' + str(resultJson))
#         redisUtils.setStrValue(client, lastVersionKey, resultJson)
#     else:
#         oldJson = ast.literal_eval(lastValue)
#         logger.info(oldJson)
#         oldJson['lastVersion']['data'].append(lastVersion)
#         newJson = json.dumps(oldJson)
#         logger.info(lastVersionKey + '  :  ' + str(newJson))
#         redisUtils.setStrValue(client,lastVersionKey,newJson)
#
#     response = make_response(jsonify(response=out))
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'POST'
#     response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
#
#     return response

@app.route('/upload',methods=['POST'])
def uploadXMLCase():
    '''
    {
"shenqingh":"201830064781X",//申请号
"wenjianlx":"130001",//文件类型
"fid":"GD000157639932",//文件id
"url":"ftp://efsftp_w:123456@10.1.10.229:21/20180719/13/494306658.zip",
"urltype":"0"//文件获取方式 0-ftp方式获取
}
    通过申请号、文献类型、日期上传zip
    上传相同案件、上传不同案件
    :return:
    '''
    #1.获取ftp列表json
    jsonData = request.get_json('jsonData')
    if jsonData is None:
        raise InvalidUsage('<uploadXMLCase> @ get params exception',status_code=401)
    if 'cases' in jsonData.keys():
        cases = jsonData['cases']
    for case in cases:
        #2.从ftp服务器下载zip到origin,并解压到modify目录
        try:
            logger.info("download start")
            appLogic.ftpDownload(case)
            logger.info("download end")
        except Exception as e:
            logger.info(traceback.format_exc())
        #4.解析xml文件,并保存到redis
        logger.info("save redis start")
        appLogic.parseXmlToJson(case,client)
        logger.info("save redis end")


@app.route('/image/load',methods=['GET'])
def loadData(shenqingh,documentType):

    '''
    第一次最上面公告
    获取pid:origin ，pid 对应的json进行组装成新的json。
    将最新版和授权版进行返回
    :param shenqingh:
    :param documentType:
    :return: 组装后的json
    '''
    #1.获取整体json
    key = utils.getKey(shenqingh,documentType,'')
    value = redisUtils.getStrValue(client,key)
    if value is not None:
        resultJson = json.loads(value)
    authKey = utils.getKey(shenqingh,documentType,'auth')
    #2.获取授权版
    authValue = redisUtils.getStrValue(client,authKey)
    if authValue is not None:
        authJson = json.loads(authValue)
        resultJson['authVersion'] = authJson
    return resultJson


# @app.route('/image/modify',methods=['PUT,POST'])
# def modifyImg(shenqingh,documentType):
#     '''
#     ?结构中图片版本如何更新
#     ？前端如何维护图片的版本号
#     :param shenqingh:
#     :param documentType:
#     :param img_id:
#     :param img_version:
#     :param img_base64:
#     :param operate:
#     :return: 最高版本号
#     '''
#     try:
#         pic_name = request.values.get('pic_name')
#         rotate_desc = request.values.get('rotate_desc')
#         img_str = request.values.get('image_data')
#         img_str = img_str.replace('\n', '').replace('\r', '').replace(' ', '+')
#         img_base64 = img_str.decode('base64')
#     except Exception as e:
#         logger.info(traceback.format_exc())
#         raise InvalidUsage('Invalid "img" param, must be a blob string',
#                        status_code=431)
#     try:
#         tmpImg = Image.open(StringIO.StringIO(img_base64))
#         #path
#         nameIndex1 = pic_name.rfind('~')
#         nameIndex2 = pic_name.rfind('.')
#         picName = pic_name[0:nameIndex1] + pic_name[nameIndex2:]
#         #从json获取图片版本号并加一
#         key = utils.getKey(shenqingh,documentType)
#         value = redisUtils.getStrValue(key)
#         if value is not None:
#             valueJson = json.loads(value)
#             version = getVersion(valueJson,picName)
#             picName = pic_name[0:nameIndex1] + '~' + str(version) + pic_name[nameIndex2:]
#             img_path = basePath + utils.getAuthImgPath(shenqingh,documentType) + picName
#             tmpImg.save(img_path)
#             #添加描述信息
#             info = IPTCInfo(picName, force=True)
#             info.data['keywords'] = [rotate_desc]
#             info.save()
#             # info.saveAs(picName)
#     except Exception as e:
#         logger.info(traceback.format_exc())
#         raise InvalidUsage('save update image fail ',
#                            status_code=432)
#     return version

@app.route('/tree/modify',methods=['POST'])
def modifyTree(shenqingh,documentType):
    jsonData = request.get_json()
    json_str = json.dumps(jsonData)
    key = utils.getKey(shenqingh,documentType)
    redisUtils.setStrValue(client,key,json_str)

# @app.route('/image/saveAuthImgs',methods=['POST'])
# def saveAuthImgs(shenqingh,documentType,json):
#     '''
#     修改下 保存图片  存储redis
#     流程：
#     1.删除上一版本图片
#     2.将图片保存到授权路径下
#     3.修改授权json
#     4.存储redis
#     :param authImg_zip: 图片和xml
#     :return:
#     '''
#     key = utils.getKey(shenqingh,documentType)
#     value = redisUtils.getStrValue(client,key)


@app.route('/image/thumbImgs', methods=['POST'])
def thumbImgs():
    '''
    将当前文件夹下的所有图片生成相应的缩略图到指定的目录
    :return:
    '''
    srcImgPath = request.values.get('srcImgPath')
    desImgPath = request.values.get('desImgPath')
    logger.info("srcImgPath: " + srcImgPath + ' desImgPath: ' + desImgPath)
    weight = int(request.values.get('weight',default=210))
    height = int(request.values.get('height',default=210))
    if srcImgPath is None or desImgPath is None:
        raise InvalidUsage('<thumbImgs> @ get Params exception',status_code=401)
    if not os.path.exists(srcImgPath):
        raise InvalidUsage('<thumbImgs> @ ' + srcImgPath + ' is not exists',status_code=401)
    else:
        size = (weight, height)
        files = os.listdir(srcImgPath)
        for file in files:
            logger.info("file: " + file)
            try:
                if not os.path.isdir(srcImgPath + '/' +file) and 'JPG' in file:
                    fileId,ext = os.path.splitext(file)
                    saveImgPath = desImgPath + '/' + fileId + '_' + str(weight) + '_' + str(height) + ext
                    im = Image.open(srcImgPath + '/' + file)
                    im.thumbnail(size)
                    im.save(saveImgPath)
            except Exception as e:
                logger.info(traceback.format_exc())
        out = {'status':200}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/image/copyDir',methods=['POST'])
def copyDir():
    '''
    复制文件夹所有图片到指定目录
    :return:
    '''
    srcPath = request.values.get('srcPath')
    desPath = request.values.get('desPath')
    if srcPath is None or desPath is None:
        raise InvalidUsage('<copyDir> @ get param exception', status_code=401)
    if not os.path.exists(srcPath):
        raise InvalidUsage('<copyDir> @ ' + srcPath + ' dir is not exist', status_code=401)
    else:
        files = os.listdir(srcPath)
        for file in files:
            try:
                if not os.path.isdir(srcPath + '/' +file):
                    if not os.path.exists(desPath):
                        os.makedirs(desPath)
                    shutil.copyfile(srcPath + '/' + file, desPath + '/' + file)
            except Exception as e:
                logger.info(traceback.format_exc())
        out={'status':200}

    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response



# @app.route()
# def CreateJson():
#     pass

@app.route('/redis/saveStr',methods=['POST'])
def saveStrValue():
    key = request.values.get('key')
    value = request.values.get('value')
    redisUtils.setStrValue(client,key,value)
    out = {"status":200}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/redis/getStr',methods=['POST'])
def getStrValue():
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('documentType')
    if shenqingh is None or documentType is None:
        raise InvalidUsage('<getStrValue> @ get params exception',status_code=401)
    try:
        str = redisUtils.getStrValue(client,shenqingh + '_' +documentType)
    except Exception as e:
        logger.info(traceback.format_exc())
    out = {'data': str}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

# def response(out):
#     response = make_response(jsonify(response=out))
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'POST'
#     response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
#     return response

@app.route('/upload/singleImg',methods=['POST'])
def saveSingleImg():
    '''
    保存单个图片到指定的目录
    :return:
    '''
    file = request.files['file']
    filePath = request.values.get('filepath')
    if file is None  or filePath is None :
        raise InvalidUsage('<saveSingleImg> @ get file exception',status_code=401)
    index = filePath.rfind("/")
    filedir = filePath[0:index]
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    try:
        file.save(filePath)
    except Exception as e:
        logger.info(traceback.format_exc())
    out = {'status':200}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/redis/updateStr',methods=['POST'])
def updateStrValue():
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('documentType')
    value = request.values.get('value')
    if shenqingh is None or documentType is None:
        raise InvalidUsage('<updateStrValue @ get param exception>',status_code=401)
    try:
        redisUtils.setStrValue(client,shenqingh+'_'+documentType,value)
    except Exception as e:
        logger.info(traceback.format_exc())
    out = {"status":200}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/image/resize',methods=['POST'])
def UpdateImgSize():
    imgPath = request.values.get('imgPath')
    weight = request.values.get('weight',default=210)
    height = request.values.get('height',default=210)
    if imgPath is None:
        raise InvalidUsage('<UpdateImgSize> @ get param exception',status_code=401)
    if not os.path.isfile(imgPath):
        raise InvalidUsage('<UpdateImgSize> @ file is not exist',status_code=402)
    try:
        size = (int(weight),int(height))
        im = Image.open(imgPath)
        im.resize(size,Image.ANTIALIAS)
        index = imgPath.rfind('/')
        filename = imgPath[index +1:]
        fileId,ext = os.path.splitext(filename)
        desname = imgPath[:index + 1] + fileId + '_' + weight + '_' + height +ext
        im.save(desname)
    except Exception as e:
        logger.info(traceback.format_exc())
    response = make_response(jsonify(response={"status":200}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route("/saveImgs",methods=['POST'])
def SaveImgs():
    file = request.files['file']
    filePath = request.values.get('filepath')
    if file is None or filePath is None:
        raise InvalidUsage('<saveSingleImg> @ get file exception', status_code=401)
    index = filePath.rfind("/")
    filedir = filePath[0:index]
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    try:
        file.save(filePath)
        utils.unzip(filePath, filedir)
    except Exception as e:
        logger.info(traceback.format_exc())
    out = {'status': 200}
    response = make_response(jsonify(response=out))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route("/createJson",methods=['POST'])
def CreateAuthJson():
    shenqingh = request.values.get('shenqingh')
    documentType = request.values.get('documentType')
    path = request.values.get('path')
    files = glob.glob(path + '/*.JPG')
    json = {}
    json['name'] = []
    for file in files:
        filename = os.basename(file)
        logger.info("file: " + filename)
        json['name'].append(filename)
    redisUtils.setStrValue(client,shenqingh+'_'+documentType+'_auth',str(json))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,use_reloader=True)