#!/usr/bin/python
# -*- coding: UTF-8 -*-
from jira import JIRA
import re
import requests
import MySQLdb
import time
import json
import re
import datetime

#return issues need to scan
def get_issues():
	jira = JIRA('http://jira.qudian.com/')
	issues = jira.search_issues('issuetype = 业务需求 AND status = 待安全测试 AND assignee in (weichongfeng)')
	return issues

#return target host
def get_host(issue):
	host_url = issue.fields.customfield_10333
	pattern = re.compile('(http|https)://(\S+)$')
	m = pattern.match(str(host_url))
	if m:
		host = m.group()
	else:
		host = 'host wrong!'
	return host

#return cookie string
def get_cookie(issue):
	issue = str(issue)
	qd_security_account = '18515667715'
	lfq_security_account = '4342719'
	hostname = issue.split('-')[0]
	try:
		if hostname == 'QD':
			host = get_host(issue)
			tag = re.findall(r"http://(\S\S\S\d)",host)[0]
			login_url = 'http://'+tag+'.apitest.qufenqi.com/test/18515667715'
			r = requests.get(login_url,allow_redirects = False)
			cookie = r.headers['Set-Cookie']

		elif hostname == 'LFQ':
			cookie_uri = 'http://lfqshop.apprd.test.qudian.com/test/login?id=' + lfq_security_account
			cookie_url = cookie_uri
			r = requests.get(cookie_url)
			cookie = r.headers['Set-Cookie']

		else:
			cookie = 'SecurityTest'

		return cookie
	except Exception,e: 
		print e
		return 'wrong cookie!'

#insert jira No. and scan id into db
def insert_db(jira_no,scan_id):
	try:
		now = str(datetime.datetime.now())
		conn = MySQLdb.connect(host='localhost',port=3306,user='wei',passwd='hehe',db='arachni_test')
		cur = conn.cursor()
		sql = "insert into arachni (jira,scanid,start) values (%s,%s,%s);"
		param = (jira_no,scan_id,now)
		n = cur.execute(sql,param)            
		cur.close()                           
		conn.commit()                         
	except Exception,e:                       
		print e                               
		conn.rollback()    

#return scan id
def make_scan(issue,target):
	arachni_host = 'http://121.199.30.51:7331/scans'
	cookie = get_cookie(issue)
	host = get_host(issue)
	print target

	data = {
  		"url" : target,
  		"http" : {
  		  "user_agent" : "Arachni/v2.0dev Qudian_Security",
  		  "request_timeout" : 10000,
  		  "request_redirect_limit" : 5,
  		  "request_concurrency" : 10,
  		  "request_queue_size" : 50,
  		  "request_headers" : {},
  		  "response_max_size" : 500000,
  		  "cookie_string" : cookie
  		},
  		"audit" : {
  		  "parameter_values" : 'true',
  		  "exclude_vector_patterns" : [],
  		  "include_vector_patterns" : [],
  		  "link_templates" : [],
  		  "headers": 'true',
  		  "forms": 'true'
  		},
  		"input" : {
  		  "values" : {},
  		  "default_values" : {
  		    "(?i-mx:name)" : "",
  		    "(?i-mx:user)" : "",
  		    "(?i-mx:usr)" : "",
  		    "(?i-mx:pass)" : "5543!%",
  		    "(?i-mx:txt)" : "",
  		    "(?i-mx:num)" : "",
  		    "(?i-mx:amount)" : "",
  		    "(?i-mx:mail)" : "weichongfeng@qudian.com",
  		    "(?i-mx:account)" : "",
  		    "(?i-mx:id)" : "1"
  		  },
  		  "without_defaults" : 'false',
  		  "force" : 'false'
  		},
  		"browser_cluster" : {
  		  "wait_for_elements" : {},
  		  "pool_size" : 10,
  		  "job_timeout" : 10,
  		  "worker_time_to_live" : 100,
  		  "ignore_images" : 'true',
  		  "screen_width" : 1600,
  		  "screen_height" : 1200
  		},
  		"scope" : {
  		  "redundant_path_patterns" : {},
  		  "dom_depth_limit" : 3,
  		  "exclude_path_patterns" : ["/assets/*","/css/*","/js/*","/i/message*","/i/goods_detail/*","/qufenqi/static/*","/laifenqi/static/*","/v2/login/*"],
  		  "exclude_content_patterns" : [],
  		  "include_path_patterns" : [],
  		  "restrict_paths" : [],
  		  "extend_paths" : [],
  		  "url_rewrites" : {}
  		},
  		"session" : {},
  		"checks" : ["sql_injection",],
  		"platforms" : [],
  		"plugins" : {},
  		"no_fingerprinting" : 'false',
  		"authorized_by" : 'null'
	}
	r = requests.post(arachni_host,json=data)
	res = json.loads(r.text)
	insert_db(issue,res['id'])
	return res['id'] #unicode type

def change_jira(issue):
	authed_jira = JIRA('http://jira.qudian.com/',basic_auth=('qudian_sec', 'Qudian_sec110'))
	authed_jira.assign_issue(issue, 'qudian_sec')


if __name__ == '__main__':
	while 1:
		scan_todo = list()
		issues = get_issues()
		for i in issues:
			host = get_host(i)
			hostname = str(i).split('-')[0]
			if host != 'host wrong!' and hostname == 'QD':
				change_jira(i)
				target = host + '/v2/home'
				scan_todo.append(str(i)+'|'+str(target))

			elif host !='host wrong!' and hostname == 'LFQ':
				change_jira(i)
				target == 'http://lfqshop.apprd.test.qudian.com/i/user'
				make_scan(i,target)
			else:
				pass
		time.sleep(300)
		now = time.strftime('%H-%M-%S',time.localtime(time.time()))
		if now == '23-00-00':
			for t in scan_todo:
				make_scan(t.split('|')[0],t.split('|')[1])





