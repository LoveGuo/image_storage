#-*- coding:utf-8 -*-
import os,shutil
src = '/data/imgs/'
des = '/data/images/'
def move():
    print 'start'
    count = 0
    with open('nag.txt') as f:
        lines = f.readlines()
        for line in lines:
            count = count + 1
            print str(count)
            line = line.strip()
            fileName = line.split('/')[-1]
            srcFile = src + line
            desFile = des + fileName
            if os.path.isfile(srcFile):
                if not os.path.isfile(desFile):
                    shutil.copyfile(srcFile, desFile)
    print 'end!'

if __name__=='__main__':
    move()