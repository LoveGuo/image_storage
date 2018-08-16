#-*- coding:utf-8 -*-
from suds.client import Client
import cx_Oracle,time

'''
E系统数据迁移到分布式系统
'''

conn = cx_Oracle.connect('data_user','gwssi123','10.50.160.2:1522/DZSPSCP1602')

url = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
client = Client(url)
version = 1

def getFTP(fid,version=1):
    '''

    :param fid:
    :param version:
    :return: 若存在则返回ftp路径；若不存在，则返回None
    '''
    ftp = client.service.RetrieveFile(fid,version)
    return ftp

def migrate():
    oneTime = 10  #每次获取申请号的数量
    start = 0
    end = oneTime
    cursor = conn.cursor()
    while(True):
        #1.获取申请号
        shenqinghs = getShenqingH(cursor,start,end)
        if shenqinghs is None:   #没有新数据
            time.sleep(3600)
            continue
        for shenqingh in shenqinghs:
            originFtp = []
            #2.获取fid 和提交日期 ，并根据fid和version获取ftp路径
            l1 = getOriginFileFTP(conn,cursor,shenqingh)
            if len(l1) == 0:
                insertExceptionTable(conn, cursor, shenqingh, fid=None, filingno=None,originfid=None)
                continue
            for l in l1:
                originFtp.append(l)
            #3.获取fid和中间日期 ，并根据fid和version获取ftp路径
            l2 = getSecondFileFTP(conn, cursor, shenqingh)
            for l in l2:
                originFtp.append(l)
            #调用原始入库接口

            #获取授权版本 ，并根据saomiaojid和version获取ftp路径
            authFtp = getAuthFtp(cursor,shenqingh)
            if authFtp is not None:
                #调用授权入库接口
                pass

        start = start + oneTime
        end = end + oneTime
    cursor.close()
    conn.close()


def getShenqingH(cursor,start,end):
    shenqinghSql = '''
      select shenqingh 
      from (select rownum num, shenqingh from gg_zlx_zhu where zhuanlilx='3' and youxiaobj='0' and shenqingr>='20090101' and rownum<:end ) 
      where num>=:start
      '''
    curCount = cursor.execute(shenqinghSql,end=end,start=start)
    if curCount > 0:
        return cursor.fetchall()
    return None


def getOriginFileFTP(conn,cursor,shenqingh):
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
    flag = True
    fidTuples = getFid(cursor,fidSql,shenqingh)
    ftpList = []
    for fidTuple in fidTuples:
        fid = fidTuple[2]
        if fid is not None:
            submitDate = getDate(cursor, submitDateSql, shenqingh,fid)
            if submitDate is not None:
                ftp = getFTP(fid,version)
                if ftp is not None:
                    ftpList.append(ftp)
                    flag = False
        if flag:
            insertExceptionTable(conn,cursor, shenqingh,fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2])
    return ftpList


def getSecondFileFTP(conn,cursor,shenqingh):
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
    flag = True
    fidTuples = getFid(cursor,fidSql,shenqingh)
    ftpList = []
    for fidTuple in fidTuples:
        fid = fidTuple[2]
        if fid is not None:
            submitDate = getDate(cursor, dateSql, shenqingh,fid)
            if submitDate is not None:
                ftp = getFTP(fid,version)
                ftpList.append(ftp)
                flag = False
        if flag:
            insertExceptionTable(conn, cursor, shenqingh, fid=fidTuple[0], filingno=fidTuple[1], originfid=fidTuple[2])
    return ftpList


def getAuthFtp(cursor,shenqingh):
    authSql = '''
        select saomiaojid
        from gg_wj_sqwjgdbb
        where shendingwjlx = '130001' and wenjianxclb in ('design publish', 'gzgg publish') and youxiaobz = '0' and shenqingh=:shenqingh
    '''
    cur = cursor.execute(authSql,shenqingh=shenqingh)
    if cur > 0:
        fid = cursor.fetchone()[0]
        if fid is not None:
            return getFTP(fid,version)
    return None


def insertExceptionTable(conn,cursor, shenqingh,fid=None, filingno=None, originfid=None):
    insertSql = "insert into migrate_failure(shenqingh, fid, filingno, originfid) values(:shenqingh,:fid,:filingno,:originfid)"
    cursor.execute(insertSql,shenqingh=shenqingh, fid=fid, filingno=filingno, originfid = originfid)
    conn.commit()

#获取fid
def getFid(cursor,sql,shenqingh):
    cur = cursor.execute(sql, shenqingh=shenqingh)
    if cur > 0:
        return cursor.fetchall()
    return None


#获取提交日期和中间提交日期
def getDate(cursor,sql,shenqingh,fid):
    cur = cursor.execute(sql,shenqingh=shenqingh,fid=fid)
    if cur > 0:
        return cursor.fetchone()[0]
    return None



if __name__=='__main__':
    migrate()