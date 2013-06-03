## coding: utf-8

__author__ = 'Seonghyun Kim'

import os
import webapp2
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from storyengine.model.account import Account
from storyengine.model.category import Category
from storyengine.model.story import Story
from storyengine.model.story import CategoryStoryLink
from django import forms
import storyengine
import storyengine.model
import json
import re
from defines import APP_TITLE
from defines import USER_AGENT
from defines import CATEGORY_LANGSUPPORT_SHOW

class CategoryForm(storyengine.model.TransForm):
	key_name = forms.CharField(label='(*) key_name (^[A-Z0-9]+)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class CategoryStoryAddForm(forms.Form):
	storyid = forms.CharField(label='storyid',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class CategoryIndexHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		categories = Category.all()
		categorylist = []
		keytodel = self.request.get('del')
		for c in categories:
			c.key_name = c.key().name()
			categorylist.append(c)
		categorysortedlist = sorted(categorylist, key=lambda p: p.index)

		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'size':Category.all().count(),
			'keytodel':keytodel,
			'langsupport':CATEGORY_LANGSUPPORT_SHOW,
			'categories':categorysortedlist}
		self.render_to_response('category_index.html',context)

class CategoryNewHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = CategoryForm(None)
		del s_form.fields['index']
		del s_form.fields['visible']
		del s_form.fields['price']
		del s_form.fields['expiration_days']
		del s_form.fields['expiration_mins']
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self): 
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		key_name = self.request.get('key_name')
		assert(None!=re.match('^[A-Z0-9]+', key_name))
		category = Category.new(key_name,account)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		category.setter(params)
		self.redirect('/category')

class CategoryStoryAddHandler(storyengine.SessionHandler):
	def get(self,category_name):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = CategoryStoryAddForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,category_name): 
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		storyid = self.request.get('storyid')
		category = Category.getter(category_name)
		story = Story.get_by_id(int(storyid))
		CategoryStoryLink.new(category,story)
		self.redirect('/category/'+category_name)

class CategoryReadHandler(storyengine.SessionHandler):
	def get(self,key_name):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		category = Category.getter(key_name)
		stories = []
		links = category.stories
		for link in links:
			story = link.story
			story.keyid = story.key().id()
			stories.append(story)
		storysortedlist = sorted(stories, key=lambda p: p.index)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'category':category,
			'stories':storysortedlist,
			'keyid':category.key().name()}
		self.render_to_response('category_read.html',context)

class CategoryUpdateHandler(storyengine.SessionHandler):
	def get(self,key_name):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		category = Category.getter(key_name)
		s_form = storyengine.model.TransForm.update_form(category)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,key_name):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		category = Category.getter(key_name)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		category.setter(params)
		self.redirect('/category')

class CategoryDelHandler(storyengine.SessionHandler):
	def get(self,key_name):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		category = Category.getter(key_name)
		for link in category.stories:
			link.delete()
		category.delete()
		self.redirect('/category')

class CategoryStoryDelHandler(storyengine.SessionHandler):
	def get(self, key_name, storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		category = Category.getter(key_name)
		story = Story.get_by_id(int(storyid))
		for link in category.stories:
			if int(storyid)==link.story.key().id():
				link.delete()
				break
		self.redirect('/category/'+key_name)

class CategoryLangNativeAddHandler(storyengine.SessionHandler):
	def get(self,categoryid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		category = Category.getter(categoryid)
		category.support_lang_add(lang)
		category.put()
		self.redirect('/category/'+categoryid)

class CategoryLangNativeDelHandler(storyengine.SessionHandler):
	def get(self,categoryid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		category = Category.getter(categoryid)
		category.support_lang_del(lang)
		category.put()
		self.redirect('/category/'+categoryid)

class CategoryLangToStudyAddHandler(storyengine.SessionHandler):
	def get(self,categoryid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		category = Category.getter(categoryid)
		category.support_tostudy_add(lang)
		category.put()
		self.redirect('/category/'+categoryid)

class CategoryLangToStudyDelHandler(storyengine.SessionHandler):
	def get(self,categoryid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		category = Category.getter(categoryid)
		category.support_tostudy_del(lang)
		category.put()
		self.redirect('/category/'+categoryid)

class AppCategoryIndexHandler(webapp2.RequestHandler):
	def get(self):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		lang = self.request.get('lang')
		tostudy = self.request.get('tostudy')
		logging.info('lang[%s] tostudy[%s]',lang,tostudy)
		if None == tostudy or "" == tostudy:
			tostudy = "en"

		ret = Category.api_index(lang,tostudy)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

class AppCategoryReadHandler(webapp2.RequestHandler):
	def get(self,keyID):
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		lang = self.request.get('lang')
		ret = Category.api_read(keyID, lang)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))
