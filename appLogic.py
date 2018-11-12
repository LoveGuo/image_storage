#-*- coding:utf-8 -*-
from config import ipPort,basePath
import os,glob,shutil
from ftplib import FTP
from config import logger,thumbSizeList,originDirName,modifyDirName
import traceback
from utils import utils,redisUtils
from xml.dom import minidom
from PIL import Image,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# def handler(originData,lastVersionPath):
#     data = originData['data']
#     for doc in data:
#         if 'path' in doc.keys():
#             doc['path'] = handlerPath(doc['path'],lastVersionPath)
#         elif 'children' in doc.keys():
#             handler(doc['children'],lastVersionPath)
#     return originData


# def handlerPath(srcPath,lastVersionPath):
#     name = srcPath.split('/')[-1]
#     return ipPort + basePath + lastVersionPath + name

def getFtpInfo(url):
    # "ftp://efsftp_w:123456@10.1.10.229:21/20180719/13/494306658.zip"
    infoStr = url.replace('ftp://','').strip()
    splits = infoStr.split('@')
    userAndPasswd = splits[0].split(':')
    user = userAndPasswd[0]
    passwd = userAndPasswd[1]
    connInfo = splits[1].split(':')
    host = connInfo[0]
    portIndex = connInfo[1].find('/')
    port = connInfo[1][0:portIndex]
    fileName = connInfo[1][portIndex:]
    return user,passwd,host,port,fileName[1:]

def getZipFilePath(case):
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    fid = case['fid']
    url = case['url']
    submitDate = case['submitDate']
    user, passwd, host, port, fileName = getFtpInfo(url)
    fileIndex = fileName.rfind('/')
    fileName2 = fileName[fileIndex + 1:]
    # utils.createOriginDir(shenqingh, documentType, submitDate, fid)
    fileDir = utils.getOriginBasePath(shenqingh, documentType, submitDate, fid)
    currentDir = utils.getModifyBasePath(shenqingh,documentType,submitDate,fid)
    return currentDir,fileDir,fileDir + '/' + fileName2



def ftpDownload(case):
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    fid = case['fid']
    url = case['url']
    submitDate = case['submitDate']
    user, passwd, host, port, fileName = getFtpInfo(url)
    fileIndex = fileName.rfind('/')
    fileName2 = fileName[fileIndex + 1:]
    ftp = FTP()
    fileDir = utils.createOriginDir(shenqingh,documentType,submitDate,fid)
    file = fileDir + '/'+ fileName2
    try:
        #1.下载
        ftp.connect(host, int(port))
        ftp.login(user,passwd)
        with open(file,'wb') as f:
            ftp.retrbinary('RETR ' + fileName, f.write)
        #2.解压到原始目录下
        success = utils.unzip(file,fileDir)
        if success == 0:
            return False
        #验证xml文件是否唯一
        files = glob.glob(fileDir + '/*.xml')
        if len(files) != 1:
            logger.info("xml文件个数不为1")
            if os.path.exists(fileDir):
                shutil.rmtree(fileDir)
            return False
        #3.删除压缩包
        #4.将原始目录中的图片生成缩略图到原图同一文件夹下
        for thumb in thumbSizeList:
            thrumbImgs(fileDir, fileDir, thumb[0], thumb[1])
        # #5.复制原始目录到当前版目录下
        modifyPath = utils.createModifyDir(shenqingh,documentType,submitDate,fid)
        copyDir(fileDir,modifyPath)
        ftp.quit()
    except Exception as e:
        logger.info(traceback.format_exc())
        return False
    return True


def parseXmlToJson(case):
    currentJson = {}
    #根据原始路径获取原始json
    originPath = utils.getOriginBasePath(case['shenqingh'],case['wenjianlx'], case['submitDate'], case['fid'])
    originJson, noticePath = getParse(case,originPath)
    if len(originJson) > 0:
        curPath = utils.getModifyBasePath(case['shenqingh'],case['wenjianlx'], case['submitDate'], case['fid'])
        #根据当前路径获取当前json
        currentJson, noticePath = getParse(case, curPath)
    return originJson,currentJson,noticePath


