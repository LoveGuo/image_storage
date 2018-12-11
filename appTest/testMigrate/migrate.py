#-*- conding:utf-8 -*-


#migrate.log -> shenqinghs
def getShenqinghs():
    data = set()
    with open('migrate0_1.log','r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            index = line.find('execute')
            if index != -1:
                shenqingh = line[index + 18:]
                data.add(shenqingh)
    with open('result.txt','w') as f:
        for ele in data:
            f.write(ele + '\n')


if __name__=='__main__':
    getShenqinghs()