#-*- coding:utf-8 -*-
from PIL import Image
import traceback
from PIL import ImageFile
import matplotlib.pyplot as plt
# ImageFile.LOAD_TRUNCATED_IMAGES = True

def thrumbImg():
    '''
    缩略单个图片到相同目录下
    :param srcImgPath:
    :param desImgPath:
    :param weight:
    :param height:
    :return:
    '''
    size = [90,90]
    saveImgPath = '1_90.jpg'
    try:
        im = Image.open('1.jpg')
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
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(saveImgPath,quality=100)
    except Exception as e:
        print traceback.format_exc()


def io():
    import cv2
    size = (90,90)
    saveImgPath = '2_90_90.TIF'
    im = cv2.imread('2.TIF')
    h, w = im.shape[0], im.shape[1]
    if h > size[0]:
        w = int(max(w * size[0] / h, 1))
        h = int(size[0])
    if w > size[1]:
        h = int(max(h * size[1] / w, 1))
        w = int(size[1])
    size = (w, h)
    im = cv2.resize(im, size)
    cv2.imwrite(saveImgPath, im)



if __name__ == '__main__':
    # thrumbImg()
    io()