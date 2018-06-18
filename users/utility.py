#!/usr/bin/env python

from provisioning import API
import sys,argparse,os

default_infra='defaultinfra'

def get_input(text):
    if sys.version_info.major==2:
        return raw_input(text)
    else:
        return input(text)

def get_api(infra):

# Checkuser id
#    if os.getuid()!=0:
#        sys.stderr.write('You need to be super user to run this command\n')
#        sys.exit(1)

# Import the module with the credentials to access the appropriate instance
    try:
        exec("from %s import url, username, password" %(infra))
    except ImportError:
        sys.stderr.write('Unknown instance: '+infra+'\n')
        sys.exit(1)
    except:
        sys.stderr.write('Something went wrong\n')
        sys.exit(1)

    return API(url,username,password)

def process_commandline_input(text='',item=None):

    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-i", "--infra", dest = "infra", default = default_infra, help="The infrastructure you want to access. The default is "+default_infra+".")
    if item!=None:
        if item=='user' or item=='usergroup':
            parser.add_argument("user",help="The user that you want to perform this action for.")

        if item=='useredit':
            required = parser.add_argument_group('required arguments')
            required.add_argument("-k", "--key", dest = "key", required=True, help="The field to edit for a user.")
            required.add_argument("-v", "--value", dest = "value", required=True, help="The new value for the field.")
            parser.add_argument("user",help="The user that you want to perform this action for.")
                
        if item=='group' or item=='usergroup':
            parser.add_argument("group",help="The group that you want to perform this action for.")

        if item=='app':
            parser.add_argument("app",help="The app that you want to perform this action for.")

    return parser.parse_args()
