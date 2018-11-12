#-*-coding:utf-8-*-
import cx_Oracle

'''
    在oracle上创建表
'''

conn = cx_Oracle.connect('txsb_user','Txsb^user!','10.50.160.45:1521/DZSPSCLS')
cursor = conn.cursor()


def createTable():
    sql1 = '''
    CREATE TABLE migrate_failure(
       shenqingh Varchar2(20),
       fid Varchar2(20),
       filingno Varchar2(20),
       originfid Varchar2(20),
       statuscode Number(10)
    )
    '''
    # sql2 = "CREATE SEQUENCE migrate_failure_seq INCREMENT BY 1  START WITH 1 NOCACHE"
    # sql3 = '''
    # CREATE OR REPLACE TRIGGER migrate_failure_id_trigger
    #   BEFORE INSERT ON migrate_failure
    #   for each row
    # BEGIN
    #   SELECT migrate_failure_seq.nextval into :new.failId from dual
    # END migrate_failure_id_trigger
    # '''
    cursor.execute(sql1)
    # cursor.execute(sql2)
    # cursor.execute(sql3)
    conn.commit()
    createSuccess()

def dropTable():
    sql1 = "drop table migrate_failure"
    # sql2 = "drop sql1equence migrate_failure_seq"
    cursor.execute(sql1)
    # cursor.execute(sql2)
    conn.commit()


def createSuccess():
    sql = "select count(*) from migrate_failure"
    cursor.execute(sql)
    count = cursor.fetchone()
    print 'total: ' + str(count)


def show():
    sql1 = "select * from user_tables where table_name = upper('migrate_failure')"
    sql2 = "select * from user_sequences where SEQUENCE_NAME = UPPER('migrate_failure_seq')"
    sql3 = "select * from user_triggers"
    print "table: "
    cursor.execute(sql1)
    print cursor.fetchall()
    # print "sequence: "
    # cursor.execute(sql2)
    # print cursor.fetchall()
    # print "trigger: "
    # cursor.execute(sql3)
    # print cursor.fetchall()


def insert():
    sql = "insert into migrate_failure(shenqingh, fid, filingno, originfid,statuscode) values(:shenqingh,:fid,:filingno,:originfid,:statuscode)"
    cursor.execute(sql,shenqingh='000',fid='000',filingno='000',originfid='000',statuscode=0)
    conn.commit()
    # createSuccess()


if __name__=='__main__':
    dropTable()
    createTable()
    #show()
    #insert()