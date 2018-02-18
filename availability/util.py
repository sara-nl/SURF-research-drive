def print_listing(xml_object):
   responses=xml_object.getchildren()
   for response in responses:
       a=response.getchildren()
       for i in a:
           if i.tag=='{DAV:}href': print i.text
   return
