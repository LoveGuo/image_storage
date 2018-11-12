#-*- coding:utf-8 -*-
from suds.client import Client
import time,traceback
import json,requests, logging
from ConnectionPool import pool1521
import sys
reload(sys)
sys.setdefaultencoding('utf8')

'''
E系统数据迁移到分布式系统
迁移失败,插入异常数据表，code字段，0：原始查找失败，1，原始迁移失败，2，中间查找失败，3，中间迁移失败 4，授权迁移失败 5,执行异常
'''

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("migrate0_1.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


wsdlUrl = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
client = Client(wsdlUrl)
version = 1

serverUrl = 'http://10.50.167.111:5000/'
originEnter = serverUrl + 'upload'
authEnter = serverUrl + 'uploadAuthImgs'


documentType='130001'
headers = {'Content-Type': 'application/json'}


def getFTP(fid,version=1):
    '''
    :param fid:
    :param version:
    :return: 若存在则返回ftp路径；若不存在，则返回None
    '''
    ftp = client.service.RetrieveFile(fid,version)
    return ftp

def migrate(startNum=0,totalNum=0):
    oneTime = 5000  #每次获取申请号的数量
    endNum = startNum + oneTime
    while(True):
        if startNum >= totalNum:
            logger.info("execute end, totalNum: " + str(totalNum))
            break
        try:
            #1.获取申请号
            shenqinghs = getShenqingH(startNum,endNum)
            if shenqinghs is None:
                logger.info("execute end!")
                break
            for shenqingh in shenqinghs:
                logger.info('execute shenqingh:' + str(shenqingh[0]))
                try:
                    shenqingh = shenqingh[0]
                    dic = {}
                    #2.获取fid 和提交日期 ，并根据fid和version获取ftp路径
                    originCases = getOriginFileFTP(shenqingh,documentType)
                    if len(originCases) == 0:
                        continue
                    else:
                        #原始迁移
                        dic['cases'] = originCases
                        executeMigrate(shenqingh, dic, 1)
                    #3.获取fid和中间日期 ，并根据fid和version获取ftp路径
                    secondCases = getSecondFileFTP(shenqingh,documentType)
                    #中间迁移
                    if len(secondCases) > 0:
                        dic['cases'] = secondCases
                        executeMigrate(shenqingh, dic,3)
                    #获取授权版本 ，并根据saomiaojid和version获取ftp路径
                    authCase = getAuthFtp(shenqingh,documentType)
                    if authCase is not None:
                        executeAuthMigrate(shenqingh, authCase)
                except Exception as e:
                    insertExceptionTable(shenqingh, None, None, None, 5)
                    logger.info(str(shenqingh) + ': ' + traceback.format_exc())
            startNum = startNum + oneTime
            endNum = endNum + oneTime
        except Exception as e:
            logger.info("batch excute exception: " + traceback.format_exc())
            break


def getShenqingH(startNum,endNum):
    logger.info("oracle start: " + str(startNum) + ", end: " + str(endNum))
    shenqinghSql = '''
      select shenqingh 
      from (select rownum num, shenqingh from gg_zlx_zhu where zhuanlilx='3' and youxiaobj='0' and shenqingr>='20090101' and rownum<:endNum ) 
      where num>=:startNum
      '''
    conn = pool1521.acquire()
    cursor = conn.cursor()
    cursor.execute(shenqinghSql,endNum=endNum,startNum=startNum)
    result = cursor.fetchall()
    cursor.close()
    pool1521.release(conn)
    return result



def getOriginFileFTP(shenqingh,documentType):
    fidSql = '''
        select t.fid, t.filingno, t.originfid
        from wg_qtbxxb t
        where t.shenqingrbj = '1'
        and  t.filingno=:shenqingh
    '''
    submitDateSql = '''
        select tijiaorq
        from gg_wj_sqwj
        where shenqingh =:shenqingh
        and shendingwjlx = '130001' and gg_wj_sqwj.saomiaojid=:fid
    '''
    cases = []
    fidTuples = getFid(fidSql,shenqingh)
    if len(fidTuples) == 0:
        insertExceptionTable(shenqingh, fid=None, filingno=None, originfid=None,statuscode=0)
        return cases
    for fidTuple in fidTuples:
        flag = True
        fid = fidTuple[0]
        originFid = fidTuple[2]
        if fid is not None and originFid is not None:
            submitDate = getDate(submitDateSql, shenqingh,originFid)
            ftp = getFTP(fid,version)
            if submitDate is not None and ftp is not None:
                case = {}
                case['shenqingh'] = shenqingh
                case['wenjianlx'] = documentType
                case['fid'] = originFid
                case['submitDate'] = submitDate
                case['url'] = ftp
                cases.append(case)
                flag = False
        if flag:
            insertExceptionTable(shenqingh,fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2],statuscode=0)
    return cases


