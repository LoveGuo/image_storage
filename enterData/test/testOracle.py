# -*- coding:utf-8 -*-
import cx_Oracle

#申请号库
conn = cx_Oracle.connect('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS')
#错误表库
# conn = cx_Oracle.connect('data_user','gwssi123','10.50.160.2:1522/DZSPSCP')
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

if __name__=='__main__':
    #测试错误库是否连通
    print getShenqingH()
    #测试申请号库是否连通
    print getShenqinghOracle()