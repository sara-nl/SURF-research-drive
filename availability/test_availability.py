#!/usr/bin/env python

import sys,md5,os
from webdavclient import Client
from testconfig import url,path,oz
from lxml import objectify, etree

md5_file='cb34a143651668570fb0961259ac5bd9'
file='/tmp/bla'+md5_file+'.jpg'

if __name__ == '__main__':
   reload(sys)
   sys.setdefaultencoding('utf8') # http://tinyurl.com/why-we-need-sys-setdefaultenco
  
   URL=url
   PATH=path
   USER=oz['username']
   PASS=oz['password']
  
   client = Client(URL, USER, PASS, PATH)
   client.authenticate()

   result=client.download_file(file,'oz_permanent_dir/frank.jpeg')
   if not result:
       print 'not OK'
       sys.exit(1)

   f=open(file)
   l=f.read()
   f.close()
   
   m=md5.new()
   m.update(l)
   thismd5=m.hexdigest()
   if thismd5 == md5_file:
       print 'OK'

   os.remove(file)

