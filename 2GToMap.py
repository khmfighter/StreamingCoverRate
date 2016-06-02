#!/usr/bin/env python
## -*- coding:utf-8 -*-
from __future__ import print_function
from multiprocessing import Process, Manager
__author__ = 'KHM'
import os, sys, datetime, time, math, multiprocessing
from operator import itemgetter
from getopt import getopt, GetoptError
t1=time.time()
type_map = {0:'室内',1:'室外',2:'室内外'}
type_city = {'HAZ':'杭州','HUZ':'湖州','JX':'嘉兴','JH':'金华','LS':'丽水','NB':'宁波','QZ':'衢州','WZ':'温州','TZ':'台州','SX':'绍兴','ZS':'舟山'}

EARTH_RADIUS = 6378137
#gsm_map={}
#gsm_map_total={}
#lte_map_total={}



try:
    opts, hosts = getopt(sys.argv[1:], 'd:p:t:')
except GetoptError:
    print("Syntax error")
    sys.exit(1)
#strdir = os.path.split(os.path.realpath(sys.argv[0]))[0]
for opt in opts:
	if opt[0] == '-d':
		#日期时间
		_date_type = opt[1]
	if opt[0] == '-p':
		# 地市类型
		_country_type = opt[1]
	if opt[0] == '-t':
    	# 室内or室外
		_jz_type = opt[1]

def rad(d):
    return d * math.pi / 180.0

def ReturnDistance(tag):
	if tag==0:
		return 50#0.05
	if tag==1:
		return 300#0.3


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

def saveFileToLocal(city,type,var_map,var_list):
	file = open(city+"_"+type+"_"+_date_type+'.txt', 'w')
	for key in var_map.keys():
		if key not in var_list:
			file.write(key+'\n')
	file.close()


def ComputerData(result_map,country_type,jz_type):
	gsm_map={}
	gsm_map_total={}
	lte_map_total={}
	result_list=[]
	count=0
	total_count=0
	use_count=0
	#获取GSM基站信息
	f_sub = open("/home/khuaming/WYJZ/files/ZJ_GSM-R01_CellResources_"+_date_type+".csv",'r')
	for line_sub in f_sub.readlines():
		s_sub=line_sub.decode('gbk').encode('utf-8').split(',')
		if type_city[country_type]==s_sub[1] and int(jz_type)==0:
			if type_map[0] == s_sub[40]:
				str_in=s_sub[1]+"#"+s_sub[10]+"#"+s_sub[11]
				#经度#维度#室内外
				#gsm_map_total[str_in]=s_sub[15]+"#"+s_sub[16]+"#"+s_sub[40]
				gsm_map_total[str_in]=s_sub[15]+"#"+s_sub[16]
		if type_city[country_type]==s_sub[1] and int(jz_type)==1:
			if type_map[1] == s_sub[40] or type_map[2] == s_sub[40]:
				str_in=s_sub[1]+"#"+s_sub[10]+"#"+s_sub[11]
				#经度#维度#室内外
				#gsm_map_total[str_in]=s_sub[15]+"#"+s_sub[16]+"#"+s_sub[40]
				gsm_map_total[str_in]=s_sub[15]+"#"+s_sub[16]
	f_sub.close()
	#获取LTE基站信息
	f_lte = open("/home/khuaming/WYJZ/files/ZJ_LTE-R01_CellResources_"+_date_type+".csv",'r')
	for line_lte in f_lte.readlines():
		s_lte=line_lte.decode('gbk').encode('utf-8').split(',')
		if type_city[country_type]==s_lte[2] and int(jz_type)==0:
			if type_map[0] == s_lte[13]:
				#经度#维度
				str_in=s_lte[18]+"#"+s_lte[19]
				#地市名称#室内外
				lte_map_total[str_in]=s_lte[2]+"#"+type_map[0]
		if type_city[country_type]==s_lte[2] and int(jz_type)==1:
			if type_map[1] == s_lte[13] or type_map[2] == s_lte[13]:
				#经度#维度
				str_in=s_lte[18]+"#"+s_lte[19]
				#地市名称#室内外
				lte_map_total[str_in]=s_lte[2]+"#"+type_map[1]
	f_lte.close()


	#计算相关指标
	f = open("/home/khuaming/WYJZ/files/2G_"+_date_type+".csv",'r')
	for line in f.readlines():
		s=line.decode("gbk").encode("utf-8").split(',')
		#地市#LAC#CI
		str_out=s[0]+"#"+s[1]+"#"+s[2]
		if gsm_map_total.has_key(str_out):
			#gsm_map_total[str_out]为：经度#维度#室内外
			gsm_map[str_out]=gsm_map_total[str_out]
			count=count+1
	f.close()

	total_count=float(len(gsm_map))

	#print (type_city[country_type]+"-GSM总条数:"+str(len(gsm_map)))
	#print (type_city[country_type]+"-LTE总条数:"+str(len(lte_map_total)))
	value_str=type_city[country_type]+"#"+type_map[int(jz_type)]
	for k2g,v2g in gsm_map.items():
		#print("1:"+k2g+"---->"+v2g)
		#print("2:"+value_str+"--->"+str(len(lte_map_total)))
		for k4g,v4g in lte_map_total.items():
			if v4g==value_str:
				#print (str(GetDistance(k4g,v2g)))
				int_value=GetDistance(k4g,v2g)
				if int_value<ReturnDistance(int(jz_type)):
					use_count=use_count+1
					#print ("3:"+str(int_value))
					#存在LTE基站的GSM基站
					result_list.append(k2g)
					break
	saveFileToLocal(type_city[country_type],type_map[int(jz_type)],gsm_map,result_list)
	print (type_city[country_type]+"-LTE条数:"+str(int(use_count)))
	print (type_city[country_type]+"-GSM条数:"+str(int(total_count)))
	print(value_str+":"+str(round((use_count/total_count)*100,2))+"%")
	result_map[value_str]=str(use_count)+"#"+str(total_count)
	t2=time.time()
	#print("计算所需时间:"+str(round(t2-t1,1))+"秒")
	result_list=[]
	gsm_map.clear()
	lte_map_total.clear()
	gsm_map_total.clear()

