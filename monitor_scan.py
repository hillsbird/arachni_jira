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
	jira = JIRA('http://jira.xxx.com/')
	issues = jira.search_issues('xxx')
	return issues

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

def mail(a,b,c):
	user = "xxx"
 	password = "xxx"
	to_list = ["xxx"]
	msg = a+'---'+b+'---'+c
	message = MIMEText(msg, 'plain', 'utf-8')
	message['Subject'] = Header('You have a syslog warn', 'utf-8')
	message['From'] = Header('xxx')
	message['To'] = Header('xxx')
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
		r = requests.get('xxx'+scanid[0][0]+'/report')
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
	authed_jira = JIRA('http://jira.xxx.com/',basic_auth=('qudian_sec', 'xxx'))
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
			r = requests.get('xxx'+scanid[0][0])
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
