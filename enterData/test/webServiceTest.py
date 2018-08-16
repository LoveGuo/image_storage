#-*- coding:utf-8 -*-
import cx_Oracle
from suds.client import Client

url = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
fid = 'SA000014301032'
authFid = 'GY000003031251'
conn = cx_Oracle.connect('data_user','gwssi123','10.50.160.2:1522/DZSPSCP')

def getFtp():
    client = Client(url)
    print client.service.RetrieveFile(authFid,1)


def getFid():
    cursor = conn.cursor()
    sql = '''
            select t.fid, t.filingno,t.originfid
            from wg_qtbxxb t
            where t.shenqingrbj = '1'
            and  t.filingno=:shenqingh
        '''
    cur = cursor.execute(sql, shenqingh='2017301168358')
    if cur > 0:
        result = cursor.fetchall()
        print result
    return None

def insert():
    cursor = conn.cursor()
    shenqingh = '2017301168358'
    insertSql = "insert into migrate_failure(shenqingh, fid, filingno, originfid) values(:shenqingh,:fid,:filingno,:originfid)"
    cursor.execute(insertSql, shenqingh=shenqingh, fid=None, filingno=None, originfid=None)
    conn.commit()
    cursor.close()
    conn.close()

if __name__=="__main__":
    # insert()
    getFtp()