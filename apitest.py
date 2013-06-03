## coding: utf-8
import os
import webapp2
from webapp2_extras import sessions
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from google.appengine.ext.webapp import template
from storyengine.model.category import Category
from storyengine.model.story import Story
from storyengine.model.story import Page
from storyengine.model.content import Content
from storyengine.model.links import AccountCategoryLink
from storyengine.model.links import AccountPageLink
from storyengine.model.account import Account
from storyengine.model.receipt import Receipt
import json

#from django import forms
from django import forms
#from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.template import Context, loader

import storyengine
import storyengine.model

class APIForm(forms.Form):
	testcode = forms.CharField(label='testcode',
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'10',
				'wrap':'hard',
				'class':'required',
				}))

class APItestAccountLoginHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		result = self.request.get('result')
		f_data = {
			'testcode':
			'{"facebookid":"1232","access_token":"assdf","name":"myname"}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/account/login?facebookid=%s&access_token=%s&name=%s"
		coutput = """[
			id=%s
			success=True/False
			created=True/False
		]"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		assert(testcode)
		d = json.loads(testcode)
		assert(d)
		exp_date = None
		det = Account.api_login(d['facebookid'],d['access_token'],exp_date,d['name'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestAccountReadHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		result = self.request.get('result')
		f_data = {
			'testcode':
			'{"facebookid":"asdf"}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/account?facebookid=%s"
		coutput = """[
			success=True/False
		]"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		assert(testcode)
		d = json.loads(testcode)
		assert(d)
		det = Account.api_read(d['facebookid'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestAccountSubmitHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		result = self.request.get('result')
		f_data = {
			'testcode':
			'{"score":"500","maxscore":"5000","candy":"1","money":2,"id":234}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/account/%d"
		coutput = """[
			success=True/False
		]"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		assert(testcode)
		d = json.loads(testcode)
		assert(d)
		params = {}
		params['money'] = d['money']
		params['candy'] = d['candy']
		params['score'] = d['score']
		params['maxscore'] = d['maxscore']
		params['id'] = d['id']
		det = Account.api_submit(params,account)
#		params['cost'] = d['candy']
#		params['itemcost'] = d['money']
#		params['receipt_type'] = 'play'
#		Receipt.new(params,account)
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestAccountConvertHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		result = self.request.get('result')
		f_data = {
			'testcode':
			'{"guestid":"asdf","facebookid":"5000","access_token":"at"}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/account/login?facebookid=%s&access_token=%s&name=%s&guestid=%s"
		coutput = """[
			success=True/False
		]"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		assert(testcode)
		d = json.loads(testcode)
		assert(d)
		d['name'] = "asdf"
		det = Account.api_convert(d['facebookid'],
				d['access_token'],
				None,
				d['name'],
				d['guestid'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestAccountGiftHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		result = self.request.get('result')
		f_data = {
			'testcode':
			'{"candy":"5","coin":1}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/account/%d"
		coutput = """[
		]"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		testcode = self.request.get('testcode')
		assert(testcode)
		d = json.loads(testcode)
		assert(d)
		det = Account.api_gift(d['coin'],d['candy'],account)
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestCategoryIndexHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"lang":"ko"}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/category"
		coutput = """success={success=True,stories=[%s,%s(key_name)]}
			error=NOT EXPECTED
		"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form,}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		det = Category.api_index(d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestCategoryReadHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"id":"TOEIC","lang":"ko"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/category/%d?lang=%s"
		coutput = """success={success=True,
		id=%s(key_name),index=%d,version=%d,visible=%d,
		expiration_date=%d,
		lang=%s,name=%s,description=%s,
		stories=[%s,%s,%s(key_id)]
		}
		error={success=False,error='the reason of error',
		id=%s(key_name),
		}
		"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		det = Category.api_read(d['id'],d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestStoryIndexHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		f_data = {
			'testcode':
			'{"lang":"ko"}'
		}
		s_form = APIForm(f_data)
		cinput = "/app/story?category=%s&lang=%s"
		coutput = """{
			stories=[%s,%s,%s,%s],
			success=True/False
		}"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form,}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		det = Story.api_index(d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestStoryReadHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"id":"4","lang":"ko"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/story/%d?lang=%s"
		coutput = """success={success=True,
		id=%s(key_id),index=%d,version=%d,visible=%d,
		expiration_date=%d,
		lang=%s,name=%s,description=%s,
		price=%d,main_categoryid=%s(key_name),
		pages=[%d(key_id),%d,%d,%d],
		purchased=True/False,
		}
		error={success=False,error='the reason of error',
		id=%s(key_id),
		}
		"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		det = Story.api_read(d['id'],d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestStoryPurchaseHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"id":"2"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/story/%d/purchase"
		coutput = """{
			id=%d,
			success=True/False
			error=%s
		}"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		testcode = self.request.get('testcode')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		d = json.loads(testcode)
		assert(d)
		det = Story.api_purchase(d['id'],accountid)
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestPageReadHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"id":"5","lang":"ko"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/page/%d?id=%d&lang=%s"
		coutput = """success={success=True,
		id=%s(key_id),index=%d,version=%d,visible=%d,
		expiration_date=%d,
		lang=%s,name=%s,description=%s,
		price=%d,score=%d,
		contents=[%d(key_id),%d,%d,%d],
		}
		error={success=False,error='the reason of error',
		id=%s(key_id),
		}
		"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		det = Page.api_read(d['id'],d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestContentReadHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"id":"5","lang":"ko","tostudy":"en"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/content/%d?lang=%s&tostudy=%s"
		coutput = """success={success=True,
		id=%s(key_id),index=%d,version=%d,visible=%d,
		expiration_date=%d,
		lang=%s,name=%s,description=%s,
		price=%d,
		part=%s,
		tran={
			lang=%s,name=%s,description=%s,
		},
		}
		error={success=False,error='the reason of error',
		id=%s(key_id),
		}
		"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		try:
			det = Content.api_read(d['id'],d['lang'],d['tostudy'])
		except:
			det = Content.api_read(d['id'],d['lang'])
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestReceiptSubmitHandler(storyengine.SessionHandler):
	def get(self):
		result = self.request.get('result')
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		f_data = {
			'testcode':
			'{"cost":"10","receipt_type":"money"}'
		}
		s_form = APIForm(f_data)

		cinput = "/app/receipt?cost=%d&receipt_type=%s"
		coutput = """{
			success=True/False
		}"""
		context = {'static_path': STATIC_PATH,
			'input':cinput,
			'output':coutput,
			'result':result,
			'form':s_form}
		self.render_to_response('apitest_index.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		testcode = self.request.get('testcode')
		d = json.loads(testcode)
		assert(d)
		params = {}
		params['dataID']=0
		params['cost']=d['cost']
		params['receipt_type']=d['receipt_type']
		det = Receipt.new(params,account)
		self.redirect(self.request.url + 'input?result='+str(det))

class APItestIndexHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		if None is accountid:
			context = {'static_path': STATIC_PATH,
			'err_msg':"You should login"}
			self.render_to_response('err_page.html',context)
			return

		context = {'static_path': STATIC_PATH}
		self.render_to_response('apitest_index.html',context)

