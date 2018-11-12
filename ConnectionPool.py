#-*- coding:utf-8 -*-
import cx_Oracle


pool1521 = cx_Oracle.SessionPool('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS',min=15,max=20,increment=5,encoding='UTF-8',threaded=True)

# oraclePool2 = cx_Oracle.SessionPool('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS',min=10,max=20,increment=5,encoding='UTF-8',threaded=True)