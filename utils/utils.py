#-*- coding:utf-8 -*-
from config import basePath,logger,originDirName,authDirName,modifyDirName
import os,zipfile
import traceback

def isValid(shenqingh,documentType):
    if not shenqingh or not documentType:
        return False
    if len(shenqingh) == 0 or len(documentType) == 0:
        return False
    return True


def getPid(shenqingh,documentType):
    '''
    pid:shenqingh_documentType
    :param shenqingh:
    :param documentType:
    :return:
    '''
    return shenqingh + '_' + documentType


def getBasePath(shenqingh, documentType, submitDate):
    '''
    basePath:storage/申请号后4位/申请号(15位,不足前面补0)/文献类型/年/月/日/fid/
    :param shenqingh:
    :param documentType:
    :return:
    '''
    sqh_last_4 = shenqingh[-4:]
    sqh_15 = shenqingh
    if len(sqh_15) < 15:
        sqh_15 = '0'*(15-len(sqh_15)) + sqh_15
    return basePath + submitDate[0:4] + '/' + submitDate[4:6] + '/' + submitDate[6:8] + '/' \
           + sqh_last_4 + "/" + sqh_15 + "/" + documentType + '/'


def getOriginBasePath(shenqingh,documentType,submitDate,fid):
    '''案件的原始版路径'''
    basePath = getBasePath(shenqingh,documentType,submitDate)
    return basePath + originDirName + '/' + fid


def getAuthBasePath(shenqingh,documentType,submitDate,fid):
    '''案件的提交版路径'''
    basePath = getBasePath(shenqingh, documentType,submitDate)
    return basePath + authDirName + '/' + fid


def getModifyBasePath(shenqingh,documentType,submitDate,fid):
    '''案件修改版路径'''
    basePath = getBasePath(shenqingh, documentType,submitDate)
    return basePath + modifyDirName + '/' + fid


# def getThumbBasePath(shenqingh,documentType,submitDate,fid):
#     '''案件修改版路径'''
#     basePath = getBasePath(shenqingh, documentType,submitDate)
#     return basePath + 't/' + fid


def createOriginDir(shenqingh,documentType,submitDate,fid):
    path = getOriginBasePath(shenqingh,documentType,submitDate,fid)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def createModifyDir(shenqingh,documentType,submitDate,fid):
    path = getModifyBasePath(shenqingh,documentType,submitDate,fid)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def createAuthDir(shenqingh,documentType,submitDate,fid):
    path = getAuthBasePath(shenqingh,documentType,submitDate,fid)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


# def createThumbDir(shenqingh,documentType,submitDate,fid):
#     path = getThumbBasePath(shenqingh,documentType,submitDate,fid)
#     if os.path.exists(path):
#         os.makedirs(path)


def unzip(file,unZipPath):
    """解压zip文件到"""
    success = False
    try:
        zip_file = zipfile.ZipFile(file)
        if not os.path.exists(unZipPath):
            os.makedirs(unZipPath)
        for name in zip_file.namelist():
            zip_file.extract(name,unZipPath+"/")
        success = True
    except Exception as e:
        logger.info(traceback.format_exc())
    finally:
        zip_file.close()
        return success






def getKey(shenqingh,documentType,cate=''):
    '''生成redis中的key'''
    key = shenqingh + '_' + documentType
    if cate == 'origin':
        key = key + '_' + 'o'
    elif cate == 'auth':
        key = key + '_' + 'a'
    return key


if __name__=="__main__":
    print getBasePath("201830064781X","130001",'20170707')
