#-*- coding:utf-8 -*-
from PIL import Image
from io import BytesIO,StringIO
import os
import glob
import config
import shutil
import imghdr


def saveAndCopyImg(file,originPath,desPath,imgNameId,ext):
    '''
    保存原图和缩略图并将原图和缩略图复制到最新版本路径下
    :param file:
    :param originPath:
    :param desPath:
    :param imgNameId:
    :param ext:
    :return:
    '''
    filename = imgNameId + ext
    filePath = config.basePath + originPath + filename
    thumbPath1 = config.basePath + originPath + imgNameId + '_' + str(config.thumbSize1[0]) + '_' + str(config.thumbSize1[1]) + ext
    thumbPath2 = config.basePath + originPath + imgNameId + '_' + str(config.thumbSize2[0]) + '_' + str(config.thumbSize2[1]) + ext
    #save
    saveDir = config.basePath + originPath
    makeDirs(saveDir)
    file.save(filePath)
    saveThumbnailImg(filePath, thumbPath1, config.thumbSize1)
    saveThumbnailImg(filePath, thumbPath2, config.thumbSize2)
    # copy

    copyImgPath = config.basePath + desPath + filename
    copyThumbPath1 = config.basePath +desPath + imgNameId + '_' + str(config.thumbSize1[0]) + '_' + str(config.thumbSize1[1]) + ext
    copyThumbPath2 = config.basePath + desPath + imgNameId + '_' + str(config.thumbSize2[0]) + '_' + str(config.thumbSize2[1]) + ext
    copyDir = config.basePath + desPath
    makeDirs(copyDir)
    if not os.path.isfile(copyImgPath):
        shutil.copyfile(filePath, copyImgPath)
    if not os.path.isfile(copyThumbPath1):
        shutil.copyfile(thumbPath1, copyThumbPath1)
    if not os.path.isfile(copyThumbPath2):
        shutil.copyfile(thumbPath2, copyThumbPath2)


def saveImgFromStream(binary,imgPath,filePath):
    pass

def saveThumbnailImg(srcImgPath,desImgPath,size):
    im = Image.open(srcImgPath)
    im.thumbnail(size,Image.ANTIALIAS)
    im.save(desImgPath)


def makeDirs(*paths):
    for path in paths:
        index = path.rfind('/')
        dirPath = path[0:index]
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)


if __name__=="__main__":
    pass