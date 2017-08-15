#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import re
import json
import MySQLdb
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from jira import JIRA
import time

def get_issues():
	jira = JIRA('http://jira.qudian.com/')
	issues = jira.search_issues('issuetype = 业务需求 AND status = 待安全测试 AND assignee in (qudian_sec)')
	return issues

def get_scanid_by_jira(id):
	try:
		conn = MySQLdb.connect(host='localhost',port=3306,user='wei',passwd='hehe',db='arachni_test')
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

def mail(a,b,c):
	user = "weichongfeng@qudian.com"
 	password = "Woshitiancai0323!"
	to_list = ["sec@qudian.com"]
	msg = a+'---'+b+'---'+c
	message = MIMEText(msg, 'plain', 'utf-8')
	message['Subject'] = Header('You have a syslog warn', 'utf-8')
	message['From'] = Header('weichongfeng@qudian.com')
	message['To'] = Header('sec@qudian.com')
	try:
		server = smtplib.SMTP("smtp.exmail.qq.com")
		server.login(user,password)
		server.sendmail("<%s>"%user, to_list,message.as_string())
		server.close()
	except Exception,e: 
		print e

def monitor_scan_summary(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		r = requests.get('http://121.199.30.51:7331/scans/'+scanid[0][0]+'/report')
		result = json.loads(r.text)
		print id
		for i in result['issues']:
			name = i['name']
			severity = i['severity']
			url = i['vector']['url']
			if severity in ['high']:
				mail(name,severity,url)
				print name+'---'+severity+'---'+url
			else:
				pass
	else:
		print 'scanid wrong'

def change_jira_done(issue):
	authed_jira = JIRA('http://jira.qudian.com/',basic_auth=('qudian_sec', 'Qudian_sec110'))
	try:
		authed_jira.transition_issue(issue,'121')
		print 'Change jira done!'
	except Exception,e:
		print e

def check_scan_done(id):
	scanid = get_scanid_by_jira(id)
	if scanid:
		change_jira_done(id)
		try:
			r = requests.get('http://121.199.30.51:7331/scans/'+scanid[0][0])
			if json.loads(r.text)['status'] == 'done':
				monitor_scan_summary(id)
		except Exception,e:
			print e
		else:
			pass
	else:
		pass


if __name__ == '__main__':
	while 1:
		issues = get_issues()
		for i in issues:
			check_scan_done(i)
		time.sleep(60)