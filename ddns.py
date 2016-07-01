#!/usr/bin/python
#coding=utf-8

# a ddns script for dns.la  #
# designed by aurorax       #
# details & how to use see  #
# http://aurorax.org/ddnsla #

import requests
import json, time, socket, re, os

tz = 'Asia/Shanghai'
apiid = 'test'
apipass = 'pass'
domain = 'domain.com'
host = '@'
type = 'A'
ttl = '600'
loop = 5 #seconds

def main():

    ip = getIP()
    dip = getIP(hostdomain)
    
    if ip != dip:
        
        file = open('data.log','a')
        
        url = 'https://api.dns.la/api/record.ashx?cmd=list'
        data = {'apiid':apiid, 'apipass':apipass, 'domain':domain}
        ret = post(url,data)
        
        if ret['status']['code'] == 300:
            for i in range(0,len(ret['datas'])):
                if ret['datas'][i]['host'] == host and ret['datas'][i]['record_type'] == type:
                    recordid = ret['datas'][i]['recordid']
                    domainid = ret['datas'][i]['domainid']
                    recordtype = ret['datas'][i]['record_type']
                    recordline = ret['datas'][i]['record_line']
                    recorddata = ret['datas'][i]['record_data']
                else:
                    continue
            
            
            if ip != recorddata:
                url = 'https://api.dns.la/api/record.ashx?cmd=edit'
                data = {'apiid':apiid, 'apipass':apipass, 'domain':domain, 'host':host,
                       'recordid':recordid, 'recordtype':recordtype, 'recordline':recordline, 'recorddata':ip, 'ttl':ttl}
                ret = post(url,data)
                if ret['status']['code'] == 300:
                    file.write(time.ctime()+'  '+hostdomain+'('+type+'):'+dip+'=>'+ip+'\n')
                    while ip != getIP(domain):
                        pass
                else:
                    file.write(hostdomain+'('+type+'):'+ret['status']['code']+' '+time.ctime()+'\n')

        else:
            file.write(hostdomain+'('+type+'):'+ret['status']['code']+' '+time.ctime()+'\n')
            
        file.close()
        
def getIP(domain=''):
    url = 'http://ip.cn'
    mid = '/index.php?ip='
    if domain != None:
        url = url+mid+domain
    return re.search('\d+\.\d+\.\d+\.\d+',requests.get(url).text).group(0)

def post(url, data=''):
    res = requests.post(url, data)
    return res.json()


def getTime():
    return time.ctime(time.time())

os.environ["TZ"] = tz
time.tzset()
hostdomain = domain
if host != '@':
    hostdomain = host+'.'+hostdomain

if __name__ == '__main__':
    while True:
        main()
        time.sleep(loop)