def getSecondFileFTP(shenqingh,documentType):
    fidSql = '''
        select t.fid, t.filingno,t.originfid
        from wg_qtbxxb t
        where t.shenqingrbj = '0' and  t.filingno=:shenqingh
    '''
    dateSql = '''
        select tijiaorq
        from gg_wj_zjwj
        where shenqingh =:shenqingh and shendingwjlx = '130001' and saomiaojid=:fid
    '''
    cases = []
    fidTuples = getFid(fidSql,shenqingh)
    if len(fidTuples) == 0:
        return cases
    for fidTuple in fidTuples:
        flag = True
        fid = fidTuple[0]
        orginFid = fidTuple[2]
        if fid is not None and orginFid is not None:
            submitDate = getDate(dateSql, shenqingh,fid)
            ftp = getFTP(fid,version)
            if submitDate is not None and ftp is not None:
                case = {}
                case['shenqingh'] = shenqingh
                case['wenjianlx'] = documentType
                case['fid'] = orginFid
                case['submitDate'] = submitDate
                case['url'] = ftp
                cases.append(case)
                flag = False
        if flag:
            insertExceptionTable(shenqingh, fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2],statuscode=2)
    return cases



def getAuthFtp(shenqingh,documentType):
    authSql = '''
        select saomiaojid,wenjianxclb
        from gg_wj_sqwjgdbb
        where shendingwjlx = '130001' and wenjianxclb in ('design publish', 'gzgg publish') and youxiaobz = '0' and shenqingh=:shenqingh
    '''
    conn = pool1521.acquire()
    cursor = conn.cursor()
    cursor.execute(authSql,shenqingh=str(shenqingh))
    #gzgg_publish对应的fid优先级最高
    authFidTuples = cursor.fetchall()
    cursor.close()
    pool1521.release(conn)
    if len(authFidTuples) == 0:
        return None
    elif len(authFidTuples) == 1:
        authResult = authFidTuples[0]
    else:
        for fidTuple in authFidTuples:
            if fidTuple[1] == 'gzgg publish':
                authResult = fidTuple
                break
    fid = authResult[0]
    ftp = getFTP(fid,version)
    if ftp is not None:
        submitDate = getTime()
        case = {}
        case['shenqingh'] = shenqingh
        case['wenjianlx'] = documentType
        case['fid'] = fid
        case['submitDate'] = submitDate
        case['url'] = ftp
        return case
    return None


def insertExceptionTable(shenqingh,fid, filingno, originfid,statuscode):
    logger.info('exception, shenqingh: ' + str(shenqingh) + ',fid: ' + str(fid) + ',statuscode: ' + str(statuscode))
    conn = pool1521.acquire()
    cursor = conn.cursor()
    insertSql = "insert into migrate_failure(shenqingh, fid, filingno, originfid,statuscode) values(:shenqingh,:fid,:filingno,:originfid,:statuscode)"
    try:
        cursor.execute(insertSql,shenqingh=str(shenqingh), fid=str(fid), filingno=str(filingno), originfid=str(originfid), statuscode=statuscode)
        conn.commit()
        cursor.close()
        pool1521.release(conn)
    except Exception as e:
        logger.info("插入表异常：" + traceback.format_exc())
        if conn is not None:
            pool1521.release(conn)

#获取fid
def getFid(sql,shenqingh):
    conn = pool1521.acquire()
    cursor = conn.cursor()
    cursor.execute(sql, shenqingh=str(shenqingh))
    result = cursor.fetchall()
    cursor.close()
    pool1521.release(conn)
    return result


#获取提交日期和中间提交日期
def getDate(sql,shenqingh,originFid):
    conn = pool1521.acquire()
    cursor = conn.cursor()
    cursor.execute(sql,shenqingh=str(shenqingh),fid=str(originFid))
    result = cursor.fetchone()
    cursor.close()
    pool1521.release(conn)
    if result is not None:
        return result[0]
    return None


def getTime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def executeMigrate(shenqingh,cases,cate):
    cases = cases['cases']
    for case in cases:
        try:
            dic = {}
            oneCaseList = []
            oneCaseList.append(case)
            dic['cases'] = oneCaseList
            originRes = requests.post(url=originEnter, headers=headers, data=json.dumps(dic))
            originText = json.loads(originRes.text)
            if originText['status'] != 1 and cate == 1:
                insertExceptionTable(shenqingh, fid=None, filingno=shenqingh, originfid=case['fid'], statuscode=1)
            elif originText['status'] != 1 and cate == 3:
                insertExceptionTable(shenqingh, fid=None, filingno=shenqingh, originfid=case['fid'], statuscode=3)
        except Exception as e:
            logger.info('入库原始接口返回异常：' + str(dic) + 'exception: ' + traceback.format_exc())


def executeAuthMigrate(shenqingh, authCase):
    try:
        authRes = requests.post(url=authEnter, headers=headers, data=json.dumps(authCase))
        authText = json.loads(authRes.text)
        if authText['status'] == 0:
            insertExceptionTable(shenqingh, fid=authCase['fid'], filingno=None, originfid=None, statuscode=4)
    except Exception as e:
        logger.info('入库授权接口返回异常：' + str(authCase) + 'exception: ' + traceback.format_exc())


if __name__=='__main__':
    startNum = 0
    totalNum = 1000000
    migrate(startNum,totalNum)