def getParse(case,path):
    originJson = {}
    submitDate = case['submitDate']
    fid = case['fid']
    files = glob.glob(path + '/*.xml')
    noticePath = ''
    if len(files) != 1:
        logger.info(str(case) + "xml文件个数不为1")
        shutil.rmtree(path)
        return originJson, noticePath
    xmlName = os.path.basename(files[0])
    if os.path.isfile(path + '/' + xmlName):
        # 1.读取xml文件
        xmldoc = minidom.parse(path + '/' + xmlName)
        itemlist = xmldoc.getElementsByTagName('picture')
        originJson['date'] = submitDate
        originJson['fid'] = fid
        data = []
        flag = True  # 若找到公示图则为False
        for item in itemlist:
            child = {}
            child['ori_name'] = item.attributes['origin_name'].value.encode('utf-8')
            child['path'] = path + '/' + item.attributes['picture_no'].value + '.jpg'
            child['imgUpdateNum'] = 0
            keys = extractWord(item.attributes['origin_name'].value)
            child['name'] = keys[-1]
            child['rotateDesc'] = {}
            # 2.解析xml to json
            toOriginJson(data, keys, child)
            # 3.处理公示图，如果没有立体图或主视图使用随意一张（最后一张）
            randNoticePath = child['path']
            if flag:
                flag, flag2 = getNoticePath(keys[-1])
                if flag2:
                    noticePath = child['path']
        if flag: #最后一张
            noticePath = randNoticePath
        originJson['data'] = data
    return originJson, noticePath


def toOriginJson(data,keys,child):
    if len(data) > 0 and len(keys) > 1:   #存在数据,进行插入
        elementJson = keysToJson(data, keys, child)
        isEqual(data, elementJson)
    else:  #不存在数据
        elementJson = keysToJson(data,keys,child)
        if elementJson is not None:
            data.append(elementJson)

def keysToJson(data,keys,child):
    if len(keys) == 1:  # 只有一个关键词，至少有一个关键词
        data.append(child)
    else:  # 有多个关键词
        i = len(keys) - 2
        return upParent(keys, i, child)

def isEqual(data,elementJson):
    for i in range(len(data)):
        dataJson = data[i]
        # elementJson = elementList[0]
        if 'children' in dataJson.keys() and 'children' in elementJson.keys() and data[i]['name'] == elementJson['name'] :
            children = isEqual(data[i]['children'],elementJson['children'][0])
            data[i]['children'] = children
            break
        elif i == len(data) - 1:
            data.append(elementJson)
            break
    return data



def upParent(keys, i, child):
    parent = {}
    parent['name'] = keys[i]
    parent['children'] = []
    parent['children'].append(child)

    i = i - 1
    if i >= 0:
        parent = upParent(keys,i,parent)
        return parent
    return parent




def extractWord(value):
    '''
    :param value:  字符串
    :return:  返回所有关键词 最后一个为图片名称
    '''
    value = value.encode('utf-8')
    keyword = []    #保存关键词，最后一个为图片名称
    number = ['0','1','2','3','4','5','6','7','8','9']
    keyDict = {'组件':-1,'套件':-1,'设计':-1}
    for key in keyDict.keys(): #查找关键词的位置
        index = value.find(key)
        if index == -1:
            keyDict.pop(key)
        else:
            keyDict[key] = index
    kvTupList = sorted(keyDict.items(),key=lambda item:item[1])  #关键词根据位置排序，位置小的在前
    #若不包含关键词或者关键词最小位置不等于0 则字符串为图片名称
    if len(kvTupList) == 0 or kvTupList[0][1] != 0:
        keyword.append(value)
    else:
        kvTupList.append(('valueLength',len(value)))  #列表尾插入字符串长度，用于判断是否结束
        for i in range(len(kvTupList)):
            if i + 1 < len(kvTupList):
                index1 = kvTupList[i][1]
                index2 = kvTupList[i+1][1]
                #每个汉字占3位，两个占6位
                temp = value[index1 + 6 :index2]
                # 若两个关键词之间有其他字符，则判断是否为数字，若是数字则关键词和数字组成新关键词加入数组
                #若两个关键词之间没有其他字符，则直接将关键词加入数组
                if len(temp) > 0:
                    tempIndex = 0
                    for j in range(len(temp)):
                        if temp[j] not in number:
                            tempIndex = j
                            break
                        else:
                            tempIndex = tempIndex + 1
                    if tempIndex == 0: #两个关键字之间没有数字,结束循环
                        keyword.append(value[index1:index1 + 6])
                        keyword.append(value[index1 + 6:])
                        break
                    elif tempIndex < len(temp):  #两个关键字之间有部分数字，结束循环
                        keyword.append(value[index1:index1 + 6 + tempIndex])
                        keyword.append(value[index1 + 6 + tempIndex:])
                        break
                    elif tempIndex == len(temp):  #两个关键字之间全部为数字,才可以继续下次循环
                        keyword.append(value[index1:index1 + 6 + tempIndex])
                else:
                    keyword.append(kvTupList[i][0])
    return keyword


