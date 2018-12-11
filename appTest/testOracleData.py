#-*-coding:utf-8-*-

import cx_Oracle,os
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import datetime

conn = cx_Oracle.connect('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS')

def getDate():
    '''
    授权入库图片日期：根据逻辑名从表中查找对应的日期
    :param logicName:
    :return:
    '''
    cursor = conn.cursor()
    sql2 = "select count(distinct shenqingh) from gg_zlx_zhu where zhuanlilx='3' and youxiaobj='0' and shenqingr>='20170101'"
    cursor.execute(sql2)
    result2 = cursor.fetchone()
    print "result1: " + str(result2)
    cursor.close()
    conn.close()

if __name__=='__main__':
    print getDate()