#-*- codding:utf-8 -*-
from suds.client import Client

def getFTP(fid,version=1):
    wsdlUrl = 'http://10.50.1.31:8080/GetFileWS/GetFileWS?wsdl'
    client = Client(wsdlUrl)
    ftp = client.service.RetrieveFile(fid,version)
    return ftp


if __name__ == '__main__':
    print getFTP('yz0000049832466')