# -*- coding:utf-8 -*-
import cx_Oracle

conn = cx_Oracle.connect('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS')
cur = conn.cursor()


def getShenqingH():
    shenqinghSql = "select * from migrate_failure where rownum < 3 "
    cur.execute(shenqinghSql)
    result = cur.fetchall()
    return result


def getShenqinghOracle():
    sql = "select rownum num, shenqingh from gg_zlx_zhu where zhuanlilx='3' and youxiaobj='0' and shenqingr>='20090101' and rownum < 3"
    cur.execute(sql)
    result = cur.fetchall()
    return result


def getDate():
    s1 = "2012302979598"
    s2 = "201430104358X"
    s3 = "2011303254261"
    sql = "select shenqingr from gg_zlx_zhu where shenqingh =:shenqingh"
    cur.execute(sql,shenqingh=s1)
    date1 = cur.fetchone()
    cur.execute(sql,shenqingh=s2)
    date2 = cur.fetchone()
    cur.execute(sql,shenqingh=s3)
    date3 = cur.fetchone()
    print "date1: " + str(date1)
    print "date2: " + str(date2)
    print "date3: " + str(date3)
    cur.close()
    conn.close()

def countErrorNum():
    sql = "select count(distinct shenqingh) from migrate_failure where statuscode =: errCode"
    cur.execute(sql,errCode=0)
    err0 = cur.fetchone()
    cur.execute(sql,errCode=1)
    err1 = cur.fetchone()
    cur.execute(sql,errCode=2)
    err2 = cur.fetchone()
    cur.execute(sql,errCode=3)
    err3 = cur.fetchone()
    cur.execute(sql,errCode=4)
    err4 = cur.fetchone()
    cur.execute(sql,errCode=5)
    err5 = cur.fetchone()
    print " 0: " + str(err0)
    print " 1: " + str(err1)
    print " 2: " + str(err2)
    print " 3: " + str(err3)
    print " 4: " + str(err4)
    print " 5: " + str(err5)
    cur.close()
    conn.close()


if __name__=='__main__':
    countErrorNum()