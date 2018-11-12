# -*- coding:utf-8 -*-
from config import ipPort
"""添加和删除路径的端口和ip"""

preffix = ipPort


#当前添加路径前缀
def currentPreffixHandle(resultJson,flag):
    handlerNoticePath(resultJson, flag)
    if resultJson.has_key('lastVersion'):
        for dataDict in resultJson['lastVersion']:
            handlerData(dataDict,flag)


def authPreffixHandle(resultJson,flag):
    handlerNoticePath(resultJson,flag)
    handlerData(resultJson,flag)


def originPreffixHandle(resultJson,flag):
    if resultJson.has_key('notice'):
        resultJson['notice'] = preffix + resultJson['notice']
    handlerData(resultJson,flag)


def handlerNoticePath(resultJson,flag):
    if resultJson.has_key('notice'):
        noticePath = resultJson['notice']
        if flag == 'addPrefix':
            resultJson['notice'] = preffix + noticePath
        elif flag == 'clearPrefix':
            resultJson['notice'] = noticePath.replace(preffix, '')


def handlerData(dataDict,flag='addPrefix'):
    if dataDict.has_key('data'):
        elementList = dataDict['data']
        for elementDict in elementList:
            if elementDict.has_key('children'):
                handlerChildren(elementDict,flag)
            elif elementDict.has_key('path'):
                handlerPath(elementDict,flag)


def handlerChildren(elementDict,flag):
    elementList = elementDict['children']
    for elementDict in elementList:
        if elementDict.has_key("children"):
            handlerChildren(elementDict,flag)
        elif elementDict.has_key('path'):
            handlerPath(elementDict,flag)



def handlerPath(elementDict,flag):
    path = elementDict['path']
    if flag == 'addPrefix':
        elementDict['path'] = preffix + path
    elif flag == 'clearPrefix':
        elementDict['path'] = path.replace(preffix,'')



def addCurrent():
    # listData = {
    #     "notice":"/abc.jpg",
    #     "lastVersion":
    #     [
    #         {
    #             "date": "20110930",
    #             "data": [
    #                 {
    #                     "name":"设计1",
    #                     "children":[{
    #                         "name":"组件1",
    #                         "children":[
    #                             {
    #                                 "path": "/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
    #                                 "rotateDesc": {},
    #                                 "imgUpdateNum": 0,
    #                                 "ori_name": "主视图",
    #                                 "name": "主视图"
    #                             },
    #                             {
    #                                 "path": "/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
    #                                 "rotateDesc": {},
    #                                 "imgUpdateNum": 0,
    #                                 "ori_name": "立体图",
    #                                 "name": "立体图"
    #                             }
    #                         ]
    #                     },
    #                         {
    #                             "path": "/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
    #                             "rotateDesc": {},
    #                             "imgUpdateNum": 0,
    #                             "ori_name": "主视图",
    #                             "name": "主视图"
    #                         },
    #                         {
    #                             "path": "/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
    #                             "rotateDesc": {},
    #                             "imgUpdateNum": 0,
    #                             "ori_name": "立体图",
    #                             "name": "立体图"
    #                         }
    #                     ]
    #                 },
    #             ],
    #             "fid": "DA000009606268"
    #         }
    #     ]}
    listData = {
        "notice": "http://10.50.167.111:80/wgzstxqy/abc.jpg",
        "lastVersion":
            [
                {
                    "date": "20110930",
                    "data": [
                        {
                            "name": "设计1",
                            "children": [{
                                "name": "组件1",
                                "children": [
                                    {
                                        "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
                                        "rotateDesc": {},
                                        "imgUpdateNum": 0,
                                        "ori_name": "主视图",
                                        "name": "主视图"
                                    },
                                    {
                                        "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
                                        "rotateDesc": {},
                                        "imgUpdateNum": 0,
                                        "ori_name": "立体图",
                                        "name": "立体图"
                                    }
                                ]
                            },
                                {
                                    "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
                                    "rotateDesc": {},
                                    "imgUpdateNum": 0,
                                    "ori_name": "主视图",
                                    "name": "主视图"
                                },
                                {
                                    "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
                                    "rotateDesc": {},
                                    "imgUpdateNum": 0,
                                    "ori_name": "立体图",
                                    "name": "立体图"
                                }
                            ]
                        },
                    ],
                    "fid": "DA000009606268"
                }
            ]}
    currentPreffixHandle(listData,'clearPrefix')
    print listData


def addOrigin():
    listData = {
                    "notice": "http://10.50.167.111:80/wgzstxqy/abc.jpg",
                    "date": "20110930",
                    "data": [
                        {
                            "name": "设计1",
                            "children": [{
                                "name": "组件1",
                                "children": [
                                    {
                                        "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
                                        "rotateDesc": {},
                                        "imgUpdateNum": 0,
                                        "ori_name": "主视图",
                                        "name": "主视图"
                                    },
                                    {
                                        "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
                                        "rotateDesc": {},
                                        "imgUpdateNum": 0,
                                        "ori_name": "立体图",
                                        "name": "立体图"
                                    }
                                ]
                            },
                                {
                                    "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105217.jpg",
                                    "rotateDesc": {},
                                    "imgUpdateNum": 0,
                                    "ori_name": "主视图",
                                    "name": "主视图"
                                },
                                {
                                    "path": "http://10.50.167.111:80/wgzstxqy/data/2011/09/30/7846/002011303497846/130001/a/DA000009606268/110929105222.jpg",
                                    "rotateDesc": {},
                                    "imgUpdateNum": 0,
                                    "ori_name": "立体图",
                                    "name": "立体图"
                                }
                            ]
                        },
                    ],
                    "fid": "DA000009606268"
                }
    authPreffixHandle(listData,'clearPrefix')
    print listData




if __name__=='__main__':
    # addCurrent()
    addOrigin()