#-*-coding:utf-8-*-

from ConnectionPool import pool1521

def getAuthDate(shenqingh):
    '''
    授权入库图片日期：获取申请号的所有图片名称、日期
    :param logicName:
    :return:map<name:date>
    '''
    context = {}
    conn = pool1521.acquire()
    cur = conn.cursor()
    sql = "select currentpicname,submitdate from wg_qtxxb where filingno =:shenqingh and passflag = '1'"
    cur.execute(sql,shenqingh=str(shenqingh))
    tups = cur.fetchall()
    if not tups:
        return context
    for tup in tups:
        if len(tup) == 2:
            key = tup[0]
            context[key] = tup[1]
    cur.close()
    pool1521.release(conn)
    return context