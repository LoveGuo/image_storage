#-*- coding:utf-8 -*-
import os
import traceback
import logging
import cv2
from PIL import Image

'''
    添加缩略图：遍历文件夹下所有的图片，在本文件夹下生成相应的缩略图
'''

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("appendthumb.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

#缩略图大小
thumbSizeList=((90,90))



def thrumbImg(names,filePath,formatList):
    '''
    缩略单个图片到相同目录下
    :param srcImgPath:
    :param desImgPath:
    :param weight:
    :param height:
    :return:
    '''
    for format in formatList:
        try:
            saveImgPath = filePath.replace('.','_' + str(format[0]) + '_' + str(format[1]) + '.')
            #判断是否存在该压缩图片
            index = saveImgPath.rfind('/')
            fileName = saveImgPath[index + 1:]
            if fileName in names:
                continue
            im = cv2.imread(filePath)
            channels = cv2.split(im)
            if channels != 3:
                pilHandler(im,saveImgPath,format)
            else:
                cvHandler(im,saveImgPath,format)
        except Exception as e:
            logger.info("thumb exception, img path: " + filePath + traceback.format_exc())


def pilHandler(im,saveImgPath,format):
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255 - x)
            im = im.convert('RGB')
            im.paste((255, 255, 255), None, bgmask)
        else:
            im = im.convert('RGB')
    im.thumbnail(format, Image.ANTIALIAS)
    im.save(saveImgPath, quality=100)


def cvHandler(im,saveImgPath,size):
    h, w = im.shape[0],im.shape[1]
    if h > size[0]:
        w = int(max(w * size[0] / h, 1))
        h = int(size[0])
    if w > size[1]:
        h = int(max(h * size[1] / w, 1))
        w = int(size[1])
    size = (w,h)
    im = cv2.resize(im,size)
    cv2.imwrite(saveImgPath,im)


#递归遍历文件夹，查找是否存在图片
def getRecurFile(filePath):
    names = os.listdir(filePath)
    if len(names) > 0:
        for name in names:
            path = filePath + '/' + name
            if os.path.isdir(path):
                getRecurFile(path)
                continue
            elif name.find('.zip') != -1 or name.find('.xml') != -1 or name.find('_') != -1 \
                    or name.find('~') != -1 or name.find('.tif') or name.find('.TIF') != -1:
                continue
            else:
                thrumbImg(names,path,thumbSizeList)



def main():
    pref = '/wgzstxqy/data/'
    PATHS = ['2009']
    for PATH in PATHS:
        PATH = pref + PATH
        logger.info("PATH: " + PATH)
        getRecurFile(PATH)
    logger.info("end!")


if __name__=='__main__':
    main()