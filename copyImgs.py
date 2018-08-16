#-*- coding:utf-8 -*-
import os
import shutil
srcBase = '/data/imgs/'
desBase = '/home/dell/copy/'

def copy():
    count = 0
    eles = set()
    with open('train_triplet.txt','r') as f:
        lines = f.readlines()
        for line in lines:
            ls = line.split(",")
            for l in ls:
                l = l.strip()
                eles.add(l)
    print "集合长度" + str(len(eles))
    for imgPath in eles:
        imgAbsPath = srcBase + imgPath
        print imgAbsPath
        if not os.path.isfile(imgAbsPath):
            continue
        index = imgPath.rfind('/')
        dir = desBase + imgPath[0:index]
        des = desBase + imgPath
        print dir
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copyfile(imgAbsPath,des)
        count = count + 1
    print "copy count: " + str(count)

def downloadImgs():
    data = []
    count = 0
    with open('labeledImgs.json','r') as f:
        lines = f.readlines()
        for line in lines:
            handlerLine(line,data)
    for path in data:
        path1 = srcBase + path
        if os.path.isfile(path1):
            index = path.rfind('/')
            # name = path[index + 1:]
            path2 = desBase + path
            desPath = desBase + path[:index]
            if not os.path.isfile(path2):
                if not os.path.exists(desPath):
                    os.makedirs(desPath)
                count = count + 1
                shutil.copyfile(path1,path2)
            else:
                print desPath + ' file is exist'
        else:
            print path1 + 'is not file'
    print 'data: ' + str(len(data))
    print 'count' + str(count)



def handlerLine(line,data):
    # cited_rn_paths  uncited_rn_paths
    if 'cited_rn_paths' in line  or 'uncited_rn_paths' in line:
        # "cited_rn_paths":"25/200203/3125993.JPG25/200209/3300580.JPG25/201203/10666161.JPG",
        pathStr = getStr(line)
        paths = pathStr.split('.JPG')
        for path in paths:
            if len(path) > 0:
                path = path + '.JPG'
                data.append(path)
    elif 'rn_path' in line:
            path = getStr(line)
            data.append(path)

def getStr(line):
    head = line.find('\":\"')
    tail = line.rfind('\"')
    s = line[head:tail].replace('\":\"', '').strip()
    return s

def test():
    s = []
    se = set()
    with open('labeledImgs.json','r') as f:
        lines = f.readlines()
        for line in lines:
            handlerLine(line,s)
    for path in s:
        index = path.rfind('/')
        name = path[index + 1:]
        se.add(name)
    print len(se)



def moveImage():
    with open('nag.txt') as f:
        lines = f.readlines()
        print lines



if __name__=='__main__':
    # copy()
    # downloadImgs()
    # test()
    moveImage()