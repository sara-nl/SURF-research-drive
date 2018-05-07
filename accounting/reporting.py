#!/usr/bin/env python

import time
import locale
from datetime import datetime,timedelta,date
import os
import sys
import commands
import re

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

import mysql.connector

db_acc=''
dbuser_acc=''
dbhost_acc=''
dbpass_acc=''

surfdrivelink=''
surfdriveurl=''
notfound='404'
http20x=re.compile('20.*')

tb=1000000000000.0

logfile='/var/log/reporting.log'

sender=''
to1=['','']
to2=['']

mail_text="""

Hallo ResearchDrivers,

Hier is de accounting data van %s.

Mvg,

PWC
"""

def get_vorigemaand():
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    today=date.today()
    first=date(day=1,month=today.month,year=today.year)
    lastdayoflastmonth=first-timedelta(days=1)
    vorige_maand=lastdayoflastmonth.strftime('%B %Y')

    return vorige_maand

def get_vandaag():
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    today=date.today()
    vandaag=today.strftime('%d %B %Y')

    return vandaag

def is_first():
    today=date.today()
    if today.day==1: return True
    return False

def log(text):
    timestamp=get_timestamp()
    f=open(logfile,'a')
    f.write(timestamp+':'+text)
    f.close()

def get_date(delta):

    thisdate=date.today()-timedelta(days=delta)

    return thisdate.isoformat()

def connect (dbhost,dbuser,dbpasswd,db):

    try:
        conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    except:
        log ("Cannot connect to database!")
        sys.exit(1)

    return conn

def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
    assert isinstance(send_to, list)
    assert isinstance(files, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


def main():

    thisdate=get_date(0)
    is1st=is_first()
    if is1st:
        csv='/tmp/researchdrive '+get_vorigemaand()+'.csv'
    else:
        csv='/tmp/researchdrive '+get_vandaag()+'.csv'
     
    f=open(csv,'w')
    f.write(';;;;;;;;;;;;;\n')
    f.write('cuser;description;email;ocgroup;quote;infra;project;usage TB;quotum TB;e-infra;contact OPS; contact BD; start date; end date\n')
    f.write(';;;;;;;;;;;;;\n')
    conn=connect(dbhost_acc,dbuser_acc,dbpass_acc,db_acc)
    c=conn.cursor()

    crmdb_query="""select ocgroup,cuser,description,project,quote,infra,email,einfra,quotum_gb,contact_ops,contact_bd,start_date,end_date from crmdb;"""
    c.execute(crmdb_query)
    groups={}
    for r in c:
        if r[0]!=None:
            l=[]
            for i in range(1,len(r)): l.append(r[i])
            groups.update({r[0]:l})

    for group in groups.keys():

        end_date=''
        start_date=''
        contact_bd=''
        contact_ops=''
        quotum=''
        einfra=''
        email=''
        table=''
        quote=''
        project=''
        description=''
        cuser=''

        if groups[group][11]!=None: end_date=groups[group][11].isoformat()
        if groups[group][10]!=None: start_date=groups[group][10].isoformat()
        if groups[group][9]!=None: contact_bd=groups[group][9]
        if groups[group][8]!=None: contact_ops=groups[group][8]
        if groups[group][7]!=None: quotum=str(round(float(groups[group][7])/1000.0,3))
        if groups[group][6]!=None: einfra=str(groups[group][6])
        if groups[group][5]!=None: email=groups[group][5]
        if groups[group][4]!=None: table=groups[group][4]
        if groups[group][3]!=None: quote=groups[group][3]
        if groups[group][2]!=None: project=groups[group][2]
        if groups[group][1]!=None: description=groups[group][1]
        if groups[group][0]!=None: cuser=groups[group][0]

        query="select sum(bytes) from "+table+"_usage where date='"+thisdate+"' and ( gid='"+group+"' or gid='"+group+"_' );"
        c.execute(query)

        terab=c.fetchone()[0]
        if terab!=None:
            terabytes=str(round(float(terab)/tb,3))
        else:
            terabytes='0.0'
        f.write(cuser+';'+description+';'+email+';'+group+';'+quote+';'+table+';'+project+';'+terabytes+';'+quotum+';'+einfra+';'+contact_ops+';'+contact_bd+';'+start_date+';'+end_date+'\n')

    f.close()
            
    
    conn.commit()
    c.close()

    if is1st:
        p=get_vorigemaand()
        to=to1
    else:
        to=to2
        p=get_vandaag()
    send_mail(sender,to,'ResearchDrive accounting '+p,mail_text%(p),[ csv ])

    today=date.today()
    if is1st:
        first=date(day=1,month=today.month,year=today.year)
        lastdayoflastmonth=first-timedelta(days=1)
        year=lastdayoflastmonth.year
    else:
        year=today.year

    cmdstring="curl -s -S -u "+surfdrivelink+" --head -X PROPFIND "+surfdriveurl+"/ResearchDrive/"+str(year)+" | grep HTTP | awk '{print $2}'"
    a=commands.getstatusoutput(cmdstring)
    if a[0]!=0 or ( http20x.match(a[1]) == None and a[1]!=notfound ): sys.exit(1)
 
    if a[1]==notfound:
        cmdstring="curl -s -S -u "+surfdrivelink+" --head -X MKCOL "+surfdriveurl+"/ResearchDrive/"+str(year)+" | grep HTTP | awk '{print $2}'"
        a=commands.getstatusoutput(cmdstring)
        if a[0]!=0 or http20x.match(a[1])==None: sys.exit(1)

    fn=os.path.basename(csv).replace(" ","%20")
    cmdstring="curl -u "+surfdrivelink+" -T \""+csv+"\" "+surfdriveurl+"/ResearchDrive/"+str(year)+"/"+fn
    a=commands.getstatusoutput(cmdstring)

    os.remove(csv)

if __name__ == '__main__':

    
    main()
