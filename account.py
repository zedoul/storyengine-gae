## coding: utf-8
#
# Copyright 2012-2013 Scipi
#

"""
Account
"""

__author__ = 'Kim Seonghyun'

ACCOUNT_MOD_NONE = 0
ACCOUNT_MOD_COMMITER = 10
ACCOUNT_MOD_MAINTAINER = 99

import os
import webapp2
from webapp2_extras import sessions
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
import logging, string
from settings import ROOT_PATH
from settings import ROOT_URL
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from defines import FACEBOOK_APP_ID
from defines import FACEBOOK_APP_SECRET
from defines import USER_AGENT

from google.appengine.ext.webapp import template
from storyengine.model.account import Account
from storyengine.model.story import Story
from storyengine.model.content import Content
from storyengine.model.receipt import Receipt
from django import forms
from django.http import HttpResponse
from django.template import Context, loader
import json
import urllib
import cgi
import datetime
import storyengine
import storyengine.model
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from defines import APP_TITLE
from defines import CACHE_RECOMMENDED_ACCOUNTNUM
from google.appengine.api import memcache
from django.forms import PasswordInput

class AccountInfoForm(forms.Form):
	name = forms.CharField(label='ID',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	facebookID = forms.CharField(label='password',
		widget=forms.PasswordInput(attrs={'size':'54',
				'maxlength':'100'}))
	thumbnail = forms.Field(label='thumbnail',
		widget=forms.FileInput,
		required=False)

class AccountReadHandler(storyengine.SessionHandler):
	def get(self,accountid):
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		createds = []
		for i in account.createds:
			createds.append(i)
		context = {'static_path': STATIC_PATH,
			'account':account,
			'createds':createds,
			'keyid':account.key().name()}
		self.render_to_response('account_read.html',context)

class AccountUpdateHandler(storyengine.SessionHandler):
	def get(self,accountid):
		account = Account.get_by_accountid(accountid)
		logging.info('get')
		if 1 != account.mod:
			return
		f_data = account.to_formdict()
		s_form = AccountInfoForm(f_data)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,accountid):
		logging.info('asdfdszzzf')
		account = Account.get_by_accountid(accountid)
		logging.info('asdfdsf')
#		if 1 != account.mod:
#			return
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		account.setter(params)
		self.redirect('/account')

class AccountFBLoginHandler(storyengine.SessionHandler):
	def get(self):
		REDIRECT_URL = ROOT_URL+"/login"
		args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=REDIRECT_URL)
		self.redirect(
				"https://graph.facebook.com/oauth/authorize?" +
				urllib.urlencode(args))

'''http://facebook-python-library.docs-library.appspot.com/facebook-python/examples/oauth.html'''
class AccountFBLoginResponseHandler(storyengine.SessionHandler):
	def get(self):
		REDIRECT_URL = ROOT_URL+"/login"
		args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=REDIRECT_URL)
		"""redirect_url points to */login* URL of our app"""
		args["client_secret"] = FACEBOOK_APP_SECRET  #facebook APP Secret
		args["code"] = self.request.get("code")
		response = cgi.parse_qs(urllib.urlopen(
					"https://graph.facebook.com/oauth/access_token?" +
					urllib.urlencode(args)).read())
		access_token_ = response["access_token"][-1]
		profile = json.load(urllib.urlopen(
			    "https://graph.facebook.com/me?" +
			        urllib.urlencode(dict(access_token=access_token_))))
		account = Account.get_by_facebookid(profile["id"])
		if None == account:
			Account.api_login(profile['id'],
					access_token_,
					"2011-03-23 13:53:39",
					profile['name'])
			account = Account.get_by_facebookid(profile["id"])

		self.session['accountid'] = str(account.key().name()) 
		self.redirect("/")

class AccountLoginHandler(storyengine.SessionHandler):
	def get(self):
		s_form = AccountInfoForm(None)
		context = {'static_path': STATIC_PATH,
			'form': s_form}
		self.render_to_response('form.html',context)
	def post(self):
		name_ = self.request.get('name')
		facebookID_ = self.request.get('facebookID')
		ret = Account.api_login(
					name=name_,
					facebookid =facebookID_,
					access_token ="asdf",
					expiration_date_ = "2013-03-23 13:53:39"
					)
		account = Account.get_by_facebookid(facebookID_)
		keyid = str(account.key().name())
		self.session['accountid'] = keyid
		context = {'static_path': STATIC_PATH,
			'accountid':keyid}
		self.redirect("/")

