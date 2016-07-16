#!/usr/bin/python
#coding=utf-8

# a ddns script for dns.la  #
# designed by aurorax       #
# details & how to use see  #
# http://aurorax.org/ddnsla #

import requests
import time, re, os, sys, signal

conf = {}
execfile('default.conf',conf)

os.environ["TZ"] = conf['tz']
time.tzset()
if conf['host'] != '@':
    hostdomain = conf['host']+'.'+conf['domain']
else:
    hostdomain = conf['domain']

debug = False
argv = sys.argv
if len(argv) > 1:
    if argv[1] == '--debug':
        debug = True

def main():

    ip = getIP()
    dip = getIP(hostdomain)
    if debug:
        print 'local ip -- domain ip:  ', ip, '--', dip
    
    if ip != dip:

        file = open(conf['logfile'],'a')
        
        url = 'https://api.dns.la/api/record.ashx?cmd=list'
        data = {'apiid':conf['apiid'], 'apipass':conf['apipass'], 'domain':conf['domain']}
        if debug:
            print '---------------------'
            print 'status: checkDNS'
            print 'postUrl:', url
            print 'postData:', data
        ret = post(url,data)
        if debug:
            print 'ret:', ret

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
                if debug:
                    print 'ip -- record: ', ip, '--', recorddata
                url = 'https://api.dns.la/api/record.ashx?cmd=edit'
                data = {'apiid':conf['apiid'], 'apipass':conf['apipass'], 'domain':conf['domain'], 'host':conf['host'],
                       'recordid':recordid, 'recordtype':recordtype, 'recordline':recordline, 'recorddata':ip, 'ttl':conf['ttl']}
                if debug:
                    print 'status: updateDNS'
                    print 'postUrl:', url
                    print 'postData:', data
                ret = post(url,data)
                if debug:
                    print 'ret:', ret
                if ret['status']['code'] == 300:
                    file.write(getTime()+'  '+hostdomain+'('+conf['type']+'): '+dip+'=>'+ip+'\n')
                    closeFile()
                    while ip != getIP(hostdomain):
                        if debug:
                            print 'local ip -- domain ip: ', ip, '--', recorddata
                        delay(conf['loop'])
                else:
                    file.write(getTime()+'  '+hostdomain+'('+conf['type']+'): '+ret['status']['code']+'\n')
            else:
                delay(60)
        else:
            file.write(getTime()+'  '+hostdomain+'('+conf['type']+'): '+ret['status']['code']+'\n')

        if debug:
            print '---------------------'
        closeFile()
        
def getIP(domain=''):
    signal.signal(signal.SIGALRM, dog)
    signal.alarm(5)
    url = 'http://www.ip138.com/ips138.asp?ip=' + domain
    ret = re.search('\d+\.\d+\.\d+\.\d+',requests.get(url).text).group(0)
    signal.alarm(0)
    return ret

def post(url, data=''):
    res = requests.post(url, data)
    return res.json()

def closeFile():
    global file
    if not file.closed:
        file.close()

def getTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def delay(sec):
    time.sleep(sec)

def dog(*args):
    raise Exception

if __name__ == '__main__':
    while True:
        try:
            main()
            delay(conf['loop'])
        except Exception as e:
            if debug:
                print str(e)
                print 'still alive'