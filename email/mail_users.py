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

sender=''

# Put SURFsara people first in the dictionary
maildict={
'':'',
'':''
}

mailtext="""
 
Dear %s,

%s

Kind Regards,

The ResearchDrive Team

"""

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

def usage():
    sys.stderr.write('Usage: mail_users.py <file with text> \"subject\"\n')


def main(text_file,subject):

    global maildict

    conn=connect(dbhost_acc,dbuser_acc,dbpass_acc,db_acc)
    c=conn.cursor()

    query="""select users.cuser,users.email,crmdb.infra from crmdb,users where users.project_id=crmdb.project_id and crmdb.state=1;"""
    c.execute(query)
    for r in c:
        name=r[0].encode('ascii')
        email=r[1].encode('ascii')
        infra=r[2].encode('ascii')
        maildict.update({name:email})

    f=open(text_file)
    lines=f.readlines()
    f.close()

    text=''
    for line in lines:
        text+=line

    for name in maildict.keys():
        email=maildict[name]
        send_mail(sender,[email],subject,mailtext%(name,text))

if __name__ == '__main__':

    if len(sys.argv)<2:
        usage()
        sys.exit(1)

    text_file=sys.argv[1]
    if not os.path.exists(text_file):
        sys.stderr.write(text_file+'does not exist.\n')
        usage()
        sys.exit(1)

    subject=sys.argv[2]
    
    main(text_file,subject)