class AccountCacheReadHandler(storyengine.SessionHandler):
	def get(self):
		print "[List]"
		print "<br \>"

		for i in range(1,CACHE_RECOMMENDED_ACCOUNTNUM+1):
			key = 'recentjoinedaccount'+str(i)
			det = memcache.get(key)
			print key + " : " + str(det)
			print "<br \>"

class AccountLogoutHandler(storyengine.SessionHandler):
	def get(self):
		del self.session['accountid']
		self.redirect("/")

class AppAccountLoginHandler(webapp2.RequestHandler):
	def post(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		self.response.headers['Content-Type'] = 'application/json'
		facebookID = self.request.get('facebookid')
		name = self.request.get('name')
		access_token = self.request.get('access_token')
		expiration_date = self.request.get('expiration_date')
		logging.info('id[%s] name[%s]',facebookID, name)

		if "" == access_token:
			access_token = None
		if "" == expiration_date:
			expiration_date = None
		if None == facebookID :
			ret = {}
			ret['err'] = 'facebookid'
			self.response.out.write(json.dumps(ret))
			return
		if None == name :
			ret = {}
			ret['err'] = 'name'
			self.response.out.write(json.dumps(ret))
			return
		ret = Account.api_login(facebookID,access_token,expiration_date,name)
		if None != ret['id']:
			del ret['id']
		ret['id'] = facebookID
		self.response.out.write(json.dumps(ret))

class AppAccountConvertHandler(webapp2.RequestHandler):
	def post(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		self.response.headers['Content-Type'] = 'application/json'
		facebookID = self.request.get('facebookid')
		guestID = self.request.get('guestid')
		name = self.request.get('name')
		access_token = self.request.get('access_token')
		expiration_date = self.request.get('expiration_date')
		if "" == access_token:
			access_token = None
		if "" == expiration_date:
			expiration_date = None
		if None == facebookID :
			ret = {}
			ret['err'] = 'facebookid'
			self.response.out.write(json.dumps(ret))
			return
		if None == guestID :
			ret = {}
			ret['err'] = 'guestid'
			self.response.out.write(json.dumps(ret))
			return
		if None == name :
			ret = {}
			ret['err'] = 'name'
			self.response.out.write(json.dumps(ret))
			return
		ret = Account.api_convert(facebookID,access_token,expiration_date,name,guestID)
		if False == ret['success']:
			ret = Account.api_login(facebookID,access_token,expiration_date,name)
		if None!=ret['id']:
			del ret['id']
		self.response.out.write(json.dumps(ret))

class AppAccountReadHandler(webapp2.RequestHandler):
	def get(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		facebookid = self.request.get('facebookid')
		ret = Account.api_read(facebookid)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

class AppAccountUpdateHandler(webapp2.RequestHandler):
	def post(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		self.response.headers['Content-Type'] = 'application/json'
		facebookid = self.request.get('facebookid')
		name = self.request.get('name')
		thumb = self.request.get('thumb')
		account = Account.get_by_facebookid(facebookid)
		params = {}
		params['name'] = self.request.get('name')
#		params['thumb'] = self.request.get('thumb')
		ret = Account.api_update(params,account)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

class AppAccountSubmitHandler(webapp2.RequestHandler):
	def post(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		self.response.headers['Content-Type'] = 'application/json'
		facebookid = self.request.get('facebookid')
		account = Account.get_by_facebookid(facebookid)
		params = {}
		params['money'] = self.request.get('money')
		params['candy'] = self.request.get('candy')
		params['score'] = self.request.get('score')
		params['maxscore'] = self.request.get('maxscore')
		params['id'] = self.request.get('id')
		logging.info('coin[%d] candy[%d] score[%d] max[%d]',
				int(params['money']),
				int(params['candy']),
				int(params['score']),
				int(params['maxscore']))
		ret = Account.api_submit(params,account)
#		params['cost'] = self.request.get('candy')
#		params['itemcost'] = self.request.get('money')
#		params['receipt_type'] = 'play'
#		Receipt.new(params,account)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

class AppAccountThumbnailHandler(webapp2.RequestHandler):
	def get(self):
		facebookid = self.request.get("img_id")
		account = Account.get_by_facebookid(str(facebookid))
		assert(account)
		if account.thumbnail:
			self.response.headers['Content-Type'] = "image/jpg"
			self.response.out.write(images.resize(account.thumbnail,50,50))
		else:
			self.response.out.write("no image")

#class AppAccountGiftHandler(storyengine.SessionHandler):
#	def post(self):
#		self.response.headers['Content-Type'] = 'application/json'
#		facebookid = self.request.get('facebookid')
#		account = Account.get_by_facebookid(facebookid)
#		money = self.request.get('money')
#		candy = self.request.get('candy')
#		Account.api_gift(money,candy,account)

