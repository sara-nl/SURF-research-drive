import os, sys, requests, re
from lxml import objectify,etree

HTTPOK=200
OCOK=100

datematch=re.compile('\d{4}-\d{2}-\d{2}')

class API:
    def __init__(self, url, username, password, path='ocs/v1.php/apps/files_sharing/api/v1'):
        self._url = url
        self._remotedir = path
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._requestpath = '{0}/{1}/{2}'.format(url, path, 'shares')

    def send_request(self, verb, path, query='', body='', headers=None, properties=None):
        if not headers:
            headers = {}
        response = self._session.request(verb, path, params=query, data=body, headers=headers)

        return response

    def get_result_list(self,tag,response):
        xml_without_encoding_declaration = '\n'.join(response.text.split('\n')[1:])
        obj=objectify.fromstring(xml_without_encoding_declaration)
    
        resultlist=[]
        for item in obj.findall(".//"+tag):
            children=item.getchildren()
            result={}
            for child in children:
                result.update({child.tag:child.text})
            resultlist.append(result)

        return resultlist

    def get_shares(self,path='',reshares=False,subfiles=False):
        requestpath=self._requestpath

        if path=='' or path=='/':
            query=''
        else:
            query={'path':path,
                   'reshares':reshares,
                   'subfiles':subfiles}

        response=self.send_request('GET', requestpath,query=query)
        if response.status_code != HTTPOK: return False

        result=self.get_result_list('meta',response)[0]
        if int(result['statuscode'])!=OCOK:
            return result

        return self.get_result_list('element',response)

    def get_info_from_share(self,shareid):
        requestpath=self._requestpath+'/'+str(shareid)
        response=self.send_request('GET', requestpath)
        if response.status_code != HTTPOK: return False

        result=self.get_result_list('meta',response)[0]
        if int(result['statuscode'])!=OCOK:
            return result

        return self.get_result_list('element',response)

    def create_share(self,name=None,path=None,shareType=None,shareWith=None,publicUpload=False,password=None,permissions=None,expireDate=None):

        body={}
        if path==None or permissions==None or shareType==None: return False

        body.update({'path':path})
        body.update({'shareType':shareType})
        body.update({'permissions':permissions})

        if name!=None: body.update({'name':name})
        if shareWith!=None: body.update({'shareWith':shareWith})
        if publicUpload!=None: body.update({'publicUpload':publicUpload})
        if password!=None: body.update({'password':password})

        if expireDate!=None:
            if datematch.match(expireDate)!=None:
                body.update({'expireDate':expireDate})
            else:
                return False

        requestpath=self._requestpath
        response=self.send_request('POST', requestpath,body=body)

        if response.status_code != HTTPOK: return False

        result=self.get_result_list('meta',response)[0]
        if int(result['statuscode'])!=OCOK:
            return result

        return self.get_result_list('element',response)

    def delete_share(self,shareid):
        requestpath=self._requestpath+'/'+str(shareid)
        response=self.send_request('DELETE', requestpath)
        if response.status_code != HTTPOK: return False

        return self.get_result_list('meta',response)[0]

    def update_share(self,shareid,name=None,permissions=None,password=None,publicUpload=False,expireDate=None):

        body={}

        if permissions!=None: body.update({'permissions':permissions})
        if password!=None: body.update({'password':password})
        if publicUpload!=None: body.update({'publicUpload':publicUpload})
        if expireDate!=None:
            if datematch.match(expireDate)!=None:
                body.update({'expireDate':expireDate})
            else:
                return False

        requestpath=self._requestpath+'/'+str(shareid)
        response=self.send_request('PUT', requestpath,body=body)

        if response.status_code != HTTPOK: return False

        result=self.get_result_list('meta',response)[0]
        if int(result['statuscode'])!=OCOK:
            return result

        return self.get_result_list('data',response)

