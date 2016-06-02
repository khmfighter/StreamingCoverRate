# /bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function

__author__ = 'KHM'
import os, sys, datetime, time, math, thread
from operator import itemgetter
from getopt import getopt, GetoptError

try:
    opts, hosts = getopt(sys.argv[1:], 'p:')
except GetoptError:
    print("Syntax error")
    sys.exit(1)

strdir = os.path.split(os.path.realpath(sys.argv[0]))[0]

for opt in opts:
    if opt[0] == '-p':
        # 0.06
        path = opt[1]

map2g={}
map4g={}
mapresult={}
result=[]

EARTH_RADIUS = 6371004

def rad(d):
    return d * math.pi / 180.0

def GetDistance(str1,str2):
    items_f=str1.split('#')
    items_l=str2.split('#')
    lat1 = rad(float(items_f[1]))
    lat2 = rad(float(items_l[1]))
    a = lat1 - lat2
    b = rad(float(items_f[0]) - float(items_l[0]))
    sa2 = math.sin(a / 2.0)
    sb2 = math.sin(b / 2.0)
    d = 2 * EARTH_RADIUS * math.asin(math.sqrt(sa2 * sa2 + math.cos(lat1) * math.cos(lat2) * sb2 * sb2))
    return d

def timer(num, sub_item):
    mapresult={}
    amap={}
    print 'Thread:(%d) Time:%s\n'%(no, time.ctime())
    for k2g,v2g in sub_item.items():
        mapresult.clear()
        for k4g,v4g in map4g.items():
            mapresult[k2g+"-->"+k4g]=GetDistance(v2g,v4g)
        amap=sorted(mapresult.iteritems(), key=lambda d:d[1])[0:10]
    for item in amap:   
        print (item)
    amap.clear()
    thread.exit_thread()

def computeDist(path):
    count=0
    for parent, dirs, files in os.walk(path):
        print (parent)
        for strfile in files:
            if (strfile.startswith('2G')):
                print ("2G")
                f = open(parent + "/" + strfile, 'r')
                for line in f.readlines():
                    s=line.strip('\n').split(",")
                    if len(s[2])>=4 or len(s[3])>=3:
                        map2g[s[0]+"#"+s[1]]=s[2]+"#"+s[3]

            if (strfile.startswith('4G')):
                print ("4G")
                f = open(parent + "/" + strfile, 'r')
                for line in f.readlines():
                    s=line.strip('\n').split(",")
                    if len(s[2])>=4 or len(s[3])>=3:
                        map4g[s[0]+"#"+s[1]]=s[2]+"#"+s[3]
    num=len(map2g.items())/1000
    for i in range(0,num):
        thread.start_new_thread(timer, (i,map2g.items()[i*1000:(i+1)*1000]))

    #amap=sorted(map4g.iteritems(), key=itemgetter(1), reverse=True)
    #amap=sorted(map4g.iteritems(), key=lambda d:d[1])[0:10]
    #for item in amap:   
    #    print (item)
    #for key in map4g.keys():   
        #print (key+','+map4g[key])

if __name__ == '__main__':
    print('''***********************
*     网优基站距离项目    *
***********************''')
    print('''基站距离计算开始...''')
    # time.sleep(60)
    print (strdir)
    computeDist(strdir)
    for item in result:   
        print (item)