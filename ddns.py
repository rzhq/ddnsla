#!/usr/bin/python
#coding=utf-8

# a ddns script for dns.la  #
# designed by aurorax       #
# details & how to use see  #
# http://aurorax.org/ddnsla #

import requests
import json, time, socket, re, os, sys

conf = {}
execfile("default.conf",conf)

os.environ["TZ"] = conf['tz']
time.tzset()
if conf['host'] == '@':
    hostdomain = conf['host']+'.'+conf['domain']
else:
    hostdomain = conf['domain']

def main():

    ip = getIP()
    dip = getIP(hostdomain)
    
    if ip != dip:
        
        file = open(conf['logfile'],'a')
        
        url = 'https://api.dns.la/api/record.ashx?cmd=list'
        data = {'apiid':conf['apiid'], 'apipass':conf['apipass'], 'domain':conf['domain']}
        ret = post(url,data)

        if ret['status']['code'] == 300:
            for i in range(0,len(ret['datas'])):
                if ret['datas'][i]['host'] == conf['host'] and ret['datas'][i]['record_type'] == conf['type']:
                    recordid = ret['datas'][i]['recordid']
                    domainid = ret['datas'][i]['domainid']
                    recordtype = ret['datas'][i]['record_type']
                    recordline = ret['datas'][i]['record_line']
                    recorddata = ret['datas'][i]['record_data']
                else:
                    continue
            
            
            if ip != recorddata:
                url = 'https://api.dns.la/api/record.ashx?cmd=edit'
                data = {'apiid':conf['apiid'], 'apipass':conf['apipass'], 'domain':conf['domain'], 'host':conf['host'],
                       'recordid':recordid, 'recordtype':recordtype, 'recordline':recordline, 'recorddata':ip, 'ttl':conf['ttl']}
                ret = post(url,data)
                if ret['status']['code'] == 300:
                    file.write(time.ctime()+'  '+hostdomain+'('+conf['type']+'):'+dip+'=>'+ip+'\n')
                    while ip != getIP(conf['domain']):
                        pass
                else:
                    file.write(hostdomain+'('+conf['type']+'):'+ret['status']['code']+' '+time.ctime()+'\n')

        else:
            file.write(hostdomain+'('+conf['type']+'):'+ret['status']['code']+' '+time.ctime()+'\n')
            
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

if __name__ == '__main__':
    while True:
        main()
        time.sleep(conf['loop'])
