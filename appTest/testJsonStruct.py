#-*- coding:utf-8 -*-
from xml.dom import minidom
import sys

reload(sys)
sys.setdefaultencoding('utf8')

def extractWord(value):
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


def process():
    xmldoc = minidom.parse('130001.xml')
    itemlist = xmldoc.getElementsByTagName('picture')
    data = []
    for item in itemlist:
        child = {}
        child['ori_name'] = item.attributes['origin_name'].value.encode('utf-8')
        # child['path'] = path + '/' + item.attributes['picture_no'].value + '.jpg'
        child['imgUpdateNum'] = 0
        keys = extractWord(item.attributes['origin_name'].value)
        child['name'] = keys[-1]
        child['rotateDesc'] = {}
        # 2.解析xml to json
        toOriginJson(data, keys, child)
    print data



if __name__=='__main__':
    process()