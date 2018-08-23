#-*- coding:utf-8 -*-
import glob
import os,json
import shutil
import traceback
from ftplib import FTP
from xml.dom import minidom
from utils import redisUtils
from PIL import Image, ImageFile

from config import ipPort, authPath
from config import logger, thumbSizeList
from utils import utils

ImageFile.LOAD_TRUNCATED_IMAGES = True

def ftpDownload(client,case):
    '''
    入库授权路径：storage/auth/year/month/day/hour/申请号/文献类型/abc.zip
    :param case:
    :return:
    '''
    flag = True
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    fid = case['fid']
    url = case['url']
    logger.info("ftp url : " + str(url))
    submitDate = case['submitDate']
    user, passwd, host, port, fileName = getFtpInfo(url)
    fileIndex = fileName.rfind('/')
    fileName2 = fileName[fileIndex + 1:]
    ftp = FTP()
    try:
        #1.创建授权文件夹
        fileDir = getAuthDir(shenqingh, documentType, submitDate, fid)
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        file = fileDir + '/'+ fileName2
        #1.下载
        ftp.connect(host, int(port))
        ftp.login(user,passwd)
        with open(file,'wb') as f:
            ftp.retrbinary('RETR ' + fileName, f.write)
        ftp.quit()
        #2.解压到原始目录下
        logger.info("解压")
        utils.unzip(file,fileDir)
        files = glob.glob(fileDir + '/*.xml')
        if len(files) != 1:
            logger.info("xml文件个数不为1,删除目录，路径为：" + fileDir)
            if os.path.exists(fileDir):
                shutil.rmtree(fileDir)
            return False
        #3.删除压缩包
        #4.将原始目录中的图片生成缩略图到原图同一文件夹下
        logger.info("缩略图")
        for thumb in thumbSizeList:
            thrumbImgs(fileDir, fileDir, thumb[0], thumb[1])
        return True
    except Exception as e:
        #发生异常后将下载的压缩包进行删除
        if os.path.exists(fileDir):
            shutil.rmtree(fileDir)
        logger.info(traceback.format_exc() + '---' + str(case))
        return False


def parseXmlToJson(case):
    result = {}
    shenqingh = case['shenqingh']
    documentType = case['wenjianlx']
    submitDate = case['submitDate']
    fid = case['fid']
    #获取xml文件名
    path = getAuthDir(shenqingh,documentType,submitDate,fid)
    files = glob.glob(path + '/*.xml')
    if len(files) != 1:
        logger.info("xml文件个数不为1 且path：" + path)
        if os.path.exists(path):
            shutil.rmtree(path)
        return result
    #1.解析xml文件
    xmlDataList = parsexml(files[0])
    authJson = {}
    #授权文件路径，再次插入时进行删除使用
    authJson['path'] = path
    data = []
    authJson['noticePath'] = ''
    for xmlData in xmlDataList:
        child = {}
        child['ori_name'] = xmlData['logicalName'].encode('utf-8')
        child['path'] = ipPort + path + '/' + xmlData['physicalName']
        child['version'] = 0
        child['date'] = submitDate
        keys = extractWord(xmlData['logicalName'])
        child['name'] = keys[-1]
        #2.解析xml to json
        toOriginJson(data,keys,child)
        #3.处理公示图
        if xmlData['fengpiFlag'] == '1':
            authJson['noticePath'] = child['path']
    authJson['data'] = data
    return authJson


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
            if not os.path.isdir(srcImgPath + '/' + file) and not '_' in file and not 'xml' in file and 'zip' not in file :
                fileId, ext = os.path.splitext(file)
                saveImgPath = desImgPath + '/' + fileId + '_' + str(weight) + '_' + str(height) + ext
                im = Image.open(srcImgPath + '/' + file)
                im.thumbnail(size)
                im.save(saveImgPath)
        except Exception as e:
            logger.info(traceback.format_exc())


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
        try:
            if not os.path.isdir(srcPath + '/' + file):
                if not os.path.exists(desPath):
                    os.makedirs(desPath)
                shutil.copyfile(srcPath + '/' + file, desPath + '/' + file)
        except Exception as e:
            logger.info(traceback.format_exc())


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
        else:
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


def getNoticePath(name):
    if name == '立体图':
        return False, True
    elif name == '主视图':
        return True, True
    return True, False


def deleteAuthDir(client,authKey):
    authJson = redisUtils.getStrValue(client,authKey)
    if authJson is not None:
        authDic = json.loads(authJson)
        oldPath = authDic["path"]
        logger.info("delete old dir: " + authKey + " , " + oldPath)
        #删除旧文件
        if os.path.exists(oldPath):
            shutil.rmtree(oldPath)
        #删除redis中数据
        redisUtils.deleteKey(client,authKey)



def getAuthDir(shenqingh,documentType,submitDate,fid):
    # storage/auth/year/month/day/hour/申请号/文献类型/abc.zip
    year = submitDate[0:4]
    month = submitDate[5:7]
    day = submitDate[8:10]
    hour = submitDate[11:13]
    return authPath + year + '/' + month + '/' + day + '/' + hour + '/' + shenqingh + '/' + documentType + '/' + fid


def parsexml(path):
    result = []
    doc = minidom.parse(path)
    root = doc.documentElement
    imageNodes = root.getElementsByTagName('image')
    for imageNode in imageNodes:
        dic = {}
        physicalNameNode = imageNode.getElementsByTagName('physical-name')[0]
        physicalName = physicalNameNode.childNodes[0].nodeValue
        logicalNameNode = imageNode.getElementsByTagName('logical-name')[0]
        logicalName = logicalNameNode.childNodes[0].nodeValue
        fengpiFlagNode = imageNode.getElementsByTagName('fengpi-flag')[0]
        fengpiFlag = fengpiFlagNode.childNodes[0].nodeValue
        dic['physicalName'] = physicalName
        dic['logicalName'] = logicalName
        dic['fengpiFlag'] = fengpiFlag
        result.append(dic)
    return result



if __name__=="__main__":
    # print getFtpInfo("ftp://efsftp_w:123456@10.1.10.229:21/20180719/13/494306658.zip")
    print extractWord('主视图'.encode('utf-8'))