def thrumbImgs(srcImgPath,desImgPath,weight,height):
    '''
    压缩目录下的所有图片到指定目录下
    :param srcImgPath:
    :param desImgPath:
    :return:
    '''
    size = (weight, height)
    files = os.listdir(srcImgPath)
    for file in files:
        try:
            filepath = srcImgPath + '/' + file
            if not os.path.isdir(filepath) and not '_' in file and not 'xml' in file and 'zip' not in file :
                fileId, ext = os.path.splitext(file)
                saveImgPath = desImgPath + '/' + fileId + '_' + str(weight) + '_' + str(height) + ext
                im = Image.open(srcImgPath + '/' + file)
                # originMode = im.mode
                im.thumbnail(size,Image.ANTIALIAS)
                im.save(saveImgPath,'JPEG')
        except Exception as e:
            logger.info("filepath: " + str(filepath) + traceback.format_exc())


def thrumbImg(filePath,formatList):
    '''
    缩略单个图片到相同目录下
    :param srcImgPath:
    :param desImgPath:
    :param weight:
    :param height:
    :return:
    '''
    for format in formatList:
        size = (format[0],format[1])
        saveImgPath = filePath.replace('.','_' + str(format[0]) + '_' + str(format[1]) + '.')
        im = Image.open(filePath)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(saveImgPath)


def copyDir(srcPath,desPath):
    '''
    复制文件夹
    :param srcPath:
    :param desPath:
    :return:
    '''
    logger.info('copy src: ' + srcPath + ' , des: ' + desPath)
    files = os.listdir(srcPath)
    for file in files:
        #不复制压缩包
        if file.find('.zip') != -1:
            continue
        if not os.path.isdir(srcPath + '/' + file):
            if not os.path.exists(desPath):
                os.makedirs(desPath)
            shutil.copyfile(srcPath + '/' + file, desPath + '/' + file)


def getNoticePath(name):
    if name == '立体图':
        return False, True
    elif name == '主视图':
        return True, True
    return True, False


def parsePath(path):
    '''

    :param path: http://localhost:8080/data/.../000.jpg
    :return: date fid
    '''
    #http://localhost:8080/ data / storage / 2011 / 03 / 08 / 2514 / 002011300372514 / 130001 / a / AB000000000002040495/abc.jpg
    basePathIndex = path.find(basePath)
    datas = path[basePathIndex:].replace(basePath,'').split('/')
    year = datas[0]
    month = datas[1]
    day = datas[2]
    date = year + month + day
    fid = datas[-2]
    imgName = datas[-1]
    return date, fid, imgName


#验证服务器中是否存在图片
def validRedisInfo(data):
    pass


def validCase(case):
    if 'shenqingh' not in case.keys() or 'wenjianlx' not in case.keys() or 'fid' not in case.keys() or 'url' not in case.keys() or 'submitDate' not in case.keys():
        logger.info("shenqingh or wenjianlx or fid or url or submitDate not in case keys : " + str(case))
        return 0
    else:
        shenqingh = case['shenqingh']
        documentType = case['wenjianlx']
        fid = case['fid']
        url = case['url']
        submitDate = case['submitDate']
        if shenqingh == '' or documentType == '' or fid == '' or url == '' or submitDate == '':
            logger.info('shenqingh or wenjianlx or fid or url or submitDate is none ' + str(case))
            return 0
    return 1


def deleteAll(case):
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    fid = case['fid']
    submitDate = case['submitDate']
    originPath = utils.getOriginBasePath(shenqingh,documentType,submitDate,fid)
    modifyPath = utils.getModifyBasePath(shenqingh,documentType,submitDate,fid)
    if os.path.exists(originPath):
        shutil.rmtree(originPath)
    if os.path.exists(modifyPath):
        shutil.rmtree(modifyPath)



if __name__=="__main__":
    path = "http://localhost:8080/data/storage/2011/03/08/2514/002011300372514/130001/a/AB000000000002040495/abc.jpg"
    # print parsePath(path)
    thrumbImg(path,[[40,40]])