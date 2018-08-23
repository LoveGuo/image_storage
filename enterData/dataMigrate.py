#-*- coding:utf-8 -*-
from suds.client import Client
import cx_Oracle,time,traceback
import json,requests, logging

import sys
reload(sys)
sys.setdefaultencoding('utf8')

'''
E系统数据迁移到分布式系统
迁移失败,插入异常数据表，code字段，0：原始查找失败，1，原始迁移失败，2，中间查找失败，3，中间迁移失败 4，授权迁移失败
'''

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("migrate.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

conn = cx_Oracle.connect('data_user','gwssi123','10.50.160.2:1522/DZSPSCP')

wsdlUrl = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
client = Client(wsdlUrl)
version = 1

serverUrl = 'http://10.75.13.114:5000/'
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

def migrate():
    num = 1
    oneTime = 5000  #每次获取申请号的数量
    startNum = 0
    endNum = oneTime
    cursor = conn.cursor()
    while(True):
        try:
            #1.获取申请号
            logger.info("oracle start: " + str(startNum) + ", end: " + str(endNum))
            shenqinghs = getShenqingH(cursor,startNum,endNum)
            if shenqinghs is None:   #没有新数据
                time.sleep(3600)
                continue
            for shenqingh in shenqinghs:
                num = num + 1
                shenqingh = shenqingh[0]
                dic = {}
                #2.获取fid 和提交日期 ，并根据fid和version获取ftp路径
                originCases = getOriginFileFTP(conn,cursor,shenqingh,documentType)
                if len(originCases) == 0:
                    continue
                else:
                    #原始迁移
                    dic['cases'] = originCases
                    executeMigrate(cursor, shenqingh, dic, 1)
                #3.获取fid和中间日期 ，并根据fid和version获取ftp路径
                secondCases = getSecondFileFTP(conn, cursor, shenqingh,documentType)
                #中间迁移
                if len(secondCases) > 0:
                    dic['cases'] = secondCases
                    executeMigrate(cursor, shenqingh, dic,3)
                #获取授权版本 ，并根据saomiaojid和version获取ftp路径
                authCase = getAuthFtp(cursor,shenqingh,documentType)
                if authCase is not None:
                    executeAuthMigrate(cursor, shenqingh, authCase)
            startNum = startNum + oneTime
            endNum = endNum + oneTime
        except Exception as e:
            logger.info(traceback.format_exc())
    cursor.close()
    conn.close()


def getShenqingH(cursor,startNum,endNum):
    shenqinghSql = '''
      select shenqingh 
      from (select rownum num, shenqingh from gg_zlx_zhu where zhuanlilx='3' and youxiaobj='0' and shenqingr>='20090101' and rownum<:endNum ) 
      where num>=:startNum
      '''
    logger.info("获取申请号sql语句： " + shenqinghSql)
    cursor.execute(shenqinghSql,endNum=endNum,startNum=startNum)
    result = cursor.fetchall()
    return result


def getOriginFileFTP(conn,cursor,shenqingh,documentType):
    fidSql = '''
        select t.fid, t.filingno,t.originfid
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
    fidTuples = getFid(cursor,fidSql,shenqingh)
    if len(fidTuples) == 0:
        insertExceptionTable(conn, cursor, shenqingh, fid=None, filingno=None, originfid=None,statuscode=0)
        return cases
    for fidTuple in fidTuples:
        flag = True
        fid = fidTuple[2]
        if fid is not None:
            submitDate = getDate(cursor, submitDateSql, shenqingh,fid)
            if submitDate is not None:
                ftp = getFTP(fid,version)
                if ftp is not None:
                    case = {}
                    case['shenqingh'] = shenqingh
                    case['wenjianlx'] = documentType
                    case['fid'] = fid
                    case['submitDate'] = submitDate
                    case['url'] = ftp
                    cases.append(case)
                    flag = False
        if flag:
            insertExceptionTable(conn,cursor, shenqingh,fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2],statuscode=0)
    return cases


def getSecondFileFTP(conn,cursor,shenqingh,documentType):
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
    fidTuples = getFid(cursor,fidSql,shenqingh)
    if len(fidTuples) == 0:
        return cases
    for fidTuple in fidTuples:
        flag = True
        fid = fidTuple[2]
        if fid is not None:
            submitDate = getDate(cursor, dateSql, shenqingh,fid)
            if submitDate is not None:
                ftp = getFTP(fid,version)
                if ftp is not None:
                    case = {}
                    case['shenqingh'] = shenqingh
                    case['wenjianlx'] = documentType
                    case['fid'] = fid
                    case['submitDate'] = submitDate
                    case['url'] = ftp
                    cases.append(case)
                    flag = False
        if flag:
            insertExceptionTable(conn, cursor, shenqingh, fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2],statuscode=2)
    return cases



def getAuthFtp(cursor,shenqingh,documentType):
    authSql = '''
        select saomiaojid
        from gg_wj_sqwjgdbb
        where shendingwjlx = '130001' and wenjianxclb in ('design publish', 'gzgg publish') and youxiaobz = '0' and shenqingh=:shenqingh
    '''
    cursor.execute(authSql,shenqingh=shenqingh)
    authResult = cursor.fetchone()
    if authResult is not None:
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


def insertExceptionTable(conn,cursor, shenqingh,fid, filingno, originfid,statuscode):
    # logger.info("exception table: " + shenqingh + ", code: " + str(statuscode))
    insertSql = "insert into migrate_failure(shenqingh, fid, filingno, originfid,statuscode) values(:shenqingh,:fid,:filingno,:originfid,:statuscode)"
    try:
        cursor.execute(insertSql,shenqingh=shenqingh, fid=fid, filingno=filingno, originfid = originfid, statuscode = statuscode)
        conn.commit()
    except Exception as e:
        logger.info("插入表异常：" + traceback.format_exc())

#获取fid
def getFid(cursor,sql,shenqingh):
    cursor.execute(sql, shenqingh=shenqingh)
    result = cursor.fetchall()
    return result


#获取提交日期和中间提交日期
def getDate(cursor,sql,shenqingh,fid):
    cursor.execute(sql,shenqingh=shenqingh,fid=fid)
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    return None


def getTime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def executeMigrate(cursor,shenqingh,cases,cate):
    cases = cases['cases']
    for case in cases:
        try:
            dic = {}
            oneCaseList = []
            oneCaseList.append(case)
            dic['cases'] = oneCaseList
            originRes = requests.post(url=originEnter, headers=headers, data=json.dumps(dic))
            originText = json.loads(originRes.text)
            if originText['status'] == 0 and cate == 1:
                insertExceptionTable(conn, cursor, shenqingh, fid=None, filingno=shenqingh, originfid=case['fid'], statuscode=1)
            elif originText['status'] == 0 and cate == 3:
                insertExceptionTable(conn, cursor, shenqingh, fid=None, filingno=shenqingh, originfid=case['fid'], statuscode=3)
        except Exception as e:
            logger.info(str(originRes.text))
            logger.info('接口返回异常：' + str(dic) + 'exception: ' + traceback.format_exc())


def executeAuthMigrate(cursor,shenqingh, authCase):
    try:
        authRes = requests.post(url=authEnter, headers=headers, data=json.dumps(authCase))
        authText = json.loads(authRes.text)
        if authText['status'] == 0:
            insertExceptionTable(conn, cursor, shenqingh, fid=authCase['fid'], filingno=None, originfid=None, statuscode=4)
    except Exception as e:
        logger.info(str(authRes.text))
        logger.info('接口返回异常：' + str(authCase) + 'exception: ' + traceback.format_exc())


if __name__=='__main__':
    migrate()