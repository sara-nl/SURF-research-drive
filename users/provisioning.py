import os, sys, requests, re
import xmltodict, json, yaml
from lxml import objectify,etree

HTTPOK=200
OCOK=100

class API:
# Internal methods of the class

    def __init__(self, url, username, password, path='ocs/v1.php/cloud'):
# Constructor
        self._url = url
        self._remotedir = path
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._requestpath = '{0}/{1}'.format(url, path)




    def __handle_response__(self,response):
# Handles response from http requests and Owncloud return codes. 
# It returns the result from the request.
        if response.status_code != HTTPOK: return False,str(response.status_code)

        statuscode=int(self.__get_result_list__('statuscode',response)[0])
        if statuscode!=OCOK:
            msg=self.__get_result_list__('message',response)[0]
            if msg==None: 
                message='Owncloud status code: '+str(statuscode)
            else:
                message='Owncloud status code: '+str(statuscode)+', '+msg
            return False,message

        return True,''




    def __send_request__(self, verb, path, query='', body='', headers=None, properties=None):
# Sends request to server
        if not headers:
            headers = {}
        response = self._session.request(verb, path, params=query, data=body, headers=headers)

        return response




    def __get_result_list__(self,tag,response):
# Convert the response of a request to a list
        xml_without_encoding_declaration = '\n'.join(response.text.split('\n')[1:])
        obj=objectify.fromstring(xml_without_encoding_declaration)
    
        resultlist=[]
        for item in obj.findall(".//"+tag):
            resultlist.append(item.text)

        return resultlist




    def __get_result_list_json__(self,response):
# Convert the response of a request to json output
        xml_without_encoding_declaration = '\n'.join(response.text.split('\n')[1:])
        return json.dumps(xmltodict.parse(xml_without_encoding_declaration))




    def __get_all__(self,path):
# Helper function to return all users or groups
        requestpath = '{0}/{1}'.format(self._requestpath, path)

        response=self.__send_request__('GET', requestpath)
        if response.status_code != HTTPOK: return False,str(response.status_code)

        statuscode=int(self.__get_result_list__('statuscode',response)[0])
        if statuscode!=OCOK:
            message=self.__get_result_list__('message',response)[0]
            return False,message

        return True,self.__get_result_list__('element',response)




    def __get_info__(self,item,path):
# Helper fnction to get information on users, groups, subadmins...
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, path,item)

        response=self.__send_request__('GET', requestpath)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,yaml.safe_load(self.__get_result_list_json__(response))['ocs']['data']



# Public methods of the class

    def get_all_users(self):
        return self.__get_all__('users')

    def get_user_info(self,user):
        return self.__get_info__(user,'users')

    def edit_user(self,user,key,value):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users',user)

        body={'key':key,'value':value}
        response=self.__send_request__('PUT', requestpath,body=body)
        
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def create_user(self,user,passwd):
        requestpath = '{0}/{1}'.format(self._requestpath, 'users')

        body={'userid':user,'password':passwd}
        response=self.__send_request__('POST', requestpath,body=body)
        
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def delete_user(self,user):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users', user)

        response=self.__send_request__('DELETE', requestpath)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def get_user_group_info(self,user):
        status,result=self.__get_info__(user+'/groups','users')
        if status==False: return status,result
        if result['groups']==None: return True,''
        return status,result['groups']['element']

    def add_user_to_group(self,user,group):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users', user+'/groups')

        body={'groupid':group}
        response=self.__send_request__('POST', requestpath,body=body)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def delete_user_from_group(self,user,group):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users', user+'/groups')

        body={'groupid':group}
        response=self.__send_request__('DELETE', requestpath,body=body)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def create_subadmin(self,user,group):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users', user+'/subadmins')

        body={'groupid':group}
        response=self.__send_request__('POST', requestpath,body=body)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def delete_subadmin(self,user,group):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'users', user+'/subadmins')


        body={'groupid':group}
        response=self.__send_request__('DELETE', requestpath,body=body)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def get_user_subadmin_info(self,user):
        status,result=self.__get_info__(user+'/subadmins','users')
        if status==False: return status,result
        return status,result['element']

    def get_all_groups(self):
        return self.__get_all__('groups')

    def get_group_info(self,group):
        status,result=self.__get_info__(group,'groups')
        if status==False: return status,result
        if result['users']==None: return status,''
        return status,result['users']['element']

    def get_subadmins(self,group):
        status,result=self.__get_info__(group+'/subadmins','groups')
        if status==False: return status,result
        return status,result['element']
        
    def create_group(self,group):
        requestpath = '{0}/{1}'.format(self._requestpath, 'groups')

        body={'groupid':group}
        response=self.__send_request__('POST', requestpath,body=body)
        
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''

    def delete_group(self,group):
        requestpath = '{0}/{1}/{2}'.format(self._requestpath, 'groups', group)

        response=self.__send_request__('DELETE', requestpath)
        status,message=self.__handle_response__(response)
        if not status: return status,message

        return True,''
