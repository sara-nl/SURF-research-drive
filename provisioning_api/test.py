#!/usr/bin/env python

import requests
from papi import API
import random,string

url=''
username='' 
password=''

api=API(url,username,password)

print "get_all_users"
status,result=api.get_all_users()
print status,result

print "get_all_groups"
status,result=api.get_all_groups()
print status,result

print "create_user"
tmp_passwd=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
status,result=api.create_user('rontest',tmp_passwd)
print status,result

print "get_user_info"
status,result=api.get_user_info('rontest')
print status,result

print "edit_user"
status,result=api.edit_user('rontest','email','pipo@surfsara.nl')
print status,result

print "get_user_info"
status,result=api.get_user_info('rontest')
print status,result

print "get user group info"
status,result=api.get_user_group_info('rontest')
print status,result

print "create group"
status,result=api.create_group('testgroep')
print status,result

print "add user to group"
status,result=api.add_user_to_group('rontest','testgroep')
print status,result

print "get user group info"
status,result=api.get_user_group_info('rontest')
print status,result

print "get group info"
status,result=api.get_group_info('testgroep')
print status,result

print "create subadmin"
status,result=api.create_subadmin('rontest','testgroep')
print status,result

print "get_user_subadmin_info"
status,result=api.get_user_subadmin_info('rontest')
print status,result

print "get_subadmins"
status,result=api.get_subadmins('testgroep')
print status,result

print "delete subadmin"
status,result=api.delete_subadmin('rontest','testgroep')
print status,result

print "get_user_subadmin_info"
status,result=api.get_user_subadmin_info('rontest')
print status,result

print "delete user from group"
status,result=api.delete_user_from_group('rontest','testgroep')
print status,result

print "get user group info"
status,result=api.get_user_group_info('rontest')
print status,result

print "delete group"
status,result=api.delete_group('testgroep')
print status,result

print "delete_user"
status,result=api.delete_user('rontest')
print status,result

#status,result=api.get_user_subadmin_info('ron')
#status,result=api.create_subadmin('ron','testgroep')
