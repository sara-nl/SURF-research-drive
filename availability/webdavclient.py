import os, sys, requests
from lxml import objectify, etree

WEBDAV_STATUS_CODE = { # See http://tools.ietf.org/html/rfc4918
  'OK'                  : 200,
  'CREATED'             : 201,
  'NO_CONTENT'          : 204,
  'MULTI_STATUS'        : 207,
  'NOT_FOUND'           : 404,
  'METHOD_NOT_ALLOWED'  : 405,
  'PRECONDITION_FAILED' : 412,
  'REQUEST_URI_TOO_LONG': 414,
  'UNPROCESSABLE_ENTITY': 422,
  'LOCKED'              : 423,
  'FAILED_DEPENDENCY'   : 424,
  'INSUFFICIENT_STORAGE': 507,
}

class Client:
    def __init__(self, url, username, password, path='/'):
        self._url = url
        self._remotedir = path
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._authenticated = False
    
    def authenticate(self):
        response = self._session.get(self._url)
        if response.status_code == 200:
            self._authenticated = True
        return self._authenticated
  
    def send_request(self, verb, path, body='', headers=None, properties=None):
        if not headers: 
            headers = {}
            response = self._session.request(verb, path, data=body, headers=headers)
        return response
  
    def get_request_path(self, filename, path=None):
        requestpath = ''
        if not path:
            requestpath = '{0}/{1}'.format(self._remotedir, filename)
        else:
            requestpath = '{0}/{1}'.format(self._remotedir, path)
        return self._url + requestpath
    
    def propfind(self, path, properties=None):
        if not self._authenticated:
            self.authenticate()
        verb = 'PROPFIND'
        body = self.get_propfind_body()
        requestpath = self.get_request_path('', path)
        headers = {'Depth': '1'}
        response = self.send_request(verb, requestpath, body=body, headers=headers)
        if response.status_code == WEBDAV_STATUS_CODE['MULTI_STATUS']:
            xml_without_encoding_declaration = '\n'.join(response.text.split('\n')[1:])
            return objectify.fromstring(xml_without_encoding_declaration)
        return None
    
    def download_file(self,filename, path=None):
        requestpath = self.get_request_path(filename, path)
        response=self._session.get(requestpath,stream=True)
        if response.status_code != WEBDAV_STATUS_CODE['OK']: return False
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8096): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        f.close()
        return True

    def upload_file(self,filename,path=None):
        requestpath = self.get_request_path(filename, path)

        with open(filename, 'rb') as f:
            form = encoder.MultipartEncoder({
                "documents": (filename, f, "application/octet-stream"),
                "composite": "NONE",
            })
            headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
            response = self._session.post(requestpath, headers=headers, data=f)
        return True
        
    
    def upload_file(self, filename, path=None):
        verb = 'PUT'
        requestpath = self.get_request_path(filename, path)
        file = open(filename)
        response = self.send_request(verb, requestpath, file.read())
        if response.status_code in (WEBDAV_STATUS_CODE['CREATED'], WEBDAV_STATUS_CODE['NO_CONTENT']):
            return True
        return False

  
    def delete(self, filename, path=None):
        verb = 'DELETE'
        requestpath = self.get_request_path(filename, path)
        response = self.send_request(verb, requestpath)
        if response.status_code == WEBDAV_STATUS_CODE['NO_CONTENT']:
            return True
        return False
  
    def mkcol(self, filename, path=None):
        verb = 'MKCOL'
        requestpath = self.get_request_path(filename, path=None)
        response = self.send_request(verb, requestpath)
        if response.status_code == WEBDAV_STATUS_CODE['CREATED']:
            return True
        return False
     
    def get_propfind_body(self, properties=None):
        if not properties:
            properties=[]
        body = '<?xml version="1.0" encoding="utf-8" ?>'
        body += '<D:propfind xmlns:D="DAV:">'
        if properties:
            body += '<D:prop>'
            for prop in properties:
                body += '<D:' + prop + '/>'
            body += '</D:prop>'
        else:
            body += '<D:allprop/>'
        body += '</D:propfind>'
        return body
    
'''
EXAMPLES
print client.propfind(PATH)
print 'Creating directory testdir'
print 'OK' if client.mkcol('testdir') else 'FAIL'
print 'Creating directory testdir again'
print 'OK' if client.mkcol('testdir') else 'FAIL'
print 'Removing directory testdir'
print 'OK' if client.delete('testdir') else 'FAIL'
print 'Removing directory testdir again'
print 'OK' if client.delete('testdir') else 'FAIL'
print 'Putting file test.py'
print 'OK' if client.put('test.py') else 'FAIL'
print 'getting test.py'
resp = client.get('test.py')
print resp if resp else 'FAIL'
print 'Deleting file test.py'
print 'OK' if client.delete('test.py') else 'FAIL'
print 'Deleting file test.py again'
print 'OK' if client.delete('test.py') else 'FAIL'
'''
  
