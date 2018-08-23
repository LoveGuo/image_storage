#-*- coding:utf-8 -*-
import cx_Oracle,os,shutil
from suds.client import Client

url = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
fid = 'GY000003031250'
authFid = 'GY000003031251'
conn = cx_Oracle.connect('data_user','gwssi123','10.50.160.2:1522/DZSPSCP')

def getFtp():
    client = Client(url)
    print client.service.RetrieveFile(fid,1)


def getFid():
    cursor = conn.cursor()
    sql = '''
            select t.fid, t.filingno,t.originfid
            from wg_qtbxxb t
            where t.shenqingrbj = '1'
            and  t.filingno=:shenqingh
        '''
    cur = cursor.execute(sql, shenqingh='2009300329095')
    if cur > 0:
        result = cursor.fetchall()
        print result[0]
        print len(result[0])
    return None

def insert():
    cursor = conn.cursor()
    shenqingh = '2017301168358'
    insertSql = "insert into migrate_failure(shenqingh, fid, filingno, originfid,auth) values(:shenqingh,:fid,:filingno,:originfid,:statuscode)"
    cursor.execute(insertSql, shenqingh=shenqingh, fid=None, filingno=None, originfid=None)
    conn.commit()
    cursor.close()
    conn.close()


def select():
    cursor = conn.cursor()
    shenqingh = 'GY000003031250'
    authSql = '''
            select saomiaojid
            from gg_wj_sqwjgdbb
            where shendingwjlx = '130001' and wenjianxclb in ('design publish', 'gzgg publish') and youxiaobz = '0' and shenqingh=:shenqingh
        '''
    cur = cursor.execute(authSql, shenqingh=shenqingh)
    print cur.fetchone()
    print type(cur)




if __name__=="__main__":
    # insert()
    # getFtp()
    # getFid()
    select()