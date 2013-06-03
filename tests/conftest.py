# coding: utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

LANGS = ['en','ko','ja']

def configure():
    os.environ['SERVER_NAME']='localhost'
    os.environ['SERVER_PORT']='8080'
    os.environ['USER_EMAIL']='test@example.com'
    os.environ['USER_IS_ADMIN']= '1'
    return

def langs():
	return LANGS