if __name__ == '__main__':
    print('''***********************
*  网优基站距离项目 *
***********************''')
    print('''基站距离计算开始...''')
    processings = []
    total_use_count=0.0
    total_total_count=0.0
    mgr = Manager()
    result_map=mgr.dict()
    if _country_type=="ALL":
    	for key_val in type_city.keys():
    		tdd = multiprocessing.Process(target=ComputerData,args=(result_map,key_val,_jz_type))
    		processings.append(tdd)
    	for th in processings:
    		#th.daemon=True
        	th.start()

    	#for th in threads :
        #	threading.Thread.join( th )
        	#th.join()
        while True:
        	if len(multiprocessing.active_children())==1:
        		for key,value in result_map.items():
    				total_use_count=total_use_count+float(value.split("#")[0])
    				total_total_count=total_total_count+float(value.split("#")[1])
    			print("全省"+type_map[int(_jz_type)]+":"+str(round((total_use_count/total_total_count)*100,2))+"%")
       			break
       	#print(threading.activeCount())
        #if threading.activeCount()==0:
    	#for key,value in result_map.items():
    	#	total_use_count=total_use_count+float(value.split("#")[0])
    	#	total_total_count=total_total_count+float(value.split("#")[1])
    	#print("全省"+type_map[int(_jz_type)]+":"+str(round((total_use_count/total_total_count)*100,2))+"%")
    else:
    	ComputerData(result_map,_country_type,_jz_type)
    	#print (len(result_map))
    	for key,value in result_map.items():
    		total_use_count=total_use_count+float(value.split("#")[0])
    		total_total_count=total_total_count+float(value.split("#")[1])
    	print(type_city[_country_type]+type_map[int(_jz_type)]+":"+str(round((total_use_count/total_total_count)*100,2))+"%")
