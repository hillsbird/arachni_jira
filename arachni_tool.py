import requests
import re
import json
import MySQLdb
import argparse

def list_all_scan():
	r = requests.get('xxx')
	scanids = json.loads(r.text).keys()
	for s in scanids:
		jiraid = get_jira_by_scanid(s)
		print str(jiraid)+' : '+str(s)
	

def get_scanid_by_jira(id):
	try:
		conn = MySQLdb.connect(host='localhost',port=3306,user='wei',passwd='xxx',db='arachni_test')
		cur = conn.cursor()
		sql = "select scanid from arachni where jira =%s;"
		param = (id,)
		n = cur.execute(sql,param)
		issue = cur.fetchall()           
		cur.close()                           
		conn.commit()   
		return issue        
	except Exception,e:                       
		print e                               
		conn.rollback()
		return 0    

def get_jira_by_scanid(scanid):
	try:
		conn = MySQLdb.connect(host='localhost',port=3306,user='wei',passwd='xxx',db='arachni_test')
		cur = conn.cursor()
		sql = "select jira from arachni where scanid =%s;"
		param = (scanid,)
		n = cur.execute(sql,param)
		jiraid = cur.fetchall()           
		cur.close()                           
		conn.commit()   
		return jiraid        
	except Exception,e:                       
		print e                               
		conn.rollback()
		return 0    

def check_scan_progress(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.get('xxx'+scanid[0][0])
		print r.text
		return 1
	else:
		return 0

def show_scan_result(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.get('xxx'+scanid[0][0]+'/report')
		print r.text
		return 1
	else:
		return 0
def show_scan_summary(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r1 = requests.get('xxx'+scanid[0][0])
		status = json.loads(r1.text)['status']
		print status
		r = requests.get('xxx'+scanid[0][0]+'/report')
		result = json.loads(r.text)
		print 'vuln:'+str(len(result['issues']))
		for i in result['issues']:
			name = i['name']
			severity = i['severity']
			url = i['vector']['url']
			print name+'---'+severity+'---'+url
	else:
		print 'scanid wrong'

def pause_scan(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.put('xxx'+scanid[0][0]+'/pause')
		print r.text
		return 1
	else:
		return 0

def resume_scan(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.put('xxx'+scanid[0][0]+'/resume')
		print r.text
		return 1
	else:
		return 0

def abort_scan(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.delete('xxx'+scanid[0][0])
		print r.text
		return 1
	else:
		return 0

if __name__ == '__main__':
	description = ''
	parser = argparse.ArgumentParser()
	parser.add_argument('-l','--list',help='list all scan',action="store_true")
	parser.add_argument('-p','--progress',type=str,help='check progress')
	parser.add_argument('-r','--resume',type=str,help='resume a scan')
	parser.add_argument('-pa','--pause',type=str,help='pause a scan')
	parser.add_argument('-a','--abort',type=str,help='abort a scan')
	parser.add_argument('-s','--show',type=str,help='show result')
	parser.add_argument('-su','--summary',type=str,help='show scan summary')
	args =  parser.parse_args()

	if args.list:
		list_all_scan()
	elif args.progress:
		check_scan_progress(args.progress)
	elif args.resume:
		resume_scan(args.resume)
	elif args.pause:
		pause_scan(args.pause)
	elif args.abort:
		abort_scan(args.abort)
	elif args.show:
		show_scan_result(args.show)
	elif args.summary:
		show_scan_summary(args.summary)
	else:
		print 'Try: python arachni_tool.py -h'



