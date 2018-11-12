#-*- coding:utf-8 -*-
import config
from config import logger
import os
from imgUtils import saveAndCopyImg
import json

def parseJson(request,formDict,originPath,lastVersionPath):
    data = []
    contentList = []
    #single
    if 'single' in formDict.keys() and len(json.loads(formDict['single'])) > 0:
        parentName = ''
        singleData = json.loads(request.form.get('single'))
        if 'views' in singleData.keys() and len(singleData['views']) > 0:   #只有视图
            handlerViews(request,singleData['views'], originPath, lastVersionPath, data,parentName)
            return data
        else:
            contentList = singleData['components']
            parseJsonContentList(request, contentList, originPath, lastVersionPath, data)
    else: #no-single
        designList = request.form.getlist('designList')
        suiteList = request.form.getlist('suiteList')
        if 'designList' in formDict.keys() and len(designList) > 0:
            parseJsonContentList(request, designList, originPath, lastVersionPath, data)
        if 'suiteList' in formDict.keys() and len(suiteList) > 0:
            parseJsonContentList(request,suiteList, originPath, lastVersionPath, data)

    return data


def parseJsonContentList(request,contentList,originPath,lastVersionPath,data):
    for content in contentList: #组件+视图
        if not isinstance(content,dict):
            content = json.loads(content)
        if 'views' in content:
            doc = {}
            docList = []
            parentName = content['name']
            doc['name'] = parentName
            doc['children'] = docList
            handlerViews(request,content['views'],originPath,lastVersionPath,docList,parentName)
            data.append(doc)
        else:
            # doc = {}
            # docList = []
            # doc['children'] = docList
            for content_child in content:
                design = {}
                childList = []
                design['name'] = content_child['name']
                design['children'] = childList
                if 'components' in content_child.keys():   #设计+ 组件 + 视图
                    for component in content_child['components']:  #组件
                        compo = {}
                        compoList = []
                        compo['name'] = component['name']
                        compo['children'] = compoList
                        parentName = content_child['name'] + component['name']
                        handlerViews(request, component['views'], originPath, lastVersionPath, compoList, parentName)
                        childList.append(compo)
                else:                                      #设计+视图
                    parentName = content_child['name']
                    handlerViews(request, content_child['views'], originPath, lastVersionPath, childList, parentName)
                data.append(design)
            # data.append(doc)


def handlerViews(request,views,originPath,lastVersionPath,list,parentName):
    for view in views:  # view包含name、fileLink
        imgInfo = {}
        fileLink = view['fileLink']
        file = request.files[fileLink]
        ext = '.' + file.filename.encode('utf-8').rsplit('.',1)[1]
        # 生成唯一图片实体名字（使用文件个数？考虑高并发上传情况）
        countDir = config.basePath + originPath
        imgNameId = getEntityId(countDir)
        saveAndCopyImg(file, originPath, lastVersionPath, imgNameId, ext)
        imgInfo['name'] = view['name']
        imgInfo['ori_name'] = parentName + view['name']
        #组装新json时原始与最新版二选一
        imgInfo['path'] =config.ipPort + config.basePath + originPath + imgNameId + ext
        # imgInfo['lastVersionPath'] = config.ipPort + config.basePath + lastVersionPath + imgNameId + ext
        imgInfo['imgUpdateNum'] = 0
        list.append(imgInfo)


def getEntityId(originPath):
    '''
    图片唯一实体名
    :return: 6位文件名000001
    '''
    #统计文件数量
    fileNum = 0
    for root, dirs, files in os.walk(originPath):
        fileNum = len(files)
    fileNum = fileNum + 1
    l = len(str(fileNum))
    if l < 6:
        return str('0' * (6 - l) + str(fileNum))
    else:
        return str('0' * (10 - l) + str(fileNum))


def getVersionPath(dataList,imgId,pic_version,rotate_desc=None):
    '''
    从json中获取某个图片的版本号
    :param valueJson:json
    :return:
    '''
    return traversalChildren(dataList,imgId,pic_version,rotate_desc)


def traversalChildren(dataList,imgId,pic_version,rotate_desc):
    for l in dataList:
        if 'children' in l.keys():
            return traversalChildren(l['children'],imgId,pic_version=None,rotate_desc=None)
        elif 'path' in l.keys() and comparePath(imgId,l['path']):
            #当前版本号加一，并返回
            l['imgUpdateNum'] = int(l['imgUpdateNum']) + 1
            #添加旋转描述
            rotateDescDict = l['rotateDesc']
            rotateInfo = ''
            if rotate_desc is not None and  rotate_desc != '':
                rotateDescDict[str(l['imgUpdateNum'])] = rotate_desc
                rotateInfo = rotate_desc
            elif rotateDescDict.has_key(pic_version):
                rotateDescDict[str(l['imgUpdateNum'])] = rotateDescDict[pic_version]
                rotateInfo = rotateDescDict[pic_version]
            path = l['path'].replace('.','~' + str(l['imgUpdateNum']) + '.')
            return path,rotateInfo



def comparePath(imgId,filePath):
    if imgId in filePath:
        return True
    return False

def getAuthPaths(dataList):
    #返回授权json中的所有路径
    paths = []
    for data in dataList:
        if 'children' in data.keys():
            paths = getAuthPaths(data['children'])
        elif 'path' in data.keys():
            c = {}
            c['path'] = data['path']
            c['version'] = data['version']
            paths.append(c)
    return paths

def authPathsFilter(dataList):
    #修改路径为授权路径
    paths = getAuthPaths(dataList)
    #将路径加上版本号
    pathArr = []
    for context in paths:
        path = context['path']
        version = context['version']
        path = path.replace(config.ipPort,'').replace('.jpg','')
        path = path + '~' + str(version) + '.jpg'
        pathArr.append(path)
    return pathArr

if __name__=='__main__':
    dataList = [
        {
            'children':[
                {
                    'path':'http://localhost:8080/1/a/123456.jpg',
                    'version':3
                },
                {
                    'path':'http://localhost:8080/1/a/456789.jpg',
                    'version':4
                }
            ]
        }
    ]

    print authPathsFilter(dataList)