#!/usr/bin/env python

import time
import datetime
import locale
import os
import sys
import getopt
import re

import mysql.connector

# Make sure that the dbuser_oc is granted the rights to do a select on the OC 
# database. 
#
# Make sure that dbuser_acc is granted insert rights to the appropriate 
# tables in the accounting database.
#
# Naming convention: 
# Name the owncloud database <some name>_oc
# Name the corresponding table for the accounting data <some name>_usage

db_acc=''
dbuser_acc=''
dbhost_acc=''
dbpass_acc=''

tables=['','']

dbuser_oc=''
dbhost_oc=''
dbpass_oc=''

logfile='/var/log/accounting.log'

object=re.compile('object\:\:user\:')

storages_query="""select numeric_id from oc_storages where id not like 'object::%';"""
types_query="""select distinct oc_filecache.path from oc_filecache,oc_storages,oc_mimetypes where oc_filecache.mimetype=oc_mimetypes.id and oc_mimetypes.mimetype='httpd/unix-directory' and oc_filecache.path not like '%/%' and oc_filecache.path!=''"""
query="""select oc_storages.id,sum(oc_filecache.size) from oc_filecache,oc_storages,oc_mimetypes where oc_filecache.mimetype=oc_mimetypes.id and oc_mimetypes.mimetype='httpd/unix-directory' and oc_filecache.path = '%s' and oc_storages.numeric_id=oc_filecache.storage group by oc_filecache.storage;"""

def log(text):
    timestamp=get_timestamp()
    f=open(logfile,'a')
    f.write(timestamp+':'+text)
    f.close()

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def get_date():
    tm=time.localtime(time.time())
    date=time.strftime('%Y-%m-%d',tm)

    return date

def connect (dbhost,dbuser,dbpasswd,db):

    try:
        conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    except:
        log ("Cannot connect to database!")
        sys.exit(1)

    return conn


def insertdatain(db):

    db_oc=db+'_oc'

    conn=connect(dbhost_oc,dbuser_oc,dbpass_oc,db_oc)
    c=conn.cursor()

    c.execute(storages_query)
    qstring=''
    for r in c:
        qstring+=' and oc_filecache.storage!='+str(r[0])

    c.execute(types_query+qstring+';')
    types_list=[]
    for r in c:
        types_list.append(r[0])


    dict={}

    for type in types_list:

        dict[type]={}

        c.execute(query%(type))

        for r in c:
            if object.search(r[0]) != None:       
                user=object.sub('',r[0])
                dict[type].update({user:long(r[1])})

    c.execute("select userid from oc_preferences where configkey='isGuest';")
    guests=[]
    for r in c:
        guests.append(r[0])

    c.execute("select uid,gid from oc_group_user;")
    ug={}
    for r in c:
        user=r[0]
        group=r[1]
        if not ug.has_key(user): 
            ug.update({user:group})
        else:
            ug[user]+=','+group
        
    
    conn.commit()
    c.close()

    
    conn=connect(dbhost_acc,dbuser_acc,dbpass_acc,db_acc)
    c=conn.cursor()

    date=get_date()
    for type in types_list:
        for name in dict[type].keys():

            group=''

            bytes=dict[type][name]

            isguest=0
            if name in guests: isguest=1

            if ug.has_key(name): group=ug[name]
            
            s="insert into "+db+"_usage (date,uid,gid,type,isguest,bytes) values ('"+date+"','"+name+"','"+group+"','"+type+"',"+str(isguest)+","+ str(bytes)+");"
            c.execute(s)

    conn.commit()

    c.close()

#    for name in dict['files'].keys():
#        print name,dict['files'][name]

def main():

    for table in tables:
        insertdatain(table)


if __name__ == '__main__':

    
    main()
